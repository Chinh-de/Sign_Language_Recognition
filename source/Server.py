from .Preprocessing import *
from .Model import *

import cv2
import mediapipe as mp
import time
import threading
from queue import Queue
import requests
import json
from google import genai
from google.genai import types
import logging
import string


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent





# # Khởi tạo pose từ MediaPipe
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()
# mp_drawing = mp.solutions.drawing_utils
# mp_drawing_styles = mp.solutions.drawing_styles

# Queue để model xử lý
action_queue = Queue()
recognized_words_queue = Queue()
# Cấu hình timeout
MAX_IDLE_FRAMES = 5
MIN_ACTIVE_FRAMES = 15
MAX_NO_NEW_WORD_FRAMES = 60 #2s 
MIN_WORDS_FOR_SENTENCE = 2  # Tối thiểu số từ để tạo câu

IP_Message = ""
last_word_or_sentence = ""

# get mapping index to word
index_to_word = {}
 
with open(BASE_DIR /"../Model/top_300_classes.txt", "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():  # bỏ dòng trống
            parts = line.strip().split("\t")  # tách theo tab
            if len(parts) == 2:
                index = int(parts[0])
                word = parts[1]
                index_to_word[index] = word

# get gemini APIKEY
with open(BASE_DIR /"../config.json", "r") as config_file:
    config = json.load(config_file)
    GEMINI_API_KEY = config["GEMINI_API_KEY"]


# -------- tạo Model --------

# Tạo model
asl_model = Sign2PoseTransformer()

state_dict = torch.load(BASE_DIR /'../Model/best_model.pth', map_location=torch.device('cpu'))
asl_model.load_state_dict(state_dict)
asl_model.eval() 



def preprocess_sequence(landmarks_dict):
    sequence = []

    # Sắp xếp theo thứ tự thời gian
    for frame_id in sorted(landmarks_dict.keys(), key=lambda x: int(x)):
        frame_data = landmarks_dict[frame_id]
        # Trường hợp thiếu right/left/pose thì thêm toàn 0
        pose = frame_data.get('pose', [(0.0, 0.0, 0.0)] * 33)
        right = frame_data.get('right', [(0.0, 0.0, 0.0)] * 21)
        left = frame_data.get('left', [(0.0, 0.0, 0.0)] * 21)

        all_landmarks = pose + right + left
        flattened = [coord for point in all_landmarks for coord in point]
        sequence.append(flattened)

    # Trả về PyTorch tensor
    return torch.tensor(sequence, dtype=torch.float32)





# === XỬ LÝ TRẠNG THÁI TAY ===
def check_action_state(pose_landmarks):
    left_wrist = pose_landmarks.landmark[15]
    right_wrist = pose_landmarks.landmark[16]
    left_hip = pose_landmarks.landmark[23]
    right_hip = pose_landmarks.landmark[24]

    hips_y = min(left_hip.y, right_hip.y)

    # Nếu cả 2 tay thấp hơn hông hoặc nằm ngoài khung hình
    if ((left_wrist.y * 1.1 > hips_y or left_wrist.y > 1) and
        (right_wrist.y * 1.1 > hips_y or right_wrist.y > 1)):
        return "IDLE"
    
    # Nếu 1 trong 2 tay cao hơn hông và trong khung hình
    if ((left_wrist.y < hips_y and left_wrist.y < 1) or
        (right_wrist.y < hips_y and right_wrist.y < 1)):
        return "ACTIVE"
    
    return "IDLE"

# === GỬI MESSAGE ĐẾN ESP32 ===
def send_message(ip_address, message):
    if ip_address == "":
        print("❌ Địa chỉ IP Message không hợp lệ.")
        return False
    try:
        # URL endpoint gửi tin nhắn
        url = f"http://{ip_address}/send"
        
        # Gửi request POST
        response = requests.post(url, data={"message": message})
        
        # Kiểm tra kết quả
        if response.status_code == 200:
            print(f"✅ Gửi tin nhắn thành công: {message}")
            return True
        else:
            print(f"❌ Lỗi gửi tin nhắn. Mã lỗi: {response.status_code}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Lỗi kết nối: {e}")
        return False

# === LUỒNG DỰ ĐOÁN GLOSS ===
def model_worker():
    global last_word_or_sentence
    global action_queue
    while True:
        segment = action_queue.get()
        if segment is None:
            break
        print(f"[MODEL] Nhận đoạn {len(segment)} frames để xử lý.")
        keyframes = Extract_key_frames(segment)
        landmarks_dict = extract_landmarks(keyframes)
        filtered_landmarks = filter_and_interpolate_landmarks(landmarks_dict)
        sign_spaces = calculate_all_sign_space(filtered_landmarks)
        normalized_landmarks = normalize_landmarks_to_sign_space(filtered_landmarks, sign_spaces)
        # print(normalized_landmarks)


        input_tensor = preprocess_sequence(normalized_landmarks)  # (frames, features)
        input_tensor = input_tensor.unsqueeze(0)  # (1, frames, features)

        # Dự đoán
        with torch.no_grad():
            output = asl_model(input_tensor)  # (1, num_gloss)
            predicted_idx = torch.argmax(output, dim=1).item()
            predict = index_to_word[predicted_idx]
            print("Predicted:", predict)
            send_message(IP_Message, predict)
            recognized_words_queue.put(predict)


            last_word_or_sentence = predict
            

        print(f"[MODEL] Đã xử lý xong đoạn {len(segment)} frames.")

        action_queue.task_done()


# === GENERATE SENTENCE ===

def clean_text_for_cv2(text: str) -> str:
    # Chỉ giữ lại các ký tự ASCII có thể in được
    return ''.join(char for char in text if char in string.printable)

def translate_glosses(glosses: str, api_key: str) -> str:
    client = genai.Client(api_key=api_key)

    prompt = f"Please translate the following ASL sign glosses into a complete and meaningful English sentence: {glosses}"
    system_instruction = (
        "You are an expert in translating ASL (American Sign Language) glosses "
        + " into grammatically correct and natural-sounding English sentences."
        + " Output only one sentence. If you can't generate a sentence, just return: can't generate."
    )

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[prompt],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            max_output_tokens=80,
        ),
    )

    return clean_text_for_cv2(response.text) if response.text else "Can't generate sentence"


# === LUỒNG TẠO CÂU ===

def sentence_worker():
    global last_word_or_sentence
    global recognized_words_queue
    if recognized_words_queue.qsize() >= MIN_WORDS_FOR_SENTENCE:
        print("[SENTENCE] Không có từ mới trong thời gian dài. Tạo câu...")
        words = ""
        while not recognized_words_queue.empty():
            word = recognized_words_queue.get()
            words += word + " "
        print(words)
        sentence = translate_glosses(words, GEMINI_API_KEY)
        print("[SENTENCE]", sentence)
        send_message(IP_Message,sentence)

        last_word_or_sentence = sentence
        print("[SENTENCE] Tạo câu: ", last_word_or_sentence)
    else:
        print("[SENTENCE] Không đủ từ để tạo câu.")


# Khởi chạy thread xử lý model
# threading.Thread(target=model_worker, daemon=True).start()


# url = "" #= 'http://192.168.187.31:81/stream'
# cap = cv2.VideoCapture(url) if url != "" else cv2.VideoCapture(0)




# frame_buffer = []
# idle_count = 0
# is_action_active = False

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         print("Không thể đọc frame từ camera.")
#         break

#     fps = cap.get(cv2.CAP_PROP_FPS)

#     image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = pose.process(image_rgb)

#     if results.pose_landmarks:
#         state = check_action_state(results.pose_landmarks)

#         # ACTIVE → đang thực hiện động tác
#         if state == "ACTIVE":
#             frame_buffer.append(frame.copy())
#             idle_count = 0
#             if not is_action_active:
#                 print("[INFO] → BẮT ĐẦU động tác")
#                 is_action_active = True

#         # IDLE → nghỉ tay
#         elif state == "IDLE":
#             idle_count += 1
#             if is_action_active:
                
#                 frame_buffer.append(frame.copy())

#                 if idle_count >= MAX_IDLE_FRAMES:
#                     print("[INFO] → KẾT THÚC động tác, đẩy vào model")

#                     # Cắt 5 frame IDLE cuối
#                     valid_segment = frame_buffer[:-MAX_IDLE_FRAMES] if len(frame_buffer) > MAX_IDLE_FRAMES else []

#                     if valid_segment:
#                         if len(valid_segment) > MIN_ACTIVE_FRAMES:
                        
#                             action_queue.put(valid_segment)
#                     # Reset
#                     frame_buffer.clear()
#                     idle_count = 0
#                     is_action_active = False
#             elif idle_count == MAX_NO_NEW_WORD_FRAMES:
#                 print("[INFO] → Không có động tác mới trong thời gian dài, tạo câu")
#                 threading.Thread(target=sentence_worker, daemon=True).start()         
#         # Vẽ trạng thái lên màn hình
        
        
        
#         mp_drawing.draw_landmarks(
#                 frame,
#                 results.pose_landmarks,
#                 mp_pose.POSE_CONNECTIONS,
#                 landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
#         frame = cv2.flip(frame, 1)

        
#         cv2.putText(frame, f"{last_word_or_sentence}", (10, 30), 
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

#         # Dòng hiển thị ở góc dưới trái cho FPS
#         cv2.putText(frame, f"FPS: {fps:.2f}", (10, frame.shape[0] - 70),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

#         # Dòng hiển thị ở góc dưới trái cho State
#         cv2.putText(frame, f"State: {state}", (10, frame.shape[0] - 30), 
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if state == "ACTIVE" else (0, 0, 255), 2)
        
#         cv2.imshow("Sign Language Capture", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

                
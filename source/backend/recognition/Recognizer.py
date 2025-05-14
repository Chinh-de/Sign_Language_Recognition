from .Preprocessing import *
from .ModelAI import *

import cv2
import mediapipe as mp
import time
import threading
from queue import Empty, Full, Queue
import requests
import json
from google import genai
from google.genai import types
import logging
import string


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent




# ======== Hằng số cấu hình ==========
# Cấu hình timeout
MAX_IDLE_FRAMES = 5
MIN_ACTIVE_FRAMES = 15
MAX_NO_NEW_WORD_FRAMES = 60 #2s 
MIN_WORDS_FOR_SENTENCE = 2  # Tối thiểu số từ để tạo câu


# ========== Biến Global ==========
# Queue để model xử lý
action_queue = Queue()
recognized_words_queue = Queue()

last_word_or_sentence = Queue(maxsize=1)
last_frame = None # Biến lưu frame cuối cùng
# ========== Kết Thúc Biến Global ==========



# ======== Hàm làm việc với last_word_or_sentence ==========
def update_last_w_s(text, is_word):
    global last_word_or_sentence
    try:
        # Lấy giá trị hiện tại của queue nếu có
        last_text, last_index = last_word_or_sentence.get_nowait()
    except:
        last_text, last_index = None, -1  # Nếu queue trống, gán giá trị mặc định
    
    # Xác định số lượng từ liên tiếp
    if not is_word:  # Nếu là câu
        index = 0
    else:
        if last_text is None:
            # Nếu queue trống, bắt đầu từ 1 cho từ đầu tiên
            index = 1
        else:
            # Lấy index từ phần tử cuối và cộng thêm 1
            index = last_index + 1
        
    # Cập nhật queue với (text, index)
    try:
        last_word_or_sentence.put_nowait((text, index))
    except Full:
        print("Queue is full. Cannot add more items.")

def get_last_w_s():
    global last_word_or_sentence
    # Lấy giá trị đầu tiên trong queue (nếu có)
    try:
        return last_word_or_sentence.queue[0]
    except IndexError:
        return ("", 0)
    

def get_last_frame():
    global last_frame
    return last_frame

# ========================================================= 





# get mapping index to word
index_to_gloss = {}
 
index_to_gloss_df = pd.read_csv(BASE_DIR /"../../../Model/index_to_gloss.csv")
for i, row in index_to_gloss_df.iterrows():
    index_to_gloss[row['index']] = row['gloss']

# get gemini APIKEY
with open(BASE_DIR /"../../../config.json", "r") as config_file:
    config = json.load(config_file)
    GEMINI_API_KEY = config["GEMINI_API_KEY"]



class Recognizer:
    def __init__(self, esp32Cam_ip, device_ip):
        self.esp32Cam_ip = esp32Cam_ip
        self.device_ip = device_ip
        self.model_thread = threading.Thread(target=self.model_worker, daemon=True)

        # khởi tạo biến quản lý luồng
        self.running = False
        self.stop_event = threading.Event()
        # Khởi tạo pose từ MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # -------- tạo Model --------
        self.asl_model = Sign2PoseTransformer()

        state_dict = torch.load(BASE_DIR /'../../../Model/best_model_22-4_87.pth', map_location=torch.device('cpu'))
        self.asl_model.load_state_dict(state_dict)
        self.asl_model.eval() 
        # ----------------------------


    def set_esp32_ip(self, esp32_ip):
        self.esp32Cam_ip = esp32_ip
    def set_device_ip(self, device_ip):
        self.device_ip = device_ip
    def get_status(self):
        return self.running
    

    
    
    def preprocess_sequence(self, landmarks_dict):
        sequence = []

        # Sắp xếp theo thứ tự thời gian
        for frame_id in sorted(landmarks_dict.keys(), key=lambda x: int(x)):
            frame_data = landmarks_dict[frame_id]
            # Trường hợp thiếu right/left/pose thì thêm toàn 0
            pose = frame_data.get('pose', [(0.0, 0.0, 0.0)] * 15)
            right = frame_data.get('right', [(0.0, 0.0, 0.0)] * 21)
            left = frame_data.get('left', [(0.0, 0.0, 0.0)] * 21)

            all_landmarks = pose + right + left
            flattened = [coord for point in all_landmarks for coord in point]
            sequence.append(flattened)

        # Trả về PyTorch tensor
        return torch.tensor(sequence, dtype=torch.float32)


    # === XỬ LÝ TRẠNG THÁI TAY ===
    def check_action_state(self, pose_landmarks):
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
    def send_message(self, message):
        if self.device_ip == None or self.device_ip == "None":
            print("Không dùng thiết bị.")
            return False
        try:
            # URL endpoint gửi tin nhắn
            url = f"http://{self.device_ip}/send"
            
            # Gửi request POST
            response = requests.post(url, data={"message": message})
            
            # Kiểm tra kết quả
            if response.status_code == 200:
                print(f"Gửi tin nhắn thành công: {message}")
                return True
            else:
                print(f"Lỗi gửi tin nhắn. Mã lỗi: {response.status_code}")
                return False
        
        except requests.exceptions.RequestException as e:
            print(f"Lỗi kết nối: {e}")
            return False

    # === LUỒNG DỰ ĐOÁN GLOSS ===
    def model_worker(self):
        global last_word_or_sentence
        global action_queue
        while not self.stop_event.is_set():
            segment = action_queue.get()
            if segment is None:
                continue
            print(f"[MODEL] Nhận đoạn {len(segment)} frames để xử lý.")
            keyframes = Extract_key_frames(segment)
            landmarks_dict = extract_landmarks(keyframes)
            filtered_landmarks = filter_and_interpolate_landmarks(landmarks_dict)
            sign_spaces = calculate_all_sign_space(filtered_landmarks)
            normalized_landmarks = normalize_landmarks_to_sign_space(filtered_landmarks, sign_spaces)


            input_tensor = self.preprocess_sequence(normalized_landmarks)  # (frames, features)
            input_tensor = input_tensor.unsqueeze(0)  # (1, frames, features)

            # Dự đoán
            with torch.no_grad():
                output = self.asl_model(input_tensor)  # (1, num_gloss)
                predicted_idx = torch.argmax(output, dim=1).item()
                predict = index_to_gloss[predicted_idx]
                print("Predicted:", predict)
                self.send_message(predict)
                recognized_words_queue.put(predict)


                update_last_w_s(predict, is_word=True)
                

            print(f"[MODEL] Đã xử lý xong đoạn {len(segment)} frames.")

            action_queue.task_done()
        print("[MODEL] Dừng nhận diện động tác.")

    # === GENERATE SENTENCE ===

   

    def translate_glosses(self , glosses: str, api_key: str) -> str:
        def clean_text_for_cv2(text: str) -> str:
            # Chỉ giữ lại các ký tự ASCII có thể in được
            return ''.join(char for char in text if char in string.printable)
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
                max_output_tokens=80, # Kích thước tối đa của màn LCD 20x4
            ),
        )

        return clean_text_for_cv2(response.text) if response.text else "Can't generate sentence"


    # === LUỒNG TẠO CÂU ===

    def sentence_worker(self):
        global last_word_or_sentence
        global recognized_words_queue
        if recognized_words_queue.qsize() >= MIN_WORDS_FOR_SENTENCE:
            print("[SENTENCE] Không có từ mới trong thời gian dài. Tạo câu...")
            words = ""
            while not recognized_words_queue.empty():
                word = recognized_words_queue.get()
                words += word + " "
            print(words)
            sentence = self.translate_glosses(words, GEMINI_API_KEY)
            print("[SENTENCE]", sentence)
            self.send_message(sentence)

            update_last_w_s(sentence, is_word=False)
        else:
            print("[SENTENCE] Không đủ từ để tạo câu.")


    # === khởi chạy nhận diện ===
    def start_recogniton(self):
        global last_frame
        global action_queue
        global recognized_words_queue
        global last_word_or_sentence
        print("[START] Bắt đầu nhận diện...")


        threading.Thread(target=self.model_worker, daemon=True).start()
        url = f"http://{self.esp32Cam_ip}:81/stream"
        cap = cv2.VideoCapture(url) if self.esp32Cam_ip != "local" else cv2.VideoCapture(0)
        fps = cap.get(cv2.CAP_PROP_FPS)

        frame_buffer = []
        idle_count = 0
        is_action_active = False
        self.running = True
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Không thể đọc frame từ camera.")
                break
            flip_frame = cv2.flip(frame, 1)
            image_rgb = cv2.cvtColor(flip_frame, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)

            if results.pose_landmarks:
                state = self.check_action_state(results.pose_landmarks)

                # ACTIVE → đang thực hiện động tác
                if state == "ACTIVE":
                    frame_buffer.append(frame.copy())
                    idle_count = 0
                    if not is_action_active:
                        print("[INFO] → BẮT ĐẦU động tác")
                        is_action_active = True

                # IDLE → nghỉ tay
                elif state == "IDLE":
                    idle_count += 1
                    if is_action_active:
                        
                        frame_buffer.append(frame.copy())

                        if idle_count >= MAX_IDLE_FRAMES:
                            print("[INFO] → KẾT THÚC động tác, đẩy vào model")

                            # Cắt các frame IDLE cuối
                            valid_segment = frame_buffer[:-MAX_IDLE_FRAMES] if len(frame_buffer) > MAX_IDLE_FRAMES else []

                            if valid_segment:
                                if len(valid_segment) > MIN_ACTIVE_FRAMES:
                                
                                    action_queue.put(valid_segment)
                            # Reset
                            frame_buffer.clear()
                            idle_count = 0
                            is_action_active = False
                    elif idle_count == MAX_NO_NEW_WORD_FRAMES:
                        print("[INFO] → Không có động tác mới trong thời gian dài, tạo câu")
                        threading.Thread(target=self.sentence_worker, daemon=True).start()  
                # Vẽ trạng thái lên
                self.mp_drawing.draw_landmarks(
                    flip_frame,
                    results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
            

            
            cv2.putText(flip_frame,
            f"{get_last_w_s()[0]}",  # Dòng hiển thị từ/câu
            (10, 40),                           # Vị trí: thấp chút cho vừa mắt
            cv2.FONT_HERSHEY_DUPLEX,           # Font rõ nét, dày vừa phải
            0.75,                                # Cỡ chữ lớn hơn
            (0, 0, 0),                      # Màu vàng nổi bật
            1,                                  # Độ dày viền chữ
            cv2.LINE_AA) 
            # Dòng hiển thị ở góc dưới trái cho FPS
            cv2.putText(flip_frame, f"FPS: {fps:.2f}", (10, frame.shape[0] - 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Dòng hiển thị ở góc dưới trái cho State
            cv2.putText(flip_frame, f"State: {state}", (10, frame.shape[0] - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if state == "ACTIVE" else (0, 0, 255), 2)
            
            last_frame = flip_frame
                
                

            # ========== for test ==========
            # cv2.imshow("ASL Recognition", flip_frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            # =============================

    def start(self):
        global last_frame
        global action_queue
        global recognized_words_queue
        global last_word_or_sentence
        self.stop_event.clear()
        threading.Thread(target=self.start_recogniton, daemon=True).start()
    

    def stop(self):
        global last_frame
        global action_queue
        global recognized_words_queue
        global update_last_w_s
        
        print("[STOP] Dừng nhận diện...")
        action_queue.put_nowait(None)
        # Dừng vòng lặp chính
        self.running = False

        # Dừng worker
        self.stop_event.set()

        # Xóa hàng đợi action_queue
        while not action_queue.empty():
            try:
                action_queue.get_nowait()
            except Empty:
                break

        # Xóa hàng đợi recognized_words_queue
        while not recognized_words_queue.empty():
            try:
                recognized_words_queue.get_nowait()
            except Empty:
                break

        # Làm rỗng last_word_or_sentence và last_frame
        update_last_w_s ("", False)  # Gán lại giá trị mặc định
        last_frame = None  # Làm rỗng last_frame

        print("[STOP] Đã dừng nhận diện.")
                    


# # ======== TEST ========

# def main():
#     # Địa chỉ IP test (có thể là giả lập, không cần dùng thật nếu chỉ test translate)
#     esp32_ip = "local"
#     device_ip = "None"

#     # Tạo đối tượng Recognizer
#     recognizer = Recognizer(esp32_ip, device_ip)

#     recognizer.start_recogniton()


# if __name__ == "__main__":
#     main()
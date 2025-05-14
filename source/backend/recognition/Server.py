from .Preprocessing import *
from .ModelAI import *

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
import uuid

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Khởi tạo lock chung
model_lock = threading.Lock()

# Mỗi session sẽ có queue và kết quả riêng
class SessionData:
    def __init__(self, session_id, device_ip=None):
        self.session_id = session_id
        self.action_queue = Queue()
        self.recognized_words_queue = Queue()
        self.last_word_or_sentence = ""
        self.is_running = True
        self.model_thread = None
        self.lock = threading.Lock()  # Lock riêng cho mỗi session
        self.device_ip = device_ip 

# Dictionary lưu dữ liệu của tất cả session
sessions = {}
sessions_lock = threading.Lock()

# Cấu hình timeout
MAX_IDLE_FRAMES = 5
MIN_ACTIVE_FRAMES = 15
MAX_NO_NEW_WORD_FRAMES = 60  # 2s
MIN_WORDS_FOR_SENTENCE = 2  # Tối thiểu số từ để tạo câu

# get mapping index to word
index_to_gloss = {}
 
index_to_gloss_df = pd.read_csv(BASE_DIR /"../../../Model/index_to_gloss.csv")
for i, row in index_to_gloss_df.iterrows():
    index_to_gloss[row['index']] = row['gloss']

# get gemini APIKEY
with open(BASE_DIR /"../../../config.json", "r") as config_file:
    config = json.load(config_file)
    GEMINI_API_KEY = config["GEMINI_API_KEY"]

# -------- tạo Model --------
# Tạo model
asl_model = Sign2PoseTransformer()

# Load model một lần duy nhất
def load_model():
    global asl_model
    with model_lock:
        state_dict = torch.load(BASE_DIR /'../../../Model/best_model_22-4_87.pth', map_location=torch.device('cpu'))
        asl_model.load_state_dict(state_dict)
        asl_model.eval()
        print("[INFO] Model loaded successfully")

# Tải model khi khởi động
load_model()

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
    if not ip_address:
        print("[INFO] Không có địa chỉ IP để gửi tin nhắn.")
        return False
    try:
        # URL endpoint gửi tin nhắn
        url = f"http://{ip_address}/send"
        
        # Gửi request POST
        response = requests.post(url, data={"message": message}, timeout=2)
        
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

# === LUỒNG DỰ ĐOÁN GLOSS CHO MỖI SESSION ===
def model_worker(session_id):
    # Lấy dữ liệu session
    with sessions_lock:
        if session_id not in sessions:
            print(f"[MODEL] Session {session_id} không tồn tại, dừng worker.")
            return
        session_data = sessions[session_id]
    
    print(f"[MODEL] Khởi động worker cho session {session_id}")
    
    # Chạy loop xử lý cho tới khi session dừng
    while session_data.is_running:
        try:
            # Đợi với timeout để có thể kiểm tra is_running
            try:
                segment = session_data.action_queue.get(timeout=120)
            except:
                continue
                
            print(f"[MODEL:{session_id}] Nhận đoạn {len(segment)} frames để xử lý.")
            
            try:
                # Tiền xử lý frames
                keyframes = Extract_key_frames(segment)
                landmarks_dict = extract_landmarks(keyframes)
                filtered_landmarks = filter_and_interpolate_landmarks(landmarks_dict)
                sign_spaces = calculate_all_sign_space(filtered_landmarks)
                normalized_landmarks = normalize_landmarks_to_sign_space(filtered_landmarks, sign_spaces)

                # Chuyển đổi dữ liệu cho model
                input_tensor = preprocess_sequence(normalized_landmarks)  # (frames, features)
                input_tensor = input_tensor.unsqueeze(0)  # (1, frames, features)

                # Dự đoán với model
                with model_lock, torch.no_grad():  # Sử dụng lock khi truy cập model
                    output = asl_model(input_tensor)  # (1, num_gloss)
                    predicted_idx = torch.argmax(output, dim=1).item()
                    predict = index_to_gloss[predicted_idx]
                    
                print(f"[MODEL:{session_id}] Predicted: {predict}")
                
                # Cập nhật kết quả vào session
                with session_data.lock:
                    session_data.last_word_or_sentence = predict
                    session_data.recognized_words_queue.put(predict)

                # Gửi tin nhắn đến ESP32device
                if session_data.device_ip:
                    print(f"[MODEL:{session_id}] Gửi tin nhắn '{predict}' đến {session_data.device_ip}")
                    send_message(session_data.device_ip, predict)
                
                # Đánh dấu công việc đã hoàn thành
                session_data.action_queue.task_done()
                
            except Exception as e:
                print(f"[MODEL:{session_id}] Lỗi xử lý segment: {str(e)}")
                session_data.action_queue.task_done()
                
        except Exception as e:
            print(f"[MODEL:{session_id}] Lỗi trong worker: {str(e)}")
            time.sleep(0.5)  # Tránh CPU cao trong trường hợp lỗi
    
    print(f"[MODEL:{session_id}] Worker đã dừng.")

# === CLEAN TEXT VÀ DỊCH GLOSS ===
def clean_text_for_cv2(text: str) -> str:
    # Chỉ giữ lại các ký tự ASCII có thể in được
    return ''.join(char for char in text if char in string.printable)

def translate_glosses(glosses: str, api_key: str) -> str:
    try:
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
    except Exception as e:
        print(f"[ERROR] Lỗi khi dịch glosses: {e}")
        return f"Error: {str(e)}"

# === LUỒNG TẠO CÂU CHO MỖI SESSION ===
def sentence_worker(session_id):
    # Lấy dữ liệu session
    with sessions_lock:
        if session_id not in sessions:
            print(f"[SENTENCE] Session {session_id} không tồn tại, không thể tạo câu.")
            return
        session_data = sessions[session_id]
    
    try:
        with session_data.lock:
            queue_size = session_data.recognized_words_queue.qsize()
            
        if queue_size >= MIN_WORDS_FOR_SENTENCE:
            print(f"[SENTENCE:{session_id}] Tạo câu từ {queue_size} từ...")
            words = []
            
            with session_data.lock:
                while not session_data.recognized_words_queue.empty():
                    word = session_data.recognized_words_queue.get()
                    words.append(word)
            
            words_text = " ".join(words)
            print(f"[SENTENCE:{session_id}] Glosses: {words_text}")
            
            # Dịch các từ thành câu
            sentence = translate_glosses(words_text, GEMINI_API_KEY)
            print(f"[SENTENCE:{session_id}] Câu: {sentence}")

            if sentence and session_data.device_ip:
                print(f"[SENTENCE:{session_id}] Gửi câu '{sentence}' đến {session_data.device_ip}")
                send_message(session_data.device_ip, sentence)
            
            # Cập nhật kết quả
            with session_data.lock:
                session_data.last_word_or_sentence = sentence
                
            return sentence
        else:
            print(f"[SENTENCE:{session_id}] Không đủ từ để tạo câu ({queue_size}/{MIN_WORDS_FOR_SENTENCE}).")
            return None
            
    except Exception as e:
        print(f"[SENTENCE:{session_id}] Lỗi khi tạo câu: {str(e)}")
        return None

# === TẠO SESSION MỚI ===
def create_session(device_ip=None):
    session_id = str(uuid.uuid4())
    
    with sessions_lock:
        # Tạo đối tượng dữ liệu session mới
        session_data = SessionData(session_id, device_ip)
        sessions[session_id] = session_data
        
        # Khởi động thread model_worker cho session này
        session_data.model_thread = threading.Thread(
            target=model_worker,
            args=(session_id,),
            daemon=True
        )
        session_data.model_thread.start()
    
    print(f"[INFO] Đã tạo session mới với ID: {session_id}, Device IP: {device_ip}")
    return session_id

# === DỪNG SESSION ===
def stop_session(session_id):
    with sessions_lock:
        if session_id in sessions:
            # Đánh dấu để dừng thread
            sessions[session_id].is_running = False
            # Đợi thread kết thúc (không block)
            
            # Xóa session khỏi dictionary
            del sessions[session_id]
            print(f"[INFO] Đã dừng session {session_id}")
            return True
        return False

# === LẤY DỮ LIỆU SESSION ===
def get_session_data(session_id):
    with sessions_lock:
        if session_id in sessions:
            return sessions[session_id]
        return None

# === THÊM FRAMES VÀO QUEUE CỦA SESSION ===
def add_action_to_queue(session_id, frames):
    with sessions_lock:
        if session_id in sessions:
            sessions[session_id].action_queue.put(frames)
            return True
        return False

# === LẤY KẾT QUẢ NHẬN DIỆN MỚI NHẤT CỦA SESSION ===
def get_latest_result(session_id):
    with sessions_lock:
        if session_id in sessions:
            with sessions[session_id].lock:
                return sessions[session_id].last_word_or_sentence
        return ""

# === KHỞI TẠO TẠO CÂU ===
def generate_sentence(session_id):
    t = threading.Thread(target=sentence_worker, args=(session_id,), daemon=True)
    t.start()
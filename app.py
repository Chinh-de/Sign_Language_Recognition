import streamlit as st
import cv2
import mediapipe as mp
from source import Server


MAX_IDLE_FRAMES = 5
MIN_ACTIVE_FRAMES = 15
MAX_NO_NEW_WORD_FRAMES = 60 #2s 

cap = None

# ==== Tiêu đề và giao diện ====
st.set_page_config(page_title="Sign Language Recognition", layout="wide")

st.markdown(
    """
    <style>
        /* Điều chỉnh độ rộng sidebar */
        .css-1d391kg {  
            width: 45% !important; 
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ==== Sidebar (Navbar) ====
st.sidebar.title("🤟 Hệ THống Nhận Diện Ngôn Ngữ Ký Hiệu")
st.sidebar.header("Tùy chọn")
source = st.sidebar.selectbox("Nguồn video", ["Webcam laptop", "ESP32-CAM"])
camera_url = ""
if source == "ESP32-CAM":
    camera_url = st.sidebar.text_input("Nhập IP ESP32cam (VD: 192.168.1.10)", "")
message_url = st.sidebar.text_input("Nhập URL gửi tin nhắn", "http://your-api-url.com/send")

    # = Nút điều khiển =
if "running" not in st.session_state:
    st.session_state.running = False
    if cap:
        cap.release()
        st.sidebar.success("Đã dừng nhận diện.")
    

start_btn = st.sidebar.button("▶️ Bắt đầu nhận diện")
stop_btn = st.sidebar.button("⏹️ Dừng")

if start_btn:
    st.session_state.running = True
if stop_btn:
    st.session_state.running = False



# ==== Khu vực hiển thị video ====
frame_placeholder = st.empty()
if st.session_state.running:    
    
    if source == "Webcam laptop":
        cap = cv2.VideoCapture(0)
    elif camera_url:
        camera_url = f"http://{camera_url}:81/stream"
        
        cap = cv2.VideoCapture(camera_url)
    else:
        st.error("Vui lòng nhập địa chỉ IP của ESP32-CAM")
        st.stop()
    
    # Khởi tạo pose từ MediaPipe
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    frame_buffer = []
    idle_count = 0
    is_action_active = False    
    # ==== Nhận diện và hiển thị ====
    Server.threading.Thread(target=Server.model_worker, daemon=True).start()

    while True:
        
        ret, frame = cap.read()
        if not ret:
            st.warning("Không nhận được ảnh từ camera!")
            break
        fps = cap.get(cv2.CAP_PROP_FPS)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(image_rgb)


        if results.pose_landmarks:
            state = Server.check_action_state(results.pose_landmarks)

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

                        # Cắt 5 frame IDLE cuối
                        valid_segment = frame_buffer[:-MAX_IDLE_FRAMES] if len(frame_buffer) > MAX_IDLE_FRAMES else None

                        if valid_segment:
                            if len(valid_segment) > MIN_ACTIVE_FRAMES:
                            
                                Server.action_queue.put(valid_segment)
                        # Reset
                        frame_buffer.clear()
                        idle_count = 0
                        is_action_active = False
                elif idle_count == MAX_NO_NEW_WORD_FRAMES:
                    print("[INFO] → Không có động tác mới trong thời gian dài, tạo câu")
                    Server.threading.Thread(target=Server.sentence_worker, daemon=True).start()         
            # Vẽ trạng thái lên màn hình
            
            
            
            mp_drawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            frame = cv2.flip(frame, 1)

            
            cv2.putText(frame, f"{Server.last_word_or_sentence}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Dòng hiển thị ở góc dưới trái cho FPS
            cv2.putText(frame, f"FPS: {fps:.2f}", (10, frame.shape[0] - 70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)

            # Dòng hiển thị ở góc dưới trái cho State
            cv2.putText(frame, f"State: {state}", (10, frame.shape[0] - 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if state == "ACTIVE" else (0, 0, 255), 2)


        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)
    










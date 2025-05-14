import logging
import threading
import time
from datetime import datetime, timedelta
import cv2
import mediapipe as mp
from . import Server

class SessionManager:
    def __init__(self):
        self.active_sessions = {}  # {session_id: session_info}
        self.session_threads = {}  # {session_id: thread}
        self.session_status = {}   # {session_id: status} 
        self.session_last_ping = {}  # {session_id: timestamp}
        self.is_running = True
        self.ping_timeout = 30  # 30 giây không ping -> chuyển sang ngầm
        self.session_frame_locks = {} 
        
        # Lock để bảo vệ các biến dùng chung
        self.sessions_lock = threading.Lock()
    
    def start(self):
        """Khởi động manager và thread kiểm tra ping"""
        # Thread kiểm tra trạng thái ping của các session
        self.ping_check_thread = threading.Thread(target=self._check_ping_status, daemon=True)
        self.ping_check_thread.start()
    
    def _check_ping_status(self):
        """Định kỳ kiểm tra và chuyển sang BACKGROUND nếu không có ping"""
        while self.is_running:
            time.sleep(10)  # Kiểm tra mỗi 10 giây
            
            try:
                # Lấy thời điểm hiện tại
                now = datetime.now()
                timeout_threshold = now - timedelta(seconds=self.ping_timeout)
                
                with self.sessions_lock:
                    # Tạo bản sao để tránh RuntimeError khi thay đổi dict trong vòng lặp
                    sessions_to_check = list(self.session_status.keys())
                
                # Kiểm tra từng session
                for session_id in sessions_to_check:
                    with self.sessions_lock:
                        # Chỉ kiểm tra session đang ONLINE
                        if (session_id in self.session_status and 
                            self.session_status[session_id] == 'ONLINE' and
                            session_id in self.session_last_ping):
                            
                            last_ping = self.session_last_ping[session_id]
                            
                            # Nếu không ping trong 30s -> chuyển sang ngầm
                            if last_ping < timeout_threshold:
                                self.session_status[session_id] = 'BACKGROUND'
                                print(f"Session {session_id} chuyển sang ngầm (không ping)")
                
            except Exception as e:
                print(f"Lỗi kiểm tra ping: {e}")
    
    def process_session(self, session_id):
        """Xử lý một phiên nhận diện"""
        with self.sessions_lock:
            if session_id not in self.active_sessions:
                return
            session_info = self.active_sessions[session_id]
        
        cap = session_info['cap']
        pose = session_info['pose']
        mp_drawing = session_info['mp_drawing']
        mp_pose = session_info['mp_pose']
        server_session_id = session_info['server_session_id']
        esp32device_ip = session_info.get('esp32device_ip')
        
        frame_buffer = []
        idle_count = 0
        is_action_active = False
        
        # Các giá trị timeout
        MAX_IDLE_FRAMES = 5
        MIN_ACTIVE_FRAMES = 15
        MAX_NO_NEW_WORD_FRAMES = 60
        
        # Vòng lặp xử lý
        while self.is_running:
            try:
                # Kiểm tra trạng thái session
                with self.sessions_lock:
                    if (session_id not in self.active_sessions or 
                        session_id not in self.session_status or
                        self.session_status[session_id] == 'INACTIVE'):
                        # Session không tồn tại hoặc không hoạt động
                        break
                
                # Đọc frame từ camera
                success, frame = cap.read()
                if not success:
                    # Không đọc được frame -> đánh dấu inactive
                    self._mark_inactive(session_id, "Không đọc được frame từ camera")
                    break
                
                # Xử lý frame với MediaPipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    state = Server.check_action_state(results.pose_landmarks)

                    # ACTIVE → đang thực hiện động tác
                    if state == "ACTIVE":
                        frame_buffer.append(frame.copy())
                        idle_count = 0
                        if not is_action_active:
                            print(f"[Session {session_id}] → BẮT ĐẦU động tác")
                            is_action_active = True

                    # IDLE → nghỉ tay
                    elif state == "IDLE":
                        idle_count += 1
                        if is_action_active:
                            frame_buffer.append(frame.copy())

                            if idle_count >= MAX_IDLE_FRAMES:
                                print(f"[Session {session_id}] → KẾT THÚC động tác, đẩy vào model")

                                # Cắt 5 frame IDLE cuối
                                valid_segment = frame_buffer[:-MAX_IDLE_FRAMES] if len(frame_buffer) > MAX_IDLE_FRAMES else []

                                if valid_segment and len(valid_segment) > MIN_ACTIVE_FRAMES:
                                    # Đưa frames vào queue xử lý của Server session riêng
                                    Server.add_action_to_queue(server_session_id, valid_segment)
                                    
                                # Reset
                                frame_buffer.clear()
                                idle_count = 0
                                is_action_active = False
                        elif idle_count == MAX_NO_NEW_WORD_FRAMES:
                            print(f"[Session {session_id}] → Không có động tác mới, tạo câu")
                            # Gọi hàm tạo câu của Server cho session cụ thể
                            Server.generate_sentence(server_session_id)
                      # Kiểm tra trạng thái session (một lần duy nhất)
                    is_online = False
                    with self.sessions_lock:
                        is_online = (session_id in self.session_status and 
                                    self.session_status[session_id] == 'ONLINE')
                    
                    # Xử lý frame để hiển thị (chỉ khi ONLINE)
                    if is_online:
                        processed_frame = frame.copy()
                        mp_drawing.draw_landmarks(
                            processed_frame,
                            results.pose_landmarks,
                            mp_pose.POSE_CONNECTIONS)
                        
                        processed_frame = cv2.flip(processed_frame, 1)
                        
                        # Lấy kết quả nhận diện mới nhất từ Server
                        latest_result = Server.get_latest_result(server_session_id)
                        
                        cv2.putText(processed_frame, latest_result, (10, 40),
                                    cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 1, cv2.LINE_AA)
                        
                        fps = cap.get(cv2.CAP_PROP_FPS)
                        cv2.putText(processed_frame, f"FPS: {fps:.2f}", (10, processed_frame.shape[0] - 70),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        
                        cv2.putText(processed_frame, f"State: {state}", (10, processed_frame.shape[0] - 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0) if state == "ACTIVE" else (0, 0, 255), 2)
                        
                        # Cập nhật frame mới nhất (với lock riêng biệt)
                        with self.session_frame_locks[session_id]:
                            self.active_sessions[session_id]['last_frame'] = processed_frame
                        
            except Exception as e:
                print(f"Lỗi xử lý session {session_id}: {e}")
        
        # Khi thoát vòng lặp, dọn dẹp tài nguyên
        self._cleanup_session_resources(session_id)
    
    def _cleanup_session_resources(self, session_id):
        """Giải phóng tài nguyên khi session kết thúc"""
        with self.sessions_lock:
            if session_id in self.active_sessions:
                session_info = self.active_sessions[session_id]
                
                # Giải phóng camera
                if 'cap' in session_info and session_info['cap']:
                    session_info['cap'].release()
                
                # Dừng session ở Server.py
                if 'server_session_id' in session_info:
                    Server.stop_session(session_info['server_session_id'])
                
                # Xóa khỏi các dictionary
                del self.active_sessions[session_id]
                
                if session_id in self.session_status:
                    del self.session_status[session_id]
                
                if session_id in self.session_last_ping:
                    del self.session_last_ping[session_id]
                
            if session_id in self.session_threads:
                del self.session_threads[session_id]
    
    def start_session(self, session_id, esp32cam_ip, esp32device_ip=None):
        """Bắt đầu một phiên nhận diện mới"""
        # Tạo session mới trong Server.py
        server_session_id = Server.create_session(device_ip=esp32device_ip)
        
        # Thiết lập camera
        camera_url = f"http://{esp32cam_ip}:81/stream"
        if esp32cam_ip == "local":
            cap = cv2.VideoCapture(0)  # Sử dụng camera local
        else:
            cap = cv2.VideoCapture(camera_url)
        
        if not cap.isOpened():
            # Nếu không mở được camera, dừng session ở Server.py
            Server.stop_session(server_session_id)
            return False
        
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose()  # Dùng các tham số mặc định
        mp_drawing = mp.solutions.drawing_utils
        
        
        # Lưu thông tin phiên
        with self.sessions_lock:
            self.active_sessions[session_id] = {
                'cap': cap,
                'pose': pose,
                'mp_pose': mp_pose,
                'mp_drawing': mp_drawing,
                'esp32cam_ip': esp32cam_ip,
                'esp32device_ip': esp32device_ip,
                'server_session_id': server_session_id,
                'last_frame': None,
                'last_result': "",
                'created_at': datetime.now()
            }
            
            # Lưu trạng thái và thời gian ping cuối
            self.session_status[session_id] = 'ONLINE'
            self.session_last_ping[session_id] = datetime.now()
            self.session_frame_locks[session_id] = threading.Lock()
        
        # Bắt đầu thread xử lý
        thread = threading.Thread(target=self.process_session, args=(session_id,), daemon=True)
        with self.sessions_lock:
            self.session_threads[session_id] = thread
        thread.start()

        logging.info(f"Session {session_id} đã được khởi tạo và bắt đầu xử lý")
        
        return True
    
    def stop_session(self, session_id):
        """Dừng một phiên nhận diện"""
        self._mark_inactive(session_id, "Dừng theo yêu cầu người dùng")
    
    def _mark_inactive(self, session_id, reason=""):
        """Đánh dấu session không hoạt động"""
        with self.sessions_lock:
            if session_id in self.session_status:
                self.session_status[session_id] = 'INACTIVE'
                print(f"Session {session_id} đã chuyển sang INACTIVE: {reason}")
                
                # Dừng session ở Server.py
                if session_id in self.active_sessions:
                    Server.stop_session(self.active_sessions[session_id]['server_session_id'])
    
    def update_ping(self, session_id):
        """Cập nhật thời gian ping (không thay đổi trạng thái)"""
        with self.sessions_lock:
            if session_id in self.session_status:
                current_status = self.session_status[session_id]
                
                # Chỉ cập nhật thời gian ping, không chuyển trạng thái
                if current_status != 'INACTIVE':
                    self.session_last_ping[session_id] = datetime.now()
                    return True, current_status
                return False, 'INACTIVE'
            return False, 'NOT_FOUND'
    
    def get_latest_frame(self, session_id):
        if session_id in self.active_sessions and session_id in self.session_frame_locks:
            with self.session_frame_locks[session_id]:
                return self.active_sessions[session_id]['last_frame']
        return None
        
    def get_latest_result(self, session_id):
        """Lấy kết quả nhận diện mới nhất"""
        with self.sessions_lock:
            if session_id in self.active_sessions:
                server_session_id = self.active_sessions[session_id]['server_session_id']
                logging.info(f"Session {session_id} đang lấy kết quả mới nhất từ server")
                return Server.get_latest_result(server_session_id)
            return ""
    
    def get_session_status(self, session_id):
        """Lấy trạng thái hiện tại của session"""
        with self.sessions_lock:
            if session_id in self.session_status:
                return self.session_status[session_id]
            return None
    
    def shutdown(self):
        """Dừng tất cả các phiên khi server tắt"""
        self.is_running = False
        
        # Dừng tất cả các phiên
        with self.sessions_lock:
            session_ids = list(self.active_sessions.keys())
        
        for session_id in session_ids:
            self.stop_session(session_id)

# Khởi tạo instance global
session_manager = SessionManager()
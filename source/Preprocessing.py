import os
import pandas as pd
import numpy as np
import cv2
from matplotlib import pyplot as plt
import mediapipe as mp


# -------- Trích xuất keyframes --------
def getGrayFramesAndFrames(frame_buffer):
    gray_frames = [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frame_buffer]
    return gray_frames

def calculate_histogram_differences(gray_frames):
    HDiffs = []
    # Duyệt qua tất cả các frame trừ frame cuối vì thường là frame không có giá trị
    for i in range(0, len(gray_frames)-1):
        if (i == 0):
        #[gray_frames[i]]: grayframe thứ i, [0] kênh chứa độ sáng, None: tính toàn bộ ảnh, không dùng mask, [256]: 256 bins, 0 <=[0, 256]: giá trị pixel < 256
            hist_curr = cv2.calcHist([gray_frames[i]], [0], None, [256], [0, 256])
            continue
        # Gán frame ở vòng lặp trước cho hist_prev và tính lại hist_curr
        hist_prev = hist_curr
        hist_curr = cv2.calcHist([gray_frames[i]], [0], None, [256], [0, 256])

        Hdiff = np.sum(np.abs(hist_prev - hist_curr))
        HDiffs.append(Hdiff)
    return HDiffs

def Extract_key_frames(frames, factor = 0.5):
    gray_frames = getGrayFramesAndFrames(frames)
    HDiffs = calculate_histogram_differences(gray_frames)
    mean = np.mean(HDiffs)
    std = np.std(HDiffs)
    threshold = mean + factor * std
    # Chọn keyframes dựa trên ngưỡng
    keyframes = []
    for i in range(len(HDiffs)):
        if HDiffs[i] > threshold:
            # Lấy frame i+1 vì Hdiffs[i] là độ khác biệt của frame thứ i +1 với thứ i
            keyframes.append(frames[i+1])
    return keyframes



# -------- Trích xuất landmarks --------
def euclidean_distance(v1, v2):
    return np.sqrt((float(v1[0]) - float(v2[0])) ** 2 + (float(v1[1]) - float(v2[1])) ** 2)

def extract_pose_landmarks(rgb_frame, mp_pose):
    pose_results = mp_pose.process(rgb_frame)
    pose_landmarks = []

    if pose_results.pose_landmarks:
        for i, lm in enumerate(pose_results.pose_landmarks.landmark):
            if i < 17 and i not in [7, 8]:  # Loại bỏ từ hông trở xuống và 2 tai
                pose_landmarks.append((lm.x, lm.y))

    return pose_landmarks

def classify_hands (pose_landmarks, hand_landmarks):
    left_wrist_pose  = pose_landmarks[13]  # Cổ tay trái từ Pose là 15 trừ đi 2 tai đã lượt bỏ nên idx = 13
    right_wrist_pose = pose_landmarks[14]  # Cổ tay phải từ Pose là 16 trừ đi 2 tai đã lượt bỏ nên idx = 14
    wrist = hand_landmarks[0] 
    

    dleft = euclidean_distance(left_wrist_pose, wrist)
    dright = euclidean_distance(right_wrist_pose, wrist)
   
    if(dleft < dright):
        return "Left"
    else:
        return "Right"
    

def extract_hand_landmarks(rgb_frame, mp_hands, pose_landmarks):
    hands_results = mp_hands.process(rgb_frame)
    left_hand_landmarks = []
    right_hand_landmarks = []
    

    if hands_results.multi_hand_landmarks and hands_results.multi_handedness:
        for hand_landmarks, handedness in zip(hands_results.multi_hand_landmarks, hands_results.multi_handedness):
            # Không sử dụng hướng tay của mediapipe vì độ chính xác thấp và thường ngược hướng
            landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]
            if classify_hands(pose_landmarks, landmarks) == "Right":
                right_hand_landmarks = landmarks
            else:
                left_hand_landmarks = landmarks   



        
    
    return left_hand_landmarks, right_hand_landmarks


def extract_landmarks(frames):
    mp_pose = mp.solutions.pose.Pose(static_image_mode=True)
    mp_hands = mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.1)
    
    landmarks_dict = {}
    
    for idx, frame in enumerate(frames):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        pose_landmarks = extract_pose_landmarks(rgb_frame, mp_pose)
        left_hand_landmarks, right_hand_landmarks = extract_hand_landmarks(rgb_frame, mp_hands ,pose_landmarks)
        
        landmarks_dict[idx] = {
            "pose": pose_landmarks,
            "left": left_hand_landmarks,
            "right": right_hand_landmarks
        }
    #giải phóng tài nguyên
    mp_pose.close()
    mp_hands.close()
    return landmarks_dict


def filter_invalid_landmarks(landmarks_dict):
    validated = {}
    for landmarks_idx, landmarks_data in landmarks_dict.items():
        validated_landmarks = {}
        # Nếu không có pose thì bỏ qua frame
        if  not landmarks_data["pose"]:
            continue
        for part in ["pose", "right", "left"]:
            # Nếu không có dữ liệu cho phần này, gán mặc định
            if part not in landmarks_data or not landmarks_data[part]:
                if part in ["right", "left"]:
                    validated_landmarks[part] = [(0.0, 0.0)] * 21
            else:
                processed_points = []
                for point in landmarks_data[part]:
                    x = float(point[0])
                    y = float(point[1])
                    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
                        x, y = 0.0, 0.0
                    processed_points.append((x, y))
                validated_landmarks[part] = processed_points
        validated[landmarks_idx] = validated_landmarks
    return validated


# -------- Chuẩn hóa --------

def calculate_head_unit(pose_landmarks):

    left_eye, right_eye = pose_landmarks[3], pose_landmarks[6]
    # mép ngoài 2 mắt
    head_unit = euclidean_distance(left_eye,right_eye)
    return head_unit


def calculate_sign_space(pose_landmarks):
    head_unit = calculate_head_unit(pose_landmarks)

    nose = pose_landmarks[0]
   
   
    width = 7 * head_unit
    # height = 9.5 * head_unit 
    
    center_x, center_y = nose

    x1 = center_x - width / 2

    y1 = center_y - 1.5 * head_unit  # Cạnh trên cách 1,5 head unit
    x2 = center_x + width / 2
    # y2 = min(1.0 , int(center_y + 7.5 * head_unit))
    y2 = center_y + 8 * head_unit 
    return [x1, y1, x2, y2]


def calculate_all_sign_space(landmarks_dict):
    sign_spaces = {}
    for idx, landmarks_data in landmarks_dict.items():
        sign_spaces[idx] = calculate_sign_space(landmarks_data["pose"])
    return sign_spaces

def normalize_landmarks_to_sign_space(landmarks_dict, sign_spaces):
    
    normalized = {}
    for landmarks_idx, landmarks_data in landmarks_dict.items():
        Xmin, Ymin, Xmax, Ymax = sign_spaces[landmarks_idx]
        w = Xmax - Xmin
        h = Ymax - Ymin
        normalized_landmarks = {}
        for part in ["pose", "right", "left"]:
            processed_points = []
            for point in landmarks_data[part]:
                x = float(point[0])
                y = float(point[1])
                if x != 0.0 and y != 0.0:
                   x = (x - Xmin) / w
                   y = (y - Ymin) / h
                processed_points.append((x, y))
            normalized_landmarks[part] = processed_points
        normalized[landmarks_idx] = normalized_landmarks
    return normalized

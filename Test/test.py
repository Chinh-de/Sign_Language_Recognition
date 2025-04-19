# import cv2
# import mediapipe as mp

# # Khởi tạo MediaPipe Pose
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose()

# # Tạo cửa sổ để hiển thị video
# cap = cv2.VideoCapture(0)
# # url = 'http://192.168.187.31:81/stream'  # Thay đúng IP 
# # cap = cv2.VideoCapture(url)
# # Tạo cửa sổ với tên 'Pose Landmarks' và thay đổi kích thước
# cv2.namedWindow('Pose Landmarks', cv2.WINDOW_NORMAL)
# cv2.resizeWindow('Pose Landmarks', 1200, 800)  # Điều chỉnh kích thước cửa sổ

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         continue

#     # Chuyển đổi ảnh thành RGB vì MediaPipe yêu cầu
#     image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#     # Phát hiện pose landmarks
#     results = pose.process(image_rgb)

#     if results.pose_landmarks:
#         # Vẽ pose landmarks lên ảnh
#         for landmark in results.pose_landmarks.landmark:
#             # Lấy x, y, z từ các landmarks
#             x = int(landmark.x * frame.shape[1])
#             y = int(landmark.y * frame.shape[0])
#             z = landmark.z  # Giá trị z

#             # Bỏ các điểm liên quan đến đầu (nose, eyes, ears, mouth)
#             # Chúng ta chỉ vẽ các điểm không phải đầu như shoulder, elbow, wrist, v.v.
#             if landmark == results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EYE] or \
#                landmark == results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EYE] or \
#                landmark == results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR] or \
#                landmark == results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR] or \
#                landmark == results.pose_landmarks.landmark[mp_pose.PoseLandmark.MOUTH_LEFT] or \
#                landmark == results.pose_landmarks.landmark[mp_pose.PoseLandmark.MOUTH_RIGHT]:
#                 continue  # Bỏ qua các điểm của đầu

#             # Vẽ các điểm còn lại lên ảnh
#             cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

#             # In ra giá trị z
#             cv2.putText(frame, f'Z: {z:.2f}', (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
    
#     # Hiển thị ảnh đã vẽ landmarks
#     cv2.imshow('Pose Landmarks', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()






# # import cv2
# # import mediapipe as mp

# # # Khởi tạo MediaPipe Hands
# # mp_hands = mp.solutions.hands
# # hands = mp_hands.Hands(static_image_mode=False,
# #                        max_num_hands=2,
# #                        min_detection_confidence=0.5,
# #                        min_tracking_confidence=0.5)

# # # Dùng drawing utils
# # mp_drawing = mp.solutions.drawing_utils
# # mp_hand_landmarks = mp_hands.HandLandmark

# # # Chỉ lấy các đầu ngón tay
# # finger_tips = [
# #     mp_hand_landmarks.THUMB_TIP,
# #     mp_hand_landmarks.INDEX_FINGER_TIP,
# #     mp_hand_landmarks.MIDDLE_FINGER_TIP,
# #     mp_hand_landmarks.RING_FINGER_TIP,
# #     mp_hand_landmarks.PINKY_TIP
# # ]

# # # Mở webcam
# # cap = cv2.VideoCapture(0)

# # cv2.namedWindow('Finger Tips', cv2.WINDOW_NORMAL)
# # cv2.resizeWindow('Finger Tips', 1200, 800)

# # while cap.isOpened():
# #     ret, frame = cap.read()
# #     if not ret:
# #         break

# #     # Chuyển ảnh sang RGB
# #     image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #     results = hands.process(image_rgb)

# #     if results.multi_hand_landmarks:
# #         for hand_landmarks in results.multi_hand_landmarks:
# #             h, w, _ = frame.shape

# #             for idx in finger_tips:
# #                 lm = hand_landmarks.landmark[idx]
# #                 x, y, z = int(lm.x * w), int(lm.y * h), lm.z

# #                 cv2.circle(frame, (x, y), 8, (0, 255, 0), -1)
# #                 cv2.putText(frame, f'{idx} Z:{z:.2f}', (x + 5, y - 5),
# #                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

# #     cv2.imshow('Finger Tips', frame)

# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()




import cv2
import mediapipe as mp

# Khởi tạo MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Dùng drawing utils
mp_drawing = mp.solutions.drawing_utils

# Mở camera
url = 'http://192.168.187.31:81/stream'  # Thay đúng IP 
cap = cv2.VideoCapture(url)
cv2.namedWindow('Pose Landmarks', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Pose Landmarks', 1200, 800)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        continue

    # Chuyển sang RGB cho MediaPipe
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        h, w, _ = frame.shape

        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            z = landmark.z

            # Bỏ qua các điểm đầu (để đỡ rối)
            if idx in [
                mp_pose.PoseLandmark.NOSE.value,
                mp_pose.PoseLandmark.LEFT_EYE.value,
                mp_pose.PoseLandmark.RIGHT_EYE.value,
                mp_pose.PoseLandmark.LEFT_EAR.value,
                mp_pose.PoseLandmark.RIGHT_EAR.value,
                mp_pose.PoseLandmark.MOUTH_LEFT.value,
                mp_pose.PoseLandmark.MOUTH_RIGHT.value
            ]:
                continue

            # Vẽ điểm
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

            # Gắn nhãn điểm
            name = mp_pose.PoseLandmark(idx).name  # tên landmark, ví dụ LEFT_SHOULDER
            cv2.putText(frame, f'{name}', (x + 5, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1, cv2.LINE_AA)

    # Hiển thị frame
    cv2.imshow('Pose Landmarks', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

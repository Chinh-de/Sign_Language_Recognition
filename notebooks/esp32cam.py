import cv2

# wifi : esp32
# pass : phuc1502

# Nếu ip thay đổi bật arduino ide
# vào phần serial monitor, thay đổi baud 115200 --> ấn reset cam --> hiển thị ip mới

url = 'http://192.168.187.31:81/stream'  # Thay đúng IP 
cap = cv2.VideoCapture(url)

while True:
    ret, frame = cap.read()
    if not ret:
        print("NOOO")
        break
    cv2.imshow('ESP32-CAM Stream', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
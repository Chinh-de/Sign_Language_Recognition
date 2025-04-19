import requests

def send_message(ip_address, message):
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

def main():
    # Nhập địa chỉ IP
    ESP32_IP = input("Nhập địa chỉ IP của ESP32 (VD: 192.168.1.100): ")
    
    while True:
        # Nhập tin nhắn từ bàn phím
        message = input("Nhập tin nhắn (Enter để thoát): ")
        
        if message == "":
            break
        
        send_message(ESP32_IP, message)

if __name__ == "__main__":
    main()
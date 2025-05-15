
# ASL Sign Language Recognition System

This project is a sign language recognition system using deep learning and various computer vision techniques. It uses mediapipe for hand landmarks detection and PyTorch for model inference.

## Requirements

To get started, you'll need to install the required Python libraries. You can do this by running:

```bash
pip install -r requirements.txt
```

This will install the following dependencies:

- torch
- scikit-learn
- matplotlib
- pandas
- numpy
- opencv-python
- mediapipe
- tqdm
- requests
- google-genai

## Setup Google Cloud API Key

1. Go to [Google AI Studio](https://aistudio.google.com/apikey) and log in with your Google account.
2. Click on the "Generate API Key" button to get your unique API key.
3. Create a `config.json` file in the root directory of this project.
4. Add the following content to `config.json`, replacing `YOUR_API_KEY` with the API key you just obtained:

```json
{
    "GEMINI_API_KEY": "YOUR_API_KEY"
}
```

## Run the Application

After setting up the environment and API key, you can run the Streamlit application using the following command:

```bash
streamlit run app.py --server.runOnSave=false
```

This command will start the application locally. Open the browser and navigate to the provided URL (usually `http://localhost:8501`) to use the ASL recognition system.

## Notes

- Make sure to have the necessary hardware and camera set up for live video feed.
- Ensure your Python environment is set up with all required libraries.
- If you're running the app in a virtual environment, make sure to activate it before installing dependencies or running the app.

---

# Hệ thống nhận diện ngôn ngữ ký hiệu ASL

Dự án này là một hệ thống nhận diện ngôn ngữ ký hiệu ASL (American Sign Language) sử dụng học sâu và các kỹ thuật xử lý ảnh. Nó sử dụng mediapipe để phát hiện các điểm đặc trưng của bàn tay và PyTorch để suy luận mô hình.

## Yêu cầu

Để bắt đầu, bạn cần cài đặt các thư viện Python yêu cầu. Bạn có thể làm điều này bằng cách chạy:

```bash
pip install -r requirements.txt
```

Lệnh trên sẽ cài đặt các phụ thuộc sau:

- torch
- scikit-learn
- matplotlib
- pandas
- numpy
- opencv-python
- mediapipe
- tqdm
- requests
- google-genai

## Cấu hình API Key của Google Cloud

1. Truy cập [Google AI Studio](https://aistudio.google.com/apikey) và đăng nhập bằng tài khoản Google của bạn.
2. Nhấn nút "Generate API Key" để tạo API key duy nhất của bạn.
3. Tạo một file `config.json` trong thư mục gốc của dự án.
4. Thêm nội dung sau vào file `config.json`, thay thế `YOUR_API_KEY` bằng API key bạn vừa lấy được:

```json
{
    "GEMINI_API_KEY": "YOUR_API_KEY"
}
```

## Chạy ứng dụng

Sau khi thiết lập môi trường và API key, bạn có thể chạy ứng dụng Streamlit bằng cách sử dụng lệnh sau:

```bash
streamlit run app.py --server.runOnSave=false
```

Lệnh này sẽ khởi động ứng dụng trên máy tính của bạn. Mở trình duyệt và điều hướng đến URL được cung cấp (thường là `http://localhost:8501`) để sử dụng hệ thống nhận diện ASL.

## Lưu ý

- Đảm bảo bạn đã có phần cứng và camera cần thiết để truyền tải video trực tiếp.
- Kiểm tra xem môi trường Python của bạn đã được thiết lập đầy đủ các thư viện cần thiết chưa.
- Nếu bạn chạy ứng dụng trong môi trường ảo (virtual environment), hãy chắc chắn kích hoạt môi trường đó trước khi cài đặt các thư viện hoặc chạy ứng dụng.


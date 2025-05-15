# ASL Sign Language Recognition System Setup Guide

This guide provides detailed instructions for setting up and running both the backend and frontend components of the ASL Sign Language Recognition System.

## Project Structure

The project consists of two main components:
- **Backend**: A Django REST API that handles sign language recognition
- **Frontend**: A React application that provides the user interface

## Requirements

### Backend Requirements
- Python 3.10+ 
- Django 5.1+
- Other Python libraries (listed in `source/backend/requirements.txt`)

### Frontend Requirements
- Node.js 18+
- npm or yarn

## Backend Setup

1. Navigate to the backend directory:
```bash
cd source/backend
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

4. Install the required dependencies:
```bash
pip install -r requirements.txt
```

5. Set up the database:
```bash
python manage.py migrate
```

6. Populate the dictionary database with seed data:
```bash
python manage.py seed_dictionary
```

7. Run the backend server:
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000/`.

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd source/frontend
```

2. Install the required npm packages:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend application will be available at `http://localhost:5173/`.

## Running the Complete System

1. Start the backend server (in one terminal):
```bash
cd source/backend
# Activate virtual environment if needed
python manage.py runserver
```

2. Start the frontend development server (in another terminal):
```bash
cd source/frontend
npm run dev
```

3. Open your web browser and navigate to `http://localhost:5173/` to use the application.

## Configuration

### Google Gemini API Key
For certain features, a Google Gemini API key is required:

1. Get your API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Create/update the `config.json` file at the project root:
```json
{
    "GEMINI_API_KEY": "YOUR_API_KEY"
}
```

### Backend Configuration
The backend uses SQLite by default. If you need to customize the database or other settings, modify the `source/backend/SignLangugeRecognition/settings.py` file.

## Running Streamlit Application for Testing

The project also includes a Streamlit application for demonstration and testing. To run the complete system with all components:

1. Start the backend server (in one terminal):
```bash
cd source/backend
# Activate virtual environment if needed
python manage.py runserver
```

2. Start the frontend development server (in another terminal):
```bash
cd source/frontend
npm run dev
```

3. Start the Streamlit app for testing (in a third terminal):
```bash
# Make sure you're in the project root directory
# Activate your virtual environment if needed
streamlit run app.py --server.runOnSave=false
```

4. Access the different parts of the system:
   - Frontend: `http://localhost:5173/`
   - Backend API: `http://localhost:8000/`
   - Streamlit app: `http://localhost:8501/`

## Development Notes

- The backend API is configured to accept CORS requests from the frontend running at `http://localhost:5173`.
- Both servers (backend and frontend) need to be running simultaneously for the application to work properly.
- After making changes to the backend models, run `python manage.py makemigrations` and then `python manage.py migrate` to update the database schema.

## Troubleshooting

### Backend Issues
- If you encounter database errors, try deleting the `db.sqlite3` file and running migrations again.
- Check that your virtual environment is activated when running backend commands.

### Frontend Issues
- If you encounter Node.js or npm errors, ensure that you have compatible versions installed.
- Clear npm cache with `npm cache clean --force` if you have package installation issues.

### Streamlit Issues
- If the camera doesn't work, make sure your computer has a working webcam and you've granted browser permissions.
- For model inference issues, check that the model file is correctly placed in the `Model/` directory.

## Important Note

> **Warning**: Videos in the dictionary are stored on Google Drive and may not be viewable immediately. Please open videos in a new tab and reload once to allow Google Drive to create a preview.

---

For general application usage instructions, please refer to the main [README.md](./README.md) file.

---

# Hướng dẫn Cài đặt Hệ thống Nhận diện Ngôn ngữ Ký hiệu ASL

Hướng dẫn này cung cấp các bước chi tiết để cài đặt và chạy cả hai thành phần backend và frontend của Hệ thống Nhận diện Ngôn ngữ Ký hiệu ASL.

## Cấu trúc Dự án

Dự án bao gồm hai thành phần chính:
- **Backend**: API REST Django xử lý nhận diện ngôn ngữ ký hiệu
- **Frontend**: Ứng dụng React cung cấp giao diện người dùng

## Yêu cầu

### Yêu cầu Backend
- Python 3.10+ 
- Django 5.1+
- Các thư viện Python khác (được liệt kê trong `source/backend/requirements.txt`)

### Yêu cầu Frontend
- Node.js 18+
- npm hoặc yarn

## Cài đặt Backend

1. Di chuyển đến thư mục backend:
```bash
cd source/backend
```

2. Tạo môi trường ảo (khuyến nghị):
```bash
python -m venv venv
```

3. Kích hoạt môi trường ảo:
```bash
# Trên Windows
venv\Scripts\activate

# Trên macOS/Linux
source venv/bin/activate
```

4. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

5. Thiết lập cơ sở dữ liệu:
```bash
python manage.py migrate
```

6. Tạo dữ liệu từ điển mẫu cho ứng dụng:
```bash
python manage.py seed_dictionary
```

7. Chạy máy chủ backend:
```bash
python manage.py runserver
```

API backend sẽ khả dụng tại `http://localhost:8000/`.

## Cài đặt Frontend

1. Di chuyển đến thư mục frontend:
```bash
cd source/frontend
```

2. Cài đặt các gói npm cần thiết:
```bash
npm install
```

3. Khởi động máy chủ phát triển:
```bash
npm run dev
```

Ứng dụng frontend sẽ khả dụng tại `http://localhost:5173/`.

## Chạy Hệ thống Hoàn chỉnh

1. Khởi động máy chủ backend (trong một terminal):
```bash
cd source/backend
# Kích hoạt môi trường ảo nếu cần
python manage.py runserver
```

2. Khởi động máy chủ phát triển frontend (trong terminal khác):
```bash
cd source/frontend
npm run dev
```

3. Mở trình duyệt web và truy cập `http://localhost:5173/` để sử dụng ứng dụng.

## Chạy Ứng dụng Streamlit để Kiểm thử

Dự án còn bao gồm một ứng dụng Streamlit để demo và kiểm thử. Để chạy hệ thống hoàn chỉnh với tất cả các thành phần:

1. Khởi động máy chủ backend (trong terminal thứ nhất):
```bash
cd source/backend
# Kích hoạt môi trường ảo nếu cần
python manage.py runserver
```

2. Khởi động máy chủ phát triển frontend (trong terminal thứ hai):
```bash
cd source/frontend
npm run dev
```

3. Khởi động ứng dụng Streamlit để kiểm thử (trong terminal thứ ba):
```bash
# Đảm bảo bạn đang ở thư mục gốc của dự án
# Kích hoạt môi trường ảo nếu cần
streamlit run app.py --server.runOnSave=false
```

4. Truy cập các phần khác nhau của hệ thống:
   - Frontend: `http://localhost:5173/`
   - Backend API: `http://localhost:8000/`
   - Ứng dụng Streamlit: `http://localhost:8501/`

## Cấu hình

### Google Gemini API Key
Đối với một số tính năng, cần có Google Gemini API key:

1. Lấy API key từ [Google AI Studio](https://aistudio.google.com/apikey)
2. Tạo/cập nhật file `config.json` tại thư mục gốc của dự án:
```json
{
    "GEMINI_API_KEY": "YOUR_API_KEY"
}
```

### Cấu hình Backend
Backend sử dụng SQLite mặc định. Nếu bạn cần tùy chỉnh cơ sở dữ liệu hoặc các cài đặt khác, hãy sửa đổi file `source/backend/SignLangugeRecognition/settings.py`.

## Ghi chú Phát triển

- Backend API được cấu hình để chấp nhận yêu cầu CORS từ frontend chạy tại `http://localhost:5173`.
- Cả hai máy chủ (backend và frontend) cần phải chạy đồng thời để ứng dụng hoạt động chính xác.
- Sau khi thay đổi models trong backend, chạy `python manage.py makemigrations` và sau đó `python manage.py migrate` để cập nhật schema cơ sở dữ liệu.

## Xử lý sự cố

### Vấn đề Backend
- Nếu gặp lỗi cơ sở dữ liệu, hãy thử xóa file `db.sqlite3` và chạy migrations lại.
- Kiểm tra xem môi trường ảo của bạn đã được kích hoạt khi chạy lệnh backend chưa.

### Vấn đề Frontend
- Nếu gặp lỗi Node.js hoặc npm, hãy đảm bảo rằng bạn đã cài đặt các phiên bản tương thích.
- Xóa cache npm với lệnh `npm cache clean --force` nếu bạn gặp vấn đề về cài đặt gói.

### Vấn đề Streamlit
- Nếu camera không hoạt động, hãy đảm bảo máy tính của bạn có webcam hoạt động và bạn đã cấp quyền truy cập cho trình duyệt.
- Đối với các vấn đề về suy luận mô hình, hãy kiểm tra xem file mô hình đã được đặt đúng vào thư mục `Model/` chưa.

## Lưu ý quan trọng

> **Cảnh báo**: Video trong từ điển được lưu trữ bằng Google Drive nên có thể không xem được ngay. Hãy mở video ở tab mới và reload lại một lần để Google Drive tạo preview.

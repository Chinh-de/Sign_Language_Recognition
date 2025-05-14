from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
import cv2
import time
import json
import logging

from .tasks import session_manager
from . import Server 

class StartRecognitionView(APIView):
    """API để bắt đầu phiên nhận diện mới"""
    def post(self, request):
        
        logging.info("StartRecognitionView: Bắt đầu phiên nhận diện mới")

        esp32cam_ip = request.data.get('esp32cam_ip')
        esp32device_ip = request.data.get('esp32device_ip', '')
        
        if not esp32cam_ip:
            return Response({'error': 'ESP32CAM IP là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Tạo session ID mới
        session_id = str(uuid.uuid4())
        
        # Bắt đầu phiên
        success = session_manager.start_session(session_id, esp32cam_ip, esp32device_ip)
        
        if not success:
            return Response({'error': 'Không thể kết nối đến ESP32CAM'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'session_id': session_id,
            'message': 'Phiên nhận diện đã được khởi tạo'
        }, status=status.HTTP_201_CREATED)

class StopRecognitionView(APIView):
    """API để dừng phiên nhận diện"""
    def post(self, request):

        logging.info("StopRecognitionView: Dừng phiên nhận diện")


        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({'error': 'Session ID là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Dừng phiên
        session_manager.stop_session(session_id)
        
        return Response({'message': 'Phiên đã được dừng thành công'}, status=status.HTTP_200_OK)

class PingView(APIView):
    """API để client ping và duy trì trạng thái"""
    def post(self, request):

        logging.info("PingView: Client ping để duy trì trạng thái")

        session_id = request.data.get('session_id')
        
        if not session_id:
            return Response({'error': 'Session ID là bắt buộc'}, status=status.HTTP_400_BAD_REQUEST)
        
        success, current_status = session_manager.update_ping(session_id)
        
        if not success:
            return Response({
                'error': 'Phiên không tồn tại hoặc không hoạt động',
                'status': current_status
            }, status=status.HTTP_404_NOT_FOUND)
        
        
        return Response({
            'result': "latest_result",
            'status': current_status
        }, status=status.HTTP_200_OK)

class SessionStatusView(APIView):
    """API để kiểm tra trạng thái session"""
    def get(self, request, session_id):


        logging.info("SessionStatusView: Kiểm tra trạng thái session")

        status = session_manager.get_session_status(session_id)
        
        if status is None:
            return Response({'error': 'Session không tồn tại'}, status=status.HTTP_404_NOT_FOUND)
            
        return Response({'status': status}, status=status.HTTP_200_OK)

class VideoFeedView(APIView):
    """API để stream video"""
    def get(self, request, session_id):
        def generate_frames():

            logging.info("VideoFeedView: Bắt đầu stream video")

            while True:
                # Kiểm tra session có tồn tại và đang ONLINE
                status = session_manager.get_session_status(session_id)
                
                if status != 'ONLINE':
                    # Chỉ stream khi ONLINE
                    break
                    
                # Lấy frame mới nhất
                frame = session_manager.get_latest_frame(session_id)
                if frame is None:
                    continue
                
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                
                frame_bytes = buffer.tobytes()
                
                yield (b'--frame\r\n'
                      b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                time.sleep(0.1)
        
        return StreamingHttpResponse(
            generate_frames(),
            content_type='multipart/x-mixed-replace; boundary=frame'
        )

class ResultSSEView(APIView):
    """API để stream kết quả qua SSE"""
    def get(self, request, session_id):
        def event_stream():
            last_result = ""
            last_status = ""
            
            # while True:
            #     # Kiểm tra trạng thái session
            #     current_status = session_manager.get_session_status(session_id)
                
            #     # Gửi thông tin status khi có thay đổi
            #     if current_status != last_status:
            #         data = json.dumps({'status': current_status})
            #         yield f"event: status\ndata: {data}\n\n"
            #         last_status = current_status
                    
            #         if current_status == 'INACTIVE' or current_status is None:
            #             break
                
            #     # Lấy kết quả mới nhất
            #     current_result = session_manager.get_latest_result(session_id)
                
            #     # Gửi kết quả nếu có thay đổi
            #     if current_result != last_result:
            #         data = json.dumps({'result': current_result})
            #         yield f"event: result\ndata: {data}\n\n"
            #         last_result = current_result
                
        
        # response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
        # response['Cache-Control'] = 'no-cache'
        # response['X-Accel-Buffering'] = 'no'
        # return response
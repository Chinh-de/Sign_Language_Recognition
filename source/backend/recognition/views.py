import time
from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import cv2
import numpy as np
import base64
import threading

# Import Recognizer class và các biến/hàm từ module Recognizer
from .Recognizer import Recognizer, get_last_w_s, get_last_frame

recognizer_instance = None
isStop = True

class RecognizerControl(APIView):
    def post(self, request):
        global recognizer_instance
        global isStop
        
        # Parse request data
        try:
            data = json.loads(request.body)
            esp32_ip = data.get('esp32CamIp', 'local')  # Default to 'local' if not provided
            device_ip = data.get('deviceIp', 'None')    # Default to 'None' if not provided
            action = data.get('action', '')
            
            if action not in ['start', 'stop']:
                return Response({'error': 'Invalid action. Use "start" or "stop".'}, 
                                status=status.HTTP_400_BAD_REQUEST)
                
            # Handle stop action
            if action == 'stop' and recognizer_instance:
                recognizer_instance.stop()
                isStop = True
                return Response({'status': 'Recognition stopped successfully'}, 
                                status=status.HTTP_200_OK)
              # Handle start action
            if action == 'start':
                isStop = False
                # If recognizer is already running, stop it first
                if recognizer_instance and recognizer_instance.get_status():
                    recognizer_instance.stop()
                    print("Stopping current recognition before starting a new one")
                  # Initialize recognizer if it doesn't exist yet
                if recognizer_instance is None:
                    recognizer_instance = Recognizer(esp32_ip, device_ip)
                else:
                    # Update IPs if the recognizer already exists
                    recognizer_instance.set_esp32_ip(esp32_ip)
                    recognizer_instance.set_device_ip(device_ip)
                
                # Start recognition
                
                recognizer_instance.start()
                
                
                return Response({'status': 'Recognition started successfully'}, 
                                status=status.HTTP_200_OK)
                
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_frames():
    """Generate video frames for streaming"""
    global isStop
    if (isStop): 
        time.sleep(1)
    while not isStop:
    # while True:
        try:
            last_frame = get_last_frame()
            # Get the last frame from Recognizer
            if last_frame is not None:
                # Encode the image to JPEG
                ret, buffer = cv2.imencode('.jpg', last_frame)
                if ret:
                    # Convert to bytes
                    frame = buffer.tobytes()
                    # Yield the frame in the format expected by multipart HTTP response
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                # If no frame is available, yield a blank frame
                blank_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                ret, buffer = cv2.imencode('.jpg', blank_frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            time.sleep(0.03) 
        except Exception as e:
            print(f"Error in frame generation: {e}")
            # Yield an empty response if there's an error
            yield b''
    print("Video stream stopped.")
        


def video_feed(request):
    """Stream video frames"""
    return StreamingHttpResponse(generate_frames(),
                                content_type='multipart/x-mixed-replace; boundary=frame')


last_index_value = -2  # Initialize with a value that won't match any real index

class PollResultView(APIView):
    def get(self, request):
        global last_index_value  # Dùng biến toàn cục để lưu giá trị index cuối cùng

        try:
            result = get_last_w_s()
            if not result or len(result) != 2:
                raise ValueError("get_last_w_s() không trả ra 2 giá trị")

            word_or_sentence, index = result

            # Kiểm tra nếu index khác last_index_value thì mới trả kết quả
            if index != last_index_value and index >-1:
                last_index_value = index  # Cập nhật giá trị index
                print(word_or_sentence, index)
                return Response({
                    "text": word_or_sentence,
                    "index": index,
                    "has_new": True
                })
            else:
                # Nếu index không thay đổi, trả về trạng thái không có kết quả mới
                return Response({
                    "text": word_or_sentence,
                    "index": index,
                    "has_new": False
                })

        except Exception as e:
            print("❌ Lỗi trong PollResultView:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

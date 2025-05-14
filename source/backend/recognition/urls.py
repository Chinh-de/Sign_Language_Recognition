from django.urls import path
from .views import (
    StartRecognitionView, StopRecognitionView, PingView, 
    VideoFeedView, ResultSSEView, SessionStatusView
)

urlpatterns = [
    path('start/', StartRecognitionView.as_view(), name='start_recognition'),
    path('stop/', StopRecognitionView.as_view(), name='stop_recognition'),
    path('ping/', PingView.as_view(), name='ping'),
    path('status/<str:session_id>/', SessionStatusView.as_view(), name='session_status'),
    path('video_feed/<str:session_id>/', VideoFeedView.as_view(), name='video_feed'),
    path('result_sse/<str:session_id>/', ResultSSEView.as_view(), name='result_sse'),
]
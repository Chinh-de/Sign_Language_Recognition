from django.urls import path
from . import views

urlpatterns = [
    path('control/', views.RecognizerControl.as_view(), name='recognizer_control'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('poll_result/', views.PollResultView.as_view(), name='polling_recognition_result'),
]
from django.urls import path
from .views import *

urlpatterns = [
    path('glosses/', GlossListView.as_view(), name='gloss-list'),
    path('glosses/<str:gloss_value>/', GlossDetailView.as_view(), name='gloss-detail'),
]
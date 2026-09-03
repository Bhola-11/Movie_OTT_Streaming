from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.StreamHistoryView.as_view(), name='stream_history'),
    path('api/progress/', views.ProgressSyncAPIView.as_view(), name='progress_sync'),
    path('clear/', views.ClearHistoryView.as_view(), name='clear'),
]

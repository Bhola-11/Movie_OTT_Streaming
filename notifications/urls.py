from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationInboxView.as_view(), name='inbox'),
    path('<uuid:pk>/read/', views.MarkReadAPIView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]

from django.urls import path
from . import views

app_name = 'episodes'

urlpatterns = [
    path('<uuid:pk>/', views.EpisodeDetailView.as_view(), name='detail'),
    path('<uuid:pk>/api/next/', views.episode_next_api, name='next_api'),
]

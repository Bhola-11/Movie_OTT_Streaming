from django.urls import path
from . import views

app_name = 'player'

urlpatterns = [
    path('movie/<slug:slug>/', views.MoviePlayerView.as_view(), name='movie_player'),
    path('episode/<uuid:pk>/', views.EpisodePlayerView.as_view(), name='episode_player'),
]

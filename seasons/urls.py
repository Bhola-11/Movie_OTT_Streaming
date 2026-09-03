from django.urls import path
from . import views

app_name = 'seasons'

urlpatterns = [
    path('<uuid:pk>/episodes/json/', views.season_episodes_json, name='episodes_json'),
]

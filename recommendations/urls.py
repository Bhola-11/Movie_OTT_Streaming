from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.PersonalizedFeedView.as_view(), name='for_you'),
]

from django.urls import path
from . import views

app_name = 'series'

urlpatterns = [
    path('', views.SeriesBrowseView.as_view(), name='browse'),
    path('<slug:slug>/', views.SeriesDetailView.as_view(), name='detail'),
]

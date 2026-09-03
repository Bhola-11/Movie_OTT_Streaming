from django.urls import path
from . import views

app_name = 'people'

urlpatterns = [
    path('', views.PersonListView.as_view(), name='list'),
    path('directors/', views.DirectorDirectoryView.as_view(), name='directors'),
    path('<slug:slug>/', views.PersonDetailView.as_view(), name='detail'),
]

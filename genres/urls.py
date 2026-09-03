from django.urls import path
from . import views

app_name = 'genres'

urlpatterns = [
    path('', views.GenreListView.as_view(), name='list'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/<slug:slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('moods/', views.MoodExploreView.as_view(), name='moods'),
    path('<slug:slug>/', views.GenreDetailView.as_view(), name='detail'),
]

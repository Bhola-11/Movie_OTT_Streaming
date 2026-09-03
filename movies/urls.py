from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.MovieBrowseView.as_view(), name='browse'),
    path('catalog/', views.MovieListView.as_view(), name='catalog'),
    path('api/search/', views.movie_search_api, name='search_api'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='detail'),
]

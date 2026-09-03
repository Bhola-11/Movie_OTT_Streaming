from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.WatchlistListView.as_view(), name='my_list'),
    path('favorites/', views.FavoritesListView.as_view(), name='favorites'),
    path('api/toggle/', views.WatchlistToggleAPIView.as_view(), name='toggle_api'),
    path('api/favorite/', views.FavoriteToggleAPIView.as_view(), name='favorite_api'),
]

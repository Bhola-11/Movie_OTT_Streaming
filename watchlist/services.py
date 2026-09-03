from .models import WatchlistItem, FavoriteItem
from movies.models import Movie
from series.models import Series

class WatchlistService:
    @staticmethod
    def toggle_watchlist(user, content_type, content_id):
        movie = Movie.objects.filter(pk=content_id).first() if content_type == 'MOVIE' else None
        series = Series.objects.filter(pk=content_id).first() if content_type == 'SERIES' else None

        item = WatchlistItem.objects.filter(user=user, movie=movie, series=series).first()
        if item:
            item.delete()
            return False  # Removed
        else:
            WatchlistItem.objects.create(user=user, movie=movie, series=series)
            return True   # Added

    @staticmethod
    def toggle_favorite(user, content_type, content_id):
        movie = Movie.objects.filter(pk=content_id).first() if content_type == 'MOVIE' else None
        series = Series.objects.filter(pk=content_id).first() if content_type == 'SERIES' else None

        fav = FavoriteItem.objects.filter(user=user, movie=movie, series=series).first()
        if fav:
            fav.delete()
            return False
        else:
            FavoriteItem.objects.create(user=user, movie=movie, series=series)
            return True

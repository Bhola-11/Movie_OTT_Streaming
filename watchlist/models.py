import uuid
from django.db import models
from django.conf import settings
from movies.models import Movie
from series.models import Series

class WatchlistItem(models.Model):
    """
    User curated 'My List' bookmarked movies and TV series.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watchlist_items')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='in_watchlists')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True, related_name='in_watchlists')
    priority = models.PositiveSmallIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-added_at']

    def __str__(self):
        title = self.movie.title if self.movie else (self.series.title if self.series else "Item")
        return f"{self.user.email} -> {title}"

    @property
    def content_title(self):
        return self.movie.title if self.movie else self.series.title

    @property
    def content_poster(self):
        return self.movie.poster_url if self.movie else self.series.poster_url

    @property
    def content_url(self):
        return self.movie.get_absolute_url() if self.movie else self.series.get_absolute_url()


class FavoriteItem(models.Model):
    """
    'Liked' titles signaling positive affinity to the recommendation matrix.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='favorites')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True, related_name='favorites')
    favorited_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-favorited_at']

    def __str__(self):
        title = self.movie.title if self.movie else (self.series.title if self.series else "Item")
        return f"{self.user.email} liked {title}"

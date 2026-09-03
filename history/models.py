import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from movies.models import Movie
from episodes.models import Episode

class WatchHistory(models.Model):
    """
    Detailed watch progress and resume checkpoint per user across Movies and Episodes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='watch_histories')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='watch_records')
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, null=True, blank=True, related_name='watch_records')
    
    current_position_seconds = models.PositiveIntegerField(default=0)
    total_duration_seconds = models.PositiveIntegerField(default=1)
    percentage_watched = models.FloatField(default=0.0)
    is_completed = models.BooleanField(default=False)
    device_type = models.CharField(max_length=50, default='Desktop')
    
    last_watched_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-last_watched_at']
        indexes = [
            models.Index(fields=['user', '-last_watched_at']),
            models.Index(fields=['user', 'is_completed']),
        ]

    def __str__(self):
        title = self.movie.title if self.movie else (self.episode.title if self.episode else 'Media')
        return f"{self.user.email} watched {title} ({self.percentage_watched:.1f}%)"

    @property
    def target_title(self):
        if self.movie:
            return self.movie.title
        if self.episode:
            return f"{self.episode.series.title}: {self.episode.title}"
        return "Unknown Title"

    @property
    def target_thumbnail(self):
        if self.movie:
            return self.movie.backdrop_url
        if self.episode:
            return self.episode.thumbnail_url
        return "https://picsum.photos/seed/cine/640/360"

    @property
    def resume_url(self):
        if self.movie:
            return self.movie.get_absolute_url()
        if self.episode:
            return self.episode.get_absolute_url()
        return "#"

    def update_progress(self, position_sec, duration_sec):
        self.current_position_seconds = position_sec
        self.total_duration_seconds = max(duration_sec, 1)
        self.percentage_watched = min((position_sec / self.total_duration_seconds) * 100, 100.0)
        if self.percentage_watched >= 90.0:
            self.is_completed = True
        self.last_watched_at = timezone.now()
        self.save()

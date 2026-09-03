import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from movies.models import Movie
from series.models import Series

class DailyPlatformMetric(models.Model):
    """
    Daily aggregated streaming telemetry, unique viewers, and watch hours.
    """
    date = models.DateField(unique=True, db_index=True)
    total_views = models.PositiveBigIntegerField(default=0)
    total_watch_seconds = models.PositiveBigIntegerField(default=0)
    unique_active_users = models.PositiveIntegerField(default=0)
    new_registrations = models.PositiveIntegerField(default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}: {self.total_views} views (${self.gross_revenue})"

    @property
    def total_watch_hours(self):
        return round(self.total_watch_seconds / 3600, 1)


class ContentPerformance(models.Model):
    """
    Per-title performance scorecard tracking views, completions, and watch time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    
    views_count = models.PositiveBigIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)
    total_watch_minutes = models.PositiveBigIntegerField(default=0)
    average_watch_percentage = models.FloatField(default=0.0)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = self.movie.title if self.movie else (self.series.title if self.series else 'Content')
        return f"Performance: {title} ({self.views_count} views)"

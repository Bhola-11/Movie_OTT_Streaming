import uuid
from django.db import models
from django.conf import settings
from movies.models import Movie
from series.models import Series

class UserRecommendation(models.Model):
    """
    Personalized recommendations computed by collaborative filtering and genre affinity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recommendations')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True)
    
    match_score = models.FloatField(default=95.0, help_text="Percentage affinity (e.g. 98.5%)")
    recommendation_reason = models.CharField(max_length=255, default="Because you loved Cyberpunk films")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-match_score']

    def __str__(self):
        target = self.movie.title if self.movie else (self.series.title if self.series else 'Title')
        return f"{self.user.email} -> {target} ({self.match_score:.1f}%)"

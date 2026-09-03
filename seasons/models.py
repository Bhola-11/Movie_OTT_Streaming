import uuid
from django.db import models
from django.utils import timezone
from series.models import Series

class Season(models.Model):
    """
    Specific season of a TV Series containing a sequenced set of episodes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='seasons')
    season_number = models.PositiveSmallIntegerField(default=1)
    title = models.CharField(max_length=150, blank=True)
    synopsis = models.TextField(blank=True)
    poster_image = models.ImageField(upload_to='seasons/posters/%Y/', null=True, blank=True)
    air_date = models.DateField(default=timezone.now)
    trailer_url = models.URLField(max_length=500, blank=True)

    class Meta:
        ordering = ['season_number']
        unique_together = ('series', 'season_number')

    def __str__(self):
        return f"{self.series.title} - Season {self.season_number}"

    @property
    def name(self):
        return self.title if self.title else f"Season {self.season_number}"

    @property
    def episode_count(self):
        return self.episodes.count()

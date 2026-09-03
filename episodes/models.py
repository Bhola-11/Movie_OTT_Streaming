import uuid
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from seasons.models import Season

class Episode(models.Model):
    """
    Individual Episode entity with high-precision intro/outro markers
    for 'Skip Intro' and seamless binge auto-playback.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    season = models.ForeignKey(Season, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, blank=True)
    synopsis = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=45)
    air_date = models.DateField(default=timezone.now)
    
    thumbnail_image = models.ImageField(upload_to='episodes/thumbnails/%Y/', null=True, blank=True)
    video_file = models.FileField(upload_to='episodes/videos/%Y/', null=True, blank=True)
    stream_url = models.URLField(max_length=500, blank=True)

    # Markers for Interactive Player UX
    intro_start_sec = models.PositiveIntegerField(default=60, help_text="Timestamp where opening theme begins")
    intro_end_sec = models.PositiveIntegerField(default=150, help_text="Timestamp where opening theme ends")
    outro_start_sec = models.PositiveIntegerField(default=2550, help_text="Timestamp where end credits begin")

    is_free_preview = models.BooleanField(default=False)
    view_count = models.PositiveBigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['season__season_number', 'episode_number']
        unique_together = ('season', 'episode_number')

    def __str__(self):
        return f"S{self.season.season_number:02d}E{self.episode_number:02d} - {self.title}"

    @property
    def series(self):
        return self.season.series

    @property
    def thumbnail_url(self):
        if self.thumbnail_image:
            return self.thumbnail_image.url
        return f"https://picsum.photos/seed/{self.id}/640/360"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"s{self.season.season_number}e{self.episode_number}-{self.title}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('player:episode_player', kwargs={'pk': self.pk})


class EpisodeSubtitle(models.Model):
    episode = models.ForeignKey(Episode, on_delete=models.CASCADE, related_name='subtitles')
    language_code = models.CharField(max_length=10, default='en')
    language_name = models.CharField(max_length=50, default='English')
    vtt_file = models.FileField(upload_to='episodes/subtitles/%Y/', null=True, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('episode', 'language_code')

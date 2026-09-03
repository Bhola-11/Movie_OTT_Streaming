import uuid
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from genres.models import Genre, Tag
from people.models import Person

class Movie(models.Model):
    """
    Core Feature Film entity in CineVerse.
    Includes technical stream specs, content ratings, and relations to cast/genres.
    """
    class ContentRating(models.TextChoices):
        G = 'G', 'G (General Audiences)'
        PG = 'PG', 'PG (Parental Guidance Suggested)'
        PG13 = 'PG-13', 'PG-13 (Parents Strongly Cautioned)'
        R = 'R', 'R (Restricted 17+)'
        NC17 = 'NC-17', 'NC-17 (Adults Only)'
        NR = 'NR', 'Not Rated'

    class ResolutionTier(models.TextChoices):
        UHD_4K = '4K', '4K Ultra HD (2160p HDR)'
        FHD_1080P = '1080P', 'Full HD (1080p)'
        HD_720P = '720P', 'HD (720p)'
        SD_480P = '480P', 'SD (480p)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    synopsis = models.TextField()
    release_date = models.DateField(default=timezone.now)
    duration_minutes = models.PositiveIntegerField(help_text="Runtime in minutes", default=120)
    
    content_rating = models.CharField(max_length=10, choices=ContentRating.choices, default=ContentRating.PG13)
    resolution = models.CharField(max_length=10, choices=ResolutionTier.choices, default=ResolutionTier.UHD_4K)
    audio_format = models.CharField(max_length=50, default='Dolby Atmos 5.1')
    aspect_ratio = models.CharField(max_length=20, default='2.39:1 Anamorphic')
    
    poster_image = models.ImageField(upload_to='movies/posters/%Y/', null=True, blank=True)
    backdrop_image = models.ImageField(upload_to='movies/backdrops/%Y/', null=True, blank=True)
    trailer_url = models.URLField(max_length=500, blank=True, help_text="YouTube or HLS trailer URL")
    video_file = models.FileField(upload_to='movies/videos/%Y/', null=True, blank=True)
    stream_url = models.URLField(max_length=500, blank=True, help_text="CDN or HLS Stream manifest (.m3u8 / .mp4)")

    genres = models.ManyToManyField(Genre, related_name='movies', blank=True)
    tags = models.ManyToManyField(Tag, related_name='movies', blank=True)
    directors = models.ManyToManyField(Person, related_name='directed_movies', blank=True)
    cast_members = models.ManyToManyField(Person, through='MovieCast', related_name='acted_movies', blank=True)

    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_original = models.BooleanField(default=False, help_text="CineVerse Original Production")
    is_vip_only = models.BooleanField(default=False, help_text="Restricted to 4K VIP subscribers")
    is_published = models.BooleanField(default=True)
    published_at = models.DateTimeField(default=timezone.now)

    view_count = models.PositiveBigIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=8.5, validators=[MinValueValidator(1.0), MaxValueValidator(10.0)])
    ratings_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', 'is_featured']),
            models.Index(fields=['-view_count']),
        ]

    def __str__(self):
        return f"{self.title} ({self.release_year})"

    @property
    def release_year(self):
        return self.release_date.year if self.release_date else 2024

    @property
    def formatted_duration(self):
        hours = self.duration_minutes // 60
        mins = self.duration_minutes % 60
        return f"{hours}h {mins}m" if hours else f"{mins}m"

    @property
    def poster_url(self):
        if self.poster_image:
            return self.poster_image.url
        return f"https://picsum.photos/seed/{self.slug}/500/750"

    @property
    def backdrop_url(self):
        if self.backdrop_image:
            return self.backdrop_image.url
        return f"https://picsum.photos/seed/{self.slug}-bg/1920/1080"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('movies:detail', kwargs={'slug': self.slug})


class MovieCast(models.Model):
    """
    Intermediary table linking Actors to Movies with character billing information.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_cast')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='character_roles')
    character_name = models.CharField(max_length=150)
    billing_order = models.PositiveSmallIntegerField(default=1)
    is_lead = models.BooleanField(default=False)

    class Meta:
        ordering = ['billing_order']
        unique_together = ('movie', 'person', 'character_name')

    def __str__(self):
        return f"{self.person.full_name} as {self.character_name} in {self.movie.title}"


class MovieSubtitle(models.Model):
    """
    Subtitle tracks (WebVTT format) for multiple global languages.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='subtitles')
    language_code = models.CharField(max_length=10, default='en')
    language_name = models.CharField(max_length=50, default='English')
    vtt_file = models.FileField(upload_to='movies/subtitles/%Y/', null=True, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        unique_together = ('movie', 'language_code')

    def __str__(self):
        return f"{self.movie.title} Subtitle ({self.language_name})"


class MovieQuality(models.Model):
    """
    Multi-bitrate video stream variants for adaptive bitrate streaming.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='quality_variants')
    resolution_label = models.CharField(max_length=20)  # e.g. 4K UHD, 1080p, 720p
    bitrate_kbps = models.PositiveIntegerField(default=5000)
    video_stream_url = models.URLField(max_length=500)
    file_size_mb = models.FloatField(default=1500.0)

    def __str__(self):
        return f"{self.movie.title} - {self.resolution_label} ({self.bitrate_kbps} kbps)"

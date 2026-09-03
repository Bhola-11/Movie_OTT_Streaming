import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. MOVIES APP MODELS
# ==============================================================================

write('movies/models.py', '''import uuid
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
''')

# ==============================================================================
# 2. SERIES, SEASONS & EPISODES MODELS
# ==============================================================================

write('series/models.py', '''import uuid
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone
from genres.models import Genre, Tag
from people.models import Person

class Series(models.Model):
    """
    Multi-Season Television Series and Original Web Shows.
    """
    class SeriesStatus(models.TextChoices):
        ONGOING = 'ONGOING', 'Ongoing Series'
        CONCLUDED = 'CONCLUDED', 'Concluded'
        UPCOMING = 'UPCOMING', 'Upcoming Premiere'
        HIATUS = 'HIATUS', 'On Hiatus'

    class ContentRating(models.TextChoices):
        TV_Y = 'TV-Y', 'TV-Y (All Children)'
        TV_PG = 'TV-PG', 'TV-PG (Parental Guidance)'
        TV_14 = 'TV-14', 'TV-14 (Parents Strongly Cautioned)'
        TV_MA = 'TV-MA', 'TV-MA (Mature Audiences Only)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    tagline = models.CharField(max_length=300, blank=True)
    synopsis = models.TextField()
    first_air_date = models.DateField(default=timezone.now)
    last_air_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=SeriesStatus.choices, default=SeriesStatus.ONGOING)
    content_rating = models.CharField(max_length=10, choices=ContentRating.choices, default=ContentRating.TV_MA)
    
    poster_image = models.ImageField(upload_to='series/posters/%Y/', null=True, blank=True)
    backdrop_image = models.ImageField(upload_to='series/backdrops/%Y/', null=True, blank=True)
    trailer_url = models.URLField(max_length=500, blank=True)

    genres = models.ManyToManyField(Genre, related_name='series', blank=True)
    tags = models.ManyToManyField(Tag, related_name='series', blank=True)
    creators = models.ManyToManyField(Person, related_name='created_series', blank=True)
    cast_members = models.ManyToManyField(Person, through='SeriesCast', related_name='acted_series', blank=True)

    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    is_original = models.BooleanField(default=True, help_text="CineVerse Original Series")
    is_vip_only = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)

    view_count = models.PositiveBigIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=1, default=9.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-first_air_date', 'title']
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title

    @property
    def total_seasons(self):
        return self.seasons.count()

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
        return reverse('series:detail', kwargs={'slug': self.slug})


class SeriesCast(models.Model):
    series = models.ForeignKey(Series, on_delete=models.CASCADE, related_name='series_cast')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='series_roles')
    character_name = models.CharField(max_length=150)
    billing_order = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['billing_order']
        unique_together = ('series', 'person', 'character_name')

    def __str__(self):
        return f"{self.person.full_name} as {self.character_name} in {self.series.title}"
''')

write('seasons/models.py', '''import uuid
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
''')

write('episodes/models.py', '''import uuid
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
''')

# ==============================================================================
# 3. PLAYER ENGINE & SECURITY TOKENS MODELS
# ==============================================================================

write('player/models.py', '''import uuid
import secrets
from django.db import models
from django.conf import settings
from django.utils import timezone

class StreamingToken(models.Model):
    """
    Time-limited cryptographically secure playback token protecting video URLs
    from direct scraping, link scraping, and hotlinking.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='streaming_tokens')
    token = models.CharField(max_length=64, unique=True, db_index=True)
    content_type = models.CharField(max_length=20)  # 'MOVIE' or 'EPISODE'
    content_id = models.UUIDField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    expires_at = models.DateTimeField()
    is_consumed = models.BooleanField(default=False)

    def __str__(self):
        return f"Token for {self.user.email} [{self.content_type}]"

    @classmethod
    def generate_token(cls, user, content_type, content_id, ip_address='127.0.0.1', ttl_hours=6):
        raw_token = secrets.token_hex(32)
        expires_at = timezone.now() + timezone.timedelta(hours=ttl_hours)
        return cls.objects.create(
            user=user,
            token=raw_token,
            content_type=content_type,
            content_id=content_id,
            ip_address=ip_address,
            expires_at=expires_at
        )

    @property
    def is_valid(self):
        return timezone.now() < self.expires_at


class PlaybackSession(models.Model):
    """
    Active live streaming session recording device, bitrate, and concurrent streams.
    """
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='playback_sessions')
    device_id = models.CharField(max_length=100)
    content_type = models.CharField(max_length=20)
    content_id = models.UUIDField()
    started_at = models.DateTimeField(auto_now_add=True)
    last_heartbeat = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-last_heartbeat']

    def __str__(self):
        return f"Session {self.session_id} - {self.user.email}"
''')

print("Phase 2 Models built successfully.")

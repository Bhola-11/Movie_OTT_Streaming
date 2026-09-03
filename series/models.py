import uuid
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

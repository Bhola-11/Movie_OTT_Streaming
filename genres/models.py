from django.db import models
from django.utils.text import slugify
from django.urls import reverse

class Genre(models.Model):
    """
    Primary cinematic genres (Action, Sci-Fi, Thriller, Romance, Drama, Animation, etc.)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, help_text="Editorial synopsis of the genre.")
    icon_svg = models.TextField(blank=True, help_text="Inline SVG path or icon name")
    backdrop_image = models.ImageField(upload_to='genres/backdrops/', null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)
    meta_keywords = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('genres:detail', kwargs={'slug': self.slug})


class Category(models.Model):
    """
    Broad streaming classifications (Feature Films, Web Series, Documentaries, Anime, Stand-up Specials).
    """
    class CategoryType(models.TextChoices):
        MOVIE = 'MOVIE', 'Movie'
        SERIES = 'SERIES', 'TV Series'
        DOCUMENTARY = 'DOCUMENTARY', 'Documentary'
        ANIME = 'ANIME', 'Anime'
        STANDUP = 'STANDUP', 'Stand-Up Comedy'
        SHORT = 'SHORT', 'Short Film'

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    category_type = models.CharField(max_length=20, choices=CategoryType.choices, default=CategoryType.MOVIE)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('genres:category_detail', kwargs={'slug': self.slug})


class Mood(models.Model):
    """
    Experiential filters for discovery (Adrenaline Rush, Mind-Bending, Heartwarming, Spine-Chilling).
    """
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.CharField(max_length=255, blank=True)
    color_gradient = models.CharField(max_length=100, default='from-purple-900 to-indigo-900', help_text="CSS gradient identifiers")
    icon = models.CharField(max_length=50, default='sparkles')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """
    Fine-grained thematic keywords (Time Travel, Cyberpunk, Based on True Story, Oscar Winner).
    """
    name = models.CharField(max_length=60, unique=True)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    is_trending = models.BooleanField(default=False)

    def __str__(self):
        return f"#{self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

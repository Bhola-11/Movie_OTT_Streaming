import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. HISTORY APP MODELS
# ==============================================================================

write('history/models.py', '''import uuid
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
''')

# ==============================================================================
# 2. WATCHLIST & FAVORITES MODELS
# ==============================================================================

write('watchlist/models.py', '''import uuid
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
''')

# ==============================================================================
# 3. REVIEWS & RATINGS MODELS
# ==============================================================================

write('reviews/models.py', '''import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from movies.models import Movie
from series.models import Series

class Review(models.Model):
    """
    User star rating (1 to 10) and written critique with spoiler warnings.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True, related_name='reviews')
    
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)], default=8)
    title = models.CharField(max_length=200)
    content = models.TextField()
    contains_spoilers = models.BooleanField(default=False)
    
    is_approved = models.BooleanField(default=True)
    helpful_votes_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-helpful_votes_count', '-created_at']

    def __str__(self):
        target = self.movie.title if self.movie else (self.series.title if self.series else 'Content')
        return f"{self.rating}★ by {self.user.email} on {target}"


class ReviewVote(models.Model):
    """
    Upvotes/downvotes determining helpful review community rankings.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_votes')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='votes')
    is_helpful = models.BooleanField(default=True)
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'review')
''')

# ==============================================================================
# 4. RECOMMENDATIONS MODELS
# ==============================================================================

write('recommendations/models.py', '''import uuid
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
''')

print("Phase 3 Models written successfully.")

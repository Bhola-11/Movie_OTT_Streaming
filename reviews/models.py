import uuid
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

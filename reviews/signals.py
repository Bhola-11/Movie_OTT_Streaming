from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review
from movies.models import Movie
from series.models import Series

@receiver([post_save, post_delete], sender=Review)
def update_content_ratings(sender, instance, **kwargs):
    """
    Recalculates average_rating and ratings_count on Movie or Series.
    """
    if instance.movie:
        stats = Review.objects.filter(movie=instance.movie, is_approved=True).aggregate(
            avg=Avg('rating'), count=Count('id')
        )
        instance.movie.average_rating = round(stats['avg'] or 8.5, 1)
        instance.movie.ratings_count = stats['count'] or 0
        instance.movie.save(update_fields=['average_rating', 'ratings_count'])

    if instance.series:
        stats = Review.objects.filter(series=instance.series, is_approved=True).aggregate(
            avg=Avg('rating')
        )
        instance.series.average_rating = round(stats['avg'] or 9.0, 1)
        instance.series.save(update_fields=['average_rating'])

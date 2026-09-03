from django.db import models
from django.db.models import Q, Count, Avg, F
from django.utils import timezone

class MovieQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def featured(self):
        return self.published().filter(is_featured=True)

    def trending(self):
        return self.published().filter(is_trending=True).order_by('-view_count')

    def by_genre(self, genre_slug):
        return self.published().filter(genres__slug=genre_slug)

    def by_resolution(self, res):
        return self.published().filter(resolution=res)

    def by_content_rating(self, rating):
        return self.published().filter(content_rating=rating)

    def search(self, query):
        if not query:
            return self.none()
        return self.published().filter(
            Q(title__icontains=query) |
            Q(synopsis__icontains=query) |
            Q(tagline__icontains=query) |
            Q(directors__full_name__icontains=query) |
            Q(cast_members__full_name__icontains=query)
        ).distinct()

    def top_rated(self, min_rating=8.0):
        return self.published().filter(average_rating__gte=min_rating).order_by('-average_rating')

    def recent(self, days=90):
        cutoff = timezone.now().date() - timezone.timedelta(days=days)
        return self.published().filter(release_date__gte=cutoff).order_by('-release_date')

    def classics(self, year=2000):
        return self.published().filter(release_date__year__lt=year).order_by('release_date')

    def duration_range(self, min_mins=60, max_mins=180):
        return self.published().filter(duration_minutes__gte=min_mins, duration_minutes__lte=max_mins)

    def with_subtitles(self, lang_code='en'):
        return self.published().filter(subtitles__language_code=lang_code).distinct()

    def vip_exclusive(self):
        return self.published().filter(is_vip_only=True)

    def free_tier(self):
        return self.published().filter(is_vip_only=False)

    def annotate_cast_count(self):
        return self.annotate(total_cast=Count('movie_cast', distinct=True))

    def annotate_review_stats(self):
        return self.annotate(total_critiques=Count('reviews', distinct=True), calculated_avg=Avg('reviews__rating'))


class MovieManager(models.Manager):
    def get_queryset(self):
        return MovieQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def featured(self):
        return self.get_queryset().featured()

    def search(self, query):
        return self.get_queryset().search(query)

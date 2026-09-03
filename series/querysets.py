from django.db import models
from django.db.models import Q, Count, Avg

class SeriesQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)

    def ongoing(self):
        return self.published().filter(status='ONGOING')

    def concluded(self):
        return self.published().filter(status='CONCLUDED')

    def featured(self):
        return self.published().filter(is_featured=True)

    def trending(self):
        return self.published().filter(is_trending=True).order_by('-view_count')

    def by_genre(self, genre_slug):
        return self.published().filter(genres__slug=genre_slug)

    def search(self, query):
        if not query:
            return self.none()
        return self.published().filter(
            Q(title__icontains=query) |
            Q(synopsis__icontains=query) |
            Q(tagline__icontains=query) |
            Q(creators__full_name__icontains=query)
        ).distinct()

    def multi_season(self, min_seasons=2):
        return self.published().annotate(s_count=Count('seasons')).filter(s_count__gte=min_seasons)


class SeriesManager(models.Manager):
    def get_queryset(self):
        return SeriesQuerySet(self.model, using=self._db)

    def published(self):
        return self.get_queryset().published()

    def search(self, query):
        return self.get_queryset().search(query)

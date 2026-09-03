from django.db.models import Q
from .models import Movie

class MovieCatalogService:
    @staticmethod
    def get_hero_featured_movies(limit=5):
        return Movie.objects.filter(is_published=True, is_featured=True).order_by('-release_date')[:limit]

    @staticmethod
    def get_trending_movies(limit=12):
        return Movie.objects.filter(is_published=True).order_by('-view_count')[:limit]

    @staticmethod
    def get_recent_releases(limit=12):
        return Movie.objects.filter(is_published=True).order_by('-release_date')[:limit]

    @staticmethod
    def get_top_rated_movies(limit=12):
        return Movie.objects.filter(is_published=True).order_by('-average_rating')[:limit]

    @staticmethod
    def filter_movies(genre_slug=None, year=None, rating=None, query=None):
        qs = Movie.objects.filter(is_published=True).prefetch_related('genres', 'directors')
        if genre_slug:
            qs = qs.filter(genres__slug=genre_slug)
        if year:
            qs = qs.filter(release_date__year=year)
        if rating:
            qs = qs.filter(content_rating=rating)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(synopsis__icontains=query) | Q(tagline__icontains=query))
        return qs.distinct()

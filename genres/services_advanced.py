from django.db.models import Count, Q
from .models import Genre, Category, Mood, Tag

class AdvancedTaxonomyService:
    """
    Analytical service for computing genre affinities, mood clustering,
    and trending taxonomies across movies and series.
    """
    @staticmethod
    def get_genre_stats():
        """
        Returns all genres annotated with total available titles and active status.
        """
        return Genre.objects.annotate(
            total_movies=Count('movies', distinct=True),
            total_series=Count('series', distinct=True)
        ).order_by('-total_movies', 'name')

    @staticmethod
    def resolve_mood_recommendations(mood_slug):
        """
        Maps emotional mood tags (e.g. 'adrenaline-rush') to primary cinematic genres.
        """
        mood_mapping = {
            'adrenaline-rush': ['Action', 'Thriller', 'Sci-Fi'],
            'mind-bending': ['Sci-Fi', 'Mystery', 'Psychological'],
            'heartwarming': ['Comedy', 'Family', 'Animation', 'Drama'],
            'spine-chilling': ['Horror', 'Supernatural', 'Thriller'],
            'romantic': ['Romance', 'Drama', 'Comedy'],
            'epic-adventures': ['Adventure', 'Fantasy', 'Action']
        }
        target_genres = mood_mapping.get(mood_slug, ['Action', 'Drama'])
        return Genre.objects.filter(name__in=target_genres)

    @staticmethod
    def get_trending_tags(limit=10):
        """
        Returns high-velocity tags for editorial home shelf carousels.
        """
        return Tag.objects.filter(is_trending=True)[:limit]

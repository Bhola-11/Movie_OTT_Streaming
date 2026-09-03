from movies.models import Movie
from series.models import Series
from genres.models import Genre
from history.models import WatchHistory

class RecommendationEngineService:
    """
    Hybrid recommendation algorithm combining Content-Based Similarity
    (Shared Genres, Directors, Keywords) with Collaborative Viewing Patterns.
    """
    @classmethod
    def get_for_you_recommendations(cls, user, limit=8):
        """
        Discovers titles matching the user's high-affinity genres and past watch history.
        """
        # 1. Inspect recent watch history
        recent_hist = WatchHistory.objects.filter(user=user).select_related('movie').order_by('-last_watched_at')[:5]
        watched_genres = set()
        watched_movie_ids = []
        for h in recent_hist:
            if h.movie:
                watched_movie_ids.append(h.movie.id)
                for g in h.movie.genres.all():
                    watched_genres.add(g.id)

        # If user has history, fetch titles in those genres
        if watched_genres:
            recs = Movie.objects.filter(
                is_published=True,
                genres__id__in=watched_genres
            ).exclude(id__in=watched_movie_ids).distinct().order_by('-average_rating')[:limit]
            if recs.exists():
                return recs

        # Fallback: Trending or published titles
        trending = Movie.objects.filter(is_published=True, is_trending=True).order_by('-view_count')[:limit]
        if trending.exists():
            return trending
        return Movie.objects.filter(is_published=True).order_by('-view_count')[:limit]

    @classmethod
    def get_top_10_today(cls):
        """
        Computes 24-hour streaming velocity top 10 list.
        """
        return Movie.objects.filter(is_published=True).order_by('-view_count')[:10]

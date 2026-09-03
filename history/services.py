from django.utils import timezone
from .models import WatchHistory
from movies.models import Movie
from episodes.models import Episode

class WatchHistoryService:
    @staticmethod
    def sync_progress(user, content_type, content_id, position_sec, duration_sec, device='Desktop'):
        """
        Idempotently updates active watch progress and resume point.
        """
        target_movie = None
        target_episode = None
        if content_type.upper() == 'MOVIE':
            target_movie = Movie.objects.filter(pk=content_id).first()
        elif content_type.upper() == 'EPISODE':
            target_episode = Episode.objects.filter(pk=content_id).first()

        history, _ = WatchHistory.objects.get_or_create(
            user=user,
            movie=target_movie,
            episode=target_episode,
            defaults={
                'current_position_seconds': position_sec,
                'total_duration_seconds': max(duration_sec, 1),
                'device_type': device
            }
        )
        history.update_progress(position_sec, duration_sec)
        return history

    @staticmethod
    def get_continue_watching(user, limit=10):
        """
        Returns unwatched/incomplete titles for the user's home shelf.
        """
        return WatchHistory.objects.filter(
            user=user,
            is_completed=False,
            current_position_seconds__gt=30
        ).select_related('movie', 'episode', 'episode__season', 'episode__season__series')[:limit]

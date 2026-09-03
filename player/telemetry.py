import time
from django.utils import timezone
from .models import PlaybackSession

class StreamTelemetryService:
    """
    QoE (Quality of Experience) Telemetry engine.
    Ingests heartbeat pings, buffer stalling events, and bitrate switches from web clients.
    """
    @staticmethod
    def record_heartbeat(session_id, current_timestamp, buffered_seconds, dropped_frames=0, current_bitrate_kbps=5000):
        try:
            session = PlaybackSession.objects.get(session_id=session_id)
            session.last_heartbeat = timezone.now()
            session.save(update_fields=['last_heartbeat'])
            return {
                'status': 'OK',
                'session_active': session.is_active,
                'recommended_bitrate': current_bitrate_kbps
            }
        except PlaybackSession.DoesNotExist:
            return {'status': 'EXPIRED', 'session_active': False}

    @staticmethod
    def terminate_session(session_id):
        try:
            session = PlaybackSession.objects.get(session_id=session_id)
            session.is_active = False
            session.save(update_fields=['is_active'])
            return True
        except PlaybackSession.DoesNotExist:
            return False

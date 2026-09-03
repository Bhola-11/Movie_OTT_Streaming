import uuid
from django.utils import timezone
from .models import StreamingToken, PlaybackSession

class PlayerSecurityService:
    @staticmethod
    def issue_playback_token(user, content_type, content_id, ip='127.0.0.1'):
        """
        Generates an authorized, time-fenced token required to stream video chunks.
        """
        return StreamingToken.generate_token(user, content_type, content_id, ip_address=ip)

    @staticmethod
    def validate_playback_token(token_str, content_id, user):
        try:
            token = StreamingToken.objects.get(token=token_str, content_id=content_id, user=user)
            return token.is_valid
        except StreamingToken.DoesNotExist:
            return False

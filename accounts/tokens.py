import base64
import hashlib
import hmac
import time
from django.conf import settings
from django.utils.crypto import constant_time_compare

class EmailVerificationTokenGenerator:
    """
    Cryptographic HMAC-based token generator for secure account email verification
    and password reset challenges without requiring temporary database tokens.
    """
    def make_token(self, user):
        timestamp = int(time.time())
        value = f"{user.pk}:{user.email}:{user.password}:{timestamp}"
        digest = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            value.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        raw = f"{user.pk}:{timestamp}:{digest}"
        return base64.urlsafe_b64encode(raw.encode('utf-8')).decode('utf-8')

    def check_token(self, user, token, max_age_seconds=86400):
        try:
            raw = base64.urlsafe_b64decode(token.encode('utf-8')).decode('utf-8')
            parts = raw.split(':')
            if len(parts) != 3:
                return False
            user_pk, timestamp_str, digest = parts
            timestamp = int(timestamp_str)
            
            # Verify user pk match
            if str(user.pk) != user_pk:
                return False

            # Verify expiration window
            if time.time() - timestamp > max_age_seconds:
                return False

            expected_value = f"{user.pk}:{user.email}:{user.password}:{timestamp}"
            expected_digest = hmac.new(
                settings.SECRET_KEY.encode('utf-8'),
                expected_value.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            return constant_time_compare(digest, expected_digest)
        except Exception:
            return False

email_verification_token = EmailVerificationTokenGenerator()

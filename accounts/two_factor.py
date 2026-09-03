import os
import hmac
import hashlib
import struct
import time
import base64
import secrets
from django.conf import settings

class TwoFactorAuthService:
    """
    Standard RFC 6238 Time-Based One-Time Password (TOTP) engine
    implemented using pure Python standard library (no external C-extensions required).
    Fully compatible with Google Authenticator, Authy, and Microsoft Authenticator.
    """
    @staticmethod
    def generate_secret_key(length=32):
        """Generates a random RFC 3548 Base32 secret string."""
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def get_provisioning_uri(user, secret_key):
        issuer = getattr(settings, 'CINEVERSE_ISSUER_NAME', 'CineVerse')
        user_label = getattr(user, 'email', 'user')
        return f"otpauth://totp/{issuer}:{user_label}?secret={secret_key}&issuer={issuer}&algorithm=SHA1&digits=6&period=30"

    @classmethod
    def generate_totp_code(cls, secret_key, time_step=30, for_time=None):
        if for_time is None:
            for_time = int(time.time())
        counter = int(for_time // time_step)
        
        # Base32 decode secret
        padding = '=' * ((8 - len(secret_key) % 8) % 8)
        key_bytes = base64.b32decode(secret_key.upper() + padding)
        
        # Pack counter as 8-byte big-endian
        counter_bytes = struct.pack(">Q", counter)
        
        # HMAC-SHA1
        hmac_hash = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic truncation (RFC 4226)
        offset = hmac_hash[-1] & 0x0F
        truncated = struct.unpack(">I", hmac_hash[offset:offset + 4])[0] & 0x7FFFFFFF
        code = truncated % 1000000
        return f"{code:06d}"

    @classmethod
    def verify_totp_code(cls, secret_key, code, valid_window=1):
        """
        Verifies code within +/- valid_window * 30 seconds for clock drift tolerance.
        """
        code_str = str(code).strip()
        now = int(time.time())
        for delta in range(-valid_window, valid_window + 1):
            test_time = now + (delta * 30)
            if cls.generate_totp_code(secret_key, for_time=test_time) == code_str:
                return True
        return False

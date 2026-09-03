import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# 1. accounts/permissions.py
write('accounts/permissions.py', '''from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator enforcing that the current user has one of the specified roles.
    Allowed roles can be a list or tuple of User.RoleChoices.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, "Please log in to access this section.")
                return redirect(f"{reverse('accounts:login')}?next={request.path}")
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role not in allowed_roles:
                messages.error(request, "You do not have the required role permissions to view this resource.")
                raise PermissionDenied("User does not possess required role.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator ensuring that only administrators or superusers have access."""
    return role_required(['ADMIN'])(view_func)


def creator_required(view_func):
    """Decorator ensuring that only creators or admins have access to studio upload tools."""
    return role_required(['CREATOR', 'ADMIN'])(view_func)


def moderator_required(view_func):
    """Decorator ensuring that only content moderators or admins have access."""
    return role_required(['MODERATOR', 'ADMIN'])(view_func)


class RoleRequiredMixin:
    """
    CBV mixin enforcing role-based access control.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to access this page.")
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        if not request.user.is_superuser and self.allowed_roles:
            if request.user.role not in self.allowed_roles:
                messages.error(request, "Access forbidden: insufficient permissions.")
                raise PermissionDenied("Insufficient permissions")

        return super().dispatch(request, *args, **kwargs)


class AdminOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']


class CreatorOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['CREATOR', 'ADMIN']


class ModeratorOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['MODERATOR', 'ADMIN']
''')

# 2. accounts/tokens.py
write('accounts/tokens.py', '''import base64
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
''')

# 3. accounts/two_factor.py
write('accounts/two_factor.py', '''import pyotp
import qrcode
import io
import base64
from django.conf import settings

class TwoFactorAuthService:
    """
    TOTP-based two-factor authentication service compatible with
    Google Authenticator, Microsoft Authenticator, and 1Password.
    """
    @staticmethod
    def generate_secret_key():
        return pyotp.random_base32()

    @staticmethod
    def get_provisioning_uri(user, secret_key):
        issuer_name = getattr(settings, 'CINEVERSE_ISSUER_NAME', 'CineVerse')
        totp = pyotp.TOTP(secret_key)
        return totp.provisioning_uri(name=user.email, issuer_name=issuer_name)

    @staticmethod
    def generate_qr_code_base64(provisioning_uri):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=8,
            border=2,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="white", back_color="#101217")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"

    @staticmethod
    def verify_totp_code(secret_key, code):
        totp = pyotp.TOTP(secret_key)
        # Validates code with a +/- 30s window to handle clock drift
        return totp.verify(str(code).strip(), valid_window=1)
''')

# 4. Additional accounts templates
write('templates/accounts/verify_email.html', '''{% extends 'base.html' %}
{% block title %}Verify Email Address — CineVerse{% endblock %}

{% block content %}
<div class="auth-wrapper">
  <div class="auth-card" style="text-align: center;">
    <div style="font-size: 3rem; margin-bottom: 1rem;">✉️</div>
    <h2 style="margin-bottom: 0.75rem;">Verify Your Email Address</h2>
    <p style="margin-bottom: 1.5rem;">We have dispatched an activation link to <strong>{{ user.email }}</strong>. Please check your inbox or spam folder to complete registration.</p>
    <a href="{% url 'accounts:profile' %}" class="btn btn-primary" style="width: 100%;">Continue to Profile</a>
  </div>
</div>
{% endblock %}
''')

write('templates/accounts/delete_account.html', '''{% extends 'base.html' %}
{% block title %}Delete CineVerse Account{% endblock %}

{% block content %}
<div class="container" style="max-width: 650px; padding-top: 3rem;">
  <div style="background: var(--cv-bg-surface); border: 1px solid rgba(229, 9, 20, 0.4); border-radius: var(--cv-radius-lg); padding: 2.5rem;">
    <h2 style="color: var(--cv-primary); margin-bottom: 1rem;">Delete CineVerse Account</h2>
    <p style="margin-bottom: 1.5rem;">Warning: Deleting your account will immediately cancel your active subscriptions, remove your watch history, watchlist, and personalized recommendations. This action cannot be reversed.</p>
    <form method="post">
      {% csrf_token %}
      <div class="form-group">
        <label class="form-label">Type your password to confirm termination</label>
        <input type="password" name="confirm_password" class="form-input" required>
      </div>
      <div style="display: flex; gap: 1rem; margin-top: 2rem;">
        <button type="submit" class="btn btn-primary" style="background: #990000;">Permanently Delete Account</button>
        <a href="{% url 'accounts:security' %}" class="btn btn-secondary">Cancel</a>
      </div>
    </form>
  </div>
</div>
{% endblock %}
''')

write('templates/accounts/security_audit.html', '''{% extends 'base.html' %}
{% block title %}Account Security Audit — CineVerse{% endblock %}

{% block content %}
<div class="container" style="max-width: 900px; padding-top: 2rem;">
  <h2>Account Security Audit Trail</h2>
  <p style="margin-bottom: 2rem;">Full log of credential modifications, active sessions, and authorized devices.</p>
  
  <div style="background: var(--cv-bg-surface); border: 1px solid var(--cv-border); border-radius: var(--cv-radius-md); overflow: hidden;">
    <table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">
      <thead>
        <tr style="background: rgba(255, 255, 255, 0.04); border-bottom: 1px solid var(--cv-border); text-align: left;">
          <th style="padding: 1rem;">Event</th>
          <th style="padding: 1rem;">Details</th>
          <th style="padding: 1rem;">IP Address</th>
          <th style="padding: 1rem;">Date & Time</th>
        </tr>
      </thead>
      <tbody>
        {% for log in security_logs %}
          <tr style="border-bottom: 1px solid var(--cv-border);">
            <td style="padding: 1rem; font-weight: 600; color: #fff;">{{ log.event_type }}</td>
            <td style="padding: 1rem; color: var(--cv-text-muted);">{{ log.description }}</td>
            <td style="padding: 1rem; font-family: monospace;">{{ log.ip_address|default:"127.0.0.1" }}</td>
            <td style="padding: 1rem; color: var(--cv-text-muted);">{{ log.created_at|date:"Y-m-d H:i:s" }}</td>
          </tr>
        {% empty %}
          <tr>
            <td colspan="4" style="padding: 2rem; text-align: center; color: var(--cv-text-muted);">No security events recorded.</td>
          </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
</div>
{% endblock %}
''')

# 5. genres/services_advanced.py
write('genres/services_advanced.py', '''from django.db.models import Count, Q
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
''')

# 6. people/services_advanced.py
write('people/services_advanced.py', '''from django.db.models import Count, Avg
from .models import Person, Profession

class AdvancedPeopleService:
    """
    Talent catalog service for retrieving acclaimed filmmakers,
    actor filmographies, and award-winning creators.
    """
    @staticmethod
    def get_hall_of_fame(min_awards=1):
        """
        Returns cinematic creators who have achieved major competitive awards.
        """
        return Person.objects.annotate(
            awards_count=Count('awards')
        ).filter(awards_count__gte=min_awards).order_by('-popularity_score', '-awards_count')

    @staticmethod
    def get_directors_by_genre(genre_name):
        """
        Discovers directors who have helmed titles in the specified genre.
        """
        return Person.objects.filter(
            primary_profession__slug='director',
            directed_movies__genres__name=genre_name
        ).distinct()[:15]
''')

# 7. tests/test_accounts_deep.py
write('tests/test_accounts_deep.py', '''import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from accounts.permissions import role_required, admin_required, creator_required
from accounts.tokens import email_verification_token
from accounts.two_factor import TwoFactorAuthService

User = get_user_model()

@pytest.mark.django_db
def test_email_verification_token_lifecycle():
    user = User.objects.create_user(email='token.test@cineverse.io', password='Password123!')
    token = email_verification_token.make_token(user)
    assert token is not None
    assert len(token) > 20
    
    # Valid check
    is_valid = email_verification_token.check_token(user, token)
    assert is_valid is True

    # Invalid user check
    other_user = User.objects.create_user(email='other@cineverse.io', password='Password123!')
    assert email_verification_token.check_token(other_user, token) is False

@pytest.mark.django_db
def test_two_factor_auth_service():
    secret = TwoFactorAuthService.generate_secret_key()
    assert len(secret) == 32
    user = User.objects.create_user(email='totp@cineverse.io', password='Password123!')
    uri = TwoFactorAuthService.get_provisioning_uri(user, secret)
    assert 'otpauth://totp/' in uri
    assert 'CineVerse' in uri

@pytest.mark.django_db
def test_role_decorators_and_rbac(rf):
    user = User.objects.create_user(email='viewer@cineverse.io', password='Password123!', role='VIEWER')
    admin = User.objects.create_superuser(email='admin@cineverse.io', password='Password123!')

    @role_required(['ADMIN'])
    def sample_admin_view(request):
        return "Admin Area Accessed"

    request = rf.get('/admin/secret/')
    request.user = admin
    res = sample_admin_view(request)
    assert res == "Admin Area Accessed"

    request.user = user
    with pytest.raises(PermissionDenied):
        sample_admin_view(request)
''')

print("Phase 1 extensions created successfully.")

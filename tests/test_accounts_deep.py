import pytest
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

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from analytics.services import AnalyticsAggregationService
from moderation.models import ContentReport
from moderation.services import ModerationService
from audit.models import AuditEntry
from audit.services import AuditLoggerService
from reviews.models import Review
from movies.models import Movie

User = get_user_model()

@pytest.mark.django_db
def test_analytics_kpis_calculation():
    kpis = AnalyticsAggregationService.get_dashboard_kpis()
    assert 'total_users' in kpis
    assert 'total_revenue' in kpis
    assert 'total_watch_hours' in kpis
    assert 'top_titles' in kpis

@pytest.mark.django_db
def test_analytics_dashboard_access(client):
    admin = User.objects.create_superuser(email='exec@cineverse.io', password='Password123!')
    client.force_login(admin)

    res = client.get(reverse('analytics:dashboard'))
    assert res.status_code == 200
    assert 'Platform Analytics' in res.content.decode()

@pytest.mark.django_db
def test_moderation_queue_and_resolution(client):
    mod = User.objects.create_superuser(email='moderator@cineverse.io', password='Password123!')
    reporter = User.objects.create_user(email='whistleblower@cineverse.io', password='Password123!')
    movie = Movie.objects.create(title='Flagged Title', synopsis='Plot')
    review = Review.objects.create(user=reporter, movie=movie, rating=1, title='Spam', content='Check out my link spam.com')

    # Create report
    report = ContentReport.objects.create(
        reporter=reporter,
        review=review,
        reason=ContentReport.ReasonChoices.SPAM,
        explanation='Promotional link'
    )
    assert report.status == ContentReport.StatusChoices.PENDING

    # Resolve report
    resolved = ModerationService.resolve_report(report.pk, mod, action='RESOLVED', notes='Confirmed violation.')
    assert resolved.status == 'RESOLVED'
    review.refresh_from_db()
    assert review.is_approved is False

@pytest.mark.django_db
def test_audit_logging_service():
    admin = User.objects.create_superuser(email='auditor@cineverse.io', password='Password123!')
    entry = AuditLoggerService.log_action(
        actor=admin,
        action_type=AuditEntry.ActionChoices.ROLE_CHANGED if hasattr(AuditEntry.ActionChoices, 'ROLE_CHANGED') else AuditEntry.ActionChoices.USER_LOGIN,
        details='Promoted user to Moderator role'
    )
    assert entry.actor == admin
    assert 'Promoted' in entry.details

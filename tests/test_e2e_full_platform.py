import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from movies.models import Movie
from series.models import Series
from seasons.models import Season
from episodes.models import Episode
from subscriptions.models import Plan
from payments.models import PaymentTransaction, Invoice
from payments.services import PaymentProcessingService
from history.services import WatchHistoryService
from watchlist.services import WatchlistService
from reviews.models import Review
from analytics.services import AnalyticsAggregationService
from player.services import PlayerSecurityService

User = get_user_model()

@pytest.mark.django_db
def test_full_platform_subscriber_journey(client):
    """
    End-to-End simulation of a user:
    1. Register new account
    2. Browse featured catalog and search
    3. Add movie to Watchlist and Favorites
    4. Start playback in cinema player & receive secure streaming token
    5. Sync playback progress to WatchHistory
    6. Verify Continue Watching rail
    7. Submit a 10-star review
    8. Upgrade to VIP 4K Ultra plan via checkout
    9. Download official ReportLab PDF invoice
    10. Verify executive analytics KPIs reflect the new revenue and watch hours
    """
    # 1. Register user
    reg_res = client.post(reverse('accounts:register'), {
        'email': 'sarah.connor@cineverse.io',
        'first_name': 'Sarah',
        'last_name': 'Connor',
        'password': 'SkynetHunter2026!',
        'password_confirm': 'SkynetHunter2026!',
        'terms_accepted': True
    })
    user = User.objects.get(email='sarah.connor@cineverse.io')
    assert user is not None
    client.force_login(user)

    # 2. Browse & Search
    movie = Movie.objects.create(
        title='Cyber Revolution 2088',
        synopsis='An epic struggle against rogue synthetic minds.',
        duration_minutes=140,
        resolution='4K',
        is_published=True,
        is_featured=True,
        is_trending=True
    )
    res_browse = client.get(reverse('movies:browse'))
    assert res_browse.status_code == 200
    assert 'Cyber Revolution 2088' in res_browse.content.decode()

    # 3. Watchlist & Favorites
    added_wl = WatchlistService.toggle_watchlist(user, 'MOVIE', movie.pk)
    assert added_wl is True
    added_fav = WatchlistService.toggle_favorite(user, 'MOVIE', movie.pk)
    assert added_fav is True

    # 4. Stream player & security token
    res_player = client.get(reverse('player:movie_player', kwargs={'slug': movie.slug}))
    assert res_player.status_code == 200
    token = res_player.context['stream_token']
    assert PlayerSecurityService.validate_playback_token(token, movie.pk, user) is True

    # 5. Sync progress (at 45 minutes)
    history = WatchHistoryService.sync_progress(
        user=user,
        content_type='MOVIE',
        content_id=movie.pk,
        position_sec=2700,
        duration_sec=8400,
        device='Desktop'
    )
    assert history.percentage_watched > 30.0
    assert history.is_completed is False

    # 6. Check continue watching
    cw = WatchHistoryService.get_continue_watching(user)
    assert cw.count() == 1
    assert cw.first().movie == movie

    # 7. Submit 10-star Review
    review = Review.objects.create(
        user=user,
        movie=movie,
        rating=10,
        title='Phenomenal World Building and Action',
        content='The pacing, cinematography, and score are world-class.',
        is_approved=True
    )
    movie.refresh_from_db()
    assert movie.average_rating == 10.0

    # 8. Upgrade to VIP 4K Ultra plan
    plan = Plan.objects.get_or_create(tier_code='VIP_4K', defaults={'name': 'VIP Ultra 4K', 'price_monthly': 19.99})[0]
    tx, invoice = PaymentProcessingService.process_checkout(
        user=user,
        plan_id=plan.pk,
        billing_cycle='MONTHLY'
    )
    assert tx.status == PaymentTransaction.StatusChoices.SUCCESS
    assert float(tx.amount) == 19.99
    assert tx.subscription.is_active is True

    # 9. Download PDF Invoice
    res_pdf = client.get(invoice.get_absolute_url())
    assert res_pdf.status_code == 200
    assert res_pdf['Content-Type'] == 'application/pdf'
    assert len(res_pdf.content) > 1000

    # 10. Executive Analytics
    kpis = AnalyticsAggregationService.get_dashboard_kpis()
    assert kpis['total_users'] >= 1
    assert float(kpis['total_revenue']) >= 19.99
    assert kpis['total_watch_hours'] > 0

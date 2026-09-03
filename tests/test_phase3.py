import pytest
import json
from django.urls import reverse
from django.contrib.auth import get_user_model
from movies.models import Movie
from history.models import WatchHistory
from history.services import WatchHistoryService
from watchlist.models import WatchlistItem, FavoriteItem
from watchlist.services import WatchlistService
from reviews.models import Review, ReviewVote
from recommendations.services import RecommendationEngineService

User = get_user_model()

@pytest.mark.django_db
def test_watch_history_and_progress_sync():
    user = User.objects.create_user(email='history.user@cineverse.io', password='Password123!')
    movie = Movie.objects.create(title='Deep Space Odyssey', synopsis='Space voyage', duration_minutes=120)

    # Sync at 30 minutes
    h = WatchHistoryService.sync_progress(
        user=user,
        content_type='MOVIE',
        content_id=movie.pk,
        position_sec=1800,
        duration_sec=7200,
        device='SmartTV'
    )
    assert h.percentage_watched == 25.0
    assert h.is_completed is False

    # Sync at 110 minutes (over 90%)
    h = WatchHistoryService.sync_progress(
        user=user,
        content_type='MOVIE',
        content_id=movie.pk,
        position_sec=6600,
        duration_sec=7200,
        device='SmartTV'
    )
    assert h.percentage_watched > 90.0
    assert h.is_completed is True

@pytest.mark.django_db
def test_progress_sync_api_view(client):
    user = User.objects.create_user(email='beacon.user@cineverse.io', password='Password123!')
    client.force_login(user)
    movie = Movie.objects.create(title='Cyberpunk Signal', synopsis='Cyberpunk', duration_minutes=100)

    url = reverse('history:progress_sync')
    payload = {
        'content_type': 'MOVIE',
        'content_id': str(movie.pk),
        'position_seconds': 3000,
        'duration_seconds': 6000
    }
    res = client.post(url, data=json.dumps(payload), content_type='application/json')
    assert res.status_code == 200
    data = res.json()
    assert data['status'] == 'OK'
    assert data['percentage'] == 50.0

@pytest.mark.django_db
def test_watchlist_and_favorite_toggle_services():
    user = User.objects.create_user(email='watchlist.user@cineverse.io', password='Password123!')
    movie = Movie.objects.create(title='Neon Noir', synopsis='Noir thriller')

    # Add to watchlist
    added = WatchlistService.toggle_watchlist(user, 'MOVIE', movie.pk)
    assert added is True
    assert WatchlistItem.objects.filter(user=user, movie=movie).exists()

    # Remove from watchlist
    removed = WatchlistService.toggle_watchlist(user, 'MOVIE', movie.pk)
    assert removed is False
    assert not WatchlistItem.objects.filter(user=user, movie=movie).exists()

    # Toggle favorite
    fav_added = WatchlistService.toggle_favorite(user, 'MOVIE', movie.pk)
    assert fav_added is True
    assert FavoriteItem.objects.filter(user=user, movie=movie).exists()

@pytest.mark.django_db
def test_reviews_and_signals_recalculation():
    user = User.objects.create_user(email='critic@cineverse.io', password='Password123!')
    movie = Movie.objects.create(title='Cerebral Matrix', synopsis='Sci-Fi mystery', average_rating=5.0)

    review = Review.objects.create(
        user=user,
        movie=movie,
        rating=10,
        title='Outstanding achievement',
        content='Brilliant visuals and narrative.',
        is_approved=True
    )

    # Refresh movie to verify signal updated average_rating
    movie.refresh_from_db()
    assert movie.average_rating == 10.0
    assert movie.ratings_count == 1

@pytest.mark.django_db
def test_recommendations_service():
    user = User.objects.create_user(email='ai.recs@cineverse.io', password='Password123!')
    movie = Movie.objects.create(title='Top Velocity', synopsis='Fast cars', is_published=True, view_count=50000)

    top_10 = RecommendationEngineService.get_top_10_today()
    assert top_10.count() >= 1

    for_you = RecommendationEngineService.get_for_you_recommendations(user)
    assert for_you.count() >= 1

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from movies.models import Movie, MovieCast
from series.models import Series
from seasons.models import Season
from episodes.models import Episode
from player.models import StreamingToken
from player.services import PlayerSecurityService

User = get_user_model()

@pytest.mark.django_db
def test_movie_model_and_methods():
    movie = Movie.objects.create(
        title='Interstellar Odyssey',
        synopsis='An epic voyage across spacetime.',
        duration_minutes=150,
        resolution=Movie.ResolutionTier.UHD_4K
    )
    assert movie.slug == 'interstellar-odyssey'
    assert movie.formatted_duration == '2h 30m'
    assert movie.resolution == '4K'
    assert 'picsum.photos' in movie.poster_url

@pytest.mark.django_db
def test_series_seasons_episodes_hierarchy():
    series = Series.objects.create(
        title='Galactic Empire',
        synopsis='A dynasty controls star clusters across millenniums.'
    )
    assert series.slug == 'galactic-empire'
    
    season1 = Season.objects.create(series=series, season_number=1, title='Fall of the Core')
    assert season1.name == 'Fall of the Core'
    
    ep1 = Episode.objects.create(
        season=season1,
        episode_number=1,
        title='The Emperor Dies',
        duration_minutes=60,
        intro_start_sec=45,
        intro_end_sec=90
    )
    assert ep1.series == series
    assert 's1e1' in ep1.slug
    assert ep1.season.episode_count == 1

@pytest.mark.django_db
def test_streaming_token_lifecycle():
    user = User.objects.create_user(email='stream.user@cineverse.io', password='Password123!')
    movie = Movie.objects.create(title='Apex Predator', synopsis='Deep sea thriller')
    
    token = PlayerSecurityService.issue_playback_token(user, 'MOVIE', movie.pk)
    assert token.token is not None
    assert len(token.token) == 64
    assert token.is_valid is True

    # Validate token
    assert PlayerSecurityService.validate_playback_token(token.token, movie.pk, user) is True
    assert PlayerSecurityService.validate_playback_token('invalid_token', movie.pk, user) is False

@pytest.mark.django_db
def test_movie_views_and_catalog(client):
    movie = Movie.objects.create(
        title='The Obsidian Paradox',
        synopsis='A classified government experiment.',
        is_published=True,
        is_featured=True
    )
    
    # Browse view
    res_browse = client.get(reverse('movies:browse'))
    assert res_browse.status_code == 200
    assert 'The Obsidian Paradox' in res_browse.content.decode()

    # Detail view
    res_detail = client.get(movie.get_absolute_url())
    assert res_detail.status_code == 200
    assert 'The Obsidian Paradox' in res_detail.content.decode()

    # Search API
    res_search = client.get(f"{reverse('movies:search_api')}?q=Obsidian")
    assert res_search.status_code == 200
    data = res_search.json()
    assert len(data['results']) >= 1
    assert data['results'][0]['title'] == 'The Obsidian Paradox'

@pytest.mark.django_db
def test_series_views_and_episodes_api(client):
    series = Series.objects.create(title='Blackout 2099', synopsis='Global blackout', is_published=True)
    season = Season.objects.create(series=series, season_number=1)
    ep1 = Episode.objects.create(season=season, episode_number=1, title='Dark Grid', duration_minutes=45)
    ep2 = Episode.objects.create(season=season, episode_number=2, title='Off The Wire', duration_minutes=48)

    # Series detail view
    res_series = client.get(series.get_absolute_url())
    assert res_series.status_code == 200
    assert 'Blackout 2099' in res_series.content.decode()

    # Season JSON API
    res_episodes = client.get(reverse('seasons:episodes_json', kwargs={'pk': season.pk}))
    assert res_episodes.status_code == 200
    ep_data = res_episodes.json()
    assert len(ep_data['episodes']) == 2
    assert ep_data['episodes'][0]['title'] == 'Dark Grid'

    # Episode Next API
    res_next = client.get(reverse('episodes:next_api', kwargs={'pk': ep1.pk}))
    assert res_next.status_code == 200
    assert res_next.json()['has_next'] is True
    assert res_next.json()['title'] == 'Off The Wire'

@pytest.mark.django_db
def test_player_views_authenticated(client):
    user = User.objects.create_user(email='theater.viewer@cineverse.io', password='Password123!')
    client.force_login(user)
    
    movie = Movie.objects.create(title='Cosmic Echo', synopsis='Sci-Fi exploration')
    res_player = client.get(reverse('player:movie_player', kwargs={'slug': movie.slug}))
    assert res_player.status_code == 200
    assert 'cineverseVideo' in res_player.content.decode()
    assert 'stream-token' in res_player.content.decode()

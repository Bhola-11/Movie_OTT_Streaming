import pytest
from movies.encoding import HLSManifestGenerator
from player.telemetry import StreamTelemetryService
from series.seasons_episodes_manager import SeriesBingeManager
from series.models import Series
from seasons.models import Season
from episodes.models import Episode

def test_hls_master_playlist_generator():
    playlist = HLSManifestGenerator.generate_master_playlist('https://cdn.cineverse.io/streams', 'movie-uuid-123')
    assert '#EXTM3U' in playlist
    assert '4K_UHD' in playlist
    assert '1080P_FHD' in playlist
    assert 'BANDWIDTH=16000000' in playlist

def test_hls_variant_playlist_generator():
    variant = HLSManifestGenerator.generate_variant_playlist(
        'https://cdn.cineverse.io/streams', 'movie-uuid-123', '1080P_FHD', duration_seconds=30, target_duration=6
    )
    assert '#EXT-X-TARGETDURATION:6' in variant
    assert '#EXT-X-ENDLIST' in variant
    assert 'segment_00000.ts' in variant

@pytest.mark.django_db
def test_series_binge_calculator():
    series = Series.objects.create(title='Binge Show', synopsis='Quick watch')
    s1 = Season.objects.create(series=series, season_number=1)
    Episode.objects.create(season=s1, episode_number=1, title='Pilot', duration_minutes=45)
    Episode.objects.create(season=s1, episode_number=2, title='Second', duration_minutes=55)
    
    total = SeriesBingeManager.get_total_series_duration_minutes(series)
    assert total == 100
    formatted = SeriesBingeManager.format_total_binge_time(total)
    assert '1h 40m' in formatted

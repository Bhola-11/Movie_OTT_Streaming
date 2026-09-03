import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# 1. movies/encoding.py
write('movies/encoding.py', '''import os
import math

class HLSManifestGenerator:
    """
    Simulates production HLS (HTTP Live Streaming) adaptive bitrate playlist creation.
    Generates multi-variant master.m3u8 playlists and segmented media manifests (.ts/.m4s).
    """
    PROFILES = [
        {'name': '4K_UHD', 'resolution': '3840x2160', 'bitrate': 16000000, 'codecs': 'hvc1.2.4.L153.B0,mp4a.40.2'},
        {'name': '1080P_FHD', 'resolution': '1920x1080', 'bitrate': 6000000, 'codecs': 'avc1.64002a,mp4a.40.2'},
        {'name': '720P_HD', 'resolution': '1280x720', 'bitrate': 3000000, 'codecs': 'avc1.4d401f,mp4a.40.2'},
        {'name': '480P_SD', 'resolution': '854x480', 'bitrate': 1200000, 'codecs': 'avc1.4d401e,mp4a.40.2'},
    ]

    @classmethod
    def generate_master_playlist(cls, base_url, media_id):
        lines = [
            '#EXTM3U',
            '#EXT-X-VERSION:6',
            '#EXT-X-INDEPENDENT-SEGMENTS',
            ''
        ]
        for p in cls.PROFILES:
            lines.append(f'#EXT-X-STREAM-INF:BANDWIDTH={p["bitrate"]},RESOLUTION={p["resolution"]},CODECS="{p["codecs"]}"')
            lines.append(f'{base_url}/{media_id}/{p["name"]}/index.m3u8')
        return '\n'.join(lines)

    @classmethod
    def generate_variant_playlist(cls, base_url, media_id, profile_name, duration_seconds=7200, target_duration=6):
        num_segments = math.ceil(duration_seconds / target_duration)
        lines = [
            '#EXTM3U',
            '#EXT-X-VERSION:6',
            f'#EXT-X-TARGETDURATION:{target_duration}',
            '#EXT-X-MEDIA-SEQUENCE:0',
            '#EXT-X-PLAYLIST-TYPE:VOD',
            ''
        ]
        for i in range(num_segments):
            seg_dur = min(target_duration, duration_seconds - (i * target_duration))
            lines.append(f'#EXTINF:{seg_dur:.3f},')
            lines.append(f'{base_url}/{media_id}/{profile_name}/segment_{i:05d}.ts')
        lines.append('#EXT-X-ENDLIST')
        return '\n'.join(lines)
''')

# 2. player/telemetry.py
write('player/telemetry.py', '''import time
from django.utils import timezone
from .models import PlaybackSession

class StreamTelemetryService:
    """
    QoE (Quality of Experience) Telemetry engine.
    Ingests heartbeat pings, buffer stalling events, and bitrate switches from web clients.
    """
    @staticmethod
    def record_heartbeat(session_id, current_timestamp, buffered_seconds, dropped_frames=0, current_bitrate_kbps=5000):
        try:
            session = PlaybackSession.objects.get(session_id=session_id)
            session.last_heartbeat = timezone.now()
            session.save(update_fields=['last_heartbeat'])
            return {
                'status': 'OK',
                'session_active': session.is_active,
                'recommended_bitrate': current_bitrate_kbps
            }
        except PlaybackSession.DoesNotExist:
            return {'status': 'EXPIRED', 'session_active': False}

    @staticmethod
    def terminate_session(session_id):
        try:
            session = PlaybackSession.objects.get(session_id=session_id)
            session.is_active = False
            session.save(update_fields=['is_active'])
            return True
        except PlaybackSession.DoesNotExist:
            return False
''')

# 3. series/seasons_episodes_manager.py
write('series/seasons_episodes_manager.py', '''from seasons.models import Season
from episodes.models import Episode

class SeriesBingeManager:
    """
    Calculates total series duration, binge velocity, and organizes next unviewed episodes.
    """
    @staticmethod
    def get_total_series_duration_minutes(series):
        total_mins = 0
        for season in series.seasons.all():
            for ep in season.episodes.all():
                total_mins += ep.duration_minutes
        return total_mins

    @staticmethod
    def format_total_binge_time(minutes):
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        mins = minutes % 60
        parts = []
        if days: parts.append(f"{days}d")
        if hours: parts.append(f"{hours}h")
        if mins: parts.append(f"{mins}m")
        return ' '.join(parts) if parts else '0m'
''')

# 4. tests/test_player_deep.py
write('tests/test_player_deep.py', '''import pytest
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
''')

print("Phase 2 deep modules created.")

import os
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
        return chr(10).join(lines)

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
        return chr(10).join(lines)

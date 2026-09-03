from seasons.models import Season
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

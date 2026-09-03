from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Season

def season_episodes_json(request, pk):
    season = get_object_or_404(Season, pk=pk)
    episodes_data = []
    for ep in season.episodes.all():
        episodes_data.append({
            'id': str(ep.id),
            'number': ep.episode_number,
            'title': ep.title,
            'duration': f"{ep.duration_minutes}m",
            'thumbnail': ep.thumbnail_url,
            'synopsis': ep.synopsis,
            'player_url': ep.get_absolute_url()
        })
    return JsonResponse({'season_title': season.name, 'episodes': episodes_data})

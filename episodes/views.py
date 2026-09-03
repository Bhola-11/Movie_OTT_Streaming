from django.views.generic import DetailView
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Episode

class EpisodeDetailView(DetailView):
    model = Episode
    template_name = 'episodes/episode_detail.html'
    context_object_name = 'episode'

def episode_next_api(request, pk):
    """
    Returns the subsequent episode in sequence for the OTT autoplay countdown.
    """
    current_ep = get_object_or_404(Episode, pk=pk)
    # Check next episode in current season
    next_ep = Episode.objects.filter(season=current_ep.season, episode_number=current_ep.episode_number + 1).first()
    if not next_ep:
        # Check episode 1 of next season
        next_season = current_ep.season.series.seasons.filter(season_number=current_ep.season.season_number + 1).first()
        if next_season:
            next_ep = next_season.episodes.filter(episode_number=1).first()

    if next_ep:
        return JsonResponse({
            'has_next': True,
            'id': str(next_ep.id),
            'title': next_ep.title,
            'number': f"S{next_ep.season.season_number:02d}E{next_ep.episode_number:02d}",
            'player_url': next_ep.get_absolute_url(),
            'thumbnail': next_ep.thumbnail_url
        })
    return JsonResponse({'has_next': False})

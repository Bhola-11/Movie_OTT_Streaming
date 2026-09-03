from django.views.generic import DetailView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, Http404, JsonResponse
from movies.models import Movie
from episodes.models import Episode
from .models import StreamingToken
from .services import PlayerSecurityService

class MoviePlayerView(LoginRequiredMixin, DetailView):
    """
    Dedicated fullscreen OTT cinematic player interface for Movies.
    """
    model = Movie
    template_name = 'player/player_movie.html'
    context_object_name = 'movie'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        movie = self.get_object()
        token = PlayerSecurityService.issue_playback_token(
            user=self.request.user,
            content_type='MOVIE',
            content_id=movie.pk,
            ip=getattr(self.request, 'client_ip', '127.0.0.1')
        )
        ctx['stream_token'] = token.token
        ctx['subtitles'] = movie.subtitles.all()
        # Default sample stream fallback if file not uploaded
        ctx['video_src'] = movie.video_file.url if movie.video_file else (movie.stream_url or "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/TearsOfSteel.mp4")
        return ctx


class EpisodePlayerView(LoginRequiredMixin, DetailView):
    """
    Dedicated fullscreen OTT player for Series Episodes with
    Skip Intro, Next Episode prompt, and Season Picker drawer.
    """
    model = Episode
    template_name = 'player/player_episode.html'
    context_object_name = 'episode'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ep = self.get_object()
        token = PlayerSecurityService.issue_playback_token(
            user=self.request.user,
            content_type='EPISODE',
            content_id=ep.pk,
            ip=getattr(self.request, 'client_ip', '127.0.0.1')
        )
        ctx['stream_token'] = token.token
        ctx['subtitles'] = ep.subtitles.all()
        ctx['series'] = ep.season.series
        ctx['all_episodes'] = ep.season.episodes.all()
        ctx['video_src'] = ep.video_file.url if ep.video_file else (ep.stream_url or "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4")
        return ctx

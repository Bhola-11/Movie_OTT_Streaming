import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# MOVIES VIEWS, FORMS, SERVICES & TEMPLATETAGS
# ==============================================================================

write('movies/services.py', '''from django.db.models import Q
from .models import Movie

class MovieCatalogService:
    @staticmethod
    def get_hero_featured_movies(limit=5):
        return Movie.objects.filter(is_published=True, is_featured=True).order_by('-release_date')[:limit]

    @staticmethod
    def get_trending_movies(limit=12):
        return Movie.objects.filter(is_published=True).order_by('-view_count')[:limit]

    @staticmethod
    def get_recent_releases(limit=12):
        return Movie.objects.filter(is_published=True).order_by('-release_date')[:limit]

    @staticmethod
    def get_top_rated_movies(limit=12):
        return Movie.objects.filter(is_published=True).order_by('-average_rating')[:limit]

    @staticmethod
    def filter_movies(genre_slug=None, year=None, rating=None, query=None):
        qs = Movie.objects.filter(is_published=True).prefetch_related('genres', 'directors')
        if genre_slug:
            qs = qs.filter(genres__slug=genre_slug)
        if year:
            qs = qs.filter(release_date__year=year)
        if rating:
            qs = qs.filter(content_rating=rating)
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(synopsis__icontains=query) | Q(tagline__icontains=query))
        return qs.distinct()
''')

write('movies/forms.py', '''from django import forms
from .models import Movie, MovieCast

class MovieFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search title, actor...', 'class': 'form-input'}))
    genre = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Year', 'class': 'form-input'}))
    rating = forms.ChoiceField(required=False, choices=[('', 'All Ratings')] + Movie.ContentRating.choices, widget=forms.Select(attrs={'class': 'form-select'}))
''')

write('movies/templatetags/__init__.py', '')
write('movies/templatetags/movie_tags.py', '''from django import template
from movies.models import Movie

register = template.Library()

@register.filter(name='rating_color')
def rating_color(rating):
    try:
        val = float(rating)
        if val >= 8.5:
            return '#00DF9A'  # Green
        elif val >= 7.0:
            return '#FFB800'  # Gold
        else:
            return '#8E95A5'  # Gray
    except Exception:
        return '#FFB800'
''')

write('movies/views.py', '''from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse
from django.db.models import F
from .models import Movie, MovieCast
from .services import MovieCatalogService
from genres.models import Genre

class MovieBrowseView(TemplateView):
    """
    Main Streaming Home / Browse page.
    Renders Hero Carousel, Continue Watching rail, Trending Row, and Genre rails.
    """
    template_name = 'movies/browse.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hero_movies'] = MovieCatalogService.get_hero_featured_movies()
        ctx['trending_movies'] = MovieCatalogService.get_trending_movies()
        ctx['recent_movies'] = MovieCatalogService.get_recent_releases()
        ctx['top_rated_movies'] = MovieCatalogService.get_top_rated_movies()
        ctx['featured_genres'] = Genre.objects.filter(is_featured=True)[:6]
        return ctx


class MovieListView(ListView):
    """
    Full Movie catalog directory with faceted search & filtering.
    """
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 24

    def get_queryset(self):
        return MovieCatalogService.filter_movies(
            genre_slug=self.request.GET.get('genre'),
            year=self.request.GET.get('year'),
            rating=self.request.GET.get('rating'),
            query=self.request.GET.get('q')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['all_genres'] = Genre.objects.all()
        ctx['selected_genre'] = self.request.GET.get('genre', '')
        ctx['selected_year'] = self.request.GET.get('year', '')
        ctx['selected_rating'] = self.request.GET.get('rating', '')
        ctx['search_query'] = self.request.GET.get('q', '')
        return ctx


class MovieDetailView(DetailView):
    """
    Cinematic movie overview presentation with trailer player modal,
    cast gallery, tech specs (4K HDR, Dolby Atmos), and related movies.
    """
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        movie = super().get_object(queryset)
        # Increment views atomically
        Movie.objects.filter(pk=movie.pk).update(view_count=F('view_count') + 1)
        return movie

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        movie = self.get_object()
        ctx['cast_list'] = movie.movie_cast.select_related('person').all()[:12]
        ctx['related_movies'] = Movie.objects.filter(genres__in=movie.genres.all()).exclude(pk=movie.pk).distinct()[:8]
        ctx['subtitles'] = movie.subtitles.all()
        return ctx


def movie_search_api(request):
    """
    Fast autocomplete endpoint for the global navigation search bar.
    """
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'results': []})

    movies = Movie.objects.filter(is_published=True, title__icontains=query)[:6]
    results = []
    for m in movies:
        results.append({
            'title': m.title,
            'type': 'Movie',
            'year': m.release_year,
            'poster': m.poster_url,
            'url': m.get_absolute_url()
        })
    return JsonResponse({'results': results})
''')

write('movies/urls.py', '''from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.MovieBrowseView.as_view(), name='browse'),
    path('catalog/', views.MovieListView.as_view(), name='catalog'),
    path('api/search/', views.movie_search_api, name='search_api'),
    path('<slug:slug>/', views.MovieDetailView.as_view(), name='detail'),
]
''')

write('movies/admin.py', '''from django.contrib import admin
from .models import Movie, MovieCast, MovieSubtitle, MovieQuality

class MovieCastInline(admin.TabularInline):
    model = MovieCast
    extra = 2

class MovieSubtitleInline(admin.TabularInline):
    model = MovieSubtitle
    extra = 1

class MovieQualityInline(admin.TabularInline):
    model = MovieQuality
    extra = 1

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_year', 'resolution', 'content_rating', 'is_featured', 'is_trending', 'is_vip_only', 'view_count')
    list_filter = ('resolution', 'content_rating', 'is_featured', 'is_trending', 'is_vip_only', 'genres')
    search_fields = ('title', 'synopsis', 'tagline')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres', 'tags', 'directors')
    inlines = [MovieCastInline, MovieSubtitleInline, MovieQualityInline]
''')

# ==============================================================================
# SERIES, SEASONS & EPISODES VIEWS, SERVICES & ADMIN
# ==============================================================================

write('series/views.py', '''from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import Series
from genres.models import Genre

class SeriesBrowseView(ListView):
    model = Series
    template_name = 'series/series_browse.html'
    context_object_name = 'series_list'
    paginate_by = 18

    def get_queryset(self):
        qs = Series.objects.filter(is_published=True).prefetch_related('genres')
        genre = self.request.GET.get('genre')
        if genre:
            qs = qs.filter(genres__slug=genre)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['featured_series'] = Series.objects.filter(is_published=True, is_featured=True).first()
        ctx['all_genres'] = Genre.objects.all()
        return ctx


class SeriesDetailView(DetailView):
    model = Series
    template_name = 'series/series_detail.html'
    context_object_name = 'series'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        series = super().get_object(queryset)
        Series.objects.filter(pk=series.pk).update(view_count=F('view_count') + 1)
        return series

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        series = self.get_object()
        # Fetch seasons with episodes pre-loaded
        seasons = series.seasons.prefetch_related('episodes').all()
        ctx['seasons'] = seasons
        ctx['selected_season'] = seasons.first() if seasons.exists() else None
        ctx['cast_list'] = series.series_cast.select_related('person').all()[:12]
        return ctx
''')

write('series/urls.py', '''from django.urls import path
from . import views

app_name = 'series'

urlpatterns = [
    path('', views.SeriesBrowseView.as_view(), name='browse'),
    path('<slug:slug>/', views.SeriesDetailView.as_view(), name='detail'),
]
''')

write('series/admin.py', '''from django.contrib import admin
from .models import Series, SeriesCast

class SeriesCastInline(admin.TabularInline):
    model = SeriesCast
    extra = 2

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'content_rating', 'is_featured', 'is_trending', 'is_vip_only', 'view_count')
    list_filter = ('status', 'content_rating', 'is_featured', 'is_trending', 'is_vip_only')
    search_fields = ('title', 'synopsis')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres', 'tags', 'creators')
    inlines = [SeriesCastInline]
''')

write('seasons/views.py', '''from django.http import JsonResponse
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
''')

write('seasons/urls.py', '''from django.urls import path
from . import views

app_name = 'seasons'

urlpatterns = [
    path('<uuid:pk>/episodes/json/', views.season_episodes_json, name='episodes_json'),
]
''')

write('seasons/admin.py', '''from django.contrib import admin
from .models import Season

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number', 'title', 'air_date', 'episode_count')
    list_filter = ('series',)
''')

write('episodes/views.py', '''from django.views.generic import DetailView
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
''')

write('episodes/urls.py', '''from django.urls import path
from . import views

app_name = 'episodes'

urlpatterns = [
    path('<uuid:pk>/', views.EpisodeDetailView.as_view(), name='detail'),
    path('<uuid:pk>/api/next/', views.episode_next_api, name='next_api'),
]
''')

write('episodes/admin.py', '''from django.contrib import admin
from .models import Episode, EpisodeSubtitle

class EpisodeSubtitleInline(admin.TabularInline):
    model = EpisodeSubtitle
    extra = 1

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('season', 'episode_number', 'title', 'duration_minutes', 'air_date', 'view_count')
    list_filter = ('season__series', 'season')
    search_fields = ('title', 'synopsis')
    inlines = [EpisodeSubtitleInline]
''')

# ==============================================================================
# PLAYER ENGINE, SECURITY & STREAM VIEWS
# ==============================================================================

write('player/services.py', '''import uuid
from django.utils import timezone
from .models import StreamingToken, PlaybackSession

class PlayerSecurityService:
    @staticmethod
    def issue_playback_token(user, content_type, content_id, ip='127.0.0.1'):
        """
        Generates an authorized, time-fenced token required to stream video chunks.
        """
        return StreamingToken.generate_token(user, content_type, content_id, ip_address=ip)

    @staticmethod
    def validate_playback_token(token_str, content_id, user):
        try:
            token = StreamingToken.objects.get(token=token_str, content_id=content_id, user=user)
            return token.is_valid
        except StreamingToken.DoesNotExist:
            return False
''')

write('player/views.py', '''from django.views.generic import DetailView
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
''')

write('player/urls.py', '''from django.urls import path
from . import views

app_name = 'player'

urlpatterns = [
    path('movie/<slug:slug>/', views.MoviePlayerView.as_view(), name='movie_player'),
    path('episode/<uuid:pk>/', views.EpisodePlayerView.as_view(), name='episode_player'),
]
''')

print("Phase 2 Views, Services, URLs and Admin built successfully.")

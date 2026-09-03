from django.views.generic import ListView, DetailView, TemplateView
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
        
        if self.request.user.is_authenticated:
            from history.services import WatchHistoryService
            ctx['continue_watching'] = WatchHistoryService.get_continue_watching(self.request.user)
        else:
            ctx['continue_watching'] = []
            
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

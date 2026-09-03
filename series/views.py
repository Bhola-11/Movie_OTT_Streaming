from django.views.generic import ListView, DetailView
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

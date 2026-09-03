from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Genre, Category, Mood, Tag

class GenreListView(ListView):
    model = Genre
    template_name = 'genres/genre_list.html'
    context_object_name = 'genres'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Category.objects.filter(is_active=True)
        ctx['moods'] = Mood.objects.all()
        return ctx

class GenreDetailView(DetailView):
    model = Genre
    template_name = 'genres/genre_detail.html'
    context_object_name = 'genre'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        genre = self.get_object()
        # Movies and Series associated with this genre
        ctx['movies'] = genre.movies.filter(is_published=True)[:24] if hasattr(genre, 'movies') else []
        ctx['series_list'] = genre.series.filter(is_published=True)[:24] if hasattr(genre, 'series') else []
        return ctx

class CategoryListView(ListView):
    model = Category
    template_name = 'genres/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'genres/category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

class MoodExploreView(ListView):
    model = Mood
    template_name = 'genres/mood_explore.html'
    context_object_name = 'moods'

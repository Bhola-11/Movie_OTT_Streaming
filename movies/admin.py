from django.contrib import admin
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

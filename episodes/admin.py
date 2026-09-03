from django.contrib import admin
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

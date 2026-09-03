from django.contrib import admin
from .models import Season

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('series', 'season_number', 'title', 'air_date', 'episode_count')
    list_filter = ('series',)

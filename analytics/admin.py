from django.contrib import admin
from .models import DailyPlatformMetric, ContentPerformance

@admin.register(DailyPlatformMetric)
class DailyMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_views', 'total_watch_seconds', 'gross_revenue')

@admin.register(ContentPerformance)
class ContentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('movie', 'series', 'views_count', 'completion_count')

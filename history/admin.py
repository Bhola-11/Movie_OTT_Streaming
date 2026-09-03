from django.contrib import admin
from .models import WatchHistory

@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_title', 'percentage_watched', 'is_completed', 'last_watched_at')
    list_filter = ('is_completed', 'device_type')
    search_fields = ('user__email',)

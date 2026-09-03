from django.contrib import admin
from .models import WatchlistItem, FavoriteItem

@admin.register(WatchlistItem)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_title', 'added_at')

@admin.register(FavoriteItem)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorited_at')

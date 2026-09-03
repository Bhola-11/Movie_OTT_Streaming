from django.contrib import admin
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

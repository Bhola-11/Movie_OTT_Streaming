from django.contrib import admin
from .models import Genre, Category, Mood, Tag

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'display_order', 'created_at')
    list_editable = ('is_featured', 'display_order')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category_type', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color_gradient', 'icon')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_trending')
    list_editable = ('is_trending',)
    prepopulated_fields = {'slug': ('name',)}

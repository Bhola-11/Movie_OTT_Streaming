from django.contrib import admin
from .models import Person, Profession, PersonAward

class PersonAwardInline(admin.TabularInline):
    model = PersonAward
    extra = 1

@admin.register(Profession)
class ProfessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'stage_name', 'primary_profession', 'popularity_score', 'is_featured')
    list_filter = ('primary_profession', 'is_featured', 'gender')
    search_fields = ('full_name', 'stage_name', 'biography')
    prepopulated_fields = {'slug': ('full_name',)}
    inlines = [PersonAwardInline]

@admin.register(PersonAward)
class PersonAwardAdmin(admin.ModelAdmin):
    list_display = ('person', 'award_name', 'year', 'is_winner')
    list_filter = ('is_winner', 'year')
    search_fields = ('person__full_name', 'award_name', 'work_title')

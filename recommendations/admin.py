from django.contrib import admin
from .models import UserRecommendation

@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'match_score', 'recommendation_reason', 'created_at')

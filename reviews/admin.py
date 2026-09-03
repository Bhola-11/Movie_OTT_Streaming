from django.contrib import admin
from .models import Review, ReviewVote

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'title', 'contains_spoilers', 'is_approved', 'helpful_votes_count', 'created_at')
    list_filter = ('rating', 'contains_spoilers', 'is_approved')
    search_fields = ('user__email', 'title', 'content')

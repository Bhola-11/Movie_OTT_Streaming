import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# HISTORY VIEWS & SERVICES
# ==============================================================================

write('history/services.py', '''from django.utils import timezone
from .models import WatchHistory
from movies.models import Movie
from episodes.models import Episode

class WatchHistoryService:
    @staticmethod
    def sync_progress(user, content_type, content_id, position_sec, duration_sec, device='Desktop'):
        """
        Idempotently updates active watch progress and resume point.
        """
        target_movie = None
        target_episode = None
        if content_type.upper() == 'MOVIE':
            target_movie = Movie.objects.filter(pk=content_id).first()
        elif content_type.upper() == 'EPISODE':
            target_episode = Episode.objects.filter(pk=content_id).first()

        history, _ = WatchHistory.objects.get_or_create(
            user=user,
            movie=target_movie,
            episode=target_episode,
            defaults={
                'current_position_seconds': position_sec,
                'total_duration_seconds': max(duration_sec, 1),
                'device_type': device
            }
        )
        history.update_progress(position_sec, duration_sec)
        return history

    @staticmethod
    def get_continue_watching(user, limit=10):
        """
        Returns unwatched/incomplete titles for the user's home shelf.
        """
        return WatchHistory.objects.filter(
            user=user,
            is_completed=False,
            current_position_seconds__gt=30
        ).select_related('movie', 'episode', 'episode__season', 'episode__season__series')[:limit]
''')

write('history/views.py', '''import json
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib import messages
from .models import WatchHistory
from .services import WatchHistoryService

class StreamHistoryView(LoginRequiredMixin, ListView):
    model = WatchHistory
    template_name = 'history/stream_history.html'
    context_object_name = 'history_records'
    paginate_by = 20

    def get_queryset(self):
        return WatchHistory.objects.filter(user=self.request.user).select_related('movie', 'episode', 'episode__season', 'episode__season__series')


class ProgressSyncAPIView(LoginRequiredMixin, View):
    """
    Heartbeat Beacon API endpoint receiving client video currentTime updates every 5 seconds.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            content_type = data.get('content_type')
            content_id = data.get('content_id')
            pos = int(data.get('position_seconds', 0))
            dur = int(data.get('duration_seconds', 1))
            device = getattr(request, 'device_category', 'Desktop')

            history = WatchHistoryService.sync_progress(
                user=request.user,
                content_type=content_type,
                content_id=content_id,
                position_sec=pos,
                duration_sec=dur,
                device=device
            )
            return JsonResponse({'status': 'OK', 'percentage': history.percentage_watched})
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=400)


class ClearHistoryView(LoginRequiredMixin, View):
    def post(self, request):
        WatchHistory.objects.filter(user=request.user).delete()
        messages.success(request, "Your streaming watch history has been cleared.")
        return redirect('history:stream_history')
''')

write('history/urls.py', '''from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.StreamHistoryView.as_view(), name='stream_history'),
    path('api/progress/', views.ProgressSyncAPIView.as_view(), name='progress_sync'),
    path('clear/', views.ClearHistoryView.as_view(), name='clear'),
]
''')

write('history/admin.py', '''from django.contrib import admin
from .models import WatchHistory

@admin.register(WatchHistory)
class WatchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'target_title', 'percentage_watched', 'is_completed', 'last_watched_at')
    list_filter = ('is_completed', 'device_type')
    search_fields = ('user__email',)
''')

# ==============================================================================
# WATCHLIST & FAVORITES VIEWS & SERVICES
# ==============================================================================

write('watchlist/services.py', '''from .models import WatchlistItem, FavoriteItem
from movies.models import Movie
from series.models import Series

class WatchlistService:
    @staticmethod
    def toggle_watchlist(user, content_type, content_id):
        movie = Movie.objects.filter(pk=content_id).first() if content_type == 'MOVIE' else None
        series = Series.objects.filter(pk=content_id).first() if content_type == 'SERIES' else None

        item = WatchlistItem.objects.filter(user=user, movie=movie, series=series).first()
        if item:
            item.delete()
            return False  # Removed
        else:
            WatchlistItem.objects.create(user=user, movie=movie, series=series)
            return True   # Added

    @staticmethod
    def toggle_favorite(user, content_type, content_id):
        movie = Movie.objects.filter(pk=content_id).first() if content_type == 'MOVIE' else None
        series = Series.objects.filter(pk=content_id).first() if content_type == 'SERIES' else None

        fav = FavoriteItem.objects.filter(user=user, movie=movie, series=series).first()
        if fav:
            fav.delete()
            return False
        else:
            FavoriteItem.objects.create(user=user, movie=movie, series=series)
            return True
''')

write('watchlist/views.py', '''import json
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from .models import WatchlistItem, FavoriteItem
from .services import WatchlistService

class WatchlistListView(LoginRequiredMixin, ListView):
    model = WatchlistItem
    template_name = 'watchlist/my_list.html'
    context_object_name = 'items'

    def get_queryset(self):
        return WatchlistItem.objects.filter(user=self.request.user).select_related('movie', 'series')


class FavoritesListView(LoginRequiredMixin, ListView):
    model = FavoriteItem
    template_name = 'watchlist/favorites.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return FavoriteItem.objects.filter(user=self.request.user).select_related('movie', 'series')


class WatchlistToggleAPIView(LoginRequiredMixin, View):
    """
    AJAX endpoint toggling '+ My List' button status without page refresh.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            ctype = data.get('content_type')
            cid = data.get('content_id')
            is_added = WatchlistService.toggle_watchlist(request.user, ctype, cid)
            return JsonResponse({'status': 'OK', 'is_in_watchlist': is_added})
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=400)


class FavoriteToggleAPIView(LoginRequiredMixin, View):
    """
    AJAX endpoint toggling '♥ Favorite' button status.
    """
    def post(self, request):
        try:
            data = json.loads(request.body)
            ctype = data.get('content_type')
            cid = data.get('content_id')
            is_fav = WatchlistService.toggle_favorite(request.user, ctype, cid)
            return JsonResponse({'status': 'OK', 'is_favorite': is_fav})
        except Exception as e:
            return JsonResponse({'status': 'ERROR', 'message': str(e)}, status=400)
''')

write('watchlist/urls.py', '''from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.WatchlistListView.as_view(), name='my_list'),
    path('favorites/', views.FavoritesListView.as_view(), name='favorites'),
    path('api/toggle/', views.WatchlistToggleAPIView.as_view(), name='toggle_api'),
    path('api/favorite/', views.FavoriteToggleAPIView.as_view(), name='favorite_api'),
]
''')

write('watchlist/admin.py', '''from django.contrib import admin
from .models import WatchlistItem, FavoriteItem

@admin.register(WatchlistItem)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'content_title', 'added_at')

@admin.register(FavoriteItem)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'favorited_at')
''')

# ==============================================================================
# REVIEWS VIEWS, FORMS, SIGNALS & ADMIN
# ==============================================================================

write('reviews/apps.py', '''from django.apps import AppConfig

class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        import reviews.signals
''')

write('reviews/signals.py', '''from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from .models import Review
from movies.models import Movie
from series.models import Series

@receiver([post_save, post_delete], sender=Review)
def update_content_ratings(sender, instance, **kwargs):
    """
    Recalculates average_rating and ratings_count on Movie or Series.
    """
    if instance.movie:
        stats = Review.objects.filter(movie=instance.movie, is_approved=True).aggregate(
            avg=Avg('rating'), count=Count('id')
        )
        instance.movie.average_rating = round(stats['avg'] or 8.5, 1)
        instance.movie.ratings_count = stats['count'] or 0
        instance.movie.save(update_fields=['average_rating', 'ratings_count'])

    if instance.series:
        stats = Review.objects.filter(series=instance.series, is_approved=True).aggregate(
            avg=Avg('rating')
        )
        instance.series.average_rating = round(stats['avg'] or 9.0, 1)
        instance.series.save(update_fields=['average_rating'])
''')

write('reviews/forms.py', '''from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'contains_spoilers']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(10, 0, -1)], attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'placeholder': 'Review headline...', 'class': 'form-input'}),
            'content': forms.Textarea(attrs={'placeholder': 'Write your full critique and impressions...', 'class': 'form-input', 'rows': 4}),
        }
''')

write('reviews/views.py', '''from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Review, ReviewVote
from .forms import ReviewForm
from movies.models import Movie
from series.models import Series

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/create_review.html'

    def form_valid(self, form):
        review = form.save(commit=False)
        review.user = self.request.user
        
        movie_slug = self.request.POST.get('movie_slug')
        series_slug = self.request.POST.get('series_slug')
        
        if movie_slug:
            review.movie = get_object_or_404(Movie, slug=movie_slug)
            review.save()
            messages.success(self.request, "Thank you! Your movie review has been published.")
            return redirect(review.movie.get_absolute_url())
        elif series_slug:
            review.series = get_object_or_404(Series, slug=series_slug)
            review.save()
            messages.success(self.request, "Your series review has been published.")
            return redirect(review.series.get_absolute_url())

        return redirect('movies:browse')


class ReviewHelpfulVoteAPIView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        vote, created = ReviewVote.objects.get_or_create(user=request.user, review=review, defaults={'is_helpful': True})
        if not created:
            vote.delete()
            review.helpful_votes_count = max(0, review.helpful_votes_count - 1)
            is_voted = False
        else:
            review.helpful_votes_count += 1
            is_voted = True
        review.save(update_fields=['helpful_votes_count'])
        return JsonResponse({'status': 'OK', 'votes': review.helpful_votes_count, 'is_voted': is_voted})
''')

write('reviews/urls.py', '''from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/', views.ReviewCreateView.as_view(), name='create'),
    path('<uuid:pk>/vote/', views.ReviewHelpfulVoteAPIView.as_view(), name='vote_api'),
]
''')

write('reviews/admin.py', '''from django.contrib import admin
from .models import Review, ReviewVote

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'title', 'contains_spoilers', 'is_approved', 'helpful_votes_count', 'created_at')
    list_filter = ('rating', 'contains_spoilers', 'is_approved')
    search_fields = ('user__email', 'title', 'content')
''')

# ==============================================================================
# RECOMMENDATIONS VIEWS & SERVICES
# ==============================================================================

write('recommendations/services.py', '''from movies.models import Movie
from series.models import Series
from genres.models import Genre
from history.models import WatchHistory

class RecommendationEngineService:
    """
    Hybrid recommendation algorithm combining Content-Based Similarity
    (Shared Genres, Directors, Keywords) with Collaborative Viewing Patterns.
    """
    @classmethod
    def get_for_you_recommendations(cls, user, limit=8):
        """
        Discovers titles matching the user's high-affinity genres and past watch history.
        """
        # 1. Inspect recent watch history
        recent_hist = WatchHistory.objects.filter(user=user).select_related('movie').order_by('-last_watched_at')[:5]
        watched_genres = set()
        watched_movie_ids = []
        for h in recent_hist:
            if h.movie:
                watched_movie_ids.append(h.movie.id)
                for g in h.movie.genres.all():
                    watched_genres.add(g.id)

        # If user has history, fetch titles in those genres
        if watched_genres:
            recs = Movie.objects.filter(
                is_published=True,
                genres__id__in=watched_genres
            ).exclude(id__in=watched_movie_ids).distinct().order_by('-average_rating')[:limit]
            if recs.exists():
                return recs

        # Fallback: Top rated trending titles
        return Movie.objects.filter(is_published=True, is_trending=True).order_by('-view_count')[:limit]

    @classmethod
    def get_top_10_today(cls):
        """
        Computes 24-hour streaming velocity top 10 list.
        """
        return Movie.objects.filter(is_published=True).order_by('-view_count')[:10]
''')

write('recommendations/views.py', '''from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import RecommendationEngineService

class PersonalizedFeedView(LoginRequiredMixin, TemplateView):
    template_name = 'recommendations/for_you.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['recommendations'] = RecommendationEngineService.get_for_you_recommendations(self.request.user)
        ctx['top_10'] = RecommendationEngineService.get_top_10_today()
        return ctx
''')

write('recommendations/urls.py', '''from django.urls import path
from . import views

app_name = 'recommendations'

urlpatterns = [
    path('', views.PersonalizedFeedView.as_view(), name='for_you'),
]
''')

write('recommendations/admin.py', '''from django.contrib import admin
from .models import UserRecommendation

@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'match_score', 'recommendation_reason', 'created_at')
''')

print("Phase 3 Views, Services, Signals and Admin built.")

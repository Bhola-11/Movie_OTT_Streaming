import json
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

import json
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

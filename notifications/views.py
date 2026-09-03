from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Notification
from .services import NotificationService

class NotificationInboxView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/inbox.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkReadAPIView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return JsonResponse({'status': 'OK'})


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        NotificationService.mark_all_as_read(request.user)
        return redirect('notifications:inbox')

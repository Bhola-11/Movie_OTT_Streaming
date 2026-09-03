from django.views.generic import ListView, View
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import ContentReport
from .services import ModerationService
from reviews.models import Review

class ModerationQueueView(UserPassesTestMixin, ListView):
    model = ContentReport
    template_name = 'moderation/queue.html'
    context_object_name = 'reports'

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role in ['MODERATOR', 'ADMIN'])

    def get_queryset(self):
        return ContentReport.objects.filter(status='PENDING').select_related('reporter', 'review')


class SubmitReportView(LoginRequiredMixin, View):
    def post(self, request):
        review_id = request.POST.get('review_id')
        reason = request.POST.get('reason', 'OTHER')
        explanation = request.POST.get('explanation', '')

        review = get_object_or_404(Review, pk=review_id)
        ContentReport.objects.create(
            reporter=request.user,
            review=review,
            reason=reason,
            explanation=explanation
        )
        messages.info(request, "Report submitted. Our moderation team will investigate.")
        return redirect(review.movie.get_absolute_url() if review.movie else 'movies:browse')


class ResolveReportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role in ['MODERATOR', 'ADMIN'])

    def post(self, request, pk):
        action = request.POST.get('action', 'RESOLVED')
        notes = request.POST.get('notes', '')
        ModerationService.resolve_report(pk, request.user, action=action, notes=notes)
        messages.success(request, f"Report #{pk} marked as {action}.")
        return redirect('moderation:queue')

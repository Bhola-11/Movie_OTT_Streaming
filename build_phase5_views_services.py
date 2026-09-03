import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. ANALYTICS VIEWS & SERVICES
# ==============================================================================

write('analytics/services.py', '''from django.db.models import Sum, Count, Avg
from django.utils import timezone
from .models import DailyPlatformMetric, ContentPerformance
from movies.models import Movie
from series.models import Series
from payments.models import PaymentTransaction
from accounts.models import User
from history.models import WatchHistory

class AnalyticsAggregationService:
    """
    Computes enterprise platform KPIs, streaming metrics, and revenue analytics.
    """
    @classmethod
    def get_dashboard_kpis(cls):
        total_users = User.objects.count()
        total_movies = Movie.objects.filter(is_published=True).count()
        total_series = Series.objects.filter(is_published=True).count()
        
        # Aggregate revenue
        rev_stats = PaymentTransaction.objects.filter(status='SUCCESS').aggregate(total=Sum('amount'))
        total_revenue = rev_stats['total'] or 0.00
        
        # Aggregate watch hours
        watch_stats = WatchHistory.objects.aggregate(total_secs=Sum('current_position_seconds'))
        total_watch_hours = round((watch_stats['total_secs'] or 0) / 3600, 1)

        # Top 5 most streamed titles
        top_titles = Movie.objects.filter(is_published=True).order_by('-view_count')[:5]

        return {
            'total_users': total_users,
            'total_movies': total_movies,
            'total_series': total_series,
            'total_revenue': total_revenue,
            'total_watch_hours': total_watch_hours,
            'top_titles': top_titles,
        }
''')

write('analytics/views.py', '''from django.views.generic import TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse
from .services import AnalyticsAggregationService
from .models import DailyPlatformMetric
from movies.models import Movie

class AnalyticsDashboardView(UserPassesTestMixin, TemplateView):
    """
    Executive dashboard with KPI metric cards, watch time charts, and top content performance.
    """
    template_name = 'analytics/dashboard.html'

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role in ['ADMIN', 'CREATOR'])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['kpis'] = AnalyticsAggregationService.get_dashboard_kpis()
        ctx['recent_movies'] = Movie.objects.filter(is_published=True).order_by('-view_count')[:10]
        return ctx


def stream_stats_api(request):
    """
    JSON API providing streaming telemetry data for charts.
    """
    kpis = AnalyticsAggregationService.get_dashboard_kpis()
    return JsonResponse({
        'total_revenue': float(kpis['total_revenue']),
        'total_watch_hours': kpis['total_watch_hours'],
        'total_users': kpis['total_users']
    })
''')

write('analytics/urls.py', '''from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
    path('api/stats/', views.stream_stats_api, name='stats_api'),
]
''')

write('analytics/admin.py', '''from django.contrib import admin
from .models import DailyPlatformMetric, ContentPerformance

@admin.register(DailyPlatformMetric)
class DailyMetricAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_views', 'total_watch_seconds', 'gross_revenue')

@admin.register(ContentPerformance)
class ContentPerformanceAdmin(admin.ModelAdmin):
    list_display = ('movie', 'series', 'views_count', 'completion_count')
''')

# ==============================================================================
# 2. MODERATION VIEWS & SERVICES
# ==============================================================================

write('moderation/services.py', '''from django.utils import timezone
from .models import ContentReport
from reviews.models import Review

class ModerationService:
    PROFANITY_WORDS = {'spam', 'scam', 'cheat', 'hack', 'pirate'}

    @classmethod
    def auto_screen_review(cls, content):
        """Screens critique content for flagged words."""
        lower = content.lower()
        return any(bad in lower for bad in cls.PROFANITY_WORDS)

    @classmethod
    def resolve_report(cls, report_id, moderator, action='RESOLVED', notes=''):
        report = ContentReport.objects.get(pk=report_id)
        report.status = action
        report.moderator = moderator
        report.moderator_notes = notes
        report.resolved_at = timezone.now()
        report.save()

        if action == 'RESOLVED' and report.review:
            # Unpublish or hide review
            report.review.is_approved = False
            report.review.save(update_fields=['is_approved'])

        return report
''')

write('moderation/views.py', '''from django.views.generic import ListView, View
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
''')

write('moderation/urls.py', '''from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    path('queue/', views.ModerationQueueView.as_view(), name='queue'),
    path('submit/', views.SubmitReportView.as_view(), name='submit'),
    path('<uuid:pk>/resolve/', views.ResolveReportView.as_view(), name='resolve'),
]
''')

write('moderation/admin.py', '''from django.contrib import admin
from .models import ContentReport

@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'reason', 'status', 'reporter', 'created_at')
    list_filter = ('status', 'reason')
''')

# ==============================================================================
# 3. AUDIT VIEWS & SERVICES
# ==============================================================================

write('audit/services.py', '''from django.utils import timezone
from .models import AuditEntry

class AuditLoggerService:
    @staticmethod
    def log_action(actor, action_type, details, ip_address='127.0.0.1'):
        return AuditEntry.objects.create(
            actor=actor,
            action=action_type,
            details=details,
            ip_address=ip_address,
            timestamp=timezone.now()
        )
''')

write('audit/views.py', '''import csv
from django.views.generic import ListView, View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from .models import AuditEntry

class AuditLogListView(UserPassesTestMixin, ListView):
    model = AuditEntry
    template_name = 'audit/log_list.html'
    context_object_name = 'audit_entries'
    paginate_by = 30

    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role == 'ADMIN')


class AuditExportCSVView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user.role == 'ADMIN')

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="CineVerse_Audit_Logs.csv"'
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'Actor', 'Action', 'IP Address', 'Details'])

        for log in AuditEntry.objects.all()[:500]:
            actor_email = log.actor.email if log.actor else 'System'
            writer.writerow([log.timestamp, actor_email, log.action, log.ip_address, log.details])

        return response
''')

write('audit/urls.py', '''from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.AuditLogListView.as_view(), name='log_list'),
    path('export/csv/', views.AuditExportCSVView.as_view(), name='export_csv'),
]
''')

write('audit/admin.py', '''from django.contrib import admin
from .models import AuditEntry

@admin.register(AuditEntry)
class AuditEntryAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'actor', 'action', 'ip_address')
    list_filter = ('action',)
    search_fields = ('actor__email', 'details')
''')

print("Phase 5 Views and Services built.")

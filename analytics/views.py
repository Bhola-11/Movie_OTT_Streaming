from django.views.generic import TemplateView
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

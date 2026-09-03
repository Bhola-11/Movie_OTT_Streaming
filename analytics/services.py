from django.db.models import Sum, Count, Avg
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

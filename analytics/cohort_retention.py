from datetime import timedelta
from django.utils import timezone
from accounts.models import User
from history.models import WatchHistory
from payments.models import PaymentTransaction

class CohortRetentionAnalytics:
    """
    Computes weekly and monthly cohort retention, churn rates, and streaming LTV.
    """
    @classmethod
    def calculate_7_day_retention(cls):
        now = timezone.now()
        seven_days_ago = now - timedelta(days=7)
        cohort_users = User.objects.filter(date_joined__gte=seven_days_ago, date_joined__lte=now)
        cohort_count = cohort_users.count()
        if cohort_count == 0:
            return {'cohort_size': 0, 'active_today': 0, 'retention_rate': 100.0}

        # Users who streamed content today
        today_start = now.replace(hour=0, minute=0, second=0)
        active_today = WatchHistory.objects.filter(
            user__in=cohort_users,
            last_watched_at__gte=today_start
        ).values('user').distinct().count()

        rate = round((active_today / cohort_count) * 100, 2)
        return {
            'cohort_size': cohort_count,
            'active_today': active_today,
            'retention_rate': rate
        }

    @classmethod
    def calculate_arpu(cls):
        """Average Revenue Per User"""
        total_users = User.objects.count()
        if total_users == 0:
            return 0.0
        total_rev = PaymentTransaction.objects.filter(status='SUCCESS').aggregate(models.Sum('amount'))['amount__sum'] or 0.0
        return round(float(total_rev) / total_users, 2)

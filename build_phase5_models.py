import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. ANALYTICS APP MODELS
# ==============================================================================

write('analytics/models.py', '''import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from movies.models import Movie
from series.models import Series

class DailyPlatformMetric(models.Model):
    """
    Daily aggregated streaming telemetry, unique viewers, and watch hours.
    """
    date = models.DateField(unique=True, db_index=True)
    total_views = models.PositiveBigIntegerField(default=0)
    total_watch_seconds = models.PositiveBigIntegerField(default=0)
    unique_active_users = models.PositiveIntegerField(default=0)
    new_registrations = models.PositiveIntegerField(default=0)
    new_subscriptions = models.PositiveIntegerField(default=0)
    gross_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Metrics for {self.date}: {self.total_views} views (${self.gross_revenue})"

    @property
    def total_watch_hours(self):
        return round(self.total_watch_seconds / 3600, 1)


class ContentPerformance(models.Model):
    """
    Per-title performance scorecard tracking views, completions, and watch time.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True, blank=True, related_name='analytics')
    
    views_count = models.PositiveBigIntegerField(default=0)
    completion_count = models.PositiveIntegerField(default=0)
    total_watch_minutes = models.PositiveBigIntegerField(default=0)
    average_watch_percentage = models.FloatField(default=0.0)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        title = self.movie.title if self.movie else (self.series.title if self.series else 'Content')
        return f"Performance: {title} ({self.views_count} views)"
''')

# ==============================================================================
# 2. MODERATION APP MODELS
# ==============================================================================

write('moderation/models.py', '''import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from reviews.models import Review

class ContentReport(models.Model):
    """
    Flagged reviews, comments, or user profiles awaiting administrative review.
    """
    class ReasonChoices(models.TextChoices):
        SPAM = 'SPAM', 'Spam or Commercial Promotion'
        SPOILER = 'SPOILER', 'Unmarked Critical Plot Spoiler'
        HARASSMENT = 'HARASSMENT', 'Harassment or Hate Speech'
        OFFENSIVE = 'OFFENSIVE', 'Inappropriate or Offensive Content'
        OTHER = 'OTHER', 'Other Policy Violation'

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        RESOLVED = 'RESOLVED', 'Action Taken / Resolved'
        DISMISSED = 'DISMISSED', 'Dismissed / False Report'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submitted_reports')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True, related_name='reports')
    
    reason = models.CharField(max_length=30, choices=ReasonChoices.choices, default=ReasonChoices.SPOILER)
    explanation = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    
    moderator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_reports')
    moderator_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} ({self.reason}) - {self.status}"
''')

# ==============================================================================
# 3. AUDIT APP MODELS
# ==============================================================================

write('audit/models.py', '''import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone

class AuditEntry(models.Model):
    """
    Security and administrative audit trail recording critical platform mutations.
    """
    class ActionChoices(models.TextChoices):
        USER_LOGIN = 'USER_LOGIN', 'User Sign In'
        USER_REGISTER = 'USER_REGISTER', 'User Registration'
        SUBSCRIPTION_UPGRADE = 'SUBSCRIPTION_UPGRADE', 'Subscription Upgraded'
        PASSWORD_RESET = 'PASSWORD_RESET', 'Password Reset Initiated'
        CONTENT_PUBLISHED = 'CONTENT_PUBLISHED', 'Content Published'
        REPORT_RESOLVED = 'REPORT_RESOLVED', 'Moderation Report Resolved'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_actions')
    action = models.CharField(max_length=50, choices=ActionChoices.choices, default=ActionChoices.USER_LOGIN)
    details = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Audit Entries'

    def __str__(self):
        actor_email = self.actor.email if self.actor else 'System'
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {actor_email} -> {self.action}"
''')

print("Phase 5 Models written.")

import uuid
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

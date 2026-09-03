from django.utils import timezone
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

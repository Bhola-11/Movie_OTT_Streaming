from .models import Notification

class NotificationService:
    @staticmethod
    def send_notification(user, ntype, title, message, target_url='/'):
        return Notification.objects.create(
            user=user,
            notification_type=ntype,
            title=title,
            message=message,
            target_url=target_url
        )

    @staticmethod
    def mark_all_as_read(user):
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)

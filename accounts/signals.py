from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically initializes a UserProfile upon user account creation.
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            display_name=instance.full_name
        )
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()

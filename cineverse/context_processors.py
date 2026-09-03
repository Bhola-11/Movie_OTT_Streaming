from django.conf import settings
from django.utils import timezone

def cineverse_globals(request):
    """
    Injects platform-wide configurations, genres, navigation links, and active subscriptions.
    """
    context = {
        'SITE_NAME': 'CineVerse',
        'SITE_TAGLINE': 'The Next-Gen Cinema & OTT Streaming Universe',
        'CURRENT_YEAR': timezone.now().year,
        'DEBUG_MODE': settings.DEBUG,
        'SUPPORTED_QUALITIES': ['4K UHD', '1080p FHD', '720p HD', '480p SD'],
        'NAV_CATEGORIES': [
            {'name': 'Movies', 'url_name': 'movies:browse'},
            {'name': 'TV Shows', 'url_name': 'series:browse'},
            {'name': 'Genres', 'url_name': 'genres:list'},
            {'name': 'People & Stars', 'url_name': 'people:list'},
            {'name': 'Plans & VIP', 'url_name': 'subscriptions:plans'},
        ],
    }

    if request.user.is_authenticated:
        context['unread_notifications_count'] = getattr(request.user, 'unread_notifications_count', 0)
        context['user_profile'] = getattr(request.user, 'profile', None)
        context['is_vip'] = getattr(request.user, 'is_vip_subscriber', False)
        context['active_subscription'] = getattr(request.user, 'current_subscription', None)
        context['watchlist_count'] = getattr(request.user, 'watchlist_count', 0)
    else:
        context['unread_notifications_count'] = 0
        context['user_profile'] = None
        context['is_vip'] = False
        context['active_subscription'] = None
        context['watchlist_count'] = 0

    return context

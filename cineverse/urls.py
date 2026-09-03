import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 18 App Routes
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('genres/', include('genres.urls', namespace='genres')),
    path('people/', include('people.urls', namespace='people')),
    path('movies/', include('movies.urls', namespace='movies')),
    path('series/', include('series.urls', namespace='series')),
    path('seasons/', include('seasons.urls', namespace='seasons')),
    path('episodes/', include('episodes.urls', namespace='episodes')),
    path('player/', include('player.urls', namespace='player')),
    path('history/', include('history.urls', namespace='history')),
    path('watchlist/', include('watchlist.urls', namespace='watchlist')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('recommendations/', include('recommendations.urls', namespace='recommendations')),
    path('subscriptions/', include('subscriptions.urls', namespace='subscriptions')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('moderation/', include('moderation.urls', namespace='moderation')),
    path('audit/', include('audit.urls', namespace='audit')),
    
    # Homepage default redirect to movies catalog
    path('', RedirectView.as_view(pattern_name='movies:browse', permanent=False), name='root_home'),
]

if settings.DEBUG:
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

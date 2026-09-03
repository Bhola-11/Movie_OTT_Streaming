import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')

# movies
write('movies/views.py', '''from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView

class MovieBrowseView(TemplateView):
    template_name = 'movies/browse.html'

def movie_search_api(request):
    return JsonResponse({'results': []})
''')

write('movies/urls.py', '''from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.MovieBrowseView.as_view(), name='browse'),
    path('api/search/', views.movie_search_api, name='search_api'),
]
''')

# series
write('series/views.py', '''from django.views.generic import TemplateView

class SeriesBrowseView(TemplateView):
    template_name = 'series/browse.html'
''')

write('series/urls.py', '''from django.urls import path
from . import views

app_name = 'series'

urlpatterns = [
    path('', views.SeriesBrowseView.as_view(), name='browse'),
]
''')

# watchlist
write('watchlist/views.py', '''from django.views.generic import TemplateView

class WatchlistView(TemplateView):
    template_name = 'watchlist/my_list.html'
''')

write('watchlist/urls.py', '''from django.urls import path
from . import views

app_name = 'watchlist'

urlpatterns = [
    path('', views.WatchlistView.as_view(), name='my_list'),
]
''')

# subscriptions
write('subscriptions/views.py', '''from django.views.generic import TemplateView

class PlansView(TemplateView):
    template_name = 'subscriptions/plans.html'

class MySubscriptionView(TemplateView):
    template_name = 'subscriptions/my_subscription.html'
''')

write('subscriptions/urls.py', '''from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.PlansView.as_view(), name='plans'),
    path('mine/', views.MySubscriptionView.as_view(), name='my_subscription'),
]
''')

# history
write('history/views.py', '''from django.views.generic import TemplateView

class StreamHistoryView(TemplateView):
    template_name = 'history/stream_history.html'
''')

write('history/urls.py', '''from django.urls import path
from . import views

app_name = 'history'

urlpatterns = [
    path('', views.StreamHistoryView.as_view(), name='stream_history'),
]
''')

# notifications
write('notifications/views.py', '''from django.views.generic import TemplateView

class NotificationInboxView(TemplateView):
    template_name = 'notifications/inbox.html'
''')

write('notifications/urls.py', '''from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationInboxView.as_view(), name='inbox'),
]
''')

# analytics
write('analytics/views.py', '''from django.views.generic import TemplateView

class AnalyticsDashboardView(TemplateView):
    template_name = 'analytics/dashboard.html'
''')

write('analytics/urls.py', '''from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsDashboardView.as_view(), name='dashboard'),
]
''')

# Also create placeholder template files so rendering them doesn't fail
placeholders = [
    'movies/browse.html', 'series/browse.html', 'watchlist/my_list.html',
    'subscriptions/plans.html', 'subscriptions/my_subscription.html',
    'history/stream_history.html', 'notifications/inbox.html', 'analytics/dashboard.html'
]
for p in placeholders:
    write(f'templates/{p}', '{% extends "base.html" %}\n{% block content %}<div class="container" style="padding-top:2rem;"><h2>Coming in Phase</h2></div>{% endblock %}')

print("Placeholder views and templates created.")

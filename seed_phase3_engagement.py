import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
django.setup()

from django.contrib.auth import get_user_model
from movies.models import Movie
from series.models import Series
from history.models import WatchHistory
from watchlist.models import WatchlistItem, FavoriteItem
from reviews.models import Review

User = get_user_model()
admin = User.objects.filter(email='admin@cineverse.io').first()
viewer = User.objects.filter(email='viewer@cineverse.io').first()

neo_tokyo = Movie.objects.filter(title__icontains='Neo Tokyo').first()
quantum = Movie.objects.filter(title__icontains='Quantum Singularity').first()
vanguard = Movie.objects.filter(title__icontains='Vanguard').first()

if viewer and neo_tokyo:
    # 1. Watch History & Continue Watching entry
    h, _ = WatchHistory.objects.get_or_create(
        user=viewer,
        movie=neo_tokyo,
        defaults={
            'current_position_seconds': 4200,
            'total_duration_seconds': 8880,
            'percentage_watched': 47.3,
            'is_completed': False,
            'device_type': 'Desktop'
        }
    )
    print(f"Watch History seeded: {h}")

    # 2. Watchlist & Favorites
    w, _ = WatchlistItem.objects.get_or_create(user=viewer, movie=quantum)
    fav, _ = FavoriteItem.objects.get_or_create(user=viewer, movie=neo_tokyo)
    print("Watchlist & Favorites seeded.")

    # 3. Reviews with ratings
    r1, _ = Review.objects.get_or_create(
        user=viewer,
        movie=neo_tokyo,
        defaults={
            'rating': 10,
            'title': 'A Cyberpunk Masterpiece for the Ages',
            'content': 'The world-building, sound design in Dolby Atmos, and Keanu Reeves performance redefine modern sci-fi.',
            'helpful_votes_count': 14,
            'contains_spoilers': False
        }
    )
    print(f"Review seeded: {r1.title}")

if admin and vanguard:
    r2, _ = Review.objects.get_or_create(
        user=admin,
        movie=vanguard,
        defaults={
            'rating': 9,
            'title': 'High-stakes espionage thriller done right',
            'content': 'Pacing never slows down. Incredible stunt choreography.',
            'helpful_votes_count': 8,
            'contains_spoilers': False
        }
    )
    print(f"Admin review seeded: {r2.title}")

print("Phase 3 Engagement Data Populated Successfully.")

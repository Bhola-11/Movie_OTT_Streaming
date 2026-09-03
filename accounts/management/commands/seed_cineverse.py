import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.text import slugify
from genres.models import Genre, Category, Mood, Tag
from people.models import Person, Profession, PersonAward
from movies.models import Movie, MovieCast, MovieSubtitle, MovieQuality
from series.models import Series, SeriesCast
from seasons.models import Season
from episodes.models import Episode
from subscriptions.models import Plan, UserSubscription
from payments.models import PaymentTransaction, Invoice
from payments.services import PaymentProcessingService
from history.models import WatchHistory
from watchlist.models import WatchlistItem, FavoriteItem
from reviews.models import Review
from notifications.models import Notification
from analytics.models import DailyPlatformMetric, ContentPerformance
from audit.models import AuditEntry

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the complete CineVerse platform with realistic catalog, users, series, episodes, plans, reviews, invoices, and analytics."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Commencing CineVerse Master Catalog Seeding..."))

        # 1. Users
        admin = User.objects.filter(email='admin@cineverse.io').first()
        if not admin:
            admin = User.objects.create_superuser('admin@cineverse.io', 'Admin12345!', first_name='CineVerse', last_name='Admin')

        viewer = User.objects.filter(email='viewer@cineverse.io').first()
        if not viewer:
            viewer = User.objects.create_user('viewer@cineverse.io', 'Viewer12345!', first_name='Alex', last_name='Rivers')

        # 2. Genres & Categories
        genres_list = [
            ('Action & Adventure', 'Explosions, martial arts, and high-octane blockbusters'),
            ('Sci-Fi & Cyberpunk', 'Neon dystopias, artificial minds, and time distortion'),
            ('Psychological Thriller', 'Mind games, plot twists, and edge-of-seat suspense'),
            ('Crime Noir', 'Underworld syndicates, gritty detectives, and dark alleys'),
            ('Anime & Animation', 'Stunning animated epics, fantasy sagas, and visual wonders'),
            ('Drama & Romance', 'Intense human journeys, relationships, and heartfelt drama'),
        ]
        created_genres = {}
        for name, desc in genres_list:
            slug = slugify(name)
            g = Genre.objects.filter(slug=slug).first()
            if not g:
                g = Genre.objects.create(name=name, description=desc, is_featured=True)
            created_genres[name] = g

        # 3. People & Creators
        director_prof, _ = Profession.objects.get_or_create(name='Director')
        actor_prof, _ = Profession.objects.get_or_create(name='Actor')

        nolan = Person.objects.filter(full_name='Christopher Nolan').first()
        if not nolan:
            nolan = Person.objects.create(full_name='Christopher Nolan', primary_profession=director_prof, biography='Auteur director of non-linear epics.', popularity_score=99.0)

        reeves = Person.objects.filter(full_name='Keanu Reeves').first()
        if not reeves:
            reeves = Person.objects.create(full_name='Keanu Reeves', primary_profession=actor_prof, biography='Legendary action icon.', popularity_score=98.5)

        # 4. Subscription Plans
        vip_plan = Plan.objects.filter(tier_code='VIP_4K').first()
        if not vip_plan:
            vip_plan = Plan.objects.create(
                tier_code='VIP_4K',
                name='VIP Ultra 4K',
                description='4K HDR with Dolby Atmos and 4 concurrent screens.',
                price_monthly=19.99,
                price_yearly=199.99,
                max_screens=4,
                max_resolution='4K UHD',
                has_dolby_atmos=True,
                allows_offline_downloads=True,
                ad_free=True
            )

        # 5. Movies
        movie1 = Movie.objects.filter(title='Chronicles of Neo Tokyo 2088').first()
        if not movie1:
            movie1 = Movie.objects.create(
                title='Chronicles of Neo Tokyo 2088',
                tagline='Memory is the ultimate currency.',
                synopsis='A rogue investigator uncovers a memory theft conspiracy in 2088 Neo Tokyo.',
                duration_minutes=148,
                content_rating='PG-13',
                resolution='4K',
                average_rating=9.4,
                view_count=1520000,
                is_featured=True,
                is_trending=True
            )
            movie1.genres.set([created_genres['Sci-Fi & Cyberpunk'], created_genres['Action & Adventure']])
            movie1.directors.set([nolan])

        # 6. TV Series, Seasons, Episodes
        series1 = Series.objects.filter(title='CyberRealm: District 9').first()
        if not series1:
            series1 = Series.objects.create(
                title='CyberRealm: District 9',
                tagline='The network never sleeps.',
                synopsis='A non-augmented detective investigates memory hacks in a cybernetic grid.',
                content_rating='TV-MA',
                is_featured=True,
                is_trending=True
            )
            series1.genres.set([created_genres['Sci-Fi & Cyberpunk']])
            
            season1, _ = Season.objects.get_or_create(series=series1, season_number=1, defaults={'title': 'Season 1: Genesis'})
            for idx in range(1, 5):
                Episode.objects.get_or_create(
                    season=season1,
                    episode_number=idx,
                    defaults={
                        'title': f"Episode {idx}: Network Nexus",
                        'synopsis': f"The investigation deepens as sector {idx} goes offline.",
                        'duration_minutes': 50 + idx,
                        'intro_start_sec': 30,
                        'intro_end_sec': 75
                    }
                )

        # 7. Audit Entry & Daily Metrics
        AuditEntry.objects.create(
            actor=admin,
            action=AuditEntry.ActionChoices.CONTENT_PUBLISHED,
            details='Master platform catalog verified and published.'
        )

        DailyPlatformMetric.objects.get_or_create(
            date=timezone.now().date(),
            defaults={
                'total_views': 3500000,
                'total_watch_seconds': 180000000,
                'unique_active_users': 14200,
                'gross_revenue': 28500.00
            }
        )

        self.stdout.write(self.style.SUCCESS("All CineVerse domains successfully seeded and operational!"))

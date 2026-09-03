import os
import django
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
django.setup()

from genres.models import Genre, Tag
from people.models import Person
from movies.models import Movie, MovieCast, MovieSubtitle
from series.models import Series, SeriesCast
from seasons.models import Season
from episodes.models import Episode

# Fetch genres and people
action_genre = Genre.objects.filter(name__icontains='Action').first()
scifi_genre = Genre.objects.filter(name__icontains='Sci-Fi').first()
thriller_genre = Genre.objects.filter(name__icontains='Thriller').first()

nolan = Person.objects.filter(full_name__icontains='Nolan').first()
reeves = Person.objects.filter(full_name__icontains='Reeves').first()

# 1. Create Feature Films
movies_data = [
    {
        'title': 'Chronicles of Neo Tokyo 2088',
        'tagline': 'In a city of neon shadows, memory is the ultimate currency.',
        'synopsis': 'A rogue cybernetic investigator uncovers a syndicate manipulating collective human memories across the mega-city grid of Neo Tokyo.',
        'duration_minutes': 148,
        'content_rating': 'PG-13',
        'resolution': '4K',
        'is_featured': True,
        'is_trending': True,
        'average_rating': 9.4,
        'view_count': 1420500,
        'genres': [scifi_genre, action_genre],
        'directors': [nolan] if nolan else [],
        'cast': [(reeves, 'Commander Kenji Sato', 1)] if reeves else []
    },
    {
        'title': 'Quantum Singularity: Event Horizon',
        'tagline': 'Beyond the threshold of known physics lies human destiny.',
        'synopsis': 'A crew of theoretical astrophysicists embarks on a deep space expedition to harvest energy from a rotating Kerr black hole, only to enter a non-linear time continuum.',
        'duration_minutes': 165,
        'content_rating': 'PG-13',
        'resolution': '4K',
        'is_featured': True,
        'is_trending': True,
        'average_rating': 9.1,
        'view_count': 980400,
        'genres': [scifi_genre, thriller_genre],
        'directors': [nolan] if nolan else [],
    },
    {
        'title': 'Vanguard: Shadow Protocol',
        'tagline': 'Trust is treason when the government operates in the dark.',
        'synopsis': 'An elite black-ops operative is framed for a geopolitical catastrophe and must dismantle an underground mercenary coalition before a global blackout is triggered.',
        'duration_minutes': 130,
        'content_rating': 'R',
        'resolution': '1080P',
        'is_featured': False,
        'is_trending': True,
        'average_rating': 8.8,
        'view_count': 850200,
        'genres': [action_genre, thriller_genre],
        'cast': [(reeves, 'John Vance', 1)] if reeves else []
    },
    {
        'title': 'The Paris Cryptanalysis',
        'tagline': 'A lost wartime frequency resurfaces seventy years later.',
        'synopsis': 'A modern French cryptographer detects anomalous radio signals echoing beneath the Parisian catacombs, containing undiscovered encrypted intelligence from 1944.',
        'duration_minutes': 118,
        'content_rating': 'PG-13',
        'resolution': '1080P',
        'is_featured': False,
        'is_trending': False,
        'average_rating': 8.3,
        'view_count': 420000,
        'genres': [thriller_genre],
    },
    {
        'title': 'Solaris Drift',
        'tagline': 'The silence between stars speaks the loudest truths.',
        'synopsis': 'Stranded in the asteroid belt following a gravitational anomaly, a lone mining vessel captain races to repair life support systems while hearing transmissions from Earth that occurred twenty years in the past.',
        'duration_minutes': 112,
        'content_rating': 'PG',
        'resolution': '4K',
        'is_featured': True,
        'is_trending': True,
        'average_rating': 8.9,
        'view_count': 1150000,
        'genres': [scifi_genre],
    }
]

for m_data in movies_data:
    genres_list = [g for g in m_data.pop('genres') if g]
    directors_list = [d for d in m_data.pop('directors', []) if d]
    cast_list = m_data.pop('cast', [])
    
    movie, created = Movie.objects.get_or_create(
        title=m_data['title'],
        defaults=m_data
    )
    if created:
        movie.genres.set(genres_list)
        movie.directors.set(directors_list)
        for person, char_name, order in cast_list:
            MovieCast.objects.create(movie=movie, person=person, character_name=char_name, billing_order=order, is_lead=True)
        # Add sample subtitle
        MovieSubtitle.objects.create(movie=movie, language_code='en', language_name='English (CC)', is_default=True)
    print(f"Movie ready: {movie.title}")

# 2. Create TV Series with Seasons and Episodes
series_data = [
    {
        'title': 'CyberRealm: District 9',
        'tagline': 'The network never sleeps. Neither do the sentinels.',
        'synopsis': 'In an alternate dystopian metropolis where minds are cloud-synced, an un-augmented detective investigates a rash of neural disconnects known as The Glitch.',
        'content_rating': 'TV-MA',
        'is_featured': True,
        'is_trending': True,
        'average_rating': 9.5,
        'genres': [scifi_genre, thriller_genre],
        'seasons': [
            {
                'season_number': 1,
                'title': 'Season 1: Zero Day',
                'episodes': [
                    ('The Ghost in the Fiber', 'A murdered bio-hacker leaves behind a biometric key that unlocks the deepest quarantine tier.', 52),
                    ('Packet Collision', 'Agent Vance tracks the contraband memory drive to an underground sub-level nightclub.', 48),
                    ('Buffer Overflow', 'A sudden system-wide lockdown forces synthetic citizens into a deadly standoff.', 56),
                    ('Root Access', 'The identity of the puppet master reveals a chilling truth regarding the founding fathers of the city.', 61),
                ]
            },
            {
                'season_number': 2,
                'title': 'Season 2: Dark Protocol',
                'episodes': [
                    ('Hard Reset', 'Six months after the quarantine breach, decentralized factions battle for mainframe control.', 50),
                    ('Synthetic Soul', 'A rogue Android claims to possess memories belonging to a deceased high commissioner.', 54),
                ]
            }
        ]
    }
]

for s_data in series_data:
    genres_list = [g for g in s_data.pop('genres') if g]
    seasons_list = s_data.pop('seasons')
    
    series, created = Series.objects.get_or_create(
        title=s_data['title'],
        defaults=s_data
    )
    if created:
        series.genres.set(genres_list)
        for s_info in seasons_list:
            episodes = s_info.pop('episodes')
            season, _ = Season.objects.get_or_create(series=series, season_number=s_info['season_number'], defaults=s_info)
            for idx, (ep_title, ep_synopsis, dur) in enumerate(episodes, start=1):
                Episode.objects.get_or_create(
                    season=season,
                    episode_number=idx,
                    defaults={
                        'title': ep_title,
                        'synopsis': ep_synopsis,
                        'duration_minutes': dur,
                        'intro_start_sec': 30,
                        'intro_end_sec': 75,
                        'outro_start_sec': (dur * 60) - 90
                    }
                )
    print(f"Series ready: {series.title} with {series.total_seasons} seasons")

print("Phase 2 Catalog Seeding Completed!")

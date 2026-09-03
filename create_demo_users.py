import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
django.setup()

from django.contrib.auth import get_user_model
from genres.models import Genre, Category, Mood
from people.models import Person, Profession

User = get_user_model()

# 1. Superuser & Viewer
if not User.objects.filter(email='admin@cineverse.io').exists():
    User.objects.create_superuser('admin@cineverse.io', 'Admin12345!', first_name='CineVerse', last_name='Admin')
    print('Created admin: admin@cineverse.io / Admin12345!')

if not User.objects.filter(email='viewer@cineverse.io').exists():
    User.objects.create_user('viewer@cineverse.io', 'Viewer12345!', first_name='Alex', last_name='Viewer')
    print('Created viewer: viewer@cineverse.io / Viewer12345!')

# 2. Seed initial sample genres & moods
genres = [
    ('Action & Adventure', 'High octane explosions, martial arts, and global quests.'),
    ('Sci-Fi & Cyberpunk', 'Futuristic dystopias, neon cities, and artificial intelligence.'),
    ('Psychological Thriller', 'Mind-bending twists, suspense, and psychological games.'),
    ('Crime & Noir', 'Underworld syndicates, detectives, and gritty streets.'),
    ('Animation & Anime', 'Stunning animated epics, shonen battles, and fantasy realms.'),
    ('Drama & Romance', 'Emotional storytelling, relationships, and human experiences.')
]

for name, desc in genres:
    Genre.objects.get_or_create(name=name, defaults={'description': desc, 'is_featured': True})

moods = [
    ('Adrenaline Rush', 'Fast-paced, explosive action to get your heart pumping.'),
    ('Mind-Bending', 'Cerebral plots and shocking mysteries that keep you guessing.'),
    ('Heartwarming', 'Comforting, uplifting stories for family and friends.'),
    ('Spine-Chilling', 'Dark tension, terror, and supernatural thrills.')
]

for name, desc in moods:
    Mood.objects.get_or_create(name=name, defaults={'description': desc})

# 3. Sample professions & people
actor_prof, _ = Profession.objects.get_or_create(name='Actor')
director_prof, _ = Profession.objects.get_or_create(name='Director')

Person.objects.get_or_create(
    full_name='Christopher Nolan',
    defaults={
        'primary_profession': director_prof,
        'biography': 'Acclaimed auteur filmmaker known for Inception, Interstellar, The Dark Knight, and Oppenheimer.',
        'popularity_score': 99.5,
        'is_featured': True
    }
)

Person.objects.get_or_create(
    full_name='Keanu Reeves',
    defaults={
        'primary_profession': actor_prof,
        'biography': 'Beloved action icon celebrated for The Matrix, John Wick, and Speed.',
        'popularity_score': 98.0,
        'is_featured': True
    }
)

print('Demo content & users successfully populated.')

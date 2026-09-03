import os
import json
import uuid
import random

def generate_fixtures():
    os.makedirs('fixtures', exist_ok=True)
    
    genres = [
        'Action & Adventure', 'Sci-Fi & Cyberpunk', 'Psychological Thriller',
        'Crime & Underworld', 'Epic Fantasy', 'Anime & Animation',
        'Historical Drama', 'Mystery & Detective', 'Horror & Paranormal',
        'Documentary & True Crime', 'Comedy & Parody', 'Romance & Passion'
    ]

    directors = [
        'Christopher Nolan', 'Denis Villeneuve', 'Ridley Scott', 'David Fincher',
        'Quentin Tarantino', 'Hayao Miyazaki', 'Guillermo del Toro', 'Martin Scorsese',
        'James Cameron', 'Stanley Kubrick', 'Greta Gerwig', 'Bong Joon-ho'
    ]

    actors = [
        'Keanu Reeves', 'Cillian Murphy', 'Leonardo DiCaprio', 'Christian Bale',
        'Scarlett Johansson', 'Florence Pugh', 'Ryan Gosling', 'Tom Hardy',
        'Zendaya', 'Timothee Chalamet', 'Margot Robbie', 'Oscar Isaac',
        'Matthew McConaughey', 'Pedro Pascal', 'Mads Mikkelsen', 'Ana de Armas'
    ]

    titles_adjectives = [
        'Silent', 'Neon', 'Quantum', 'Dark', 'Infinite', 'Forgotten', 'Cyber', 'Iron',
        'Golden', 'Vicious', 'Astral', 'Lost', 'Electric', 'Solar', 'Velvet', 'Frozen',
        'Crimson', 'Midnight', 'Hyper', 'Shadow', 'Savage', 'Atomic', 'Hidden', 'Final'
    ]

    titles_nouns = [
        'Horizon', 'Protocol', 'Legacy', 'Echo', 'Empire', 'Paradox', 'Chronicles', 'Syndicate',
        'Requiem', 'Vanguard', 'Matrix', 'Nexus', 'Enigma', 'Obsidian', 'Singularity', 'Odyssey',
        'Drift', 'Ascent', 'Revenant', 'Genesis', 'Conspiracy', 'Phantom', 'Frontier', 'Eclipse'
    ]

    resolutions = ['4K', '1080P', '720P']
    ratings = ['G', 'PG', 'PG-13', 'R']

    catalog = []

    # Generate 500 Realistic Movies
    for i in range(1, 501):
        adj = titles_adjectives[(i * 7) % len(titles_adjectives)]
        noun = titles_nouns[(i * 11) % len(titles_nouns)]
        title = f"{adj} {noun}: Chapter {((i % 5) + 1)}"
        dur = random.randint(85, 175)
        res = resolutions[i % len(resolutions)]
        rating = ratings[i % len(ratings)]
        score = round(random.uniform(7.5, 9.8), 1)
        views = random.randint(50000, 5000000)
        
        catalog.append({
            "model": "movies.movie",
            "pk": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cineverse-movie-{i}")),
            "fields": {
                "title": title,
                "slug": f"{adj.lower()}-{noun.lower()}-chapter-{(i % 5) + 1}-{i}",
                "tagline": f"The story of {adj.lower()} forces colliding against the ultimate {noun.lower()}.",
                "synopsis": f"In a world where {adj.lower()} technology alters the balance of power, a lone operative must navigate through the secrets of the {noun.lower()} before disaster strikes.",
                "release_date": f"{2000 + (i % 26):04d}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "duration_minutes": dur,
                "content_rating": rating,
                "resolution": res,
                "audio_format": "Dolby Atmos 5.1" if res == '4K' else "Stereo",
                "aspect_ratio": "2.39:1 Anamorphic",
                "is_featured": (i % 15 == 0),
                "is_trending": (i % 8 == 0),
                "is_original": (i % 4 == 0),
                "is_vip_only": (res == '4K'),
                "is_published": True,
                "view_count": views,
                "average_rating": score,
                "ratings_count": int(views * 0.005)
            }
        })

    # Generate 150 Multi-Season Series
    for s_idx in range(1, 151):
        adj = titles_adjectives[(s_idx * 3) % len(titles_adjectives)]
        noun = titles_nouns[(s_idx * 5) % len(titles_nouns)]
        title = f"The {adj} {noun}"
        seasons_cnt = (s_idx % 6) + 1
        
        catalog.append({
            "model": "series.series",
            "pk": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cineverse-series-{s_idx}")),
            "fields": {
                "title": title,
                "slug": f"the-{adj.lower()}-{noun.lower()}-{s_idx}",
                "tagline": f"A multi-season deep dive into the {adj.lower()} phenomenon.",
                "synopsis": f"Follow the sprawling saga across {seasons_cnt} acclaimed seasons as secrets unravel and rival dynasties clash.",
                "status": "ONGOING" if s_idx % 2 == 0 else "CONCLUDED",
                "content_rating": "TV-MA",
                "is_featured": (s_idx % 10 == 0),
                "is_trending": (s_idx % 6 == 0),
                "is_published": True,
                "average_rating": round(random.uniform(8.2, 9.7), 1),
                "view_count": random.randint(100000, 4500000)
            }
        })

    output_path = os.path.join('fixtures', 'catalog_fixtures.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2)

    print(f"Generated {len(catalog)} fixture entries in {output_path}")

if __name__ == '__main__':
    generate_fixtures()

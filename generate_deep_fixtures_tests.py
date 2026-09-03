import os
import json
import uuid
import random

def generate_talent_and_episodes():
    os.makedirs('fixtures', exist_ok=True)
    entries = []

    # 1. 200 Cast & Crew Talent Profiles
    first_names = ['Christian', 'Emma', 'Daniel', 'Julian', 'Sophia', 'Lucas', 'Maya', 'Liam', 'Olivia', 'Ethan', 'Zoe', 'Alexander', 'Eva', 'Marcus', 'Elena', 'Gabriel']
    last_names = ['Vance', 'Mercer', 'Blackwood', 'Stirling', 'Frost', 'Sinclair', 'Castillo', 'Hawthorne', 'Nakamura', 'Kowalski', 'Dupont', 'Lindqvist', 'Sterling', 'Moretti']
    professions = ['Actor', 'Director', 'Cinematographer', 'Composer', 'Screenwriter', 'Executive Producer']

    for i in range(1, 201):
        fn = first_names[(i * 3) % len(first_names)]
        ln = last_names[(i * 5) % len(last_names)]
        full_name = f"{fn} {ln}"
        prof = professions[i % len(professions)]
        
        entries.append({
            "model": "people.person",
            "pk": i + 10,
            "fields": {
                "full_name": full_name,
                "slug": f"{fn.lower()}-{ln.lower()}-{i}",
                "stage_name": full_name,
                "biography": f"{full_name} is an internationally acclaimed {prof.lower()} known for transformative performances and cinematic masterworks spanning over two decades.",
                "birth_date": f"{1965 + (i % 35):04d}-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "place_of_birth": f"City of {fn}ville, Country {i}",
                "gender": "M" if i % 2 == 0 else "F",
                "imdb_id": f"nm{1000000 + i}",
                "tmdb_id": f"p{200000 + i}",
                "is_featured": (i % 5 == 0),
                "popularity_score": round(random.uniform(80.0, 99.8), 1)
            }
        })

    # 2. 350 Multi-Season Sequenced Episodes
    episode_verbs = ['Inception', 'Collision', 'Betrayal', 'Reckoning', 'Ascension', 'Exile', 'Convergence', 'Awakening', 'Revelation', 'Fallout']
    for ep_id in range(1, 351):
        verb = episode_verbs[ep_id % len(episode_verbs)]
        runtime = random.randint(42, 68)
        intro_st = random.randint(30, 60)
        intro_en = intro_st + random.randint(40, 60)
        outro_st = (runtime * 60) - random.randint(90, 150)
        
        entries.append({
            "model": "episodes.episode",
            "pk": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cineverse-ep-{ep_id}")),
            "fields": {
                "season_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cineverse-season-{(ep_id % 30) + 1}")),
                "episode_number": (ep_id % 12) + 1,
                "title": f"The {verb} of Sector {(ep_id % 9) + 1}",
                "slug": f"the-{verb.lower()}-of-sector-{(ep_id % 9) + 1}-{ep_id}",
                "synopsis": f"Tensions peak as the primary network nexus experiences a critical breach, forcing the lead team into an emergency extraction.",
                "duration_minutes": runtime,
                "air_date": f"2023-{(ep_id % 12) + 1:02d}-{(ep_id % 28) + 1:02d}",
                "intro_start_sec": intro_st,
                "intro_end_sec": intro_en,
                "outro_start_sec": outro_st,
                "is_free_preview": (ep_id % 8 == 0),
                "view_count": random.randint(25000, 1500000)
            }
        })

    output_path = os.path.join('fixtures', 'talent_and_episodes.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2)

    print(f"Generated {len(entries)} talent & episode entries in {output_path}")

if __name__ == '__main__':
    generate_talent_and_episodes()

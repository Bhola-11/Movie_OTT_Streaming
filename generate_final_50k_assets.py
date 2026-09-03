import os
import json
import uuid

def generate_curated_collections():
    os.makedirs('fixtures', exist_ok=True)
    collections = []

    collection_themes = [
        ("The Cyberpunk Vanguard", "Dystopian high-tech mega-cities, neon aesthetics, and synthetic intelligences."),
        ("Auteur Visions: 70mm Panavision", "Masterful cinematic scale from visionaries like Christopher Nolan and Denis Villeneuve."),
        ("The Noir Underground", "Rain-slicked streets, hard-boiled detectives, and labyrinthine conspiracies."),
        ("Space Odyssey & Time Anomalies", "Wormholes, black holes, and deep space survival across quantum horizons."),
        ("Psychological Enigmas", "Mind-bending unreliable narrators and cerebral plot twists."),
        ("Golden Age of Anime", "Iconic hand-drawn animations and mythical fantasy sagas."),
        ("Adrenaline Overdrive", "Relentless martial arts choreography and precision vehicular stunts."),
        ("Heartfelt Dramas & Romances", "Deeply touching emotional character journeys and sweeping romantic epics.")
    ]

    for c_id, (name, desc) in enumerate(collection_themes, start=1):
        for item_idx in range(1, 41):
            collections.append({
                "model": "movies.curatedcollection",
                "pk": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cineverse-collection-{c_id}-{item_idx}")),
                "fields": {
                    "collection_name": name,
                    "collection_description": desc,
                    "item_rank": item_idx,
                    "curator_notes": f"Selected as quintessential entry #{item_idx} embodying {name.lower()} aesthetic and storytelling standards.",
                    "is_featured_banner": (item_idx == 1),
                    "added_date": f"2024-{(item_idx % 12) + 1:02d}-01"
                }
            })

    output_path = os.path.join('fixtures', 'curated_collections.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(collections, f, indent=2)

    print(f"Generated {len(collections)} collection entries in {output_path}")

if __name__ == '__main__':
    generate_curated_collections()

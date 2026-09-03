import os
import json
import uuid
import random

def generate_reviews_dataset():
    os.makedirs('fixtures', exist_ok=True)
    reviews = []

    review_titles = [
        "A Visual Tour de Force That Demands the Biggest Screen",
        "Exceptional World-Building and Gripping Atmospheric Tension",
        "Subtle Narrative Perfection Paired with Kinetic Pacing",
        "A Modern Classic Destined for Enduring Cultural Legacy",
        "Uncompromising Cinematic Ambition Executed Flawlessly",
        "Hypnotic Musical Score That Elevates Every Climax",
        "Raw, Gritty, and Unforgivingly Compelling Storytelling",
        "Breathtaking 4K HDR Color Grading and Spatial Audio",
        "An Emotional Rollercoaster Anchored by Stellar Performances",
        "Redefines the Streaming Experience for Modern Audiences",
        "Riveting Dialogue That Lingers Long After the Credits Roll",
        "A Daring High-Concept Masterpiece That Pays Off Completely"
    ]

    review_bodies = [
        "From the opening tracking shot to the pulse-pounding third act resolution, this title stands as an extraordinary benchmark in cinematic craft. The cinematography is nothing short of transcendent, utilizing lighting and practical atmospheric effects that draw you completely into the characters' inner dilemmas.",
        "The sound design in Dolby Atmos delivers exceptional spatial clarity, making every whisper and explosive collision reverberate with profound emotional weight. What separates this from standard genre fare is the rigorous character development—each choice carries palpable stakes.",
        "A breathtaking fusion of meticulous directing and fearless acting. The psychological nuances explored here elevate the narrative beyond conventional expectations, rewarding multiple viewings with subtle thematic layers.",
        "Rarely does a modern release balance intellectual ambition with pure entertainment value so effortlessly. The narrative construction keeps you perpetually guessing without ever resorting to cheap gimmicks.",
        "An absolute triumph of pacing and visual storytelling. The director demonstrates complete command over mood and rhythm, building tension patiently before delivering a climax that is both shocking and poetically inevitable."
    ]

    for i in range(1, 501):
        title = review_titles[i % len(review_titles)]
        body = review_bodies[i % len(review_bodies)]
        rating = random.choice([8, 9, 10, 8, 9, 10, 7, 9])
        helpful = random.randint(3, 45)
        
        reviews.append({
            "model": "reviews.review",
            "pk": str(uuid.uuid5(uuid.NAMESPACE_DNS, f"cineverse-review-{i}")),
            "fields": {
                "rating": rating,
                "title": f"{title} (Critique #{i})",
                "content": f"{body} Overall rating of {rating}/10 reflects the immense production quality and screenwriting precision.",
                "contains_spoilers": (i % 7 == 0),
                "is_approved": True,
                "helpful_votes_count": helpful,
                "created_at": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}T12:00:00Z"
            }
        })

    output_path = os.path.join('fixtures', 'reviews_and_ratings.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(reviews, f, indent=2)

    print(f"Generated {len(reviews)} review entries in {output_path}")

if __name__ == '__main__':
    generate_reviews_dataset()

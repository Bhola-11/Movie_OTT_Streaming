import re

class ContentSafetyEngine:
    """
    Automated toxicity classifier and profanity filter with regex phrase matching.
    """
    FLAGGED_PATTERNS = [
        r'\b(pirate|torrent|crack|warez|keygen)\b',
        r'\b(free\s+stream|watch\s+free|123movies|putlocker)\b',
        r'\b(cheat|scam|crypto\s+giveaway|whatsapp\s+group)\b',
        r'\b(spoiler|dies\s+at\s+the\s+end|killer\s+is)\b',
    ]

    @classmethod
    def inspect_text(cls, text):
        if not text:
            return {'is_clean': True, 'flagged_matches': []}
            
        matches = []
        lower_text = text.lower()
        for pattern in cls.FLAGGED_PATTERNS:
            found = re.findall(pattern, lower_text)
            if found:
                matches.extend(found)

        return {
            'is_clean': len(matches) == 0,
            'flagged_matches': list(set(matches)),
            'severity_level': 'HIGH' if len(matches) > 1 else ('MEDIUM' if matches else 'NONE')
        }

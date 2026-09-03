from django.db.models import Count, Avg
from .models import Person, Profession

class AdvancedPeopleService:
    """
    Talent catalog service for retrieving acclaimed filmmakers,
    actor filmographies, and award-winning creators.
    """
    @staticmethod
    def get_hall_of_fame(min_awards=1):
        """
        Returns cinematic creators who have achieved major competitive awards.
        """
        return Person.objects.annotate(
            awards_count=Count('awards')
        ).filter(awards_count__gte=min_awards).order_by('-popularity_score', '-awards_count')

    @staticmethod
    def get_directors_by_genre(genre_name):
        """
        Discovers directors who have helmed titles in the specified genre.
        """
        return Person.objects.filter(
            primary_profession__slug='director',
            directed_movies__genres__name=genre_name
        ).distinct()[:15]

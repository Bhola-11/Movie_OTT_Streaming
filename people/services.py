from .models import Person

class PeopleService:
    @staticmethod
    def get_trending_actors():
        return Person.objects.filter(primary_profession__slug='actor').order_by('-popularity_score')[:12]

    @staticmethod
    def get_acclaimed_directors():
        return Person.objects.filter(primary_profession__slug='director').order_by('-popularity_score')[:12]

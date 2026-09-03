from .models import Genre, Category, Mood, Tag

class GenreService:
    @staticmethod
    def get_featured_genres():
        return Genre.objects.filter(is_featured=True).order_by('display_order')

    @staticmethod
    def get_active_categories():
        return Category.objects.filter(is_active=True).order_by('order')

    @staticmethod
    def get_all_moods():
        return Mood.objects.all().order_by('name')

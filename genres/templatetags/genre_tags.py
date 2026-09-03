from django import template
from genres.models import Genre, Mood

register = template.Library()

@register.inclusion_tag('genres/components/genre_pills.html')
def render_genre_pills(active_genre=None):
    return {
        'genres': Genre.objects.all()[:12],
        'active_genre': active_genre
    }

@register.inclusion_tag('genres/components/mood_chips.html')
def render_mood_chips():
    return {
        'moods': Mood.objects.all()[:8]
    }

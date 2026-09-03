from django import template
from movies.models import Movie

register = template.Library()

@register.filter(name='rating_color')
def rating_color(rating):
    try:
        val = float(rating)
        if val >= 8.5:
            return '#00DF9A'  # Green
        elif val >= 7.0:
            return '#FFB800'  # Gold
        else:
            return '#8E95A5'  # Gray
    except Exception:
        return '#FFB800'

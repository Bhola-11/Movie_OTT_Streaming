from django import template

register = template.Library()

@register.filter(name='person_avatar')
def person_avatar(person):
    if person and person.photo:
        return person.photo.url
    return f"https://api.dicebear.com/7.x/initials/svg?seed={getattr(person, 'full_name', 'Star')}&backgroundColor=1f2330"

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='role_badge')
def role_badge(role):
    """
    Renders an OTT role badge with distinct colors.
    """
    badges = {
        'ADMIN': '<span class="badge badge-admin">ADMIN</span>',
        'MODERATOR': '<span class="badge badge-moderator">MOD</span>',
        'CREATOR': '<span class="badge badge-creator">CREATOR</span>',
        'VIEWER': '<span class="badge badge-viewer">VIEWER</span>',
    }
    return mark_safe(badges.get(role, '<span class="badge">MEMBER</span>'))

@register.filter(name='avatar_url')
def avatar_url(user):
    """
    Resolves the user avatar or returns a styled SVG fallback.
    """
    if user and user.avatar:
        return user.avatar.url
    return f"https://api.dicebear.com/7.x/bottts/svg?seed={getattr(user, 'email', 'cineverse')}&backgroundColor=14161d"

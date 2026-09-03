from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def role_required(allowed_roles):
    """
    Decorator enforcing that the current user has one of the specified roles.
    Allowed roles can be a list or tuple of User.RoleChoices.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                try:
                    messages.warning(request, "Please log in to access this section.")
                except Exception:
                    pass
                return redirect(f"{reverse('accounts:login')}?next={request.path}")
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if request.user.role not in allowed_roles:
                try:
                    messages.error(request, "You do not have the required role permissions to view this resource.")
                except Exception:
                    pass
                raise PermissionDenied("User does not possess required role.")
                
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator ensuring that only administrators or superusers have access."""
    return role_required(['ADMIN'])(view_func)


def creator_required(view_func):
    """Decorator ensuring that only creators or admins have access to studio upload tools."""
    return role_required(['CREATOR', 'ADMIN'])(view_func)


def moderator_required(view_func):
    """Decorator ensuring that only content moderators or admins have access."""
    return role_required(['MODERATOR', 'ADMIN'])(view_func)


class RoleRequiredMixin:
    """
    CBV mixin enforcing role-based access control.
    """
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            try:
                messages.warning(request, "Please log in to access this page.")
            except Exception:
                pass
            return redirect(f"{reverse('accounts:login')}?next={request.path}")

        if not request.user.is_superuser and self.allowed_roles:
            if request.user.role not in self.allowed_roles:
                try:
                    messages.error(request, "Access forbidden: insufficient permissions.")
                except Exception:
                    pass
                raise PermissionDenied("Insufficient permissions")

        return super().dispatch(request, *args, **kwargs)


class AdminOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['ADMIN']


class CreatorOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['CREATOR', 'ADMIN']


class ModeratorOnlyMixin(RoleRequiredMixin):
    allowed_roles = ['MODERATOR', 'ADMIN']

import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {filepath}")

# accounts/apps.py
write('accounts/apps.py', '''from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
    verbose_name = 'Accounts & User Security'

    def ready(self):
        import accounts.signals
''')

# accounts/managers.py
write('accounts/managers.py', '''from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier for auth.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email address must be provided'))
        email = self.normalize_email(email)
        extra_fields.setdefault('role', 'VIEWER')
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)
''')

# accounts/models.py
write('accounts/models.py', '''import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager

class User(AbstractBaseUser, PermissionsMixin):
    """
    Primary User model for CineVerse.
    Email acts as the unique login credential.
    """
    class RoleChoices(models.TextChoices):
        VIEWER = 'VIEWER', _('Viewer')
        CREATOR = 'CREATOR', _('Content Creator')
        MODERATOR = 'MODERATOR', _('Content Moderator')
        ADMIN = 'ADMIN', _('Administrator')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True, db_index=True)
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    username = models.CharField(_('username'), max_length=150, unique=True, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/%Y/%m/', null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    role = models.CharField(max_length=20, choices=RoleChoices.choices, default=RoleChoices.VIEWER)
    
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    last_active_at = models.DateTimeField(default=timezone.now)
    
    country = models.CharField(max_length=100, default='United States')
    preferred_language = models.CharField(max_length=10, default='en')
    max_active_streams = models.PositiveSmallIntegerField(default=2)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'role']),
            models.Index(fields=['is_active', 'is_verified']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else (self.username or self.email.split('@')[0])

    @property
    def is_admin(self):
        return self.role == self.RoleChoices.ADMIN or self.is_superuser

    @property
    def is_creator(self):
        return self.role in [self.RoleChoices.CREATOR, self.RoleChoices.ADMIN]

    @property
    def is_moderator(self):
        return self.role in [self.RoleChoices.MODERATOR, self.RoleChoices.ADMIN]

    @property
    def is_vip_subscriber(self):
        """
        Calculates if the user currently holds an active VIP or Premium subscription tier.
        """
        active_sub = self.subscriptions.filter(status='ACTIVE', expires_at__gt=timezone.now()).first() if hasattr(self, 'subscriptions') else None
        if active_sub and active_sub.plan.tier_code in ['VIP', 'PREMIUM', 'ULTRA_4K']:
            return True
        return self.is_staff

    @property
    def current_subscription(self):
        if hasattr(self, 'subscriptions'):
            return self.subscriptions.filter(status='ACTIVE', expires_at__gt=timezone.now()).select_related('plan').first()
        return None

    def get_absolute_url(self):
        return reverse('accounts:profile')


class UserProfile(models.Model):
    """
    Detailed profile preferences controlling OTT video player behaviors,
    parental locks, audio/subtitle tracks, and playback bandwidth.
    """
    class QualityChoices(models.TextChoices):
        AUTO = 'AUTO', _('Auto (Adaptive)')
        UHD_4K = '4K', _('4K Ultra HD')
        FHD_1080P = '1080P', _('1080p Full HD')
        HD_720P = '720P', _('720p HD')
        SD_480P = '480P', _('480p Standard')

    class RatingLimitChoices(models.TextChoices):
        ALL = 'ALL', _('All Content (18+)')
        TEEN = 'PG-13', _('Teens (PG-13 / TV-14)')
        KIDS = 'PG', _('Kids & Family (G / PG / TV-Y7)')

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=100, blank=True)
    preferred_quality = models.CharField(max_length=10, choices=QualityChoices.choices, default=QualityChoices.AUTO)
    preferred_audio_lang = models.CharField(max_length=20, default='English')
    preferred_subtitle_lang = models.CharField(max_length=20, default='English')
    subtitles_enabled = models.BooleanField(default=True)
    auto_play_next = models.BooleanField(default=True)
    auto_play_trailers = models.BooleanField(default=True)
    data_saver_mode = models.BooleanField(default=False)
    
    # Parental & Kids Controls
    is_kids_mode = models.BooleanField(default=False)
    parental_pin = models.CharField(max_length=6, blank=True, null=True)
    content_rating_limit = models.CharField(max_length=10, choices=RatingLimitChoices.choices, default=RatingLimitChoices.ALL)

    # Notifications Preferences
    email_new_releases = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=False)
    browser_push_notifications = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.user.email}"


class UserDevice(models.Model):
    """
    Tracks registered active devices per account to enforce concurrent stream limits.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    device_id = models.CharField(max_length=128, db_index=True)
    device_name = models.CharField(max_length=150, default='Web Browser')
    device_type = models.CharField(max_length=50, default='Desktop')
    browser = models.CharField(max_length=100, blank=True)
    operating_system = models.CharField(max_length=100, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('user', 'device_id')
        ordering = ['-last_used_at']

    def __str__(self):
        return f"{self.device_name} ({self.device_type}) - {self.user.email}"


class LoginHistory(models.Model):
    """
    Security audit log for sign-ins, IP tracking, and geo-heuristics.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_records')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    location_city = models.CharField(max_length=100, default='Unknown City')
    location_country = models.CharField(max_length=100, default='Unknown Country')
    status = models.CharField(max_length=20, default='SUCCESS')
    login_time = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-login_time']
        verbose_name_plural = 'Login Histories'

    def __str__(self):
        return f"{self.user.email} - {self.status} at {self.login_time.strftime('%Y-%m-%d %H:%M')}"


class SecurityLog(models.Model):
    """
    Captures sensitive credential changes, 2FA updates, and access revocations.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='security_logs')
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.event_type} - {self.user.email}"
''')

# accounts/forms.py
write('accounts/forms.py', '''from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, UserDevice

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Choose a secure password', 'class': 'form-input'}), validators=[validate_password])
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'}))
    terms_accepted = forms.BooleanField(required=True, label="I agree to CineVerse Terms & Privacy Policy")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'username': forms.TextInput(attrs={'placeholder': 'Unique Username', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-input', 'autocomplete': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Your password', 'class': 'form-input', 'autocomplete': 'current-password'}))
    remember_me = forms.BooleanField(required=False, initial=True)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password. Please check your credentials.")
            if not user.is_active:
                raise forms.ValidationError("Your CineVerse account has been disabled. Please contact support.")
            self.user = user
        return self.cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'bio', 'avatar', 'country', 'preferred_language']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_language': forms.TextInput(attrs={'class': 'form-input'}),
        }


class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name', 'preferred_quality', 'preferred_audio_lang', 'preferred_subtitle_lang',
            'subtitles_enabled', 'auto_play_next', 'auto_play_trailers', 'data_saver_mode',
            'is_kids_mode', 'content_rating_limit', 'email_new_releases', 'browser_push_notifications'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_quality': forms.Select(attrs={'class': 'form-select'}),
            'preferred_audio_lang': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_subtitle_lang': forms.TextInput(attrs={'class': 'form-input'}),
            'content_rating_limit': forms.Select(attrs={'class': 'form-select'}),
        }


class PasswordChangeCustomForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), validators=[validate_password])
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise forms.ValidationError("Current password is incorrect.")
        return current

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_new_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_new_password', "New passwords do not match.")
        return cleaned_data
''')

# accounts/services.py
write('accounts/services.py', '''import uuid
from django.utils import timezone
from .models import UserDevice, LoginHistory, SecurityLog

class AuthService:
    """
    Encapsulates session creation, device registration, and security logging.
    """
    @staticmethod
    def register_login_event(request, user, status='SUCCESS'):
        ip = getattr(request, 'client_ip', '127.0.0.1')
        ua = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        LoginHistory.objects.create(
            user=user,
            ip_address=ip,
            user_agent=ua[:500],
            status=status,
            login_time=timezone.now()
        )

        # Update last active timestamp
        user.last_active_at = timezone.now()
        user.save(update_fields=['last_active_at'])

        # Register or refresh device
        device_id = request.COOKIES.get('cineverse_device_id') or str(uuid.uuid4())
        device_type = getattr(request, 'device_category', 'Desktop')
        
        device, _ = UserDevice.objects.get_or_create(
            user=user,
            device_id=device_id,
            defaults={
                'device_name': f"{device_type} - {ua.split('(')[0].strip()[:50]}",
                'device_type': device_type,
                'ip_address': ip,
                'last_used_at': timezone.now()
            }
        )
        if not _:
            device.last_used_at = timezone.now()
            device.ip_address = ip
            device.save(update_fields=['last_used_at', 'ip_address'])

        return device_id

    @staticmethod
    def log_security_event(user, event_type, description, ip='127.0.0.1'):
        SecurityLog.objects.create(
            user=user,
            event_type=event_type,
            description=description,
            ip_address=ip
        )
''')

# accounts/signals.py
write('accounts/signals.py', '''from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Automatically initializes a UserProfile upon user account creation.
    """
    if created:
        UserProfile.objects.create(
            user=instance,
            display_name=instance.full_name
        )
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
''')

# accounts/templatetags/account_tags.py
write('accounts/templatetags/__init__.py', '')
write('accounts/templatetags/account_tags.py', '''from django import template
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
''')

# accounts/views.py
write('accounts/views.py', '''from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import FormView, UpdateView, TemplateView, ListView
from django.urls import reverse_lazy
from .models import User, UserProfile, UserDevice, LoginHistory, SecurityLog
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm, UserPreferencesForm, PasswordChangeCustomForm
from .services import AuthService

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(self.request, user)
        device_id = AuthService.register_login_event(self.request, user)
        response = redirect(self.success_url)
        response.set_cookie('cineverse_device_id', device_id, max_age=86400 * 365)
        messages.success(self.request, f"Welcome to CineVerse, {user.first_name or user.email}! Start exploring thousands of titles.")
        return response


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        return next_url if next_url else reverse_lazy('movies:browse')

    def form_valid(self, form):
        user = form.user
        login(self.request, user)
        
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(86400 * 30)

        device_id = AuthService.register_login_event(self.request, user)
        response = redirect(self.get_success_url())
        response.set_cookie('cineverse_device_id', device_id, max_age=86400 * 365)
        messages.success(self.request, f"Welcome back, {user.full_name}!")
        return response


class LogoutView(View):
    def get(self, request):
        return self.post(request)

    def post(self, request):
        if request.user.is_authenticated:
            AuthService.log_security_event(request.user, 'USER_LOGOUT', 'User signed out voluntarily', getattr(request, 'client_ip', '127.0.0.1'))
        logout(request)
        messages.info(request, "You have been successfully signed out.")
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['profile'] = getattr(self.request.user, 'profile', None)
        ctx['active_devices_count'] = self.request.user.devices.filter(is_active=True).count()
        ctx['recent_logins'] = self.request.user.login_records.all()[:5]
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your CineVerse profile has been updated.")
        return super().form_valid(form)


class PreferencesView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserPreferencesForm
    template_name = 'accounts/preferences.html'
    success_url = reverse_lazy('accounts:preferences')

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Streaming and playback preferences updated.")
        return super().form_valid(form)


class DevicesView(LoginRequiredMixin, ListView):
    model = UserDevice
    template_name = 'accounts/devices.html'
    context_object_name = 'devices'

    def get_queryset(self):
        return self.request.user.devices.all()


class DeviceRevokeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        device = get_object_or_404(UserDevice, pk=pk, user=request.user)
        device_name = device.device_name
        device.delete()
        AuthService.log_security_event(request.user, 'DEVICE_REVOKED', f'Revoked access for {device_name}')
        messages.success(request, f"Device '{device_name}' removed from your account.")
        return redirect('accounts:devices')


class SecurityView(LoginRequiredMixin, FormView):
    template_name = 'accounts/security.html'
    form_class = PasswordChangeCustomForm
    success_url = reverse_lazy('accounts:security')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_pwd = form.cleaned_data['new_password']
        self.request.user.set_password(new_pwd)
        self.request.user.save()
        # Keep user logged in after password change
        login(self.request, self.request.user)
        AuthService.log_security_event(self.request.user, 'PASSWORD_CHANGED', 'Password changed via user settings')
        messages.success(self.request, "Your password has been changed securely.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['security_logs'] = self.request.user.security_logs.all()[:10]
        return ctx


class LoginHistoryView(LoginRequiredMixin, ListView):
    model = LoginHistory
    template_name = 'accounts/login_history.html'
    context_object_name = 'logins'
    paginate_by = 15

    def get_queryset(self):
        return self.request.user.login_records.all()
''')

# accounts/urls.py
write('accounts/urls.py', '''from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    path('devices/', views.DevicesView.as_view(), name='devices'),
    path('devices/<int:pk>/revoke/', views.DeviceRevokeView.as_view(), name='device_revoke'),
    path('security/', views.SecurityView.as_view(), name='security'),
    path('history/', views.LoginHistoryView.as_view(), name='login_history'),
]
''')

# accounts/admin.py
write('accounts/admin.py', '''from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, UserDevice, LoginHistory, SecurityLog

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Streaming Preferences'

class UserDeviceInline(admin.TabularInline):
    model = UserDevice
    extra = 0
    readonly_fields = ('device_id', 'device_type', 'ip_address', 'registered_at', 'last_used_at')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)
    inlines = [UserProfileInline, UserDeviceInline]
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'username', 'avatar', 'bio', 'phone_number')}),
        ('Permissions & Roles', {'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Streaming Constraints', {'fields': ('max_active_streams', 'country', 'preferred_language')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'last_active_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'first_name', 'last_name', 'role'),
        }),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_quality', 'preferred_audio_lang', 'is_kids_mode', 'data_saver_mode')
    list_filter = ('preferred_quality', 'is_kids_mode', 'data_saver_mode')

@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'device_type', 'ip_address', 'last_used_at', 'is_active')
    list_filter = ('device_type', 'is_active')
    search_fields = ('user__email', 'device_name', 'ip_address')

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'status', 'location_city', 'location_country', 'login_time')
    list_filter = ('status', 'location_country')
    search_fields = ('user__email', 'ip_address')

@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'ip_address', 'created_at')
    list_filter = ('event_type',)
    search_fields = ('user__email', 'event_type', 'description')
''')

print("accounts app files built successfully.")

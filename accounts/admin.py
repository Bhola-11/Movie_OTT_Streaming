from django.contrib import admin
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

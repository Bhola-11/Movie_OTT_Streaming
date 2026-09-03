from django.contrib import admin
from .models import Plan, UserSubscription, Coupon

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'tier_code', 'price_monthly', 'price_yearly', 'max_screens', 'max_resolution', 'is_active')
    list_editable = ('is_active',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'current_period_start', 'expires_at', 'auto_renew')
    list_filter = ('status', 'plan', 'auto_renew')
    search_fields = ('user__email',)

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_percent', 'is_active', 'valid_until')

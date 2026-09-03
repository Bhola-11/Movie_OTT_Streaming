import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse

class Plan(models.Model):
    """
    Subscription tier (Free, Basic HD, Standard Full HD, VIP 4K Ultra).
    """
    class TierCode(models.TextChoices):
        FREE = 'FREE', 'Free Ad-Supported'
        BASIC = 'BASIC', 'Basic HD (720p)'
        STANDARD = 'STANDARD', 'Standard Full HD (1080p)'
        VIP_4K = 'VIP_4K', 'VIP Ultra 4K HDR & Dolby Atmos'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    tier_code = models.CharField(max_length=20, choices=TierCode.choices, unique=True)
    description = models.TextField()
    
    price_monthly = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    price_yearly = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=5, default='USD')
    
    max_screens = models.PositiveSmallIntegerField(default=1)
    max_resolution = models.CharField(max_length=20, default='1080p')
    has_dolby_atmos = models.BooleanField(default=False)
    allows_offline_downloads = models.BooleanField(default=False)
    ad_free = models.BooleanField(default=True)
    
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveSmallIntegerField(default=0)
    badge_label = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ['display_order', 'price_monthly']

    def __str__(self):
        return f"{self.name} (${self.price_monthly}/mo)"


class UserSubscription(models.Model):
    """
    Active subscription record per user with expiration tracking and renewal status.
    """
    class StatusChoices(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        PAST_DUE = 'PAST_DUE', 'Past Due'
        CANCELED = 'CANCELED', 'Canceled'
        EXPIRED = 'EXPIRED', 'Expired'

    class BillingCycle(models.TextChoices):
        MONTHLY = 'MONTHLY', 'Monthly'
        YEARLY = 'YEARLY', 'Yearly'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name='subscribers')
    billing_cycle = models.CharField(max_length=15, choices=BillingCycle.choices, default=BillingCycle.MONTHLY)
    status = models.CharField(max_length=15, choices=StatusChoices.choices, default=StatusChoices.ACTIVE)
    
    current_period_start = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    auto_renew = models.BooleanField(default=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.plan.name} [{self.status}]"

    @property
    def is_active(self):
        return self.status == self.StatusChoices.ACTIVE and self.expires_at > timezone.now()


class Coupon(models.Model):
    """
    Promotional voucher codes providing fixed or percentage checkout discounts.
    """
    code = models.CharField(max_length=30, unique=True)
    discount_percent = models.PositiveSmallIntegerField(default=0)
    discount_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    max_redemptions = models.PositiveIntegerField(default=1000)
    times_redeemed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.code} ({self.discount_percent}% off)"

    @property
    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.valid_from <= now <= self.valid_until and self.times_redeemed < self.max_redemptions

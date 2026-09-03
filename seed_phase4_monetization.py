import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cineverse.settings')
django.setup()

from django.contrib.auth import get_user_model
from subscriptions.models import Plan
from payments.services import PaymentProcessingService

User = get_user_model()
viewer = User.objects.filter(email='viewer@cineverse.io').first()

plans = [
    {
        'name': 'Free Streamer',
        'tier_code': 'FREE',
        'description': 'Enjoy a rotating library of ad-supported movies and selected pilot episodes.',
        'price_monthly': 0.00,
        'price_yearly': 0.00,
        'max_screens': 1,
        'max_resolution': '720p',
        'has_dolby_atmos': False,
        'allows_offline_downloads': False,
        'ad_free': False,
        'display_order': 1,
    },
    {
        'name': 'Basic HD',
        'tier_code': 'BASIC',
        'description': 'Great for solo streaming on phones, tablets, or laptops in high definition.',
        'price_monthly': 8.99,
        'price_yearly': 89.99,
        'max_screens': 1,
        'max_resolution': '720p',
        'has_dolby_atmos': False,
        'allows_offline_downloads': False,
        'ad_free': True,
        'display_order': 2,
    },
    {
        'name': 'Standard Full HD',
        'tier_code': 'STANDARD',
        'description': 'Watch across 2 devices simultaneously in crystal-clear 1080p Full HD.',
        'price_monthly': 13.99,
        'price_yearly': 139.99,
        'max_screens': 2,
        'max_resolution': '1080p',
        'has_dolby_atmos': False,
        'allows_offline_downloads': True,
        'ad_free': True,
        'display_order': 3,
    },
    {
        'name': 'VIP Ultra 4K',
        'tier_code': 'VIP_4K',
        'description': 'The ultimate theater experience: 4K UHD + HDR, Dolby Atmos, and 4 concurrent screens.',
        'price_monthly': 19.99,
        'price_yearly': 199.99,
        'max_screens': 4,
        'max_resolution': '4K UHD',
        'has_dolby_atmos': True,
        'allows_offline_downloads': True,
        'ad_free': True,
        'display_order': 4,
        'badge_label': 'RECOMMENDED'
    }
]

for p_data in plans:
    plan, created = Plan.objects.get_or_create(tier_code=p_data['tier_code'], defaults=p_data)
    print(f"Plan ready: {plan.name} (${plan.price_monthly}/mo)")

# Run a simulated VIP checkout for viewer user to create transaction + PDF invoice + notification
if viewer:
    vip_plan = Plan.objects.get(tier_code='VIP_4K')
    tx, invoice = PaymentProcessingService.process_checkout(
        user=viewer,
        plan_id=vip_plan.pk,
        billing_cycle='MONTHLY'
    )
    print(f"Simulated Checkout Complete: {tx.transaction_reference}, Invoice: #{invoice.invoice_number}")

print("Phase 4 Monetization Seed Completed Successfully.")

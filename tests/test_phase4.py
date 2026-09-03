import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from subscriptions.models import Plan, UserSubscription
from payments.models import PaymentTransaction, Invoice
from payments.services import PaymentProcessingService
from notifications.models import Notification
from notifications.services import NotificationService

User = get_user_model()

@pytest.mark.django_db
def test_subscription_plans_and_pricing_view(client):
    plan = Plan.objects.get_or_create(
        tier_code='VIP_4K',
        defaults={'name': 'VIP Ultra 4K', 'price_monthly': 19.99, 'max_screens': 4}
    )[0]
    
    res = client.get(reverse('subscriptions:plans'))
    assert res.status_code == 200
    assert 'VIP Ultra 4K' in res.content.decode()

@pytest.mark.django_db
def test_checkout_pipeline_and_pdf_generation():
    user = User.objects.create_user(email='vip.subscriber@cineverse.io', password='Password123!', first_name='John', last_name='Doe')
    plan = Plan.objects.get_or_create(tier_code='VIP_4K', defaults={'name': 'VIP Ultra 4K', 'price_monthly': 19.99})[0]

    # Process checkout
    tx, invoice = PaymentProcessingService.process_checkout(
        user=user,
        plan_id=plan.pk,
        billing_cycle='MONTHLY'
    )
    assert tx.status == PaymentTransaction.StatusChoices.SUCCESS
    assert float(tx.amount) == 19.99
    assert tx.subscription.is_active is True
    assert invoice.pdf_document is not None

    # Check notification dispatched
    assert Notification.objects.filter(user=user, notification_type='PAYMENT_SUCCESS').exists()

@pytest.mark.django_db
def test_invoice_download_view(client):
    user = User.objects.create_user(email='invoice.downloader@cineverse.io', password='Password123!')
    client.force_login(user)
    plan = Plan.objects.get_or_create(tier_code='VIP_4K', defaults={'name': 'VIP Ultra 4K', 'price_monthly': 19.99})[0]
    tx, invoice = PaymentProcessingService.process_checkout(user=user, plan_id=plan.pk)

    # Download invoice PDF
    res = client.get(invoice.get_absolute_url())
    assert res.status_code == 200
    assert res['Content-Type'] == 'application/pdf'
    assert 'attachment;' in res['Content-Disposition']

@pytest.mark.django_db
def test_notifications_lifecycle(client):
    user = User.objects.create_user(email='notif.user@cineverse.io', password='Password123!')
    client.force_login(user)

    notif = NotificationService.send_notification(
        user=user,
        ntype='NEW_RELEASE',
        title='Chronicles of Neo Tokyo 2088 is out!',
        message='Watch the premiere now in 4K HDR.'
    )
    assert notif.is_read is False

    # Mark as read via API
    res_mark = client.post(reverse('notifications:mark_read', kwargs={'pk': notif.pk}))
    assert res_mark.status_code == 200
    notif.refresh_from_db()
    assert notif.is_read is True

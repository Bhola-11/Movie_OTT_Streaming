import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.urls import reverse
from subscriptions.models import UserSubscription

class PaymentTransaction(models.Model):
    """
    Immutable ledger of payment attempts, successful authorizations, and refunds.
    """
    class GatewayChoices(models.TextChoices):
        RAZORPAY = 'RAZORPAY', 'Razorpay'
        STRIPE = 'STRIPE', 'Stripe'
        MOCK_SANDBOX = 'MOCK', 'CineVerse Mock Gateway'

    class StatusChoices(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    subscription = models.ForeignKey(UserSubscription, on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    transaction_reference = models.CharField(max_length=100, unique=True, db_index=True)
    order_id = models.CharField(max_length=100, blank=True)
    gateway = models.CharField(max_length=20, choices=GatewayChoices.choices, default=GatewayChoices.MOCK_SANDBOX)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    payment_method_label = models.CharField(max_length=50, default='Credit Card (•••• 4242)')
    
    gateway_response_payload = models.TextField(blank=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_reference} - ${self.amount} ({self.status})"


class Invoice(models.Model):
    """
    Tax invoice record with generated PDF asset and accounting details.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    transaction = models.OneToOneField(PaymentTransaction, on_delete=models.CASCADE, related_name='invoice')
    
    billing_name = models.CharField(max_length=150)
    billing_email = models.EmailField()
    billing_address = models.TextField(default='100 CineVerse Boulevard, Los Angeles, CA')
    
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=5, default='USD')
    
    pdf_document = models.FileField(upload_to='invoices/%Y/%m/', null=True, blank=True)
    issued_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-issued_at']

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.user.email}"

    def get_absolute_url(self):
        return reverse('payments:invoice_download', kwargs={'pk': self.pk})

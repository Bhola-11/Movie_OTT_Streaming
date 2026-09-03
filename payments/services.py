import uuid
import secrets
from django.utils import timezone
from .models import PaymentTransaction, Invoice
from .invoice_generator import PDFInvoiceGenerator
from subscriptions.models import UserSubscription, Plan
from notifications.services import NotificationService

class PaymentProcessingService:
    @classmethod
    def process_checkout(cls, user, plan_id, billing_cycle='MONTHLY', payment_method='Credit Card (•••• 4242)'):
        plan = Plan.objects.get(pk=plan_id)
        amount = plan.price_yearly if billing_cycle == 'YEARLY' else plan.price_monthly
        days = 365 if billing_cycle == 'YEARLY' else 30
        
        # 1. Record Successful Payment Transaction
        tx_ref = f"CV-{secrets.token_hex(6).upper()}-{timezone.now().strftime('%Y%m%d')}"
        tx = PaymentTransaction.objects.create(
            user=user,
            transaction_reference=tx_ref,
            order_id=f"ORD-{secrets.token_hex(4).upper()}",
            gateway=PaymentTransaction.GatewayChoices.MOCK_SANDBOX,
            status=PaymentTransaction.StatusChoices.SUCCESS,
            amount=amount,
            currency='USD',
            payment_method_label=payment_method
        )

        # 2. Activate or Renew User Subscription
        expires_at = timezone.now() + timezone.timedelta(days=days)
        sub, _ = UserSubscription.objects.get_or_create(
            user=user,
            defaults={
                'plan': plan,
                'billing_cycle': billing_cycle,
                'status': UserSubscription.StatusChoices.ACTIVE,
                'expires_at': expires_at,
                'auto_renew': True
            }
        )
        if not _:
            sub.plan = plan
            sub.billing_cycle = billing_cycle
            sub.status = UserSubscription.StatusChoices.ACTIVE
            sub.expires_at = expires_at
            sub.save()

        tx.subscription = sub
        tx.save(update_fields=['subscription'])

        # 3. Generate Tax Invoice with ReportLab PDF
        inv_number = f"INV-{timezone.now().strftime('%Y%m')}-{secrets.token_hex(3).upper()}"
        invoice = Invoice.objects.create(
            invoice_number=inv_number,
            user=user,
            transaction=tx,
            billing_name=user.full_name,
            billing_email=user.email,
            subtotal=amount,
            tax_amount=0.00,
            total_amount=amount,
            currency='USD',
            issued_at=timezone.now()
        )
        PDFInvoiceGenerator.generate_pdf(invoice)

        # 4. Dispatch Instant In-App Notification
        NotificationService.send_notification(
            user=user,
            ntype='PAYMENT_SUCCESS',
            title=f"Payment Received: {plan.name}",
            message=f"Your subscription of ${amount} for {plan.name} was successful. Invoice #{inv_number} is ready for download.",
            target_url=invoice.get_absolute_url()
        )

        return tx, invoice

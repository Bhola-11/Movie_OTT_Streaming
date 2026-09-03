import os

def write(filepath, content):
    dirname = os.path.dirname(filepath)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created/Updated: {filepath}")

# ==============================================================================
# 1. REPORTLAB PDF INVOICE GENERATOR
# ==============================================================================

write('payments/invoice_generator.py', '''import io
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFInvoiceGenerator:
    """
    Generates CineVerse branded PDF tax invoices using ReportLab.
    """
    @classmethod
    def generate_pdf(cls, invoice):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#E50914'),
            spaceAfter=6
        )
        body_style = styles['Normal']
        body_style.fontSize = 10
        body_style.leading = 14
        
        elements = []
        
        # 1. Header Banner
        header_data = [
            [Paragraph("<b>CINEVERSE OTT MEDIA INC.</b>", title_style), Paragraph(f"<b>TAX INVOICE</b><br/>#{invoice.invoice_number}", body_style)],
            [Paragraph("100 CineVerse Blvd, Suite 800<br/>Los Angeles, CA 90028<br/>support@cineverse.io", body_style),
             Paragraph(f"<b>Date:</b> {invoice.issued_at.strftime('%B %d, %Y')}<br/><b>Status:</b> PAID<br/><b>Payment Ref:</b> {invoice.transaction.transaction_reference[:16]}", body_style)]
        ]
        header_table = Table(header_data, colWidths=[320, 210])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # 2. Billed To
        elements.append(Paragraph("<b>BILLED TO:</b>", styles['Heading4']))
        bill_to_text = f"<b>{invoice.billing_name}</b><br/>{invoice.billing_email}<br/>{invoice.billing_address}"
        elements.append(Paragraph(bill_to_text, body_style))
        elements.append(Spacer(1, 25))
        
        # 3. Line Items Table
        sub_name = invoice.transaction.subscription.plan.name if invoice.transaction.subscription else "CineVerse VIP Streaming Plan"
        table_data = [
            [Paragraph("<b>DESCRIPTION</b>", body_style), Paragraph("<b>QTY</b>", body_style), Paragraph("<b>UNIT PRICE</b>", body_style), Paragraph("<b>AMOUNT</b>", body_style)],
            [Paragraph(f"<b>{sub_name}</b><br/>Unlimited 4K HDR Streaming & Downloads", body_style), "1", f"${invoice.subtotal}", f"${invoice.subtotal}"],
            ["", "", Paragraph("<b>Subtotal:</b>", body_style), f"${invoice.subtotal}"],
            ["", "", Paragraph("<b>Tax (0%):</b>", body_style), f"${invoice.tax_amount}"],
            ["", "", Paragraph("<b>TOTAL PAID:</b>", styles['Heading4']), Paragraph(f"<b>${invoice.total_amount} {invoice.currency}</b>", styles['Heading4'])],
        ]
        
        item_table = Table(table_data, colWidths=[280, 50, 100, 100])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161922')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,1), 0.5, colors.HexColor('#DDDDDD')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(item_table)
        elements.append(Spacer(1, 40))
        
        # 4. Footer Note
        elements.append(Paragraph("Thank you for subscribing to CineVerse. Happy Streaming!", styles['Italic']))
        
        # Build Document
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        filename = f"invoice_{invoice.invoice_number}.pdf"
        invoice.pdf_document.save(filename, ContentFile(pdf_bytes), save=True)
        return invoice.pdf_document
''')

# ==============================================================================
# 2. PAYMENTS SERVICES & VIEWS
# ==============================================================================

write('payments/services.py', '''import uuid
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
''')

write('payments/views.py', '''from django.views.generic import TemplateView, View, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib import messages
from .models import PaymentTransaction, Invoice
from .services import PaymentProcessingService
from subscriptions.models import Plan

class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'payments/checkout.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        plan_id = self.request.GET.get('plan')
        ctx['plan'] = get_object_or_404(Plan, pk=plan_id) if plan_id else Plan.objects.filter(tier_code='VIP_4K').first()
        ctx['billing_cycle'] = self.request.GET.get('cycle', 'MONTHLY')
        return ctx

    def post(self, request, *args, **kwargs):
        plan_id = request.POST.get('plan_id')
        cycle = request.POST.get('billing_cycle', 'MONTHLY')
        tx, invoice = PaymentProcessingService.process_checkout(
            user=request.user,
            plan_id=plan_id,
            billing_cycle=cycle
        )
        messages.success(request, f"Congratulations! You are now subscribed to {tx.subscription.plan.name}.")
        return redirect('payments:success', pk=tx.pk)


class PaymentSuccessView(LoginRequiredMixin, DetailView):
    model = PaymentTransaction
    template_name = 'payments/success.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return PaymentTransaction.objects.filter(user=self.request.user)


class InvoiceDownloadView(LoginRequiredMixin, View):
    """
    Serves the generated ReportLab PDF invoice as an attachment download.
    """
    def get(self, request, pk):
        invoice = get_object_or_404(Invoice, pk=pk, user=request.user)
        if not invoice.pdf_document:
            from .invoice_generator import PDFInvoiceGenerator
            PDFInvoiceGenerator.generate_pdf(invoice)

        response = HttpResponse(invoice.pdf_document.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="CineVerse_Invoice_{invoice.invoice_number}.pdf"'
        return response


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'payments/invoice_list.html'
    context_object_name = 'invoices'

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user)
''')

write('payments/urls.py', '''from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/<uuid:pk>/', views.PaymentSuccessView.as_view(), name='success'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<uuid:pk>/download/', views.InvoiceDownloadView.as_view(), name='invoice_download'),
]
''')

write('payments/admin.py', '''from django.contrib import admin
from .models import PaymentTransaction, Invoice

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_reference', 'user', 'amount', 'currency', 'status', 'created_at')
    list_filter = ('status', 'gateway')
    search_fields = ('transaction_reference', 'user__email')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'user', 'total_amount', 'issued_at')
    search_fields = ('invoice_number', 'user__email')
''')

# ==============================================================================
# 3. SUBSCRIPTIONS VIEWS, SERVICES & ADMIN
# ==============================================================================

write('subscriptions/views.py', '''from django.views.generic import ListView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone
from .models import Plan, UserSubscription

class PlansPricingView(ListView):
    """
    Tiered pricing comparison table (Free vs Basic vs Standard vs VIP 4K).
    """
    model = Plan
    template_name = 'subscriptions/plans.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return Plan.objects.filter(is_active=True).order_by('display_order')


class MySubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/my_subscription.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['subscription'] = self.request.user.subscriptions.filter(status='ACTIVE').first()
        ctx['recent_invoices'] = self.request.user.invoices.all()[:5]
        return ctx


class CancelSubscriptionView(LoginRequiredMixin, View):
    def post(self, request):
        sub = request.user.subscriptions.filter(status='ACTIVE').first()
        if sub:
            sub.auto_renew = False
            sub.canceled_at = timezone.now()
            sub.save()
            messages.info(request, "Auto-renewal canceled. Your access remains active until the end of your current period.")
        return redirect('subscriptions:my_subscription')
''')

write('subscriptions/urls.py', '''from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.PlansPricingView.as_view(), name='plans'),
    path('mine/', views.MySubscriptionView.as_view(), name='my_subscription'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='cancel'),
]
''')

write('subscriptions/admin.py', '''from django.contrib import admin
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
''')

# ==============================================================================
# 4. NOTIFICATIONS SERVICES & VIEWS
# ==============================================================================

write('notifications/services.py', '''from .models import Notification

class NotificationService:
    @staticmethod
    def send_notification(user, ntype, title, message, target_url='/'):
        return Notification.objects.create(
            user=user,
            notification_type=ntype,
            title=title,
            message=message,
            target_url=target_url
        )

    @staticmethod
    def mark_all_as_read(user):
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
''')

write('notifications/views.py', '''from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from .models import Notification
from .services import NotificationService

class NotificationInboxView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/inbox.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class MarkReadAPIView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk, user=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return JsonResponse({'status': 'OK'})


class MarkAllReadView(LoginRequiredMixin, View):
    def post(self, request):
        NotificationService.mark_all_as_read(request.user)
        return redirect('notifications:inbox')
''')

write('notifications/urls.py', '''from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.NotificationInboxView.as_view(), name='inbox'),
    path('<uuid:pk>/read/', views.MarkReadAPIView.as_view(), name='mark_read'),
    path('mark-all-read/', views.MarkAllReadView.as_view(), name='mark_all_read'),
]
''')

write('notifications/admin.py', '''from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('title', 'user__email')
''')

print("Phase 4 Views, Services, PDF generator, and Admin built.")

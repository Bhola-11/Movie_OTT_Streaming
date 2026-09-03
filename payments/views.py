from django.views.generic import TemplateView, View, ListView, DetailView
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

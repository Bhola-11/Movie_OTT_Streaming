from django.contrib import admin
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

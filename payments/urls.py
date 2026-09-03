from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('success/<uuid:pk>/', views.PaymentSuccessView.as_view(), name='success'),
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<uuid:pk>/download/', views.InvoiceDownloadView.as_view(), name='invoice_download'),
]

from django.urls import path
from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('plans/', views.PlansPricingView.as_view(), name='plans'),
    path('mine/', views.MySubscriptionView.as_view(), name='my_subscription'),
    path('cancel/', views.CancelSubscriptionView.as_view(), name='cancel'),
]

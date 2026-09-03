from django.views.generic import ListView, TemplateView, View
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

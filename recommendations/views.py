from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .services import RecommendationEngineService

class PersonalizedFeedView(LoginRequiredMixin, TemplateView):
    template_name = 'recommendations/for_you.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['recommendations'] = RecommendationEngineService.get_for_you_recommendations(self.request.user)
        ctx['top_10'] = RecommendationEngineService.get_top_10_today()
        return ctx

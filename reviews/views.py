from django.views.generic import CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Review, ReviewVote
from .forms import ReviewForm
from movies.models import Movie
from series.models import Series

class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/create_review.html'

    def form_valid(self, form):
        review = form.save(commit=False)
        review.user = self.request.user
        
        movie_slug = self.request.POST.get('movie_slug')
        series_slug = self.request.POST.get('series_slug')
        
        if movie_slug:
            review.movie = get_object_or_404(Movie, slug=movie_slug)
            review.save()
            messages.success(self.request, "Thank you! Your movie review has been published.")
            return redirect(review.movie.get_absolute_url())
        elif series_slug:
            review.series = get_object_or_404(Series, slug=series_slug)
            review.save()
            messages.success(self.request, "Your series review has been published.")
            return redirect(review.series.get_absolute_url())

        return redirect('movies:browse')


class ReviewHelpfulVoteAPIView(LoginRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        vote, created = ReviewVote.objects.get_or_create(user=request.user, review=review, defaults={'is_helpful': True})
        if not created:
            vote.delete()
            review.helpful_votes_count = max(0, review.helpful_votes_count - 1)
            is_voted = False
        else:
            review.helpful_votes_count += 1
            is_voted = True
        review.save(update_fields=['helpful_votes_count'])
        return JsonResponse({'status': 'OK', 'votes': review.helpful_votes_count, 'is_voted': is_voted})

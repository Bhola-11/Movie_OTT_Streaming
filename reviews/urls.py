from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/', views.ReviewCreateView.as_view(), name='create'),
    path('<uuid:pk>/vote/', views.ReviewHelpfulVoteAPIView.as_view(), name='vote_api'),
]

from django import forms
from .models import Movie, MovieCast

class MovieFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Search title, actor...', 'class': 'form-input'}))
    genre = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-input'}))
    year = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'placeholder': 'Year', 'class': 'form-input'}))
    rating = forms.ChoiceField(required=False, choices=[('', 'All Ratings')] + Movie.ContentRating.choices, widget=forms.Select(attrs={'class': 'form-select'}))

from django import forms
from .models import Genre, Category, Mood, Tag

class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'description', 'backdrop_image', 'is_featured', 'display_order', 'meta_keywords']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'slug': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4}),
            'meta_keywords': forms.TextInput(attrs={'class': 'form-input'}),
        }

class MoodForm(forms.ModelForm):
    class Meta:
        model = Mood
        fields = ['name', 'slug', 'description', 'color_gradient', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
        }

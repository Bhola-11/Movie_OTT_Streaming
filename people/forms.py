from django import forms
from .models import Person, PersonAward

class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        fields = [
            'full_name', 'stage_name', 'slug', 'primary_profession', 'biography',
            'birth_date', 'place_of_birth', 'gender', 'photo', 'imdb_id',
            'instagram_handle', 'twitter_handle', 'is_featured', 'popularity_score'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input'}),
            'stage_name': forms.TextInput(attrs={'class': 'form-input'}),
            'biography': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'birth_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'place_of_birth': forms.TextInput(attrs={'class': 'form-input'}),
        }

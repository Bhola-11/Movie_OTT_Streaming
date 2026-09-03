from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'title', 'content', 'contains_spoilers']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Stars") for i in range(10, 0, -1)], attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'placeholder': 'Review headline...', 'class': 'form-input'}),
            'content': forms.Textarea(attrs={'placeholder': 'Write your full critique and impressions...', 'class': 'form-input', 'rows': 4}),
        }

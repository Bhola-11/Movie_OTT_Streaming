from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, UserDevice

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Choose a secure password', 'class': 'form-input'}), validators=[validate_password])
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password', 'class': 'form-input'}))
    terms_accepted = forms.BooleanField(required=True, label="I agree to CineVerse Terms & Privacy Policy")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'username']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'form-input'}),
            'username': forms.TextInput(attrs={'placeholder': 'Unique Username', 'class': 'form-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data


class UserLoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'name@example.com', 'class': 'form-input', 'autocomplete': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Your password', 'class': 'form-input', 'autocomplete': 'current-password'}))
    remember_me = forms.BooleanField(required=False, initial=True)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise forms.ValidationError("Invalid email or password. Please check your credentials.")
            if not user.is_active:
                raise forms.ValidationError("Your CineVerse account has been disabled. Please contact support.")
            self.user = user
        return self.cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'phone_number', 'bio', 'avatar', 'country', 'preferred_language']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'country': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_language': forms.TextInput(attrs={'class': 'form-input'}),
        }


class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'display_name', 'preferred_quality', 'preferred_audio_lang', 'preferred_subtitle_lang',
            'subtitles_enabled', 'auto_play_next', 'auto_play_trailers', 'data_saver_mode',
            'is_kids_mode', 'content_rating_limit', 'email_new_releases', 'browser_push_notifications'
        ]
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_quality': forms.Select(attrs={'class': 'form-select'}),
            'preferred_audio_lang': forms.TextInput(attrs={'class': 'form-input'}),
            'preferred_subtitle_lang': forms.TextInput(attrs={'class': 'form-input'}),
            'content_rating_limit': forms.Select(attrs={'class': 'form-select'}),
        }


class PasswordChangeCustomForm(forms.Form):
    current_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}), validators=[validate_password])
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get('current_password')
        if not self.user.check_password(current):
            raise forms.ValidationError("Current password is incorrect.")
        return current

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_new_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_new_password', "New passwords do not match.")
        return cleaned_data

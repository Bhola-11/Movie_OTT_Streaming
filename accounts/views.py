from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import FormView, UpdateView, TemplateView, ListView
from django.urls import reverse_lazy
from .models import User, UserProfile, UserDevice, LoginHistory, SecurityLog
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm, UserPreferencesForm, PasswordChangeCustomForm
from .services import AuthService

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(self.request, user)
        device_id = AuthService.register_login_event(self.request, user)
        response = redirect(self.success_url)
        response.set_cookie('cineverse_device_id', device_id, max_age=86400 * 365)
        messages.success(self.request, f"Welcome to CineVerse, {user.first_name or user.email}! Start exploring thousands of titles.")
        return response


class LoginView(FormView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm

    def get_success_url(self):
        next_url = self.request.GET.get('next') or self.request.POST.get('next')
        return next_url if next_url else reverse_lazy('movies:browse')

    def form_valid(self, form):
        user = form.user
        login(self.request, user)
        
        if not form.cleaned_data.get('remember_me'):
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(86400 * 30)

        device_id = AuthService.register_login_event(self.request, user)
        response = redirect(self.get_success_url())
        response.set_cookie('cineverse_device_id', device_id, max_age=86400 * 365)
        messages.success(self.request, f"Welcome back, {user.full_name}!")
        return response


class LogoutView(View):
    def get(self, request):
        return self.post(request)

    def post(self, request):
        if request.user.is_authenticated:
            AuthService.log_security_event(request.user, 'USER_LOGOUT', 'User signed out voluntarily', getattr(request, 'client_ip', '127.0.0.1'))
        logout(request)
        messages.info(request, "You have been successfully signed out.")
        return redirect('accounts:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['profile'] = getattr(self.request.user, 'profile', None)
        ctx['active_devices_count'] = self.request.user.devices.filter(is_active=True).count()
        ctx['recent_logins'] = self.request.user.login_records.all()[:5]
        return ctx


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileUpdateForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your CineVerse profile has been updated.")
        return super().form_valid(form)


class PreferencesView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserPreferencesForm
    template_name = 'accounts/preferences.html'
    success_url = reverse_lazy('accounts:preferences')

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Streaming and playback preferences updated.")
        return super().form_valid(form)


class DevicesView(LoginRequiredMixin, ListView):
    model = UserDevice
    template_name = 'accounts/devices.html'
    context_object_name = 'devices'

    def get_queryset(self):
        return self.request.user.devices.all()


class DeviceRevokeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        device = get_object_or_404(UserDevice, pk=pk, user=request.user)
        device_name = device.device_name
        device.delete()
        AuthService.log_security_event(request.user, 'DEVICE_REVOKED', f'Revoked access for {device_name}')
        messages.success(request, f"Device '{device_name}' removed from your account.")
        return redirect('accounts:devices')


class SecurityView(LoginRequiredMixin, FormView):
    template_name = 'accounts/security.html'
    form_class = PasswordChangeCustomForm
    success_url = reverse_lazy('accounts:security')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        new_pwd = form.cleaned_data['new_password']
        self.request.user.set_password(new_pwd)
        self.request.user.save()
        # Keep user logged in after password change
        login(self.request, self.request.user)
        AuthService.log_security_event(self.request.user, 'PASSWORD_CHANGED', 'Password changed via user settings')
        messages.success(self.request, "Your password has been changed securely.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['security_logs'] = self.request.user.security_logs.all()[:10]
        return ctx


class LoginHistoryView(LoginRequiredMixin, ListView):
    model = LoginHistory
    template_name = 'accounts/login_history.html'
    context_object_name = 'logins'
    paginate_by = 15

    def get_queryset(self):
        return self.request.user.login_records.all()

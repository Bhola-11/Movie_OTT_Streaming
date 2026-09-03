from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('preferences/', views.PreferencesView.as_view(), name='preferences'),
    path('devices/', views.DevicesView.as_view(), name='devices'),
    path('devices/<int:pk>/revoke/', views.DeviceRevokeView.as_view(), name='device_revoke'),
    path('security/', views.SecurityView.as_view(), name='security'),
    path('history/', views.LoginHistoryView.as_view(), name='login_history'),
]

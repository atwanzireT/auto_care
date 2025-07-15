from django.urls import path
from accounts.views.auth_views import CustomLoginView, CustomLogoutView, RegisterView
from accounts.views.dashboard_views import DashboardView

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]

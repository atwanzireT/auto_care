from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')), 
    path('accounts/', include('accounts.urls.auth_urls')),
    path('', lambda request: redirect('accounts:login', permanent=False)),
 # 👈 this line makes it all work
]

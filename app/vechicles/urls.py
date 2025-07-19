from django.urls import path
from . import views

urlpatterns = [
    path('', views.vehicles, name='vehicles'),
]
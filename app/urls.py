from django.urls import path
from . import views


urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Service Ticket Management
    path('tickets/', views.service_tickets, name='service_tickets'),
    path('tickets/<int:pk>/', views.service_ticket_detail, name='service_ticket_detail'),

    # Services
    path('services/', views.services, name='services'),
    
    # Mechanics
    path('mechanics/', views.mechanics, name='mechanics'),
]

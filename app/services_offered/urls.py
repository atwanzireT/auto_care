from django.urls import path
from . import views

urlpatterns = [
    path('', views.service_tickets, name='service_tickets'),
    path('<int:pk>/', views.service_ticket_detail, name='service_ticket_detail'),
    path('<int:pk>/close/', views.close_ticket, name='close_ticket'),
]
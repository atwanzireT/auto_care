from django.db import models
from django.core.validators import MinLengthValidator, MinValueValidator
from django.utils.translation import gettext_lazy as _
from accounts.models import CustomUser

class Mechanic(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
        help_text=_("Mechanic's name must be at least 3 characters long.")
    )
    phone = models.CharField(
        max_length=15
    )
    specialization = models.CharField(max_length=100, blank=True, help_text=_("Mechanic's area of expertise."))
   
    
    def __str__(self):
        return f"{self.name} ({self.specialization})"

class Service(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(3)],
        unique=True,
        help_text=_("Service name must be at least 3 characters long.")
    )
    description = models.TextField(blank=True, help_text=_("Detailed description of the service."))
    price = models.FloatField(
        validators=[MinValueValidator(0)],
        help_text=_("Price of the service in UGX.")
    )

    def __str__(self):
        return self.name
    

class ServiceTicket(models.Model):
    """Model to represent a service ticket."""

    customer_name = models.CharField(max_length=100, blank=True, null=True)
    customer_phone = models.CharField(max_length=15, blank=True, null=True)
    services = models.ManyToManyField('Service', related_name='tickets')
    vehicle_number_plate = models.CharField(max_length=15, blank=True, null=True)
    notes = models.TextField(blank=True, null=True, help_text=_("Additional notes or instructions for the service."))
    mechanic = models.ForeignKey('Mechanic', on_delete=models.SET_NULL, null=True, blank=True, related_name='tickets')
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='service_tickets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')

    class Meta:
        verbose_name = _('Service Ticket')
        verbose_name_plural = _('Service Tickets')
        ordering = ['-created_at']

    def __str__(self):
        service_names = ", ".join([service.name for service in self.services.all()])
        return f"{service_names} - {self.created_by.username} - {self.status}"

    @property
    def total_price(self):
        """Calculate total price based on linked services."""
        return sum(service.price for service in self.services.all())

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from accounts.models import CustomUser, Profile



class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('service category')
        verbose_name_plural = _('service categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DefinedService(models.Model):
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='services'
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text=_('Base service price in local currency')
    )
    estimated_duration = models.PositiveIntegerField(
        help_text=_('Estimated time to complete the service in minutes')
    )
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('defined service')
        verbose_name_plural = _('defined services')
    
    def __str__(self):
        return f"{self.name} - {self.base_price}"


class Customer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    preferred_contact_method = models.CharField(
        max_length=10,
        choices=[('phone', 'Phone'), ('email', 'Email')],
        default='phone'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.phone})"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def active_vehicles(self):
        return self.vehicles.filter(is_active=True)


class Vehicle(models.Model):
    class VehicleType(models.TextChoices):
        CAR = 'car', _('Car')
        TRUCK = 'truck', _('Truck')
        SUV = 'suv', _('SUV')
        VAN = 'van', _('Van')
        MOTORCYCLE = 'motorcycle', _('Motorcycle')
        OTHER = 'other', _('Other')
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year + 1)
        ]
    )
    license_plate = models.CharField(
        max_length=20,
        unique=True,
        validators=[MinLengthValidator(3)]
    )
    vin = models.CharField(
        max_length=17,
        blank=True,
        validators=[MinLengthValidator(17)],
        help_text=_('Vehicle Identification Number')
    )
    color = models.CharField(max_length=30, blank=True)
    vehicle_type = models.CharField(
        max_length=20,
        choices=VehicleType.choices,
        default=VehicleType.CAR
    )
    mileage = models.PositiveIntegerField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['make', 'model']
        verbose_name = _('vehicle')
        verbose_name_plural = _('vehicles')
        indexes = [
            models.Index(fields=['license_plate']),
            models.Index(fields=['make', 'model']),
            models.Index(fields=['customer']),
            models.Index(fields=['vin']),
        ]
    
    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"
    
    @property
    def full_name(self):
        return f"{self.year} {self.make} {self.model}"


class ServiceTicket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        WAITING_PARTS = 'waiting_parts', _('Waiting for Parts')
        WAITING_APPROVAL = 'waiting_approval', _('Waiting for Approval')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
    
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='service_tickets'
    )
    receptionist = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='created_tickets',
        limit_choices_to={'role': Profile.Role.RECEPTIONIST}
    )
    mechanic = models.ForeignKey(
        Profile,
        on_delete=models.PROTECT,
        related_name='assigned_tickets',
        null=True,
        blank=True,
        limit_choices_to={'role': Profile.Role.MECHANIC}
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    problem_description = models.TextField()
    customer_notes = models.TextField(blank=True)
    internal_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    priority = models.PositiveSmallIntegerField(
        choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
        default=2
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('service ticket')
        verbose_name_plural = _('service tickets')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['receptionist']),
            models.Index(fields=['mechanic']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.vehicle} ({self.get_status_display()})"
    
    def close_ticket(self):
        if self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            self.save()
    
    @property
    def total_cost(self):
        return sum(service.total_price for service in self.services_offered.all())


class ServiceOffered(models.Model):
    ticket = models.ForeignKey(
        ServiceTicket,
        on_delete=models.CASCADE,
        related_name='services_offered'
    )
    service = models.ForeignKey(
        DefinedService,
        on_delete=models.PROTECT,
        related_name='offered_services'
    )
    quantity = models.PositiveIntegerField(default=1)
    actual_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Final price charged to customer')
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('service offered')
        verbose_name_plural = _('services offered')
        unique_together = ['ticket', 'service']
    
    def __str__(self):
        return f"{self.service} for {self.ticket}"
    
    @property
    def total_price(self):
        return (self.actual_price or self.service.base_price) * self.quantity
    
    def save(self, *args, **kwargs):
        if not self.actual_price:
            self.actual_price = self.service.base_price
        super().save(*args, **kwargs)


class Part(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    part_number = models.CharField(max_length=50, unique=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    cost_price = models.DecimalField(max_digits=8, decimal_places=2)
    selling_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    compatible_vehicles = models.ManyToManyField(
        Vehicle,
        blank=True,
        related_name='compatible_parts'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = _('part')
        verbose_name_plural = _('parts')
    
    def __str__(self):
        return f"{self.name} ({self.part_number})"


class PartUsed(models.Model):
    service_ticket = models.ForeignKey(
        ServiceTicket,
        on_delete=models.CASCADE,
        related_name='parts_used'
    )
    part = models.ForeignKey(
        Part,
        on_delete=models.PROTECT,
        related_name='used_in_tickets'
    )
    quantity = models.PositiveIntegerField(default=1)
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2)
    notes = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('part used')
        verbose_name_plural = _('parts used')
    
    def __str__(self):
        return f"{self.part} in Ticket #{self.service_ticket.id}"
    
    @property
    def total_cost(self):
        return self.price_per_unit * self.quantity


class Page(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    content = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_pages'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated_by = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='updated_pages'
    )
    
    class Meta:
        ordering = ['title']
        verbose_name = _('page')
        verbose_name_plural = _('pages')
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
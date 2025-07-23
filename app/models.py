from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
from accounts.models import Profile

class ServiceCategory(models.Model):
    """Categories for grouping similar services"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class for UI display")
    
    class Meta:
        verbose_name = _('Service Category')
        verbose_name_plural = _('Service Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class DefinedService(models.Model):
    """Predefined services that can be offered to customers"""
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
        help_text=_('Estimated time to complete in minutes')
    )
    is_active = models.BooleanField(default=True)
    requires_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Defined Service')
        verbose_name_plural = _('Defined Services')
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'category'],
                name='unique_service_name_per_category'
            )
        ]
    
    def __str__(self):
        return f"{self.name} (${self.base_price})"

class Customer(models.Model):
    """Customer information model"""
    class ContactPreference(models.TextChoices):
        PHONE = 'phone', _('Phone')
        EMAIL = 'email', _('Email')
        SMS = 'sms', _('Text Message')
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    address = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    preferred_contact = models.CharField(
        max_length=10,
        choices=ContactPreference.choices,
        default=ContactPreference.PHONE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.phone})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def active_vehicles(self):
        return self.vehicles.filter(is_active=True)

class Vehicle(models.Model):
    """Customer vehicle information"""
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
        help_text=_('17-character Vehicle Identification Number')
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
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
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
    """Main service ticket model"""
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        WAITING_PARTS = 'waiting_parts', _('Waiting for Parts')
        WAITING_APPROVAL = 'waiting_approval', _('Waiting for Approval')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
    
    class Priority(models.IntegerChoices):
        LOW = 1, _('Low')
        MEDIUM = 2, _('Medium')
        HIGH = 3, _('High')
        CRITICAL = 4, _('Critical')
    
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
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Service Ticket')
        verbose_name_plural = _('Service Tickets')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['vehicle']),
            models.Index(fields=['receptionist']),
            models.Index(fields=['mechanic']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"Ticket #{self.id} - {self.vehicle} ({self.get_status_display()})"
    
    def close_ticket(self):
        """Mark ticket as completed"""
        if self.status != self.Status.COMPLETED:
            self.status = self.Status.COMPLETED
            self.completed_at = timezone.now()
            self.save()
    
    @property
    def total_cost(self):
        """Calculate total cost of all services"""
        return sum(service.total_price for service in self.services_offered.all())
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage based on services"""
        total_services = self.services_offered.count()
        if total_services == 0:
            return 0
        completed = self.services_offered.filter(status=ServiceOffered.Status.COMPLETED).count()
        return round((completed / total_services) * 100)

class ServiceOffered(models.Model):
    """Services offered as part of a ticket"""
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')
        CANCELLED = 'cancelled', _('Cancelled')
    
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
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    actual_price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Final price charged to customer')
    )
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    mechanic = models.ForeignKey(
        Profile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': Profile.Role.MECHANIC},
        related_name='assigned_services'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Service Offered')
        verbose_name_plural = _('Services Offered')
        constraints = [
            models.UniqueConstraint(
                fields=['ticket', 'service'],
                name='unique_service_per_ticket'
            )
        ]
    
    def __str__(self):
        return f"{self.service.name} for {self.ticket}"
    
    @property
    def total_price(self):
        """Calculate total price for this service (quantity * price)"""
        return (self.actual_price or self.service.base_price) * self.quantity
    
    @property
    def duration_minutes(self):
        """Calculate actual duration if completed"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() / 60
        return None
    
    def save(self, *args, **kwargs):
        """Handle automatic field updates"""
        if not self.actual_price:
            self.actual_price = self.service.base_price
        
        # Update timestamps based on status changes
        if self.status == self.Status.IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        elif self.status == self.Status.COMPLETED and not self.completed_at:
            self.completed_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Update parent ticket status
        self.ticket.update_status_based_on_services()

class Part(models.Model):
    """Inventory parts that can be used in services"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    part_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    manufacturer = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    minimum_stock = models.PositiveIntegerField(default=5)
    is_active = models.BooleanField(default=True)
    compatible_vehicles = models.ManyToManyField(
        'VehicleCategory',
        blank=True,
        related_name='compatible_parts'
    )
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Part')
        verbose_name_plural = _('Parts')
    
    def __str__(self):
        return f"{self.name} ({self.part_number})"
    
    @property
    def needs_restock(self):
        """Check if part needs to be reordered"""
        return self.quantity_in_stock < self.minimum_stock

class PartUsed(models.Model):
    """Parts used in specific service tickets"""
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
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    notes = models.TextField(blank=True)
    used_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Part Used')
        verbose_name_plural = _('Parts Used')
    
    def __str__(self):
        return f"{self.part} in Ticket #{self.service_ticket.id}"
    
    @property
    def total_cost(self):
        """Calculate total cost for parts used"""
        return self.part.price * self.quantity
    
    def save(self, *args, **kwargs):
        """Update inventory when parts are used"""
        if not self.pk:  # Only on creation
            self.part.quantity_in_stock = max(0, self.part.quantity_in_stock - self.quantity)
            self.part.save()
        super().save(*args, **kwargs)

class VehicleCategory(models.Model):
    """Categories for vehicle types"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    vehicle_type = models.CharField(max_length=50, unique=True)
    
    class Meta:
        verbose_name = _('Vehicle Category')
        verbose_name_plural = _('Vehicle Categories')
    
    def __str__(self):
        return self.name


class Appointment(models.Model):
    """Scheduled appointments for customers"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    scheduled_time = models.DateTimeField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_time']
        verbose_name = _('Appointment')
        verbose_name_plural = _('Appointments')
    
    def __str__(self):
        return f"Appointment for {self.customer} on {self.scheduled_time}"
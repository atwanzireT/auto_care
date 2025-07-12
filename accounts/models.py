from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$')]
    )
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.get_full_name() or self.username


class Profile(models.Model):
    class Role(models.TextChoices):
        ADMIN = 'admin', _('Administrator')
        MECHANIC = 'mechanic', _('Mechanic')
        RECEPTIONIST = 'receptionist', _('Receptionist')
        INVENTORY_MANAGER = 'inventory', _('Inventory Manager')
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MECHANIC
    )
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    specialization = models.CharField(max_length=100, blank=True)
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True
    )
    bio = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ['user__last_name', 'user__first_name']
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.get_role_display()})"

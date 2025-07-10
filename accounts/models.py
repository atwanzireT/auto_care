from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    pass


class Profile(models.Model):
    ROLES = (
        ('admin', 'Administrator'),
        ('mechanic', 'Mechanic'),
        ('receptionist', 'Receptionist'),
        )
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile', verbose_name=_('user'))
    role = models.CharField(max_length=20, choices=ROLES )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    hire_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = _('profile')
        verbose_name_plural = _('profiles')
        ordering = ['name']

    def __str__(self):
        return self.name
from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import (
    Profile, Customer, Vehicle, ServiceTicket,
    ServiceCategory, DefinedService, ServiceOffered, Part, PartUsed, Page
)

# Use the actual custom user model
User = get_user_model()
admin.site.register(User)

# Register all the rest
admin.site.register(Profile)
admin.site.register(Customer)
admin.site.register(Vehicle)
admin.site.register(ServiceTicket)
admin.site.register(ServiceCategory)
admin.site.register(DefinedService)
admin.site.register(ServiceOffered)
admin.site.register(Part)
admin.site.register(PartUsed)
admin.site.register(Page)

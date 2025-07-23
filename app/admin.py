from django.contrib import admin
from .models import (
    Vehicle, ServiceTicket, Customer,
    ServiceCategory, DefinedService, ServiceOffered, Part, PartUsed
)


# Register all the rest
admin.site.register(Customer)
admin.site.register(Vehicle)
admin.site.register(ServiceTicket)
admin.site.register(ServiceCategory)
admin.site.register(DefinedService)
admin.site.register(ServiceOffered)
admin.site.register(Part)
admin.site.register(PartUsed)

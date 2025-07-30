from django.contrib import admin
from .models import *

# Register all the rest
admin.site.register(Mechanic)
admin.site.register(ServiceTicket)
admin.site.register(Service)

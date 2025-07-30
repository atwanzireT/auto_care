from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Service, ServiceTicket, Mechanic


class MechanicForm(forms.ModelForm):
    class Meta:
        model = Mechanic
        fields = ['name', 'phone', 'specialization']
        labels = {
            'name': _('Full Name'),
            'phone': _('Phone Number'),
            'specialization': _('Specialization'),
        }
        help_texts = {
            'name': _('Minimum 3 characters'),
            'phone': _('Format: +256XXXXXXXXX'),
            'specialization': _('e.g., Engine Specialist, Electrician'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('John Doe'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'phone': forms.TextInput(attrs={'placeholder': _('+256XXXXXXXXX'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'specialization': forms.TextInput(attrs={'placeholder': _('e.g., Engine Specialist'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'price']
        labels = {
            'name': _('Service Name'),
            'description': _('Description'),
            'price': _('Price (UGX)'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('e.g., Oil Change'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'description': forms.Textarea(attrs={'placeholder': _('Describe the service...'), 'rows': 3, 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'price': forms.NumberInput(attrs={'placeholder': _('e.g., 50000'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200', 'min': '0', 'step': '0.01'}),
        }



class ServiceTicketForm(forms.ModelForm):
    class Meta:
        model = ServiceTicket
        fields = ['customer_name', 'customer_phone', 'services', 'vehicle_number_plate', 'mechanic']
        labels = {
            'customer_name': _('Customer Name'),
            'customer_phone': _('Phone Number'),
            'services': _('Services Provided'),
            'vehicle_number_plate': _('Vehicle Plate Number'),
            'mechanic': _('Assigned Mechanic'),
        }
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': _('Jane Doe'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'customer_phone': forms.TextInput(attrs={'placeholder': _('+256XXXXXXXXX'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'services': forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'}),
            'vehicle_number_plate': forms.TextInput(attrs={'placeholder': _('UAX 123C'), 'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
            'mechanic': forms.Select(attrs={'class': 'block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring focus:ring-blue-200'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Optional: Filter mechanics by active status if applicable
        self.fields['mechanic'].queryset = Mechanic.objects.all()

        # Mark required fields
        for field in self.fields.values():
            if field.required:
                field.label = f"{field.label} *"

    def clean_customer_phone(self):
        phone = self.cleaned_data.get('customer_phone')
        if phone and (not phone.startswith('+256') or len(phone) < 12):
            raise forms.ValidationError(_("Phone number must start with +256 and be at least 12 digits long."))
        return phone

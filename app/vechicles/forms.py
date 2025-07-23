from django import forms
from app.models import Vehicle
from django.utils import timezone

class VehicleForm(forms.ModelForm):
    year = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'min': 1900,
            'max': timezone.now().year + 1,
            'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
        })
    )
    
    class Meta:
        model = Vehicle
        fields = '__all__'
        exclude = ['created_at', 'updated_at']
        widgets = {
            'customer': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'make': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'model': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'license_plate': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'vin': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'minlength': '17',
                'maxlength': '17'
            }),
            'color': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'vehicle_type': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'min': '0'
            }),
            'last_service_date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': '3'
            }),
        }
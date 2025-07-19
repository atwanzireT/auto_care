from app.models import Customer
from django import forms


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['created_at', 'updated_at']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'placeholder': '+1234567890'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 3
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 3
            }),
            'preferred_contact_method': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
        }
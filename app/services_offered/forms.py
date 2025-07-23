from django import forms
from app.models import ServiceTicket, ServiceOffered, PartUsed
from django.utils import timezone

class ServiceTicketForm(forms.ModelForm):
    class Meta:
        model = ServiceTicket
        fields = '__all__'
        exclude = ['created_at', 'updated_at', 'completed_at']
        widgets = {
            'vehicle': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'receptionist': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'mechanic': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'status': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'problem_description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 3
            }),
            'customer_notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 2
            }),
            'internal_notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 2
            }),
            'estimated_completion': forms.DateTimeInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'type': 'datetime-local'
            }),
            'priority': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
        }

class ServiceOfferedForm(forms.ModelForm):
    class Meta:
        model = ServiceOffered
        fields = ['service', 'quantity', 'actual_price', 'notes']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'min': 1
            }),
            'actual_price': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'step': '0.01'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 2
            }),
        }

class PartUsedForm(forms.ModelForm):
    class Meta:
        model = PartUsed
        fields = ['part', 'quantity', 'notes']
        widgets = {
            'part': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'min': 1
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500',
                'rows': 2
            }),
        }
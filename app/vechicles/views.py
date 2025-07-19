from django.shortcuts import render, redirect
from app.models import Vehicle
from .forms import VehicleForm
from django.contrib import messages

def vehicles(request):
    vehicles = Vehicle.objects.select_related('customer').all().order_by('make', 'model')
    form = VehicleForm()
    
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('vehicles')
        else:
            messages.error(request, 'Please correct the errors below.')
    
    return render(request, 'vehicles.html', {
        'vehicles': vehicles,
        'form': form
    })
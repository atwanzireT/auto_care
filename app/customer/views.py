from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import Customer
from .forms import CustomerForm


@login_required
def customer(request):
    customers = Customer.objects.all()
    form = CustomerForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect("customer")
    return render(request, 'customer.html', {'customers': customers, 'form': form})
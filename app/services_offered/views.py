from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from app.models import ServiceTicket, ServiceOffered, PartUsed
from .forms import ServiceTicketForm, ServiceOfferedForm, PartUsedForm

def service_tickets(request):
    tickets = ServiceTicket.objects.select_related('vehicle', 'receptionist', 'mechanic').all()
    form = ServiceTicketForm()
    
    if request.method == 'POST':
        form = ServiceTicketForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Service ticket created successfully!')
            return redirect('service_tickets')
    
    return render(request, 'service_tickets.html', {
        'tickets': tickets,
        'form': form
    })

def service_ticket_detail(request, pk):
    ticket = get_object_or_404(ServiceTicket.objects.prefetch_related(
        'services_offered__service',
        'parts_used__part'
    ), pk=pk)
    
    service_form = ServiceOfferedForm(initial={'ticket': ticket})
    part_form = PartUsedForm(initial={'service_ticket': ticket})
    
    if request.method == 'POST':
        if 'add_service' in request.POST:
            service_form = ServiceOfferedForm(request.POST)
            if service_form.is_valid():
                service = service_form.save(commit=False)
                service.ticket = ticket
                service.save()
                messages.success(request, 'Service added successfully!')
                return redirect('service_ticket_detail', pk=pk)
        
        elif 'add_part' in request.POST:
            part_form = PartUsedForm(request.POST)
            if part_form.is_valid():
                part = part_form.save(commit=False)
                part.service_ticket = ticket
                part.save()
                messages.success(request, 'Part added successfully!')
                return redirect('service_ticket_detail', pk=pk)
        
        elif 'update_status' in request.POST:
            new_status = request.POST.get('status')
            ticket.status = new_status
            if new_status == ServiceTicket.Status.COMPLETED:
                ticket.completed_at = timezone.now()
            ticket.save()
            messages.success(request, 'Status updated successfully!')
            return redirect('service_ticket_detail', pk=pk)
    
    return render(request, 'service_ticket_detail.html', {
        'ticket': ticket,
        'service_form': service_form,
        'part_form': part_form,
        'status_choices': ServiceTicket.Status.choices
    })

def close_ticket(request, pk):
    ticket = get_object_or_404(ServiceTicket, pk=pk)
    ticket.close_ticket()
    messages.success(request, 'Ticket closed successfully!')
    return redirect('service_ticket_detail', pk=pk)
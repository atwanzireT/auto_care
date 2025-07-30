from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from .models import Service, ServiceTicket, Mechanic
from .forms import ServiceForm, ServiceTicketForm, MechanicForm


@login_required
def dashboard(request):
    ticket_counts = ServiceTicket.objects.aggregate(
        total=Count('id'),
        open=Count('id', filter=Q(status='open')),
        in_progress=Count('id', filter=Q(status='in_progress')),
        closed=Count('id', filter=Q(status='closed'))
    )
    
    # Changed from created_by__user to just created_by
    recent_tickets = ServiceTicket.objects.select_related(
        'created_by', 'mechanic'
    ).prefetch_related('services').order_by('-created_at')[:5]

    # Changed from request.user to request.user (since created_by is now directly a CustomUser)
    user_tickets = ServiceTicket.objects.filter(
        created_by=request.user
    ).prefetch_related('services').order_by('-created_at')[:3]

    return render(request, 'dashboard.html', {
        'ticket_counts': ticket_counts,
        'recent_tickets': recent_tickets,
        'user_tickets': user_tickets,
    })

@login_required
def service_tickets(request):
    tickets = ServiceTicket.objects.select_related(
        'created_by', 'mechanic'
    ).prefetch_related('services').order_by('-created_at')

    if request.method == 'POST':
        form = ServiceTicketForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            form.save_m2m()
            messages.success(request, _("Service ticket created successfully!"))
            return redirect('service_tickets')
    else:
        form = ServiceTicketForm(user=request.user)

    return render(request, 'service_tickets.html', {
        'tickets': tickets,
        'form': form,
    })

@login_required
def service_ticket_detail(request, pk):
    ticket = get_object_or_404(
        ServiceTicket.objects.select_related('created_by', 'mechanic').prefetch_related('services'),
        pk=pk
    )

    if not request.user.is_staff and ticket.created_by != request.user.profile:
        messages.error(request, _("You don't have permission to view this ticket."))
        return redirect('dashboard')

    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_choices = dict(ServiceTicket.STATUS_CHOICES).keys()
        if new_status in valid_choices:
            ticket.status = new_status
            ticket.save()
            messages.success(request, _("Ticket status updated!"))
            return redirect('service_ticket_detail', pk=pk)
        else:
            messages.error(request, _("Invalid status update."))

    return render(request, 'service_ticket_detail.html', {
        'ticket': ticket,
        'status_choices': ServiceTicket.STATUS_CHOICES,
    })

@login_required
def services(request):
    services = Service.objects.all().order_by('name')
    form = ServiceForm()

    if not request.user.is_staff:
        return render(request, 'services.html', {
            'services': services,
        })

    if request.method == 'POST':
        # Only handle creation of new service
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Service added successfully!"))
            return redirect('services')

    return render(request, 'services.html', {
        'services': services,
        'form': form,
    })

@login_required
def mechanics(request):
    mechanics = Mechanic.objects.all().order_by('name')

    form = MechanicForm()
    edit_form = None
    edit_instance = None

    if not request.user.is_staff:
        return render(request, 'mechanics.html', {
            'mechanics': mechanics,
        })

    if 'edit' in request.GET:
        edit_instance = get_object_or_404(Mechanic, pk=request.GET.get('edit'))
        edit_form = MechanicForm(instance=edit_instance)

    if request.method == 'POST':
        if 'edit_id' in request.POST:
            # Editing existing mechanic
            mechanic_instance = get_object_or_404(Mechanic, pk=request.POST.get('edit_id'))
            edit_form = MechanicForm(request.POST, instance=mechanic_instance)
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, _("Mechanic updated successfully!"))
                return redirect('mechanics')
        else:
            # Creating new mechanic
            form = MechanicForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, _("Mechanic added successfully!"))
                return redirect('mechanics')

    return render(request, 'mechanics.html', {
        'mechanics': mechanics,
        'form': form,
        'edit_form': edit_form,
        'edit_instance': edit_instance,
    })

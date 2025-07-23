from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum, F, Q, ExpressionWrapper, fields
from django.db.models.functions import ExtractMonth, ExtractYear, TruncMonth
from datetime import timedelta
from decimal import Decimal
from django.contrib.auth.decorators import login_required
from .models import ServiceTicket, Part, Appointment, ServiceOffered, DefinedService, Customer, Vehicle
from accounts.models import Profile


@login_required
def dashboard(request):
    """Dashboard view compatible with SQLite"""
    # Current date/time for calculations
    now = timezone.now()
    today = now.date()
    thirty_days_ago = now - timedelta(days=30)
    
    # 1. Ticket Statistics
    ticket_stats = {
        'open': ServiceTicket.objects.filter(status='open').count(),
        'in_progress': ServiceTicket.objects.filter(status='in_progress').count(),
        'waiting_parts': ServiceTicket.objects.filter(status='waiting_parts').count(),
        'waiting_approval': ServiceTicket.objects.filter(status='waiting_approval').count(),
        'completed_today': ServiceTicket.objects.filter(
            status='completed',
            completed_at__date=today
        ).count(),
    }
    
    # 2. Financial Metrics
    financials = {
        'monthly_revenue': ServiceOffered.objects.filter(
            ticket__status='completed',
            ticket__completed_at__gte=thirty_days_ago
        ).aggregate(
            total=Sum(F('quantity') * F('actual_price'))
        )['total'] or Decimal('0'),
        
        'pending_approval_value': ServiceOffered.objects.filter(
            ticket__status='waiting_approval'
        ).aggregate(
            total=Sum(F('quantity') * F('actual_price'))
        )['total'] or Decimal('0'),
    }
    
    # 3. Customer and Vehicle Metrics
    customer_metrics = {
        'total_customers': Customer.objects.count(),
        'new_customers': Customer.objects.filter(
            created_at__gte=thirty_days_ago
        ).count(),
        'active_vehicles': Vehicle.objects.filter(is_active=True).count(),
    }
    
    # 4. Recent Data
    recent_data = {
        'tickets': ServiceTicket.objects.select_related(
            'vehicle', 'vehicle__customer', 'receptionist'
        ).order_by('-created_at')[:10],
        
        'appointments': Appointment.objects.select_related(
            'customer', 'vehicle'
        ).filter(
            scheduled_time__gte=now,
            scheduled_time__lte=now + timedelta(days=7)
        ).order_by('scheduled_time')[:5],
        
        'low_stock_parts': Part.objects.filter(
            quantity_in_stock__lt=F('minimum_stock'),
            is_active=True
        ).order_by('quantity_in_stock')[:5],
    }
    
    # 5. Chart Data - SQLite compatible version
    # Monthly tickets data
    monthly_tickets = ServiceTicket.objects.filter(
        created_at__gte=now - timedelta(days=365)
    ).annotate(
        month=ExtractMonth('created_at'),
        year=ExtractYear('created_at')
    ).values('year', 'month').annotate(
        count=Count('id')
    ).order_by('year', 'month')
    
    monthly_tickets_data = {
        'labels': [f"{month['month']}/{month['year']}" for month in monthly_tickets],
        'data': [month['count'] for month in monthly_tickets],
    }
    
    # Revenue by service category
    revenue_by_category = DefinedService.objects.filter(
        offered_services__ticket__status='completed'
    ).values(
        'category__name'
    ).annotate(
        total=Sum(F('offered_services__quantity') * F('offered_services__actual_price'))
    ).order_by('-total')
    
    revenue_by_category_data = {
        'labels': [cat['category__name'] for cat in revenue_by_category],
        'data': [float(cat['total'] or 0) for cat in revenue_by_category],
    }
    
    # Mechanic performance
    mechanic_performance_data = Profile.objects.filter(
        role=Profile.Role.MECHANIC,
        assigned_services__status='completed'
    ).annotate(
        completed=Count('assigned_services')
    ).order_by('-completed')[:5].values('user__first_name', 'user__last_name', 'completed')
    
    # 6. Alerts
    alerts = {
        'overdue_tickets': ServiceTicket.objects.filter(
            Q(status='in_progress') | Q(status='waiting_parts'),
            estimated_completion__lt=now
        ).count(),
        'unassigned_tickets': ServiceTicket.objects.filter(
            status='open',
            mechanic__isnull=True
        ).count(),
        'out_of_stock': Part.objects.filter(
            quantity_in_stock=0,
            is_active=True
        ).count(),
    }
    
    context = {
        'ticket_stats': ticket_stats,
        'financials': financials,
        'customer_metrics': customer_metrics,
        'alerts': alerts,
        'recent_tickets': recent_data['tickets'],
        'upcoming_appointments': recent_data['appointments'],
        'low_stock_parts': recent_data['low_stock_parts'],
        'monthly_tickets_data': monthly_tickets_data,
        'revenue_by_category_data': revenue_by_category_data,
        'mechanic_performance_data': [
            {
                'name': f"{m['user__first_name']} {m['user__last_name']}",
                'completed': m['completed']
            } for m in mechanic_performance_data
        ],
    }
    
    return render(request, 'dashboard.html', context)
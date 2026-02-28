from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.utils import timezone
from .models import Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt, MyUser, Payment, Notification
from .forms import (
    CustomerForm, GadgetForm, GadgetRepairTransactionForm, 
    GadgetRepairLogForm, ReassignTechnicianForm, GadgetTransactionReceiptForm, PaymentForm
)
from .service import RepairTransactionService, GadgetRepairLogService, GadgetTransactionReceiptService, NotificationService
from .decorators import permission_required_or_superuser

# ============================================
# HOME & DASHBOARD VIEWS
# ============================================

@login_required
def admin_dashboard(request):
    """Admin Dashboard — supports ?month=M&year=Y filter for monthly stats."""
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('repair_shop:home')

    now = timezone.now()

    # ------ Month/Year filter from GET params ------
    try:
        filter_month = int(request.GET.get('month', now.month))
        filter_year  = int(request.GET.get('year',  now.year))
        # Clamp to valid ranges
        if not (1 <= filter_month <= 12):
            filter_month = now.month
        if filter_year < 2000 or filter_year > now.year + 1:
            filter_year = now.year
    except (ValueError, TypeError):
        filter_month = now.month
        filter_year  = now.year

    import datetime
    filter_date = datetime.date(filter_year, filter_month, 1)
    month_name  = filter_date.strftime('%B %Y')

    # Build month navigation (previous / next)
    if filter_month == 1:
        prev_month, prev_year = 12, filter_year - 1
    else:
        prev_month, prev_year = filter_month - 1, filter_year

    if filter_month == 12:
        next_month, next_year = 1, filter_year + 1
    else:
        next_month, next_year = filter_month + 1, filter_year

    # ------ All repairs queryset ------
    all_repairs = GadgetRepairTransaction.objects.select_related(
        'gadget', 'gadget__customer', 'technician'
    ).prefetch_related('repair_logs').order_by('-brought_in_date')

    completed_qs   = all_repairs.filter(status=GadgetRepairTransaction.COMPLETED)
    pending_qs     = all_repairs.filter(status=GadgetRepairTransaction.PENDING)
    inprogress_qs  = all_repairs.filter(status=GadgetRepairTransaction.INPROGRESS)

    # ------ Filtered month stats ------
    monthly_repairs = all_repairs.filter(
        brought_in_date__year=filter_year,
        brought_in_date__month=filter_month,
    )
    monthly_pending    = monthly_repairs.filter(status=GadgetRepairTransaction.PENDING)
    monthly_inprogress = monthly_repairs.filter(status=GadgetRepairTransaction.INPROGRESS)

    # Completed = repairs marked Done in the selected month (by updated_at)
    monthly_completed = all_repairs.filter(
        status=GadgetRepairTransaction.COMPLETED,
        updated_at__year=filter_year,
        updated_at__month=filter_month,
    )

    # ------ Revenue stats ------
    # Revenue = ACTUAL CASH RECEIVED (payments collected) for COMPLETED repairs only.
    # This gives a true picture of money in the bank from finished work.
    total_revenue = Payment.objects.filter(
        transaction__status=GadgetRepairTransaction.COMPLETED
    ).aggregate(total=Sum('amount'))['total'] or 0
    monthly_revenue = Payment.objects.filter(
        transaction__status=GadgetRepairTransaction.COMPLETED,
        created_at__year=filter_year,
        created_at__month=filter_month,
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Keep payments_received for backward compatibility (same as revenue now)
    total_payments_received = total_revenue
    monthly_payments_received = monthly_revenue

    # Monthly completed count (for "Fixed This Month" card)
    monthly_completed_ids = list(
        all_repairs.filter(
            status=GadgetRepairTransaction.COMPLETED,
            updated_at__year=filter_year,
            updated_at__month=filter_month,
        ).values_list('id', flat=True)
    )

    total_customers   = Customer.objects.count()
    total_technicians = MyUser.objects.filter(is_technician=True).count()

    monthly_fixed_count = len(monthly_completed_ids)

    # ------ All-time stats ------
    # total_customers is placed INSIDE stats so the template key
    # {{ stats.total_customers }} resolves correctly (was missing before).
    stats = {
        'total': all_repairs.count(),
        'pending': pending_qs.count(),
        'in_progress': inprogress_qs.count(),
        'completed': completed_qs.count(),
        'total_revenue': total_revenue,
        'total_payments_received': total_payments_received,
        'total_customers': total_customers,   # FIX: was only a top-level context var
    }

    # Template uses monthly_stats.fixed  (not .completed)
    # Template uses monthly_stats.received (not .total)
    # Both aliases are now provided alongside the original keys.
    monthly_stats = {
        'total': monthly_repairs.count(),
        'received': monthly_repairs.count(),    # FIX: template key
        'completed': monthly_fixed_count,
        'fixed': monthly_fixed_count,           # FIX: template key
        'pending': monthly_pending.count(),
        'in_progress': monthly_inprogress.count(),
        'revenue': monthly_revenue,
        'payments_received': monthly_payments_received,
        'month_name': month_name,
    }

    # Recent repairs (all statuses, last 10, with payment/log data)
    recent_repairs = list(
        all_repairs.prefetch_related('payments', 'repair_logs')[:10]
    )

    # Recent payments (last 8)
    recent_payments = Payment.objects.select_related(
        'transaction', 'transaction__gadget', 'transaction__gadget__customer', 'recorded_by'
    ).order_by('-created_at')[:8]

    # Awaiting payment: completed repairs with a price but not fully paid
    completed_with_data = list(
        completed_qs.prefetch_related('payments', 'repair_logs')[:30]
    )
    awaiting_payment = [t for t in completed_with_data if t.has_price and not t.is_fully_paid][:8]
    recent_completed  = [t for t in completed_with_data if t.is_fully_paid or not t.has_price][:8]

    context = {
        'stats': stats,
        'monthly_stats': monthly_stats,
        'recent_completed': recent_completed,
        'pending_repairs': pending_qs.select_related('gadget', 'gadget__customer', 'technician')[:8],
        'awaiting_payment': awaiting_payment,
        'recent_repairs': recent_repairs,
        'recent_payments': recent_payments,
        'total_customers': total_customers,
        'total_technicians': total_technicians,
        # Filter controls
        'filter_month': filter_month,
        'filter_year': filter_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'current_month': now.month,
        'current_year': now.year,
        'month_range': range(1, 13),
        'year_range': range(now.year, 2023, -1),
    }

    return render(request, 'repair_shop/admin_dashboard.html', context)


@login_required
def home(request):
    """
    Home view - Redirects to appropriate dashboard based on user role.
    """
    if request.user.is_superuser or request.user.is_staff:
        return redirect('repair_shop:admin_dashboard')
    elif request.user.is_secretary:
        return redirect('repair_shop:secretary_dashboard')
    elif request.user.is_technician:
        return redirect('repair_shop:technician_dashboard')
    else:
        return render(request, 'repair_shop/home.html', {
            'user_role': 'User',
            'dashboard': 'default'
        })


@login_required
def secretary_dashboard(request):
    """Secretary Dashboard — shows operational stats and recent activity."""
    if not request.user.is_secretary and not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('repair_shop:home')

    now = timezone.now()

    all_repairs = GadgetRepairTransaction.objects.select_related(
        'gadget', 'gadget__customer', 'technician'
    ).order_by('-brought_in_date')

    pending_qs    = all_repairs.filter(status=GadgetRepairTransaction.PENDING)
    inprogress_qs = all_repairs.filter(status=GadgetRepairTransaction.INPROGRESS)
    completed_qs  = all_repairs.filter(status=GadgetRepairTransaction.COMPLETED)

    # This month's repairs
    monthly_repairs = all_repairs.filter(
        brought_in_date__year=now.year,
        brought_in_date__month=now.month,
    )
    monthly_completed = all_repairs.filter(
        status=GadgetRepairTransaction.COMPLETED,
        updated_at__year=now.year,
        updated_at__month=now.month,
    )

    # Cash collected this month
    monthly_cash = Payment.objects.filter(
        transaction__status=GadgetRepairTransaction.COMPLETED,
        created_at__year=now.year,
        created_at__month=now.month,
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Completed repairs — evaluate is_fully_paid in Python (it's a property)
    completed_list = list(
        completed_qs.prefetch_related('payments', 'repair_logs').order_by('-updated_at')[:30]
    )
    awaiting_payment = [t for t in completed_list if t.has_price and not t.is_fully_paid]
    recent_completed = [t for t in completed_list if t.is_fully_paid or not t.has_price][:8]

    # Recent repairs across all statuses (last 10)
    recent_repairs = list(all_repairs.prefetch_related('payments', 'repair_logs')[:10])

    context = {
        'now': now,
        'stats': {
            'pending':             pending_qs.count(),
            'in_progress':         inprogress_qs.count(),
            'completed':           completed_qs.count(),
            'total_customers':     Customer.objects.count(),
            'received_this_month': monthly_repairs.count(),
            'fixed_this_month':    monthly_completed.count(),
            'awaiting_payment':    len(awaiting_payment),
            'cash_this_month':     monthly_cash,
        },
        'recent_repairs':    recent_repairs,
        'recent_completed':  recent_completed,
        'awaiting_payment':  awaiting_payment[:8],
    }
    return render(request, 'repair_shop/secretary_dashboard.html', context)

# ============================================
# CUSTOMER VIEWS - SECRETARY & STAFF
# ============================================

@permission_required_or_superuser('repair_shop.add_customer')
def create_customer(request):
    """Create a new customer - Secretary, Staff, Superuser"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer created successfully')
            return redirect('repair_shop:customer_list')
    else:
        form = CustomerForm()
    return render(request, 'repair_shop/customers/create_customer.html', {'form': form})


@permission_required_or_superuser('repair_shop.change_customer')
def update_customer(request, customer_id):
    """Update customer details - Secretary, Staff, Superuser"""
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Customer updated successfully')
            return redirect('repair_shop:customer_detail', customer_id=customer.id)
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'repair_shop/customers/create_customer.html', {'form': form})


@login_required
def delete_customer(request, customer_id):
    """Delete a customer - Superuser Only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete customers')
        return redirect('repair_shop:customer_list')
    
    customer = get_object_or_404(Customer, id=customer_id)
    customer.delete()
    messages.success(request, 'Customer deleted successfully')
    return redirect('repair_shop:customer_list')


@permission_required_or_superuser('repair_shop.view_customer')
def customer_list(request):
    """List all customers - Secretary, Staff, Superuser"""
    customers = Customer.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        customers = customers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    return render(request, 'repair_shop/customers/customer_list.html', {'customers': customers})


@permission_required_or_superuser('repair_shop.view_customer')
def customer_detail(request, customer_id):
    """View customer details - Secretary, Staff, Superuser"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Get all gadgets for this customer
    customer_gadgets = Gadget.objects.filter(customer=customer)
    
    # Get all repairs for this customer
    all_repairs = GadgetRepairTransaction.objects.filter(gadget__customer=customer)
    total_repairs = all_repairs.count()
    pending_repairs = all_repairs.filter(status=GadgetRepairTransaction.PENDING).count()
    inprogress_repairs = all_repairs.filter(status=GadgetRepairTransaction.INPROGRESS).count()
    completed_repairs = all_repairs.filter(status=GadgetRepairTransaction.COMPLETED).count()
    
    return render(request, 'repair_shop/customers/customer_detail.html', {
        'customer': customer,
        'customer_gadgets': customer_gadgets,
        'total_repairs': total_repairs,
        'pending_repairs': pending_repairs,
        'inprogress_repairs': inprogress_repairs,
        'completed_repairs': completed_repairs,
    })


# ============================================
# GADGET VIEWS - SECRETARY, STAFF & TECHNICIAN
# ============================================

@permission_required_or_superuser('repair_shop.add_gadget')
def create_gadget(request):
    """Create a new gadget for a customer - Secretary, Staff, Superuser"""
    if request.method == 'POST':
        form = GadgetForm(request.POST)
        if form.is_valid():
            gadget = form.save()
            messages.success(request, 'Gadget registered successfully')
            return redirect('repair_shop:gadget_detail', gadget_id=gadget.id)
    else:
        form = GadgetForm()
    return render(request, 'repair_shop/gadgets/create_gadget.html', {'form': form})


@permission_required_or_superuser('repair_shop.change_gadget')
def update_gadget(request, gadget_id):
    """Update gadget details - Secretary, Staff, Superuser"""
    gadget = get_object_or_404(Gadget, id=gadget_id)
    if request.method == 'POST':
        form = GadgetForm(request.POST, instance=gadget)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gadget updated successfully')
            return redirect('repair_shop:gadget_detail', gadget_id=gadget.id)
    else:
        form = GadgetForm(instance=gadget)
    return render(request, 'repair_shop/gadgets/create_gadget.html', {'form': form})


@login_required
def delete_gadget(request, gadget_id):
    """Delete a gadget - Superuser Only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete gadgets')
        return redirect('repair_shop:gadget_list')
    
    gadget = get_object_or_404(Gadget, id=gadget_id)
    gadget.delete()
    messages.success(request, 'Gadget deleted successfully')
    return redirect('repair_shop:gadget_list')


@permission_required_or_superuser('repair_shop.view_gadget')
def gadget_list(request):
    """List all gadgets - Secretary, Staff, Technician, Superuser"""
    gadgets = Gadget.objects.select_related('customer').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        gadgets = gadgets.filter(
            Q(gadget_brand__icontains=search_query) |
            Q(gadget_model__icontains=search_query) |
            Q(imei_number__icontains=search_query) |
            Q(customer__first_name__icontains=search_query) |
            Q(customer__last_name__icontains=search_query)
        )
    
    return render(request, 'repair_shop/gadgets/gadget_list.html', {'gadgets': gadgets})


@permission_required_or_superuser('repair_shop.view_gadget')
def gadget_detail(request, gadget_id):
    """View gadget details and repair history - Secretary, Staff, Technician, Superuser"""
    gadget = get_object_or_404(Gadget, id=gadget_id)
    repair_history = GadgetRepairTransaction.objects.filter(gadget=gadget).order_by('-brought_in_date')
    
    # Calculate statistics
    total_repairs = repair_history.count()
    pending_repairs = repair_history.filter(status=GadgetRepairTransaction.PENDING).count()
    inprogress_repairs = repair_history.filter(status=GadgetRepairTransaction.INPROGRESS).count()
    completed_repairs = repair_history.filter(status=GadgetRepairTransaction.COMPLETED).count()
    
    return render(request, 'repair_shop/gadgets/gadget_detail.html', {
        'gadget': gadget,
        'repair_history': repair_history,
        'total_repairs': total_repairs,
        'pending_repairs': pending_repairs,
        'inprogress_repairs': inprogress_repairs,
        'completed_repairs': completed_repairs,
    })


# ============================================
# REPAIR TRANSACTION VIEWS - STAFF & SECRETARY
# ============================================

@permission_required_or_superuser('repair_shop.add_gadgetrepairtransaction')
def create_repair_transaction(request):
    """Create a new repair transaction - Staff, Secretary, Superuser"""
    # Get gadget or customer from URL parameters
    gadget_id = request.GET.get('gadget')
    customer_id = request.GET.get('customer')
    
    if request.method == 'POST':
        form = GadgetRepairTransactionForm(request.POST, customer_id=customer_id, gadget_id=gadget_id)
        if form.is_valid():
            gadget = form.cleaned_data.get('gadget')
            technician = form.cleaned_data.get('technician')
            status = form.cleaned_data.get('status', 'Pending')
            
            result = RepairTransactionService.create_repair_transaction(
                gadget_id=gadget.id,
                technician_id=technician.id,
                status=status
            )
            
            if result['success']:
                messages.success(request, result['message'])
                # Notify the assigned technician
                NotificationService.notify_technician_assigned(result['transaction'])
                return redirect('repair_shop:repair_transaction_detail', transaction_id=result['transaction'].id)
            else:
                messages.error(request, result['message'])
    else:
        # GET request: check if customer was selected to filter gadgets
        customer_id = request.GET.get('customer') or customer_id
        form = GadgetRepairTransactionForm(customer_id=customer_id, gadget_id=gadget_id)
    
    return render(request, 'repair_shop/repairs/create_repair_transaction.html', {'form': form})


@permission_required_or_superuser('repair_shop.view_gadgetrepairtransaction')
def repair_transaction_detail(request, transaction_id):
    """View repair transaction details with all logs - All logged in users"""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    # Technician can only view their assigned repairs
    if not request.user.is_superuser and request.user.is_technician:
        if transaction.technician != request.user:
            messages.error(request, 'You can only view your assigned repairs')
            return redirect('repair_shop:my_assigned_repairs')
    
    logs = transaction.repair_logs.all().order_by('-created_at')
    payments = transaction.payments.all().order_by('created_at')
    
    return render(request, 'repair_shop/repairs/repair_transaction_detail.html', {
        'transaction': transaction,
        'logs': logs,
        'payments': payments,
        'total_cost': transaction.total_cost,
        'total_paid': transaction.total_paid,
        'total_due': transaction.total_due,
        'is_fully_paid': transaction.is_fully_paid,
    })


@permission_required_or_superuser('repair_shop.view_gadgetrepairtransaction')
def repair_transaction_list(request):
    """
    List all repair transactions.
    Staff: Sees all repairs with pending count and technician info
    Technician: Only sees own assigned repairs
    """
    from datetime import date
    import datetime

    transactions = GadgetRepairTransaction.objects.select_related(
        'gadget', 'technician', 'gadget__customer'
    ).prefetch_related('repair_logs', 'payments').order_by('-brought_in_date')
    
    # --- Filters ---
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    payment_filter = request.GET.get('payment', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    # Month/Year filter (new)
    selected_month = request.GET.get('month', '')
    selected_year = request.GET.get('year', '')

    if selected_month:
        try:
            transactions = transactions.filter(brought_in_date__month=int(selected_month))
        except (ValueError, TypeError):
            pass

    if selected_year:
        try:
            transactions = transactions.filter(brought_in_date__year=int(selected_year))
        except (ValueError, TypeError):
            pass

    if search_query:
        transactions = transactions.filter(
            Q(code__icontains=search_query) |
            Q(gadget__gadget_brand__icontains=search_query) |
            Q(gadget__gadget_model__icontains=search_query) |
            Q(technician__username__icontains=search_query) |
            Q(gadget__customer__first_name__icontains=search_query)
        )
    
    if status_filter:
        transactions = transactions.filter(status=status_filter)

    if date_from:
        try:
            transactions = transactions.filter(brought_in_date__date__gte=date_from)
        except Exception:
            pass

    if date_to:
        try:
            transactions = transactions.filter(brought_in_date__date__lte=date_to)
        except Exception:
            pass

    # Payment filter applied in Python (properties can't be used in DB filter)
    if payment_filter == 'paid':
        transactions = [t for t in transactions if t.is_fully_paid]
    elif payment_filter == 'unpaid':
        transactions = [t for t in transactions if not t.is_fully_paid]

    base_qs = GadgetRepairTransaction.objects.all()
    stats = {
        'total': base_qs.count(),
        'pending': base_qs.filter(status=GadgetRepairTransaction.PENDING).count(),
        'in_progress': base_qs.filter(status=GadgetRepairTransaction.INPROGRESS).count(),
        'completed': base_qs.filter(status=GadgetRepairTransaction.COMPLETED).count(),
    }

    # Generate year range for dropdown (current year ± 5)
    current_year = date.today().year
    years = list(range(current_year - 5, current_year + 2))

    # Convert month to int for template comparison
    selected_month_int = int(selected_month) if selected_month and selected_month.isdigit() else None
    selected_year_int = int(selected_year) if selected_year and selected_year.isdigit() else None
    
    return render(request, 'repair_shop/repairs/repair_transaction_list.html', {
        'transactions': transactions,
        'stats': stats,
        'search_query': search_query,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'date_from': date_from,
        'date_to': date_to,
        'selected_month': selected_month_int,
        'selected_year': selected_year_int,
        'years': years,
        'today': date.today(),
    })


@permission_required_or_superuser('repair_shop.view_gadgetrepairtransaction')
def my_assigned_repairs(request):
    """View technician's assigned repairs - Technician Only"""
    repairs = GadgetRepairTransaction.objects.filter(
        technician=request.user
    ).select_related('gadget', 'gadget__customer').order_by('-brought_in_date')
    
    stats = {
        'pending': repairs.filter(status=GadgetRepairTransaction.PENDING).count(),
        'in_progress': repairs.filter(status=GadgetRepairTransaction.INPROGRESS).count(),
        'completed': repairs.filter(status=GadgetRepairTransaction.COMPLETED).count(),
    }
    
    return render(request, 'repair_shop/repairs/my_assigned_repairs.html', {
        'repairs': repairs,
        'stats': stats
    })


@login_required
def technician_dashboard(request):
    """Technician Dashboard - Shows assigned gadgets/repairs with detailed status"""
    # Allow technicians and superusers to access
    if not (request.user.is_technician or request.user.is_superuser):
        messages.error(request, 'You do not have permission to access this page')
        return redirect('repair_shop:home')
    
    # Get all repairs assigned to technician
    repairs = GadgetRepairTransaction.objects.filter(
        technician=request.user
    ).select_related('gadget', 'gadget__customer', 'gadget__customer').prefetch_related('repair_logs').order_by('-brought_in_date')
    
    # Calculate statistics (using exact status values from model)
    stats = {
        'total': repairs.count(),
        'pending': repairs.filter(status=GadgetRepairTransaction.PENDING).count(),
        'in_progress': repairs.filter(status=GadgetRepairTransaction.INPROGRESS).count(),
        'completed': repairs.filter(status=GadgetRepairTransaction.COMPLETED).count(),
    }
    
    # Breakdown by priority (recent first, pending/in-progress first)
    pending_repairs = repairs.filter(status=GadgetRepairTransaction.PENDING)[:10]
    in_progress_repairs = repairs.filter(status=GadgetRepairTransaction.INPROGRESS)[:10]
    completed_repairs = repairs.filter(status=GadgetRepairTransaction.COMPLETED)[:5]
    
    # Get repair logs for context
    repair_logs_context = {}
    for repair in repairs[:20]:  # Last 20 repairs
        repair_logs_context[repair.id] = repair.repair_logs.all().order_by('-created_at')[:3]
    
    context = {
        'stats': stats,
        'all_repairs': repairs,
        'pending_repairs': pending_repairs,
        'in_progress_repairs': in_progress_repairs,
        'completed_repairs': completed_repairs,
        'repair_logs_context': repair_logs_context,
    }
    
    return render(request, 'repair_shop/technician_dashboard.html', context)


@login_required
def technician_update_status(request, transaction_id):
    """Update repair status - Technician can only update their assigned repairs"""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    # Technician can only update their own repairs
    if not request.user.is_superuser and request.user.is_technician:
        if transaction.technician != request.user:
            messages.error(request, 'You can only update your assigned repairs')
            return redirect('repair_shop:technician_dashboard')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Validate status
        valid_statuses = [GadgetRepairTransaction.PENDING, 
                          GadgetRepairTransaction.INPROGRESS, 
                          GadgetRepairTransaction.COMPLETED]
        
        if new_status in valid_statuses:
            old_status = transaction.status
            transaction.status = new_status
            transaction.save()
            
            status_display = dict(GadgetRepairTransaction.STATUS_CHOICES).get(new_status, new_status)
            messages.success(request, f'Repair status updated from {old_status} to {status_display}')
            
            # If marked as completed, notify staff and show special message
            if new_status == GadgetRepairTransaction.COMPLETED:
                NotificationService.notify_staff_repair_completed(transaction)
                # If no payment has been received yet, also send a payment-pending alert
                if transaction.total_paid == 0:
                    NotificationService.notify_staff_payment_pending(transaction)
                    messages.warning(request, 'Repair marked as completed! ⚠️ No payment has been recorded — admin has been alerted.')
                else:
                    messages.info(request, 'Repair marked as completed! Admin has been notified.')
            
            return redirect('repair_shop:technician_dashboard')
        else:
            messages.error(request, 'Invalid status selected')
    
    return render(request, 'repair_shop/repairs/technician_update_status.html', {
        'transaction': transaction
    })


@permission_required_or_superuser('repair_shop.change_gadgetrepairtransaction')
def update_repair_transaction(request, transaction_id):
    """Update repair transaction status and technician - Staff, Superuser"""
    transaction_obj = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    if request.method == 'POST':
        form = GadgetRepairTransactionForm(request.POST, instance=transaction_obj)
        if form.is_valid():
            technician = form.cleaned_data.get('technician')
            status = form.cleaned_data.get('status')
            
            result = RepairTransactionService.update_repair_transaction(
                transaction_id=transaction_id,
                technician_id=technician.id,
                status=status
            )
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
            else:
                messages.error(request, result['message'])
    else:
        form = GadgetRepairTransactionForm(instance=transaction_obj)
    
    return render(request, 'repair_shop/repairs/create_repair_transaction.html', {
        'form': form,
        'transaction': transaction_obj
    })


@permission_required_or_superuser('repair_shop.change_gadgetrepairtransaction')
def reassign_technician(request, transaction_id):
    """Reassign a repair to a different technician - Staff, Secretary, Superuser"""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    if request.method == 'POST':
        form = ReassignTechnicianForm(request.POST)
        if form.is_valid():
            technician = form.cleaned_data.get('technician')
            
            result = RepairTransactionService.reassign_technician(
                transaction_id=transaction_id,
                new_technician_id=technician.id
            )
            
            if result['success']:
                messages.success(request, result['message'])
                # Notify the newly assigned technician
                transaction.refresh_from_db()
                NotificationService.notify_technician_assigned(transaction)
                return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
            else:
                messages.error(request, result['message'])
    else:
        form = ReassignTechnicianForm()
    
    return render(request, 'repair_shop/repairs/reassign_technician.html', {
        'form': form,
        'transaction': transaction,
        'current_technician': transaction.technician
    })


# ============================================
# REPAIR LOG VIEWS - TECHNICIAN & STAFF
# ============================================

@permission_required_or_superuser('repair_shop.add_gadgetrepairlog')
def add_repair_log(request, transaction_id):
    """Add a repair log to a transaction - Technician, Staff, Secretary, Superuser"""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    # Block adding logs to completed repairs (superusers can still do it)
    if not request.user.is_superuser and transaction.status == GadgetRepairTransaction.COMPLETED:
        messages.error(request, 'Cannot add logs to a completed repair.')
        return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
    
    # Technician can only add logs to their assigned repairs
    if not request.user.is_superuser and request.user.is_technician:
        if transaction.technician != request.user:
            messages.error(request, 'You can only add logs to your assigned repairs')
            return redirect('repair_shop:my_assigned_repairs')
    
    if request.method == 'POST':
        form = GadgetRepairLogForm(request.POST)
        if form.is_valid():
            repair_cost = form.cleaned_data.get('repair_cost')
            issue_description = form.cleaned_data.get('issue_description')
            resolution_description = form.cleaned_data.get('resolution_description')
            
            result = GadgetRepairLogService.add_repair_log(
                transaction_id=transaction_id,
                repair_cost=repair_cost,
                issue_description=issue_description,
                resolution_description=resolution_description
            )
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
            else:
                messages.error(request, result['message'])
    else:
        form = GadgetRepairLogForm()
    
    return render(request, 'repair_shop/repairs/add_repair_log.html', {
        'form': form,
        'transaction': transaction
    })


@permission_required_or_superuser('repair_shop.view_gadgetrepairlog')
def repair_log_detail(request, log_id):
    """View a specific repair log - All authenticated users"""
    log = get_object_or_404(GadgetRepairLog, id=log_id)
    return render(request, 'repair_shop/repairs/repair_log_detail.html', {'log': log})


@permission_required_or_superuser('repair_shop.change_gadgetrepairlog')
def update_repair_log(request, log_id):
    """Update a repair log - Technician, Staff, Superuser"""
    log = get_object_or_404(GadgetRepairLog, id=log_id)
    transaction = log.transaction
    
    # Technician can only update their own logs
    if not request.user.is_superuser and request.user.is_technician:
        if transaction.technician != request.user:
            messages.error(request, 'You can only update logs for your assigned repairs')
            return redirect('repair_shop:my_assigned_repairs')
    
    if request.method == 'POST':
        form = GadgetRepairLogForm(request.POST, instance=log)
        if form.is_valid():
            repair_cost = form.cleaned_data.get('repair_cost')
            issue_description = form.cleaned_data.get('issue_description')
            resolution_description = form.cleaned_data.get('resolution_description')
            
            result = GadgetRepairLogService.update_repair_log(
                repair_log_id=log_id,
                repair_cost=repair_cost,
                issue_description=issue_description,
                resolution_description=resolution_description
            )
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction.id)
            else:
                messages.error(request, result['message'])
    else:
        form = GadgetRepairLogForm(instance=log)
    
    return render(request, 'repair_shop/repairs/add_repair_log.html', {
        'form': form,
        'log': log,
        'transaction': transaction
    })


@login_required
def delete_repair_log(request, log_id):
    """Delete a repair log - Superuser Only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete repair logs')
        return redirect('repair_shop:repair_transaction_list')
    
    log = get_object_or_404(GadgetRepairLog, id=log_id)
    transaction_id = log.transaction.id
    
    if log.transaction.status != GadgetRepairTransaction.COMPLETED:
        log.delete()
        messages.success(request, 'Repair log deleted successfully')
    else:
        messages.error(request, 'Cannot delete logs from completed repairs')
    
    return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)


# ============================================
# TRANSACTION RECEIPT VIEWS - STAFF ONLY
# ============================================

@permission_required_or_superuser('repair_shop.add_gadgettransactionreceipt')
def create_transaction_receipt(request, transaction_id):
    """Generate a receipt once the repair is Completed and fully paid."""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    # Redirect if repair is not completed
    if transaction.status != GadgetRepairTransaction.COMPLETED:
        messages.error(request, 'Cannot create receipt. Repair must be completed first.')
        return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
    
    # Redirect to existing receipt if already generated
    existing = transaction.gadgettransactionreceipt_set.first()
    if existing:
        messages.info(request, f'Receipt {existing.receipt_number} already exists.')
        return redirect('repair_shop:receipt_detail', receipt_id=existing.id)

    payments = transaction.payments.all().order_by('created_at')

    if request.method == 'POST':
            result = GadgetTransactionReceiptService.create_transaction_receipt(
            transaction_id=transaction_id
            )
            if result['success']:
                messages.success(request, result['message'])
                return redirect('repair_shop:receipt_detail', receipt_id=result['transaction_receipt'].id)
            else:
                messages.error(request, result['message'])
    
    return render(request, 'repair_shop/receipts/create_transaction_receipt.html', {
        'transaction': transaction,
        'total_cost': transaction.total_cost,
        'total_paid': transaction.total_paid,
        'total_due': transaction.total_due,
        'is_fully_paid': transaction.is_fully_paid,
        'payments': payments,
    })


@permission_required_or_superuser('repair_shop.view_gadgettransactionreceipt')
def receipt_detail(request, receipt_id):
    """View a specific receipt - Staff, Superuser"""
    receipt = get_object_or_404(GadgetTransactionReceipt, id=receipt_id)
    transaction = receipt.transaction
    
    return render(request, 'repair_shop/receipts/receipt_detail.html', {
        'receipt': receipt,
        'transaction': transaction
    })


@permission_required_or_superuser('repair_shop.view_gadgettransactionreceipt')
def receipt_list(request):
    """List all transaction receipts - Staff, Superuser"""
    receipts = GadgetTransactionReceipt.objects.select_related('transaction', 'transaction__gadget', 'transaction__gadget__customer').order_by('-issued_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        receipts = receipts.filter(
            Q(receipt_number__icontains=search_query) |
            Q(transaction__transaction_code__icontains=search_query) |
            Q(transaction__gadget__customer__first_name__icontains=search_query) |
            Q(transaction__gadget__gadget_brand__icontains=search_query)
        )
    
    return render(request, 'repair_shop/receipts/receipt_list.html', {'receipts': receipts})


# ============================================
# USER MANAGEMENT VIEWS - ADMIN ONLY
# ============================================

@login_required
def user_profile(request, user_id=None):
    """View/edit user profile"""
    if user_id:
        # Viewing other user's profile (admin only)
        if not request.user.is_superuser:
            messages.error(request, 'You do not have permission to view other profiles')
            return redirect('repair_shop:home')
        user_obj = get_object_or_404(MyUser, id=user_id)
    else:
        # Viewing own profile
        user_obj = request.user
    
    from .forms import UserProfileForm
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            # Handle password change
            current_password = request.POST.get('current_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            new_password_confirm = request.POST.get('new_password_confirm', '').strip()
            if current_password or new_password:
                if not user_obj.check_password(current_password):
                    messages.error(request, 'Current password is incorrect.')
                elif len(new_password) < 6:
                    messages.error(request, 'New password must be at least 6 characters.')
                elif new_password != new_password_confirm:
                    messages.error(request, 'New passwords do not match.')
                else:
                    user_obj.set_password(new_password)
                    user_obj.save()
                    messages.success(request, 'Password changed successfully. Please log in again.')
                    return redirect('repair_shop:login')
            messages.success(request, 'Profile updated successfully')
            return redirect('repair_shop:user_profile')
    else:
        form = UserProfileForm(instance=user_obj)

    return render(request, 'repair_shop/users/user_profile.html', {
        'form': form,
        'user_obj': user_obj
    })


@login_required
def user_list(request):
    """List all users - Superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page')
        return redirect('repair_shop:home')
    
    users = MyUser.objects.all().order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    return render(request, 'repair_shop/users/user_list.html', {'users': users})


@login_required
def create_user(request):
    """Create new user - Superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to create users')
        return redirect('repair_shop:home')
    
    if request.method == 'POST':
        from .forms import UserCreationForm
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully')
            return redirect('repair_shop:user_list')
    else:
        from .forms import UserCreationForm
        form = UserCreationForm()
    
    return render(request, 'repair_shop/users/create_user.html', {'form': form})


@login_required
def edit_user(request, user_id):
    """Edit user details - Superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to edit users')
        return redirect('repair_shop:home')
    
    user_obj = get_object_or_404(MyUser, id=user_id)
    
    if request.method == 'POST':
        from .forms import UserEditForm
        form = UserEditForm(request.POST, instance=user_obj)
        if form.is_valid():
            form.save()
            # Handle optional password change
            new_password = request.POST.get('new_password', '').strip()
            new_password_confirm = request.POST.get('new_password_confirm', '').strip()
            if new_password:
                if len(new_password) < 6:
                    messages.error(request, 'Password must be at least 6 characters.')
                elif new_password != new_password_confirm:
                    messages.error(request, 'Passwords do not match.')
                else:
                    user_obj.set_password(new_password)
                    user_obj.save()
                    messages.info(request, 'Password updated successfully.')
            messages.success(request, f'User {user_obj.username} updated successfully')
            return redirect('repair_shop:user_list')
    else:
        from .forms import UserEditForm
        form = UserEditForm(instance=user_obj)
    
    return render(request, 'repair_shop/users/edit_user.html', {
        'form': form,
        'user_obj': user_obj
    })


@login_required
def delete_user(request, user_id):
    """Delete user - Superuser only"""
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete users')
        return redirect('repair_shop:home')
    
    if request.user.id == user_id:
        messages.error(request, 'You cannot delete your own account')
        return redirect('repair_shop:user_list')
    
    user_obj = get_object_or_404(MyUser, id=user_id)
    username = user_obj.username
    user_obj.delete()
    messages.success(request, f'User {username} deleted successfully')
    return redirect('repair_shop:user_list')


# ============================================
# PAYMENT VIEWS
# ============================================

@permission_required_or_superuser('repair_shop.add_payment')
def add_payment(request, transaction_id):
    """Record a cash or mobile-money payment against a completed repair."""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)

    # Only allow payments on completed repairs
    if transaction.status != GadgetRepairTransaction.COMPLETED:
        messages.error(request, 'Payments can only be recorded for completed repairs.')
        return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)

    # If already fully paid, redirect
    if transaction.is_fully_paid:
        messages.warning(request, 'This repair is already fully paid. Generate the receipt instead.')
        return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)

    payments = transaction.payments.all().order_by('created_at')

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.transaction = transaction
            payment.recorded_by = request.user
            payment.save()

            remaining = transaction.total_due  # recalculated after save
            if transaction.is_fully_paid:
                messages.success(
                    request,
                    f'Payment of D{payment.amount:.2f} recorded. '
                    f'Repair is now FULLY PAID! You can now generate a receipt.'
                )
            else:
                messages.success(
                    request,
                    f'Payment of D{payment.amount:.2f} recorded. '
                    f'Outstanding balance: D{remaining:.2f}'
                )
            return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
    else:
        form = PaymentForm(initial={'amount': transaction.total_due})

    return render(request, 'repair_shop/payments/add_payment.html', {
        'form': form,
        'transaction': transaction,
        'total_cost': transaction.total_cost,
        'total_paid': transaction.total_paid,
        'total_due': transaction.total_due,
        'payments': payments,
    })


# ============================================
# NOTIFICATION VIEWS
# ============================================

@login_required
def notification_list(request):
    """View all notifications for the current user."""
    notifications_qs = Notification.objects.filter(
        recipient=request.user
    ).order_by('-created_at')

    # Technicians only see their own assignment notifications
    if request.user.is_technician and not (request.user.is_staff or request.user.is_superuser):
        notifications_qs = notifications_qs.filter(
            notification_type=Notification.REPAIR_ASSIGNED
        )

    # Type filter from query param
    type_filter = request.GET.get('type', '')
    if type_filter:
        notifications_qs = notifications_qs.filter(notification_type=type_filter)

    unread = notifications_qs.filter(is_read=False)

    # Mark all as read when user visits the page
    unread.update(is_read=True)

    return render(request, 'repair_shop/notifications/notification_list.html', {
        'notifications': notifications_qs,
        'unread_count': unread.count(),
        'type_filter': type_filter,
        'is_technician_only': request.user.is_technician and not (request.user.is_staff or request.user.is_superuser),
    })


@login_required
def mark_notification_read(request, notification_id):
    """Mark a single notification as read and redirect to the linked repair."""
    notif = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    notif.is_read = True
    notif.save()
    if notif.repair:
        return redirect('repair_shop:repair_transaction_detail', transaction_id=notif.repair.id)
    return redirect('repair_shop:notification_list')

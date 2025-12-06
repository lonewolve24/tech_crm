from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt
from .forms import (
    CustomerForm, GadgetForm, GadgetRepairTransactionForm, 
    GadgetRepairLogForm, ReassignTechnicianForm, GadgetTransactionReceiptForm
)
from .service import RepairTransactionService, GadgetRepairLogService, GadgetTransactionReceiptService
from .decorators import permission_required_or_superuser

# ============================================
# HOME & DASHBOARD VIEWS
# ============================================

@login_required
def home(request):
    """
    Home view - Redirects to appropriate dashboard based on user role.
    """
    if request.user.is_superuser:
        # Superuser dashboard (placeholder - can create later)
        return render(request, 'repair_shop/home.html', {
            'user_role': 'Superuser',
            'dashboard': 'admin'
        })
    elif request.user.is_staff:
        # Staff/Manager dashboard (placeholder - can create later)
        return render(request, 'repair_shop/home.html', {
            'user_role': 'Staff',
            'dashboard': 'staff'
        })
    elif request.user.is_secretary:
        # Secretary dashboard (placeholder - can create later)
        return render(request, 'repair_shop/home.html', {
            'user_role': 'Secretary',
            'dashboard': 'secretary'
        })
    elif request.user.is_technician:
        # Technician dashboard - show assigned repairs
        repairs = GadgetRepairTransaction.objects.filter(
            technician=request.user
        ).order_by('-brought_in_date')[:5]
        
        return render(request, 'repair_shop/home.html', {
            'user_role': 'Technician',
            'dashboard': 'technician',
            'recent_repairs': repairs
        })
    else:
        # Generic dashboard for users without specific role
        return render(request, 'repair_shop/home.html', {
            'user_role': 'User',
            'dashboard': 'default'
        })

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
    pending_repairs = all_repairs.filter(status='PENDING').count()
    inprogress_repairs = all_repairs.filter(status='IN_PROGRESS').count()
    completed_repairs = all_repairs.filter(status='COMPLETED').count()
    
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
    pending_repairs = repair_history.filter(status='PENDING').count()
    inprogress_repairs = repair_history.filter(status='IN_PROGRESS').count()
    completed_repairs = repair_history.filter(status='COMPLETED').count()
    
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
    # Get gadget from URL parameter (from customer detail page)
    gadget_id = request.GET.get('gadget')
    initial_data = {}
    if gadget_id:
        try:
            gadget = Gadget.objects.get(id=gadget_id)
            initial_data['gadget'] = gadget
        except Gadget.DoesNotExist:
            pass
    
    if request.method == 'POST':
        form = GadgetRepairTransactionForm(request.POST)
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
                return redirect('repair_shop:repair_transaction_detail', transaction_id=result['transaction'].id)
            else:
                messages.error(request, result['message'])
    else:
        form = GadgetRepairTransactionForm(initial=initial_data)
    
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
    
    return render(request, 'repair_shop/repairs/repair_transaction_detail.html', {
        'transaction': transaction,
        'logs': logs,
        'total_cost': transaction.total_cost
    })


@permission_required_or_superuser('repair_shop.view_gadgetrepairtransaction')
def repair_transaction_list(request):
    """
    List all repair transactions.
    Staff: Sees all repairs with pending count and technician info
    Technician: Only sees own assigned repairs
    """
    transactions = GadgetRepairTransaction.objects.select_related('gadget', 'technician', 'gadget__customer').order_by('-brought_in_date')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(transaction_code__icontains=search_query) |
            Q(gadget__gadget_brand__icontains=search_query) |
            Q(gadget__gadget_model__icontains=search_query) |
            Q(technician__username__icontains=search_query) |
            Q(gadget__customer__first_name__icontains=search_query)
        )
    
    stats = {
        'total': transactions.count(),
        'pending': transactions.filter(status='PENDING').count(),
        'in_progress': transactions.filter(status='IN_PROGRESS').count(),
        'completed': transactions.filter(status='COMPLETED').count(),
    }
    
    return render(request, 'repair_shop/repairs/repair_transaction_list.html', {
        'transactions': transactions,
        'stats': stats
    })


@permission_required_or_superuser('repair_shop.view_gadgetrepairtransaction')
def my_assigned_repairs(request):
    """View technician's assigned repairs - Technician Only"""
    repairs = GadgetRepairTransaction.objects.filter(
        technician=request.user
    ).select_related('gadget', 'gadget__customer').order_by('-brought_in_date')
    
    stats = {
        'pending': repairs.filter(status='PENDING').count(),
        'in_progress': repairs.filter(status='IN_PROGRESS').count(),
        'completed': repairs.filter(status='COMPLETED').count(),
    }
    
    return render(request, 'repair_shop/repairs/my_assigned_repairs.html', {
        'repairs': repairs,
        'stats': stats
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
    """Create a receipt for a completed repair transaction - Staff, Secretary, Superuser"""
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    # Check if repair is completed
    if transaction.status != GadgetRepairTransaction.COMPLETED:
        messages.error(request, 'Cannot create receipt. Repair must be completed first.')
        return redirect('repair_shop:repair_transaction_detail', transaction_id=transaction_id)
    
    if request.method == 'POST':
        form = GadgetTransactionReceiptForm(request.POST)
        if form.is_valid():
            amount_paid = form.cleaned_data.get('amount_paid')
            
            result = GadgetTransactionReceiptService.create_transaction_receipt(
                transaction_id=transaction_id,
                amount=amount_paid,
                payment_method=None  # Optional - can be added later
            )
            
            if result['success']:
                messages.success(request, result['message'])
                return redirect('repair_shop:receipt_detail', receipt_id=result['transaction_receipt'].id)
            else:
                messages.error(request, result['message'])
    else:
        form = GadgetTransactionReceiptForm()
    
    return render(request, 'repair_shop/receipts/create_transaction_receipt.html', {
        'form': form,
        'transaction': transaction,
        'total_cost': transaction.total_cost
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

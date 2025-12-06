from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'repair_shop'

urlpatterns = [
    # ============================================
    # AUTHENTICATION URLS
    # ============================================
    path('login/', auth_views.LoginView.as_view(
        template_name='repair_shop/login.html'
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # ============================================
    # HOME & DASHBOARD URLS
    # ============================================
    path('', views.home, name='home'),
    
    # ============================================
    # CUSTOMER URLS
    # ============================================
    # Create Customer
    path('customers/create/', views.create_customer, name='create_customer'),
    # Template: repair_shop/customers/create_customer.html
    
    # Customer List
    path('customers/', views.customer_list, name='customer_list'),
    # Template: repair_shop/customers/customer_list.html
    
    # Customer Detail
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    # Template: repair_shop/customers/customer_detail.html
    
    # Update Customer
    path('customers/<int:customer_id>/edit/', views.update_customer, name='update_customer'),
    # Template: repair_shop/customers/update_customer.html
    
    # Delete Customer
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    
    # ============================================
    # GADGET URLS
    # ============================================
    # Create Gadget
    path('gadgets/create/', views.create_gadget, name='create_gadget'),
    # Template: repair_shop/gadgets/create_gadget.html
    
    # Gadget List
    path('gadgets/', views.gadget_list, name='gadget_list'),
    # Template: repair_shop/gadgets/gadget_list.html
    
    # Gadget Detail
    path('gadgets/<int:gadget_id>/', views.gadget_detail, name='gadget_detail'),
    # Template: repair_shop/gadgets/gadget_detail.html
    
    # Update Gadget
    path('gadgets/<int:gadget_id>/edit/', views.update_gadget, name='update_gadget'),
    # Template: repair_shop/gadgets/update_gadget.html
    
    # Delete Gadget
    path('gadgets/<int:gadget_id>/delete/', views.delete_gadget, name='delete_gadget'),
    
    # ============================================
    # REPAIR TRANSACTION URLS
    # ============================================
    # Create Repair Transaction
    path('repairs/create/', views.create_repair_transaction, name='create_repair_transaction'),
    # Template: repair_shop/repairs/create_repair_transaction.html
    
    # All Repairs List (Staff View)
    path('repairs/', views.repair_transaction_list, name='repair_transaction_list'),
    # Template: repair_shop/repairs/repair_transaction_list.html
    
    # My Assigned Repairs (Technician View)
    path('repairs/my-repairs/', views.my_assigned_repairs, name='my_assigned_repairs'),
    # Template: repair_shop/repairs/my_assigned_repairs.html
    
    # Repair Transaction Detail
    path('repairs/<int:transaction_id>/', views.repair_transaction_detail, name='repair_transaction_detail'),
    # Template: repair_shop/repairs/repair_transaction_detail.html
    
    # Update Repair Transaction
    path('repairs/<int:transaction_id>/edit/', views.update_repair_transaction, name='update_repair_transaction'),
    # Template: repair_shop/repairs/update_repair_transaction.html
    
    # Reassign Technician
    path('repairs/<int:transaction_id>/reassign/', views.reassign_technician, name='reassign_technician'),
    # Template: repair_shop/repairs/reassign_technician.html
    
    # ============================================
    # REPAIR LOG URLS
    # ============================================
    # Add Repair Log
    path('repairs/<int:transaction_id>/logs/add/', views.add_repair_log, name='add_repair_log'),
    # Template: repair_shop/logs/add_repair_log.html
    
    # Repair Log Detail
    path('logs/<int:log_id>/', views.repair_log_detail, name='repair_log_detail'),
    # Template: repair_shop/logs/repair_log_detail.html
    
    # Update Repair Log
    path('logs/<int:log_id>/edit/', views.update_repair_log, name='update_repair_log'),
    # Template: repair_shop/logs/update_repair_log.html
    
    # Delete Repair Log
    path('logs/<int:log_id>/delete/', views.delete_repair_log, name='delete_repair_log'),
    
    # ============================================
    # TRANSACTION RECEIPT URLS
    # ============================================
    # Create Receipt
    path('repairs/<int:transaction_id>/receipt/create/', views.create_transaction_receipt, name='create_transaction_receipt'),
    # Template: repair_shop/receipts/create_transaction_receipt.html
    
    # Receipt Detail
    path('receipts/<int:receipt_id>/', views.receipt_detail, name='receipt_detail'),
    # Template: repair_shop/receipts/receipt_detail.html
    
    # Receipt List
    path('receipts/', views.receipt_list, name='receipt_list'),
    # Template: repair_shop/receipts/receipt_list.html
]

# URL Naming Convention:
# - List views: app_name:model_name_list
# - Create views: app_name:create_model_name
# - Detail views: app_name:model_name_detail
# - Update views: app_name:update_model_name (or model_name_edit)
# - Delete views: app_name:delete_model_name
#
# Example usage in templates:
# {% url 'repair_shop:customer_list' %}
# {% url 'repair_shop:create_customer' %}
# {% url 'repair_shop:customer_detail' customer.id %}
# {% url 'repair_shop:update_customer' customer.id %}
# {% url 'repair_shop:delete_customer' customer.id %}

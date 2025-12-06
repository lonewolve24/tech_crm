# URLs and Templates Reference Guide

## Complete URL Mapping

This document lists all URLs, their view functions, and corresponding templates.

---

## Authentication URLs

| URL | View | Template | Method | Permission |
|-----|------|----------|--------|-----------|
| `/login/` | `LoginView` | `repair_shop/login.html` | GET/POST | Public |
| `/logout/` | `LogoutView` | - | GET | Authenticated |

---

## Home & Dashboard

| URL | Name | View | Template | Permission |
|-----|------|------|----------|-----------|
| `/` | `home` | `views.home` | `repair_shop/home.html` | Authenticated |

---

## Customer Management

### Create Customer
```
URL: /customers/create/
Name: repair_shop:create_customer
View: views.create_customer
Template: repair_shop/customers/create_customer.html
Permission: repair_shop.add_customer
Method: GET, POST
```

**Template Usage:**
```html
<a href="{% url 'repair_shop:create_customer' %}" class="btn btn-primary">
    Add Customer
</a>
```

### Customer List
```
URL: /customers/
Name: repair_shop:customer_list
View: views.customer_list
Template: repair_shop/customers/customer_list.html
Permission: repair_shop.view_customer
Method: GET
```

**Template Usage:**
```html
<a href="{% url 'repair_shop:customer_list' %}" class="btn btn-info">
    View All Customers
</a>
```

### Customer Detail
```
URL: /customers/<int:customer_id>/
Name: repair_shop:customer_detail
View: views.customer_detail
Template: repair_shop/customers/customer_detail.html
Permission: repair_shop.view_customer
Method: GET
Parameters: customer_id (integer)
```

**Template Usage:**
```html
<a href="{% url 'repair_shop:customer_detail' customer.id %}" class="btn btn-info">
    View Details
</a>
```

### Update Customer
```
URL: /customers/<int:customer_id>/edit/
Name: repair_shop:update_customer
View: views.update_customer
Template: repair_shop/customers/update_customer.html
Permission: repair_shop.change_customer
Method: GET, POST
Parameters: customer_id (integer)
```

**Template Usage:**
```html
<a href="{% url 'repair_shop:update_customer' customer.id %}" class="btn btn-warning">
    <i class="bi bi-pencil"></i> Edit
</a>
```

### Delete Customer
```
URL: /customers/<int:customer_id>/delete/
Name: repair_shop:delete_customer
View: views.delete_customer
Template: None (Redirects)
Permission: Superuser only
Method: GET
Parameters: customer_id (integer)
```

**Template Usage:**
```html
{% if user.is_superuser %}
<a href="{% url 'repair_shop:delete_customer' customer.id %}" class="btn btn-danger">
    <i class="bi bi-trash"></i> Delete
</a>
{% endif %}
```

---

## Gadget Management

### Create Gadget
```
URL: /gadgets/create/
Name: repair_shop:create_gadget
View: views.create_gadget
Template: repair_shop/gadgets/create_gadget.html
Permission: repair_shop.add_gadget
Method: GET, POST
```

### Gadget List
```
URL: /gadgets/
Name: repair_shop:gadget_list
View: views.gadget_list
Template: repair_shop/gadgets/gadget_list.html
Permission: repair_shop.view_gadget
Method: GET
```

### Gadget Detail
```
URL: /gadgets/<int:gadget_id>/
Name: repair_shop:gadget_detail
View: views.gadget_detail
Template: repair_shop/gadgets/gadget_detail.html
Permission: repair_shop.view_gadget
Method: GET
Parameters: gadget_id (integer)
```

### Update Gadget
```
URL: /gadgets/<int:gadget_id>/edit/
Name: repair_shop:update_gadget
View: views.update_gadget
Template: repair_shop/gadgets/update_gadget.html
Permission: repair_shop.change_gadget
Method: GET, POST
Parameters: gadget_id (integer)
```

### Delete Gadget
```
URL: /gadgets/<int:gadget_id>/delete/
Name: repair_shop:delete_gadget
View: views.delete_gadget
Template: None (Redirects)
Permission: Superuser only
Method: GET
Parameters: gadget_id (integer)
```

---

## Repair Transaction Management

### Create Repair Transaction
```
URL: /repairs/create/
Name: repair_shop:create_repair_transaction
View: views.create_repair_transaction
Template: repair_shop/repairs/create_repair_transaction.html
Permission: repair_shop.add_gadgetrepairtransaction
Method: GET, POST
```

### All Repairs List (Staff View)
```
URL: /repairs/
Name: repair_shop:repair_transaction_list
View: views.repair_transaction_list
Template: repair_shop/repairs/repair_transaction_list.html
Permission: repair_shop.view_gadgetrepairtransaction
Method: GET
Access: Staff, Superuser only
Shows: All repairs with statistics
```

### My Assigned Repairs (Technician View)
```
URL: /repairs/my-repairs/
Name: repair_shop:my_assigned_repairs
View: views.my_assigned_repairs
Template: repair_shop/repairs/my_assigned_repairs.html
Permission: repair_shop.view_gadgetrepairtransaction
Method: GET
Access: Technician, Superuser
Shows: Only user's assigned repairs
```

### Repair Transaction Detail
```
URL: /repairs/<int:transaction_id>/
Name: repair_shop:repair_transaction_detail
View: views.repair_transaction_detail
Template: repair_shop/repairs/repair_transaction_detail.html
Permission: repair_shop.view_gadgetrepairtransaction
Method: GET
Parameters: transaction_id (integer)
```

**Template Usage:**
```html
<a href="{% url 'repair_shop:repair_transaction_detail' transaction.id %}">
    View Transaction
</a>
```

### Update Repair Transaction
```
URL: /repairs/<int:transaction_id>/edit/
Name: repair_shop:update_repair_transaction
View: views.update_repair_transaction
Template: repair_shop/repairs/update_repair_transaction.html
Permission: repair_shop.change_gadgetrepairtransaction
Method: GET, POST
Parameters: transaction_id (integer)
```

### Reassign Technician
```
URL: /repairs/<int:transaction_id>/reassign/
Name: repair_shop:reassign_technician
View: views.reassign_technician
Template: repair_shop/repairs/reassign_technician.html
Permission: repair_shop.change_gadgetrepairtransaction
Method: GET, POST
Parameters: transaction_id (integer)
```

---

## Repair Log Management

### Add Repair Log
```
URL: /repairs/<int:transaction_id>/logs/add/
Name: repair_shop:add_repair_log
View: views.add_repair_log
Template: repair_shop/logs/add_repair_log.html
Permission: repair_shop.add_gadgetrepairlog
Method: GET, POST
Parameters: transaction_id (integer)
Access: Technician, Staff, Secretary
```

### Repair Log Detail
```
URL: /logs/<int:log_id>/
Name: repair_shop:repair_log_detail
View: views.repair_log_detail
Template: repair_shop/logs/repair_log_detail.html
Permission: repair_shop.view_gadgetrepairlog
Method: GET
Parameters: log_id (integer)
```

### Update Repair Log
```
URL: /logs/<int:log_id>/edit/
Name: repair_shop:update_repair_log
View: views.update_repair_log
Template: repair_shop/logs/update_repair_log.html
Permission: repair_shop.change_gadgetrepairlog
Method: GET, POST
Parameters: log_id (integer)
```

### Delete Repair Log
```
URL: /logs/<int:log_id>/delete/
Name: repair_shop:delete_repair_log
View: views.delete_repair_log
Template: None (Redirects)
Permission: Superuser only
Method: GET
Parameters: log_id (integer)
```

---

## Transaction Receipt Management

### Create Receipt
```
URL: /repairs/<int:transaction_id>/receipt/create/
Name: repair_shop:create_transaction_receipt
View: views.create_transaction_receipt
Template: repair_shop/receipts/create_transaction_receipt.html
Permission: repair_shop.add_gadgettransactionreceipt
Method: GET, POST
Parameters: transaction_id (integer)
Requirements: Transaction must be COMPLETED
```

### Receipt Detail
```
URL: /receipts/<int:receipt_id>/
Name: repair_shop:receipt_detail
View: views.receipt_detail
Template: repair_shop/receipts/receipt_detail.html
Permission: repair_shop.view_gadgettransactionreceipt
Method: GET
Parameters: receipt_id (integer)
```

### Receipt List
```
URL: /receipts/
Name: repair_shop:receipt_list
View: views.receipt_list
Template: repair_shop/receipts/receipt_list.html
Permission: repair_shop.view_gadgettransactionreceipt
Method: GET
```

---

## Template Directory Structure

```
repair_shop/templates/repair_shop/
├── base.html                           (Main layout)
├── login.html                          (Login page)
├── home.html                           (Home/redirect)
├── customers/
│   ├── customer_list.html              (List view)
│   ├── create_customer.html            (Create form)
│   ├── update_customer.html            (Edit form)
│   └── customer_detail.html            (Detail view)
├── gadgets/
│   ├── gadget_list.html
│   ├── create_gadget.html
│   ├── update_gadget.html
│   └── gadget_detail.html
├── repairs/
│   ├── repair_transaction_list.html    (All repairs - Staff)
│   ├── my_assigned_repairs.html        (My repairs - Tech)
│   ├── create_repair_transaction.html
│   ├── update_repair_transaction.html
│   ├── repair_transaction_detail.html
│   └── reassign_technician.html
├── logs/
│   ├── add_repair_log.html
│   ├── update_repair_log.html
│   └── repair_log_detail.html
└── receipts/
    ├── receipt_list.html
    ├── create_transaction_receipt.html
    └── receipt_detail.html
```

---

## Template Usage Examples

### In Links/Navigation
```html
<!-- Customer Links -->
<a href="{% url 'repair_shop:customer_list' %}">Customers</a>
<a href="{% url 'repair_shop:create_customer' %}">Add Customer</a>

<!-- Gadget Links -->
<a href="{% url 'repair_shop:gadget_list' %}">Gadgets</a>
<a href="{% url 'repair_shop:create_gadget' %}">Add Gadget</a>

<!-- Repair Links -->
<a href="{% url 'repair_shop:repair_transaction_list' %}">All Repairs</a>
<a href="{% url 'repair_shop:my_assigned_repairs' %}">My Repairs</a>
<a href="{% url 'repair_shop:create_repair_transaction' %}">New Repair</a>

<!-- Receipt Links -->
<a href="{% url 'repair_shop:receipt_list' %}">Receipts</a>
```

### With Parameters
```html
<!-- Detail Links -->
<a href="{% url 'repair_shop:customer_detail' customer.id %}">
    View Customer
</a>

<a href="{% url 'repair_shop:repair_transaction_detail' transaction.id %}">
    View Repair
</a>

<!-- Action Links -->
<a href="{% url 'repair_shop:update_customer' customer.id %}">Edit</a>
<a href="{% url 'repair_shop:delete_customer' customer.id %}">Delete</a>

<a href="{% url 'repair_shop:add_repair_log' transaction.id %}">
    Add Log
</a>

<a href="{% url 'repair_shop:reassign_technician' transaction.id %}">
    Reassign
</a>

<a href="{% url 'repair_shop:create_transaction_receipt' transaction.id %}">
    Create Receipt
</a>
```

### With Permissions
```html
<!-- Show only to users with permission -->
{% if user.has_perm 'repair_shop.add_customer' %}
    <a href="{% url 'repair_shop:create_customer' %}" class="btn btn-primary">
        Add Customer
    </a>
{% endif %}

<!-- Show only to superuser -->
{% if user.is_superuser %}
    <a href="{% url 'repair_shop:delete_customer' customer.id %}" class="btn btn-danger">
        Delete
    </a>
{% endif %}
```

---

## Main Config URLs

You also need to include these in `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('repair_shop.urls')),  # Add this line
]
```

---

## URL Summary Table

| Feature | Count | URLs |
|---------|-------|------|
| Authentication | 2 | login, logout |
| Customers | 5 | list, create, detail, update, delete |
| Gadgets | 5 | list, create, detail, update, delete |
| Repairs | 5 | list, create, detail, update, reassign |
| Logs | 4 | add, detail, update, delete |
| Receipts | 3 | list, create, detail |
| **Total** | **24 URLs** | - |

---

## Testing URLs

To test all URLs, use the Django test client:

```python
from django.test import Client
from django.urls import reverse

client = Client()

# Test customer URLs
response = client.get(reverse('repair_shop:customer_list'))
response = client.post(reverse('repair_shop:create_customer'), {...})
response = client.get(reverse('repair_shop:customer_detail', args=[1]))
```

---

## Troubleshooting

### URL Not Found Error
```
NoReverseMatch at /page/
Reverse for 'repair_shop:customer_list' not found.
```

**Solution:**
1. Check URL name matches exactly (case-sensitive)
2. Verify `app_name` is set in `urls.py`
3. Check parameters are provided if URL has `<int:id>`

### Template Not Found Error
```
TemplateDoesNotExist: repair_shop/customers/customer_list.html
```

**Solution:**
1. Create the template file in correct directory
2. Check directory structure matches `TEMPLATES['DIRS']`
3. Verify file name matches exactly (case-sensitive)

### Permission Denied Error
```
You do not have permission to access this page
```

**Solution:**
1. User must have required permission
2. Check user is in correct group
3. Verify `@permission_required_or_superuser` decorator on view

---

## Next Steps

1. Create all template files in `repair_shop/templates/repair_shop/`
2. Test each URL is accessible
3. Build template content for each page
4. Add styling and polish

---

## Quick Reference

**View all available URLs:**
```bash
python manage.py show_urls
```

**Test a specific URL:**
```bash
python manage.py runserver
# Visit: http://localhost:8000/customers/
```

**Debug URL resolution:**
```python
from django.urls import reverse
print(reverse('repair_shop:customer_list'))  # Output: /customers/
```


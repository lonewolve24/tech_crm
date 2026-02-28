# Role-Based Access Control (RBAC) Guide

## Overview

This application uses Django Groups and Permissions to control user access. There are 3 main roles:

1. **Technician** - Repairs gadgets, adds logs, updates their own logs
2. **Secretary** - Manages customers, gadgets, creates repairs, reassigns technicians
3. **Staff** - Views all repairs, manages system, creates receipts
4. **Superuser** - Has all access, can delete anything

---



## Setup Instructions

### 1. Run Management Command to Create Groups

```bash
python manage.py create_groups
```

This creates 3 groups with all permissions automatically assigned:
- `Technician`
- `Secretary`
- `Staff`

### 2. Assign Users to Groups

Go to **Django Admin** → **Users** → Select a user:

```
1. Click on the user
2. Scroll to "Groups" section
3. Check the appropriate group(s):
   - Technician
   - Secretary
   - Staff
4. Click Save
```

The user will immediately have all permissions for that group!

---

## Permissions Matrix

| Feature | Permission | Technician | Secretary | Staff | Superuser |
|---------|-----------|---|---|---|---|
| **Customer** | | | | | |
| - Create | `add_customer` | ❌ | ✅ | ✅ | ✅ |
| - View | `view_customer` | ❌ | ✅ | ✅ | ✅ |
| - Update | `change_customer` | ❌ | ✅ | ✅ | ✅ |
| - Delete | `delete_customer` | ❌ | ❌ | ❌ | ✅ |
| **Gadget** | | | | | |
| - Create | `add_gadget` | ❌ | ✅ | ✅ | ✅ |
| - View | `view_gadget` | ✅ | ✅ | ✅ | ✅ |
| - Update | `change_gadget` | ❌ | ✅ | ✅ | ✅ |
| - Delete | `delete_gadget` | ❌ | ❌ | ❌ | ✅ |
| **Repair Transaction** | | | | | |
| - Create | `add_gadgetrepairtransaction` | ❌ | ✅ | ✅ | ✅ |
| - View All | `view_gadgetrepairtransaction` | ⚠️ (own only) | ✅ | ✅ | ✅ |
| - View Own | (Technician only) | ✅ | - | - | - |
| - Update | `change_gadgetrepairtransaction` | ❌ | ✅ | ✅ | ✅ |
| **Repair Log** | | | | | |
| - Create | `add_gadgetrepairlog` | ✅ | ✅ | ❌ | ✅ |
| - View | `view_gadgetrepairlog` | ✅ | ✅ | ✅ | ✅ |
| - Update | `change_gadgetrepairlog` | ✅ (own only) | ✅ | ✅ | ✅ |
| - Delete | `delete_gadgetrepairlog` | ❌ | ❌ | ❌ | ✅ |
| **Receipt** | | | | | |
| - Create | `add_gadgettransactionreceipt` | ❌ | ✅ | ❌ | ✅ |
| - View | `view_gadgettransactionreceipt` | ❌ | ✅ | ✅ | ✅ |

**Legend:** ✅ = Can access | ❌ = Cannot access | ⚠️ = Limited access | `-` = N/A

---

## Role Descriptions

### TECHNICIAN
**Can:**
- View assigned gadgets and their details
- View assigned repair transactions (only their own)
- Create repair logs for their assigned repairs
- Update repair logs they created
- View repair statistics for their own repairs

**Cannot:**
- Create customers or gadgets
- Create repair transactions
- Delete anything
- View other technicians' repairs
- Create receipts

**Use Case:** Person who physically repairs phones

---

### SECRETARY
**Can:**
- Create and view customers
- Update customer details
- Create and view gadgets
- Update gadget details
- Create repair transactions
- Reassign technicians
- Create receipts
- View repair transaction details

**Cannot:**
- Delete customers or gadgets
- Create repair logs (only technician can)
- Delete anything

**Use Case:** Front desk staff who manages customers and repair assignments

---

### STAFF
**Can:**
- View all customers and gadgets
- Create and update customers and gadgets
- View ALL repair transactions with statistics:
  - Total repairs
  - Pending count
  - In progress count
  - Completed count
- View which technician is assigned to each repair
- Update repair status
- Update and view repair logs
- Create receipts
- View all receipts
- Reassign technicians

**Cannot:**
- Create repair logs directly (only view/update)
- Delete anything

**Use Case:** Manager who oversees all repairs and business operations

---

### SUPERUSER
**Can do EVERYTHING:**
- All CRUD operations on all models
- Access Django Admin
- Manage users and permissions
- Delete anything
- Override any permission check

**Use Case:** System administrator

---

## How Permissions Work in Views

### View-Level Control

```python
# Only users with 'add_customer' permission can access
@permission_required_or_superuser('repair_shop.add_customer')
def create_customer(request):
    ...

# Only superuser can delete
@login_required
def delete_customer(request, customer_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to delete')
        return redirect('customer_list')
    ...

# Technician can only access their own repairs
@permission_required_or_superuser('repair_shop.add_gadgetrepairlog')
def add_repair_log(request, transaction_id):
    transaction = get_object_or_404(GadgetRepairTransaction, id=transaction_id)
    
    if not request.user.is_superuser and transaction.technician != request.user:
        messages.error(request, 'You can only add logs to your assigned repairs')
        return redirect('my_assigned_repairs')
    ...
```

---

## How Permissions Work in Templates

### Show/Hide UI Elements Based on Permissions

```html
<!-- Only show "Delete" button for superuser -->
{% if user.is_superuser %}
    <a href="{% url 'delete_customer' customer.id %}" class="btn btn-danger">
        Delete Customer
    </a>
{% endif %}

<!-- Show "Create Customer" if user has permission -->
{% if user.has_perm 'repair_shop.add_customer' %}
    <a href="{% url 'create_customer' %}" class="btn btn-primary">
        Add Customer
    </a>
{% endif %}

<!-- Show "Create Receipt" only for staff -->
{% if user.has_perm 'repair_shop.add_gadgettransactionreceipt' %}
    <a href="{% url 'create_transaction_receipt' transaction.id %}" class="btn btn-success">
        Create Receipt
    </a>
{% endif %}

<!-- Show repair statistics for staff -->
{% if user.is_staff or user.is_superuser %}
    <div class="stats">
        <p>Pending: {{ stats.pending }}</p>
        <p>In Progress: {{ stats.in_progress }}</p>
        <p>Completed: {{ stats.completed }}</p>
    </div>
{% endif %}
```

---

## Django Admin

Go to `/admin/` with superuser account to:

1. **Create new users** - Auth → Users → Add User
2. **Assign groups** - Select user → Groups → Check role(s) → Save
3. **View permissions** - Auth → Groups → View each group's permissions
4. **Add custom permissions** - (Advanced) Auth → Permissions → Add permission

---

## Troubleshooting

### User can't access a view
1. Check if user is assigned to a group
2. Check if group has the required permission
3. Verify permission name in decorator matches actual permission
4. Check Django Admin → Users → Groups

### Permission doesn't show in Django Admin
1. Run `python manage.py migrate` to create permissions
2. Re-run `python manage.py create_groups`
3. Restart Django server

### Need to add a new permission
1. Edit the model class
2. Add `permissions` in Meta class:
   ```python
   class Meta:
       permissions = [
           ('custom_perm', 'Can do something custom'),
       ]
   ```
3. Run `python manage.py makemigrations` and `python manage.py migrate`
4. Add permission to group in management command

---

## Quick Reference: Permission Codes

```

repair_shop.add_customer
repair_shop.change_customer
repair_shop.delete_customer
repair_shop.view_customer

repair_shop.add_gadget
repair_shop.change_gadget
repair_shop.delete_gadget
repair_shop.view_gadget

repair_shop.add_gadgetrepairtransaction
repair_shop.change_gadgetrepairtransaction
repair_shop.delete_gadgetrepairtransaction
repair_shop.view_gadgetrepairtransaction

repair_shop.add_gadgetrepairlog
repair_shop.change_gadgetrepairlog
repair_shop.delete_gadgetrepairlog
repair_shop.view_gadgetrepairlog

repair_shop.add_gadgettransactionreceipt
repair_shop.change_gadgettransactionreceipt
repair_shop.delete_gadgettransactionreceipt
repair_shop.view_gadgettransactionreceipt
```

---

## Example Workflow

### A Technician's Day:

1. Login with technician account
2. Go to "My Repairs" 
3. See only repairs assigned to them
4. Click on a repair to view details
5. Add new repair log (cost, issue, resolution)
6. Update existing log if they found new issue
7. Cannot create receipt or delete logs

### A Secretary's Day:

1. Login with secretary account
2. Create new customer entry
3. Register new gadget for customer
4. Create repair transaction and assign technician
5. If issue, reassign technician
6. Cannot delete anything, only create and update

### A Staff Manager's Day:

1. Login with staff account
2. View all repairs with statistics
3. See how many are pending, in progress, completed
4. View which technician is on each job
5. Create receipts when repair done
6. Update repair status to completed
7. View all receipts issued

---

## Best Practices

✅ **DO:**
- Always assign users to appropriate groups
- Use decorators on views for protection
- Check permissions in templates
- Let superuser override permissions
- Log permission denials for audit

❌ **DON'T:**
- Give all users superuser access
- Rely only on template permission checks
- Change permission names without updating code
- Allow technician to delete their logs
- Allow secretary to create repair logs

---

## Support

If you encounter issues:
1. Check this guide first
2. Run `python manage.py create_groups` to reset
3. Verify user is in correct group in Django Admin
4. Check view decorator matches actual permission
5. Contact developer if problem persists



# Tech CRM - Quick Start Guide

## 🚀 Getting Started

### 1. Activate Virtual Environment
```bash
cd /home/ai/Desktop/tech_crm
source venv/bin/activate
```

### 2. Set Up User Roles & Permissions
```bash
# Create user groups with permissions
python manage.py create_groups
```

### 3. Create Superuser (if not already created)
```bash
python manage.py createsuperuser --first-name Admin --last-name User
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### 6. Start Development Server
```bash
python manage.py runserver
```

### 7. Access the Application
- **URL:** `http://127.0.0.1:8000/`
- **Admin Panel:** `http://127.0.0.1:8000/admin/`

---

## 👥 Creating Test Users

After running `create_groups`, create users with different roles:

### Via Django Admin
1. Go to `/admin/`
2. Click "Add User"
3. Fill in username, first name, last name, password
4. Click "Save"
5. In the user detail page:
   - Set appropriate flags:
     - **is_staff**: For staff members (can view pending repairs)
     - **is_secretary**: For secretaries (can manage customers and gadgets)
     - **is_technician**: For technicians (can view and add repair logs)
   - Assign to appropriate group (Technician, Secretary, Staff)

### Via Management Command (Option)
```bash
# You could create a management command for bulk user creation
python manage.py create_users
```

---

## 📊 User Roles & Permissions

### Technician
- **Permissions:**
  - View assigned repairs only
  - Add repair logs to assigned repairs
  - Update repair logs
  - View gadget details
- **Access:** `/repairs/my-repairs/` (personal dashboard)

### Secretary
- **Permissions:**
  - Create and edit customers
  - Register and edit gadgets
  - Create repair transactions
  - Assign technicians
  - Create receipts
  - Cannot delete items
- **Access:** Full customer and gadget management

### Staff
- **Permissions:**
  - All secretary permissions
  - View all repairs and pending status
  - Reassign technicians
  - Cannot create repair logs
- **Access:** Repair transaction management without repair logs

### Superuser
- **Permissions:** Full access to all features
- **Access:** Full admin capabilities

---

## 📱 How to Use the System

### 1. Register a Customer
1. Go to **Customers** → **Add Customer**
2. Fill in customer details (name, phone, email)
3. Click **Create Customer**
4. View customer's profile and gadgets

### 2. Register a Gadget
1. Go to **Gadgets** → **Register New Gadget**
2. Select the customer
3. Enter device type, brand, model, IMEI
4. Add optional specs (color, storage, RAM)
5. Click **Register Gadget**

### 3. Create a Repair Transaction
1. Go to **Repairs** → **New Repair**
2. Select the gadget from the dropdown
3. Assign a technician
4. Set initial status (usually "Pending")
5. Click **Create Transaction**
   - **Transaction code auto-generates**

### 4. Add Repair Logs
1. Open the repair transaction
2. Click **Add Log**
3. Enter:
   - Repair cost
   - Issue description
   - Resolution description
4. Click **Add Log**
   - **Repair date auto-fills to today**
   - **Technician auto-fills from transaction**

### 5. Update Repair Status
1. Open the repair transaction
2. Click **Edit**
3. Change the status to "In Progress" or "Completed"
4. Click **Update Transaction**

### 6. Reassign Technician
1. Open the repair transaction
2. Click **Reassign**
3. Select new technician
4. Click **Reassign Technician**
   - Cannot reassign completed repairs

### 7. Create Receipt
1. Open completed repair transaction
2. Click **Create Receipt**
3. Enter amount paid (must match total cost)
4. Click **Create Receipt**
   - **Receipt number auto-generates**

### 8. View Receipt
1. Go to **Receipts**
2. Click on receipt
3. Use **Print** button for printing
   - Print-optimized format included

---

## 🔍 Search Features

### Customer Search
- Search by name, phone, email

### Gadget Search
- Search by brand, model, IMEI, customer name

### Repair Transaction Search
- Search by transaction code, device brand/model, technician, customer

### Receipt Search
- Search by receipt number, transaction code, customer, device brand

---

## 📋 Dashboard Overview

### Home Page
- Shows different content based on user role
- Technician: Shows recent 5 assigned repairs
- Staff/Admin: Quick access to all sections

### Repair Statistics
- **Total Repairs**: Count of all repairs
- **Pending**: Not started
- **In Progress**: Currently being worked on
- **Completed**: Finished repairs

---

## 🐛 Troubleshooting

### 404 Errors
- Clear browser cache (Ctrl+Shift+Delete)
- Restart Django server
- Verify URLs are namespaced correctly

### Permission Denied
- Check user roles in admin panel
- Verify group permissions with `create_groups` command
- Ensure user is assigned to correct group

### Form Not Submitting
- Check browser console for JavaScript errors
- Verify CSRF token is present
- Check form field validation messages

### Static Files Not Loading
- Run `python manage.py collectstatic --noinput`
- Clear browser cache
- Restart server

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `repair_shop/models.py` | Database models |
| `repair_shop/views.py` | View functions |
| `repair_shop/forms.py` | Form definitions |
| `repair_shop/service.py` | Business logic |
| `repair_shop/urls.py` | URL routing |
| `repair_shop/decorators.py` | Custom decorators |
| `config/settings.py` | Django settings |
| `repair_shop/templates/` | HTML templates |
| `repair_shop/static/css/style.css` | Styling |

---

## 💡 Tips & Tricks

1. **Quick Navigation:** Use the sidebar menu for main sections
2. **Bulk Edits:** Use the Django admin for bulk operations
3. **Technician Workload:** Check "My Assigned Repairs" for pending tasks
4. **Receipt Printing:** Use browser print dialog (Ctrl+P) for receipts
5. **Search Tips:** Use partial names or numbers for broader searches

---

## 🔗 Important URLs

| Page | URL |
|------|-----|
| Home | `/` |
| Login | `/login/` |
| Customers | `/customers/` |
| Gadgets | `/gadgets/` |
| Repairs | `/repairs/` |
| My Repairs (Tech) | `/repairs/my-repairs/` |
| Receipts | `/receipts/` |
| Admin | `/admin/` |

---

## 🎯 Next Steps

1. Test each page with different user roles
2. Create sample data
3. Test search functionality
4. Verify permission restrictions
5. Test receipt printing
6. Customize branding as needed
7. Deploy to production

---

## 📞 Support

For issues or questions:
1. Check the detailed documentation in `PAGES_SUMMARY.md`
2. Review model structure in `SETUP_COMPLETE.md`
3. Check permission setup in `PERMISSIONS_GUIDE.md`

---

**System is ready to use! 🎉**



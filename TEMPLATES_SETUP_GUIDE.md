# Template Setup Guide - Tech CRM

## ✅ Setup Complete!

You now have a complete Bootstrap 5 template system set up. Here's what was created:

---

## Directory Structure Created

```
repair_shop/
├── templates/
│   └── repair_shop/
│       ├── base.html              ✅ Main layout with navbar & sidebar
│       ├── home.html              ✅ Home/redirect page
│       └── login.html             ✅ Login page
└── static/
    ├── css/
    ├── js/
    └── images/
```

---

## Files Modified

### 1. `config/settings.py`
✅ Updated with:
- Template directory configuration
- Static files configuration
- Login redirect settings

**Changes:**
```python
TEMPLATES['DIRS'] = [BASE_DIR / 'repair_shop' / 'templates']
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'repair_shop' / 'static']
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'
```

---

## Bootstrap 5 Installation

✅ **Using CDN** (No pip install needed)

- **CSS:** `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css`
- **JS:** `https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js`
- **Icons:** `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css`

All included in `base.html` - ready to use!

---

## Template Files Overview

### 1. `base.html` - Main Layout
**Features:**
- ✅ Responsive navbar with logo and user info
- ✅ Collapsible sidebar with role-based menu items
- ✅ Auto-hiding alert messages
- ✅ Professional gradient colors
- ✅ Mobile responsive design
- ✅ Footer

**Sidebar Sections:**
- Dashboard (for all users)
- Customers (if has permission)
- Gadgets (if has permission)
- Repairs (different view for technicians vs staff)
- Receipts (if has permission)
- Admin (superuser only)

### 2. `login.html` - Login Page
**Features:**
- ✅ Beautiful gradient background
- ✅ Centered login form
- ✅ Email/Username field
- ✅ Password field
- ✅ Remember me checkbox
- ✅ Error message display
- ✅ Demo credentials display
- ✅ Fully responsive

### 3. `home.html` - Home/Redirect Page
**Purpose:** 
- Redirects users to their appropriate dashboard based on role

---

## How the Template System Works

### Extending Base Template
All pages extend `base.html`:

```html
{% extends 'repair_shop/base.html' %}

{% block title %}Your Page Title{% endblock %}

{% block content %}
    <!-- Your page content here -->
{% endblock %}
```

### Block System
- `{% block title %}` - Page title in browser tab
- `{% block content %}` - Main page content
- `{% block extra_css %}` - Additional CSS per page
- `{% block extra_js %}` - Additional JavaScript per page

---

## URL Routes Needed (Add to `urls.py`)

```python
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='repair_shop/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Home
    path('', views.home, name='home'),
    
    # ... rest of your URLs ...
]
```

---

## Bootstrap 5 Features Available

### Pre-built Components
- ✅ Navbar & Navbars
- ✅ Sidebar/Off-canvas
- ✅ Cards
- ✅ Tables
- ✅ Forms & Form Groups
- ✅ Buttons
- ✅ Alerts
- ✅ Badges
- ✅ Modals
- ✅ Dropdowns
- ✅ Tooltips
- ✅ Pagination
- ✅ Breadcrumbs
- ✅ And more!

### Bootstrap Icons Available
- `bi bi-speedometer2` - Dashboard
- `bi bi-people` - Customers
- `bi bi-phone` - Gadgets
- `bi bi-wrench` - Repairs
- `bi bi-receipt` - Receipts
- `bi bi-plus-circle` - Add
- `bi bi-pencil` - Edit
- `bi bi-trash` - Delete
- `bi bi-eye` - View
- And 100s more!

See: https://icons.getbootstrap.com/

---

## Color Scheme

The system uses a professional gradient color scheme:

| Color | Usage |
|-------|-------|
| `#667eea` - `#764ba2` | Primary gradient (Navbar, buttons) |
| `#2c3e50` | Sidebar background |
| `#ecf0f1` | Sidebar text |
| `#f8f9fa` | Background |
| `#e9ecef` | Borders |

You can customize these in the `:root` CSS variables in `base.html`

---

## Creating New Templates

### Step 1: Create Template File
```bash
touch repair_shop/templates/repair_shop/customers/customer_list.html
```

### Step 2: Extend Base
```html
{% extends 'repair_shop/base.html' %}

{% block title %}Customer List{% endblock %}

{% block content %}
<div class="page-header">
    <h1><i class="bi bi-people"></i> Customers</h1>
    <a href="{% url 'create_customer' %}" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> Add Customer
    </a>
</div>

<div class="card">
    <div class="card-body">
        <table class="table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for customer in customers %}
                <tr>
                    <td>{{ customer.first_name }} {{ customer.last_name }}</td>
                    <td>{{ customer.email }}</td>
                    <td>{{ customer.phone_number }}</td>
                    <td>
                        <a href="{% url 'customer_detail' customer.id %}" class="btn btn-sm btn-info">
                            <i class="bi bi-eye"></i> View
                        </a>
                        <a href="{% url 'update_customer' customer.id %}" class="btn btn-sm btn-warning">
                            <i class="bi bi-pencil"></i> Edit
                        </a>
                        {% if user.is_superuser %}
                        <a href="{% url 'delete_customer' customer.id %}" class="btn btn-sm btn-danger">
                            <i class="bi bi-trash"></i> Delete
                        </a>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
```

---

## Common Bootstrap Classes

### Spacing
- `m-1` to `m-5` - Margin
- `p-1` to `p-5` - Padding
- `ms-auto` - Margin-left auto
- `gap-3` - Gap between flexbox items

### Text
- `text-center` - Center text
- `text-white` - White text
- `text-danger` - Red text
- `text-muted` - Gray text
- `fw-bold` - Bold text
- `fs-4` - Font size 4

### Display
- `d-flex` - Flexbox
- `d-grid` - Grid
- `d-none` - Hide
- `d-block` - Display block
- `align-items-center` - Vertical center
- `justify-content-between` - Space between

### Grid
- `row` - Grid row
- `col` - Grid column
- `col-md-6` - 50% width on medium screens
- `col-lg-4` - 33% width on large screens

---

## Testing the Setup

### 1. Run migrations (if needed)
```bash
python manage.py migrate
```

### 2. Create groups
```bash
python manage.py create_groups
```

### 3. Create test user (optional)
```bash
python manage.py createsuperuser
```

### 4. Run server
```bash
python manage.py runserver
```

### 5. Visit
- Login: `http://localhost:8000/admin/login/`
- Home: `http://localhost:8000/`

---

## Next Steps

1. ✅ Create dashboard templates for each role
2. ✅ Create CRUD templates (List, Create, Edit, Detail)
3. ✅ Add custom CSS for branding
4. ✅ Add charts/graphs if needed
5. ✅ Test with different user roles

---

## Troubleshooting

### Templates not found
- Check: `TEMPLATES['DIRS']` in `settings.py`
- Ensure directory structure matches

### Bootstrap not loading
- Check browser console for CDN errors
- Ensure internet connection
- Use alternative CDN if needed

### Static files not loading
- Run: `python manage.py collectstatic`
- Check: `STATICFILES_DIRS` in `settings.py`

### Sidebar not showing
- Check: User permissions are set correctly
- Verify: `{% if user.has_perm %}` conditions

---

## Resources

- **Bootstrap Docs:** https://getbootstrap.com/docs/5.3/
- **Bootstrap Icons:** https://icons.getbootstrap.com/
- **Django Templates:** https://docs.djangoproject.com/en/4.2/topics/templates/

---

## You're All Set! 🎉

Your template system is ready to use. Now you can:
1. Create dashboard templates
2. Create CRUD pages
3. Add custom styling
4. Deploy!

Need help creating specific templates? Let me know!


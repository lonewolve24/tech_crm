from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import MyUser, Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt
from .forms import CustomerForm, GadgetForm

# ============================================
# User Creation Form (for Add User)
# ============================================
class MyUserCreationForm(forms.ModelForm):
    """Form for creating a new user with password hashing"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Enter a strong password'
    )
    password2 = forms.CharField(
        label='Password Confirmation',
        widget=forms.PasswordInput,
        help_text='Enter the same password for verification'
    )

    class Meta:
        model = MyUser
        fields = ('email', 'username', 'first_name', 'last_name')

    def clean_password2(self):
        """Verify both passwords match"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        """Hash the password before saving"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

# ============================================
# User Change Form (for Edit User)
# ============================================
class MyUserChangeForm(forms.ModelForm):
    """Form for editing an existing user"""
    password = ReadOnlyPasswordHashField(
        label='Password',
        help_text='Passwords are not stored in plain text. Click <a href=\"../password/\">here</a> to change the password.'
    )

    class Meta:
        model = MyUser
        fields = ('email', 'username', 'first_name', 'last_name', 'password', 'is_active', 'is_admin', 'is_staff', 'is_superuser', 'is_technician', 'is_secretary')

    def clean_password(self):
        """Password field is read-only"""
        return self.initial.get('password')

# ============================================
# Custom User Admin with Password Handling
# ============================================
class MyUserAdmin(admin.ModelAdmin):
    """Custom User Admin with proper password field handling"""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_technician', 'is_secretary', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_technician', 'is_secretary')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('email',)
    
    # Fieldsets for EDITING an existing user (password hidden)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Role Flags', {
            'fields': (
                'is_technician',
                'is_secretary',
                'is_staff',
            ),
            'description': 'Check the appropriate role for this user'
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_admin',
                'is_superuser',
            )
        }),
        ('Important Dates', {'fields': ('last_login',)}),
    )
    
    # Fieldsets for ADDING a new user (includes password fields with hashing)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Role Flags', {
            'fields': (
                'is_technician',
                'is_secretary',
                'is_staff',
            ),
            'description': 'Check the appropriate role for this user'
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """Use add_fieldsets when creating a new user"""
        if obj is None:  # Adding a new object
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        """Use MyUserCreationForm when adding, MyUserChangeForm when editing"""
        if obj is None:  # Adding a new object
            form = MyUserCreationForm
        else:  # Editing an existing object
            form = MyUserChangeForm
        kwargs['form'] = form
        return super().get_form(request, obj, **kwargs)

# ============================================
# Register Models
# ============================================
admin.site.register(MyUser, MyUserAdmin)  # ✅ USE CUSTOM ADMIN
admin.site.register(Customer)
admin.site.register(Gadget)
admin.site.register(GadgetRepairLog)
admin.site.register(GadgetRepairTransaction)

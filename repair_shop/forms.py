from pyexpat import model
from django import forms
from .models import Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt, MyUser, Payment
from django.forms import ModelForm
from django.utils.translation import gettext as _


# ============================================
# USER MANAGEMENT FORMS
# ============================================

class UserCreationForm(ModelForm):
    """Form for creating new users"""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password',
            'required': True,
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True,
        })
    )

    class Meta:
        model = MyUser
        fields = ['email', 'username', 'first_name', 'last_name', 'is_technician', 'is_secretary', 'is_staff']
        labels = {
            'email': _('Email Address'),
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'is_technician': _('Is Technician?'),
            'is_secretary': _('Is Secretary?'),
            'is_staff': _('Is Staff/Manager?'),
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'user@example.com',
                'required': True,
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique username',
                'required': True,
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John',
                'required': True,
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doe',
                'required': True,
            }),
            'is_technician': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_secretary': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('Passwords do not match'))
        
        if password1 and len(password1) < 6:
            raise forms.ValidationError(_('Password must be at least 6 characters'))
        
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.is_active = True
        if commit:
            user.save()
        return user


class UserEditForm(ModelForm):
    """Form for editing existing users (without password)"""
    
    class Meta:
        model = MyUser
        fields = ['email', 'username', 'first_name', 'last_name', 'is_technician', 'is_secretary', 'is_staff', 'is_active']
        labels = {
            'email': _('Email Address'),
            'username': _('Username'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'is_technician': _('Is Technician?'),
            'is_secretary': _('Is Secretary?'),
            'is_staff': _('Is Staff/Manager?'),
            'is_active': _('Is Active?'),
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'user@example.com',
            }),
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doe',
            }),
            'is_technician': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_secretary': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }


class UserProfileForm(ModelForm):
    """Form for users to edit their own profile"""
    
    class Meta:
        model = MyUser
        fields = ['email', 'first_name', 'last_name']
        labels = {
            'email': _('Email Address'),
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'user@example.com',
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doe',
            }),
        }


class UserPasswordChangeForm(forms.Form):
    """Form for changing user password"""
    current_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter current password',
            'required': True,
        })
    )
    new_password = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password',
            'required': True,
        })
    )
    confirm_password = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password',
            'required': True,
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not self.user.check_password(current_password):
            raise forms.ValidationError(_('Current password is incorrect'))
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError(_('New passwords do not match'))
        
        if new_password and len(new_password) < 6:
            raise forms.ValidationError(_('Password must be at least 6 characters'))
        
        return cleaned_data


# ============================================

class CustomerForm(ModelForm):
    class Meta:
        model = Customer
        fields = [
            "first_name", 
            "last_name", 
            "email",
            "phone_number",
            "address",
            "id_number",
            "id_type"
            
        ]
        labels = {
            "first_name": _("Customer First Name"),
            "last_name": _("Customer Last Name"),
            "email": _("Customer Email "),
            "phone_number":_("Phone Number"),
            "address": _("Customer  Address"),
            "id_number":_("Cutomer ID Number "),
            "id_type":_(" Select ID Type")    
        }


        widgets = {
            "first_name": forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'John',
                'required': True,
                'autocomplete': 'given-name',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Doe',
                'maxlength': '30',
                'required': True,
                'autocomplete': 'family-name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'john@example.com',
                'autocomplete': 'email',
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+220 123 4567',
                'autocomplete': 'tel',
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter complete address',
                'autocomplete': 'street-address',
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique ID number',
                'autocomplete': 'off',
            }),
            'id_type': forms.Select(attrs={
                'class': 'form-select',
            })
        }

        error_messages = {

            "email":{
            "unique":"This email address is already registered."
            },
            "phone_number":{
                "unique":_("This phone number already exists. Please provide your personal phone number.")
            },
            "id_number":{
                "unique":_("tThis ID number already exists. Please enter a different ID number.")
            }
        }

class GadgetForm(ModelForm):

    class Meta:
        model = Gadget
        fields = [
                                    
                   "customer",
                    "gadget_type",
                    "gadget_brand",
                    "gadget_model",
                    "imei_number",
                    "serial_number"
                                ]
        

        labels = {

            "customer": _("Select Customer"),
            "gadget_type": _("Select Gadget Type"),
            "gadget_brand": _("Enter Gadget Brand"),
            "gadget_model":_("Gadget Model"),
            "imei_number": _("Enter Unique IMEI number"),
            "serial_number": _("Enter Unique Serial Number")
        }

        widgets = {
            'customer': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'gadget_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'gadget_brand': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Samsung, Apple, Huawei, etc.',
                'required': True,
            }),
            'gadget_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Galaxy S21, iPhone 13, P30 Pro, etc.',
                'required': True,
            }),
            'imei_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '15-digit IMEI number',
                'maxlength': '15',
                'pattern': '[0-9]{15}',
            }),
            'serial_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unique device serial number',
            })
        }

        error_messages = {

            "imei_number":{
                "unique":_("IMEI number already exist this phone is in our database")
            },
            "serial_number":{
                "unique":_("Serial number already exist this phone is in our database ")
            }

        }

class GadgetRepairTransactionForm(ModelForm):
    # Add customer field (not in model, just for filtering gadgets)
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.all().order_by('first_name', 'last_name'),
        required=False,
        label=_("Select Customer"),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_customer_filter',
        }),
        help_text=_("Select a customer first to see their gadgets")
    )

    class Meta:
        model = GadgetRepairTransaction
        fields = ['gadget', 'technician', 'status']
        labels = {
            'gadget': _("Select Gadget"),
            'technician': _("Assign Technician"),
            'status': _("Select Status")
        }
        widgets = {
            'gadget': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_gadget',
            }), 
            'technician': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
            'status': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
        }
        error_messages = {
            'gadget': {
                'required': _("Please select a gadget for the repair transaction.")
            },
            'technician': {
                'required': _("Please assign a technician to the repair transaction.")
            },
            'status': {
                'required': _("Please select a status for the repair transaction." )
            }
        }

    def __init__(self, *args, **kwargs):
        customer_id = kwargs.pop('customer_id', None)
        gadget_id = kwargs.pop('gadget_id', None)
        super().__init__(*args, **kwargs)
        
        # Set initial customer if provided
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                self.fields['customer'].initial = customer
                # Filter gadgets to this customer's gadgets
                self.fields['gadget'].queryset = Gadget.objects.filter(
                    customer=customer
                ).order_by('gadget_brand', 'gadget_model')
            except Customer.DoesNotExist:
                pass
        
        # Set initial gadget if provided (from URL param)
        if gadget_id:
            try:
                gadget = Gadget.objects.get(id=gadget_id)
                self.fields['gadget'].initial = gadget
                # Also set customer to match the gadget's customer
                if gadget.customer:
                    self.fields['customer'].initial = gadget.customer
                    self.fields['gadget'].queryset = Gadget.objects.filter(
                        customer=gadget.customer
                    ).order_by('gadget_brand', 'gadget_model')
            except Gadget.DoesNotExist:
                pass
        
        # If no customer/gadget provided, show all gadgets (backward compatibility)
        if not customer_id and not gadget_id:
            self.fields['gadget'].queryset = Gadget.objects.all().order_by(
                'customer__first_name', 'customer__last_name', 'gadget_brand', 'gadget_model'
            )

    def clean(self):
        cleaned_data = super().clean()
        gadget = self.cleaned_data.get('gadget')
        technician = self.cleaned_data.get('technician')
        customer = self.cleaned_data.get('customer')
        
        if not gadget:
            raise forms.ValidationError(_("Please select a gadget for the repair transaction."))

        if not technician:
            raise forms.ValidationError(_("Please Assign a Technician to the repair transaction"))
        
        # Validate that selected gadget belongs to selected customer (if customer was selected)
        if customer and gadget.customer != customer:
            raise forms.ValidationError(
                _("The selected gadget does not belong to the selected customer.")
            )
        
        # Only check for active repairs when CREATING a new repair (not when editing)
        # self.instance.pk is None when creating, has a value when editing
        if self.instance.pk is None:  # Only for new repairs
            active_repairs = GadgetRepairTransaction.objects.filter(
                gadget=gadget,
                status__in=['Pending', 'In Progress']
            )
            if active_repairs.exists():
                raise forms.ValidationError(
                    "This gadget already has an active repair."
                )
        
        return cleaned_data

class GadgetRepairLogForm(ModelForm):
    class Meta:
        model = GadgetRepairLog
        fields = [ 'repair_cost', 'issue_description', 'resolution_description']
        labels = {
            'repair_cost': _("Repair Cost (D)"),
            'issue_description': _("Issue Description"),
            'resolution_description': _("Resolution Description")
        }
        widgets = {
            'repair_cost': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': '1000', 
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
            'issue_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the issue with the gadget',
                'required': True,
            }),
            'resolution_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe the resolution applied',
                'required': True,
            }),
        }
        error_messages = {
            'repair_cost': {
                'required': _("Please enter the repair cost.")
            },
        }

    def clean_repair_cost(self):

        repair_cost = self.cleaned_data.get('repair_cost')
        if repair_cost <= 0:
            raise forms.ValidationError(_("Repair cost must be greater than 0"))
        return repair_cost


class ReassignTechnicianForm(ModelForm):

    class Meta:
        model = GadgetRepairTransaction
        fields = ['technician']
        labels = {
            'technician': _("Assign Technician")
        }
        widgets = {
            'technician': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
            }),
        }
        error_messages = {
            'technician': {
                'required': _("Please assign a technician to the repair transaction.")
            }
        }
    
    def clean_technician(self):
        technician = self.cleaned_data.get('technician')
        if not technician:
            raise forms.ValidationError(_("Please assign a technician to the repair transaction."))
        return technician


class GadgetTransactionReceiptForm(ModelForm):
    """
    Form for creating a transaction receipt.
    Only asks for amount paid - transaction validation done in view/service.
    """

    class Meta:
        model = GadgetTransactionReceipt
        fields = ['amount_paid']
        labels = {
            'amount_paid': _("Amount Paid (D)"),
        }
        widgets = {
            'amount_paid': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '1000',
                'step': '0.01',
                'min': '0',
                'required': True,
            }),
        }
        error_messages = {
            'amount_paid': {
                'required': _("Please enter the amount paid."),
            },
        }
    
    def clean_amount_paid(self):
        """Validate amount is positive"""
        amount_paid = self.cleaned_data.get('amount_paid')
        
        if amount_paid and amount_paid <= 0:
            raise forms.ValidationError(_("Amount must be greater than 0"))
        
        return amount_paid


class PaymentForm(ModelForm):
    """Form for recording a payment (cash or mobile money) against a repair."""

    class Meta:
        model = Payment
        fields = ['payment_type', 'amount', 'mobile_provider', 'mobile_number', 'notes']
        labels = {
            'payment_type': _('Payment Method'),
            'amount': _('Amount Paid (D)'),
            'mobile_provider': _('Mobile Provider'),
            'mobile_number': _('Mobile Number / Account'),
            'notes': _('Notes (optional)'),
        }
        widgets = {
            'payment_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_payment_type',
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
                'required': True,
            }),
            'mobile_provider': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Africell, QMoney, Wave',
            }),
            'mobile_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sender phone or account number',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional notes about this payment',
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError(_("Amount must be greater than 0."))
        return amount

    def clean(self):
        cleaned_data = super().clean()
        payment_type = cleaned_data.get('payment_type')
        mobile_number = cleaned_data.get('mobile_number', '').strip()
        if payment_type == Payment.MOBILE_MONEY and not mobile_number:
            self.add_error('mobile_number', _("Mobile number is required for Mobile Money payments."))
        return cleaned_data
    

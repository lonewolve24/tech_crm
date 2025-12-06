from pyexpat import model
from django import forms
from .models import Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt,MyUser
from django.forms import ModelForm
from django.utils.translation import gettext as _



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
    def clean(self):
        cleaned_data = super().clean()
        gadget = self.cleaned_data.get('gadget')
        technician = self.cleaned_data.get('technician')
        if not gadget:
            raise forms.ValidationError(_("Please select a gadget for the repair transaction."))

        if not technician:
            raise forms.ValidationError(_("Please Assign a Technician to the repair transaction"))
        
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
            'amount_paid': _("Amount Paid (₵)"),
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
    

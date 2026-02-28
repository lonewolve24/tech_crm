
import uuid
import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser , BaseUserManager
import datetime
# Create your models here.


def current_year ():
    return datetime.date.today().year


class CreatedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class MyUserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, **extra_fields)
    def create_technician(self, username, password=None, **extra_fields):
        extra_fields['is_technician'] = True
        return self.create_user(username, password, **extra_fields)

    def create_secretary(self, username, password=None, **extra_fields):
        extra_fields['is_secretary'] = True
        return self.create_user(username, password, **extra_fields)

   

class MyUser(AbstractBaseUser,CreatedModel):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)       # Real field, not property!
    is_superuser = models.BooleanField(default=False)
    is_technician = models.BooleanField(default=False)
    is_secretary = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name']

    def __str__(self):
        return self.username
    
    objects = MyUserManager()

    # Role-based permission sets
    _TECHNICIAN_PERMS = {
        'repair_shop.view_gadget',
        'repair_shop.view_gadgetrepairtransaction',
        'repair_shop.add_gadgetrepairlog',
        'repair_shop.change_gadgetrepairlog',
        'repair_shop.view_gadgetrepairlog',
        'repair_shop.change_gadgetrepairtransaction',
    }

    _SECRETARY_PERMS = {
        'repair_shop.view_customer', 'repair_shop.add_customer', 'repair_shop.change_customer',
        'repair_shop.view_gadget', 'repair_shop.add_gadget', 'repair_shop.change_gadget',
        'repair_shop.view_gadgetrepairtransaction', 'repair_shop.add_gadgetrepairtransaction',
        # Secretary can VIEW logs (to understand what was done) but cannot ADD or EDIT them.
        # Adding/editing repair logs is the technician's responsibility.
        'repair_shop.view_gadgetrepairlog',
        'repair_shop.add_gadgettransactionreceipt', 'repair_shop.view_gadgettransactionreceipt',
        'repair_shop.add_payment', 'repair_shop.view_payment',
        'repair_shop.view_notification',
    }

    _STAFF_PERMS = _SECRETARY_PERMS | {
        'repair_shop.change_gadgetrepairtransaction',
        'repair_shop.change_gadgetrepairlog',
        'repair_shop.delete_customer',
        'repair_shop.delete_gadget',
        'repair_shop.delete_gadgetrepairlog',
        'repair_shop.delete_gadgetrepairtransaction',
        'repair_shop.view_gadgettransactionreceipt',
        'repair_shop.change_gadgettransactionreceipt',
        'repair_shop.change_payment', 'repair_shop.delete_payment',
        'repair_shop.view_notification', 'repair_shop.change_notification',
    }

    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_admin or self.is_superuser:
            return True
        # Role-based permission checking using user flag fields
        if self.is_technician and perm in self._TECHNICIAN_PERMS:
            return True
        if self.is_secretary and perm in self._SECRETARY_PERMS:
            return True
        if self.is_staff and perm in self._STAFF_PERMS:
            return True
        return False

    def has_module_perms(self, app_label):
        if not self.is_active:
            return False
        if self.is_admin or self.is_superuser:
            return True
        if app_label == 'repair_shop':
            return self.is_technician or self.is_secretary or self.is_staff
        return False

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    




class Customer(CreatedModel):


   DRIVERLICENCES ='DL'
   PASSPORT = 'PP'
   NATIONAL_ID = 'NI'
   VOTERSCARD = 'VC'
   OTHER = 'OTHER'
   ID_TYPE_CHOICES = [
       (DRIVERLICENCES, 'Driver\'s License'),
       (PASSPORT, 'Passport'),
       (NATIONAL_ID, 'National ID'),
       (VOTERSCARD, 'Voter\'s Card'),
       (OTHER, 'Other'),
   ]

   first_name = models.CharField(max_length=30)
   last_name = models.CharField(max_length=30)
   email = models.EmailField(unique=True, blank=True, null=True)
   phone_number = models.CharField(max_length=15, blank=True, null=True)
   address = models.TextField(max_length=100,blank=True, null=True)
   id_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
   id_type = models.CharField(
       max_length=6,
       choices=ID_TYPE_CHOICES,
       default=OTHER,
   )

   def __str__(self):
        
        return f"{self.first_name} {self.last_name}"






class Gadget(CreatedModel):
  
   SMARTPHONE = 'SP'
   LAPTOP = 'LT'
   DESKTOP = 'DT'
   TABLET = 'TB'
   OTHER = 'OT'

   Gadget_Type_CHOICES = [
       (SMARTPHONE, 'Smartphone'),
       (LAPTOP, 'Laptop'),
       (DESKTOP, 'Desktop'),
       (TABLET, 'Tablet'),
       (OTHER, 'Other'),
   ]
   customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
   gadget_type = models.CharField(max_length=3, choices=Gadget_Type_CHOICES, default=OTHER)
   gadget_brand = models.CharField(max_length=100)
   gadget_model = models.CharField(max_length=100, null=True, blank=True)
   imei_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
   serial_number = models.CharField(max_length=100, blank=True, null=True)


   def __str__(self):
       customer_name = f"{self.customer.first_name} {self.customer.last_name}"
       return f"{self.gadget_brand} {self.gadget_model} — {customer_name}"
   
   @property
   def has_active_repair(self):
       """Check if gadget has any pending or in-progress repairs"""
       from django.db.models import Q
       return self.gadgetrepairtransaction_set.filter(
           Q(status='Pending') | Q(status='In Progress')
       ).exists()


class GadgetRepairLog( CreatedModel):
   transaction = models.ForeignKey('GadgetRepairTransaction', on_delete=models.CASCADE, related_name='repair_logs')
   repair_date = models.DateTimeField(auto_now_add=True)
   repair_cost = models.DecimalField(max_digits=10, decimal_places=2)
   issue_description = models.TextField(blank=False)
   resolution_description = models.TextField(blank=True, null=True)

   def __str__(self):
       return f"Repair Log for {self.transaction.gadget} on {self.repair_date}"

class GadgetRepairTransaction(CreatedModel):
    PENDING = 'Pending'
    INPROGRESS = 'In Progress'
    COMPLETED = 'Completed'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (INPROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]
      
    gadget = models.ForeignKey('Gadget', on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=PENDING)
    brought_in_date = models.DateTimeField(auto_now_add=True)
    technician = models.ForeignKey(
        'MyUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_repairs',
        limit_choices_to={'is_technician': True}
    )
    code = models.CharField(max_length=100, unique=True)


    def __str__(self):
        return f"Repair Transaction for {self.gadget} -- {self.code}"
    

    class Meta:
        ordering = ['-brought_in_date']
        verbose_name = 'Repair Transaction'
        verbose_name_plural = 'Repair Transactions'

    @property
    def transaction_code(self):
        """Alias for code field for template compatibility"""
        return self.code

    @property
    def total_cost(self):
        return sum(log.repair_cost for log in self.repair_logs.all())

    @property
    def total_paid(self):
        from django.db.models import Sum
        result = self.payments.aggregate(total=Sum('amount'))
        return result['total'] or 0

    @property
    def total_due(self):
        return self.total_cost - self.total_paid

    @property
    def has_price(self):
        """Returns True if at least one repair log (price quote) exists."""
        return self.repair_logs.exists()

    @property
    def is_fully_paid(self):
        """Returns True only if price has been set AND payment is complete."""
        if not self.has_price:
            return False  # Can't be "paid" if no price has been quoted yet
        return self.total_due <= 0
    

    def save (self, *args , **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        return str(uuid.uuid4()).replace('-', '').upper()[:10]

class GadgetTransactionReceipt(models.Model):
    transaction = models.ForeignKey('GadgetRepairTransaction', on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    issued_date = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=100, unique=True)


    def save (self, *args , **kwargs):
        if not self.receipt_number:
            self.receipt_number = self.generate_receipt_number()
        super().save(*args, **kwargs)


    def generate_receipt_number (self):
        count =  self.get_num_receipt() + 1
        return f"REC-{current_year()}-{str(count).zfill(4)}"
    
    def get_num_receipt(self):
        num_receipt = GadgetTransactionReceipt.objects.filter(issued_date__year = current_year()).count()
        return num_receipt


    def __str__(self):
        return f"Receipt for {self.receipt_number}"


class Payment(CreatedModel):
    """Records individual payments (cash or mobile money) against a repair transaction."""
    CASH = 'CASH'
    MOBILE_MONEY = 'MOBILE_MONEY'
    PAYMENT_TYPE_CHOICES = [
        (CASH, 'Cash'),
        (MOBILE_MONEY, 'Mobile Money'),
    ]

    transaction = models.ForeignKey(
        'GadgetRepairTransaction', on_delete=models.CASCADE, related_name='payments'
    )
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default=CASH)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mobile_provider = models.CharField(max_length=100, blank=True, default='',
                                       help_text='e.g. Africell, QMoney (Mobile Money only)')
    mobile_number = models.CharField(max_length=30, blank=True, default='',
                                     help_text='Sender phone/account number')
    notes = models.TextField(blank=True, default='')
    recorded_by = models.ForeignKey(
        'MyUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recorded_payments'
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment D{self.amount} ({self.payment_type}) for {self.transaction.code}"


class Notification(CreatedModel):
    """In-app notifications for technicians (new assignment) and staff (repair completed)."""
    REPAIR_COMPLETED = 'COMPLETED'
    REPAIR_ASSIGNED = 'ASSIGNED'
    PAYMENT_RECEIVED = 'PAYMENT'
    PAYMENT_PENDING = 'PAY_PENDING'
    TYPE_CHOICES = [
        (REPAIR_COMPLETED, 'Repair Completed'),
        (REPAIR_ASSIGNED, 'New Assignment'),
        (PAYMENT_RECEIVED, 'Payment Received'),
        (PAYMENT_PENDING, 'Payment Pending'),
    ]

    recipient = models.ForeignKey(
        'MyUser', on_delete=models.CASCADE, related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    repair = models.ForeignKey(
        'GadgetRepairTransaction', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='notifications'
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] → {self.recipient}: {self.title}"





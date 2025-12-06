
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


    def create_user(self, email, username, password=None):

        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, first_name='', last_name=''):

        user = self.create_user(email, username, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
    def create_technician(self, email, username, password=None):

        user = self.create_user(email, username, password=password)
        user.is_technician = True
        user.save(using=self._db)
        return user

    def create_secretary(self, email, username, password=None):
        user = self.create_user(email, username, password=password)
        user.is_secretary = True
        user.save(using=self._db)
        return user

   

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

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name']

    def __str__(self):
        return self.username
    
    objects = MyUserManager()

    def has_perm(self, perm, obj=None):
        return self.is_admin or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_admin or self.is_superuser

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
       return f"{self.gadget_brand} -- {self.gadget_model}"
   
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





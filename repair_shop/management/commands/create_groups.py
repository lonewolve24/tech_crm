from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from repair_shop.models import (
    Customer, Gadget, GadgetRepairTransaction,
    GadgetRepairLog, GadgetTransactionReceipt
)


class Command(BaseCommand):
    help = 'Create groups and assign permissions for different roles'

    def handle(self, *args, **options):
        # Get content types for all models
        customer_ct = ContentType.objects.get_for_model(Customer)
        gadget_ct = ContentType.objects.get_for_model(Gadget)
        transaction_ct = ContentType.objects.get_for_model(GadgetRepairTransaction)
        log_ct = ContentType.objects.get_for_model(GadgetRepairLog)
        receipt_ct = ContentType.objects.get_for_model(GadgetTransactionReceipt)

        # Create groups
        technician_group, created = Group.objects.get_or_create(name='Technician')
        secretary_group, created = Group.objects.get_or_create(name='Secretary')
        staff_group, created = Group.objects.get_or_create(name='Staff')

        # ========== TECHNICIAN PERMISSIONS ==========
        # Can: View gadget details, create repair logs, update own logs, update repair status
        # Cannot: Delete, create customers, create repairs, reassign technicians, etc.
        technician_perms = Permission.objects.filter(
            codename__in=[
                'view_gadget',
                'view_gadgetrepairtransaction',
                'change_gadgetrepairtransaction',  # Allow technicians to update status
                'add_gadgetrepairlog',
                'change_gadgetrepairlog',
                'view_gadgetrepairlog',
            ]
        )
        technician_group.permissions.set(technician_perms)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Technician group created with {technician_perms.count()} permissions')
        )

        # ========== SECRETARY PERMISSIONS ==========
        # Can: Create/view customer, create/view gadget, create transaction, 
        #      reassign technician, create receipt
        # Cannot: Delete anything
        secretary_perms = Permission.objects.filter(
            codename__in=[
                'add_customer',
                'change_customer',
                'view_customer',
                'add_gadget',
                'change_gadget',
                'view_gadget',
                'add_gadgetrepairtransaction',
                'change_gadgetrepairtransaction',
                'view_gadgetrepairtransaction',
                'add_gadgetrepairlog',
                'add_gadgettransactionreceipt',
                'view_gadgettransactionreceipt',
            ]
        )
        secretary_group.permissions.set(secretary_perms)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Secretary group created with {secretary_perms.count()} permissions')
        )

        # ========== STAFF PERMISSIONS ==========
        # Can: Do everything except delete and cannot create repair logs
        # Can view all repairs, see pending count, see which technician assigned
        staff_perms = Permission.objects.filter(
            codename__in=[
                'add_customer',
                'change_customer',
                'view_customer',
                'add_gadget',
                'change_gadget',
                'view_gadget',
                'add_gadgetrepairtransaction',
                'change_gadgetrepairtransaction',
                'view_gadgetrepairtransaction',
                'change_gadgetrepairlog',
                'view_gadgetrepairlog',
                'add_gadgettransactionreceipt',
                'view_gadgettransactionreceipt',
            ]
        )
        staff_group.permissions.set(staff_perms)
        self.stdout.write(
            self.style.SUCCESS(f'✓ Staff group created with {staff_perms.count()} permissions')
        )

        self.stdout.write(
            self.style.SUCCESS('\n✓ All groups created successfully!')
        )
        self.stdout.write(
            self.style.WARNING('\nNext steps:')
        )
        self.stdout.write(
            self.style.WARNING('1. Go to Django Admin → Users')
        )
        self.stdout.write(
            self.style.WARNING('2. Select a user and assign them to a group')
        )
        self.stdout.write(
            self.style.WARNING('3. The user will automatically have all permissions for that group')
        )



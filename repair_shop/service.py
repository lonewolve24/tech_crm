from django.db import models
from .models import Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt, MyUser, Notification



class RepairTransactionService():

    @staticmethod
    def create_repair_transaction(gadget_id,technician_id,status= "Pending"):

        try:

            gadget = Gadget.objects.get(id=gadget_id)
            technician = MyUser.objects.get(id=technician_id)

            transaction_obj = GadgetRepairTransaction.objects.create(gadget=gadget,technician=technician,status=status)

            return {
                "success": True,
                "message": f'Repair transaction created successfully with code: {transaction_obj.code}',
                "transaction": transaction_obj
            }
        except Gadget.DoesNotExist:
            return {
                "success": False,
                "message": "Gadget not found",
                "transaction": None
            }
        except MyUser.DoesNotExist:
            return {
                "success": False,
                "message": "Technician not found",
                "transaction": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "transaction": None
            }

    @staticmethod
    def update_repair_transaction(transaction_id, technician_id, status):
        """Update only technician and status (NOT gadget)"""
        try:
            transaction_obj = GadgetRepairTransaction.objects.get(id=transaction_id)
            
            # Prevent updates to completed repairs
            if transaction_obj.status == GadgetRepairTransaction.COMPLETED:
                return {
                    "success": False,
                    "message": "Cannot update a completed repair",
                    "transaction": None
                }
            
            new_technician = MyUser.objects.get(id=technician_id)
            transaction_obj.technician = new_technician
            transaction_obj.status = status
            transaction_obj.save()
            
            return {
                "success": True,
                "message": "Repair transaction updated successfully",
                "transaction": transaction_obj
            }
        except GadgetRepairTransaction.DoesNotExist:
            return {
                "success": False,
                "message": "Repair transaction not found",
                "transaction": None
            }
        except MyUser.DoesNotExist:
            return {
                "success": False,
                "message": "Technician not found",
                "transaction": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "transaction": None
            }

    @staticmethod
    def reassign_technician(transaction_id,new_technician_id):

        try:

            transaction_obj = GadgetRepairTransaction.objects.get(id=transaction_id)
            new_technician = MyUser.objects.get(id=new_technician_id)

            if transaction_obj.status == GadgetRepairTransaction.COMPLETED:
                return {
                    "success": False,
                    "message": "Cannot reassign technician for completed repair transactions",
                    "transaction": None
                }
            if transaction_obj.technician == new_technician:
                return {
                    "success": False,
                    "message": "Technician is already assigned to this repair transaction",
                    "transaction": None
                }
            
            old_technician = transaction_obj.technician
            transaction_obj.technician = new_technician
            transaction_obj.save()
            return {
                "success": True,
                "message": f"Technician reassigned successfully from {old_technician} to {new_technician}",
                "transaction": transaction_obj
            }
        except GadgetRepairTransaction.DoesNotExist:
            return {
                "success": False,
                "message": "Repair transaction not found",
                "transaction": None
            }
        except MyUser.DoesNotExist:
            return {
                "success": False,
                "message": "New technician not found",
                "transaction": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "transaction": None
            }


class GadgetRepairLogService:

    @staticmethod
    def add_repair_log(transaction_id, repair_cost, issue_description, resolution_description):
        """Add a new repair log to a transaction"""
        try:
            transaction_obj = GadgetRepairTransaction.objects.get(id=transaction_id)
            repair_log_obj = GadgetRepairLog.objects.create(transaction=transaction_obj, repair_cost=repair_cost, issue_description=issue_description, resolution_description=resolution_description)
            return {
                "success": True,
                "message": f"Repair log created successfully",
                "repair_log": repair_log_obj
            }
        except GadgetRepairTransaction.DoesNotExist:
            return {
                "success": False,
                "message": "Repair transaction not found",
                "repair_log": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "repair_log": None
            }
    
    @staticmethod
    def update_repair_log(repair_log_id, repair_cost, issue_description, resolution_description):
        """
        Update a repair log.
        Can only update if the repair transaction is NOT completed.
        """
        try:
            repair_log_obj = GadgetRepairLog.objects.get(id=repair_log_id)
            
            # Check if repair is not completed before updating
            if repair_log_obj.transaction.status != GadgetRepairTransaction.COMPLETED:
                repair_log_obj.repair_cost = repair_cost
                repair_log_obj.issue_description = issue_description
                repair_log_obj.resolution_description = resolution_description
                repair_log_obj.save()
                
                return {
                    "success": True,
                    "message": "Repair log updated successfully",
                    "repair_log": repair_log_obj
                }
            else:
                return {
                    "success": False,
                    "message": "Cannot update repair log for completed repair transactions",
                    "repair_log": None
                }
        
        except GadgetRepairLog.DoesNotExist:
            return {
                "success": False,
                "message": "Repair log not found",
                "repair_log": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "repair_log": None
            }

class GadgetTransactionReceiptService:

    @staticmethod
    def create_transaction_receipt(transaction_id):
        """
        Create a receipt once the repair is Completed AND fully paid.
        The amount_paid is auto-calculated from all recorded Payment objects.
        """
        try:
            transaction_obj = GadgetRepairTransaction.objects.get(id=transaction_id)
            
            # Validation 1: repair must be COMPLETED
            if transaction_obj.status != GadgetRepairTransaction.COMPLETED:
                return {
                    "success": False,
                    "message": "Cannot create receipt. Repair transaction is not completed yet.",
                    "transaction_receipt": None
                }
            
            # Validation 2: must be fully paid
            if not transaction_obj.is_fully_paid:
                due = transaction_obj.total_due
                return {
                    "success": False,
                    "message": f"Cannot create receipt. Outstanding balance: D{due:.2f}",
                    "transaction_receipt": None
                }
            
            # Validation 3: prevent duplicate receipts
            existing = transaction_obj.gadgettransactionreceipt_set.first()
            if existing:
                return {
                    "success": False,
                    "message": f"Receipt {existing.receipt_number} already exists for this repair.",
                    "transaction_receipt": existing
                }

            # Create receipt — amount_paid = total payments received
            transaction_receipt_obj = GadgetTransactionReceipt.objects.create(
                transaction=transaction_obj,
                amount_paid=transaction_obj.total_paid
            )
            
            return {
                "success": True,
                "message": f"Receipt {transaction_receipt_obj.receipt_number} created successfully.",
                "transaction_receipt": transaction_receipt_obj
            }
        
        except GadgetRepairTransaction.DoesNotExist:
            return {
                "success": False,
                "message": "Repair transaction not found",
                "transaction_receipt": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "transaction_receipt": None
            }


class NotificationService:
    """Helper to create in-app notifications."""

    @staticmethod
    def notify_technician_assigned(transaction):
        """Notify technician when a repair is assigned to them."""
        if not transaction.technician:
            return
        Notification.objects.create(
            recipient=transaction.technician,
            title="New Repair Assigned",
            message=(
                f"You have been assigned a new repair: "
                f"{transaction.gadget.gadget_brand} {transaction.gadget.gadget_model} "
                f"(Code: {transaction.code})"
            ),
            notification_type=Notification.REPAIR_ASSIGNED,
            repair=transaction,
        )

    @staticmethod
    def notify_staff_repair_completed(transaction):
        """Notify all staff/admin when a repair is marked completed."""
        staff_users = MyUser.objects.filter(
            is_active=True
        ).filter(
            models.Q(is_staff=True) | models.Q(is_superuser=True)
        )
        notifications = [
            Notification(
                recipient=user,
                title="Repair Completed",
                message=(
                    f"Repair {transaction.code} has been marked as completed by "
                    f"{transaction.technician.get_full_name() if transaction.technician else 'N/A'}. "
                    f"Device: {transaction.gadget.gadget_brand} {transaction.gadget.gadget_model}."
                ),
                notification_type=Notification.REPAIR_COMPLETED,
                repair=transaction,
            )
            for user in staff_users
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)

    @staticmethod
    def notify_staff_payment_pending(transaction):
        """Notify staff/admin when a repair is completed but no payment has been made."""
        staff_users = MyUser.objects.filter(
            is_active=True
        ).filter(
            models.Q(is_staff=True) | models.Q(is_superuser=True)
        )
        notifications = [
            Notification(
                recipient=user,
                title="Payment Pending",
                message=(
                    f"⚠️ Repair {transaction.code} is COMPLETED but payment of "
                    f"D{transaction.total_cost:.2f} has NOT been received yet. "
                    f"Customer: {transaction.gadget.customer}. "
                    f"Device: {transaction.gadget.gadget_brand} {transaction.gadget.gadget_model}."
                ),
                notification_type=Notification.PAYMENT_PENDING,
                repair=transaction,
            )
            for user in staff_users
        ]
        if notifications:
            Notification.objects.bulk_create(notifications)

from .models import Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog, GadgetTransactionReceipt, MyUser



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
    def create_transaction_receipt(transaction_id, amount, payment_method):
        """
        Create a transaction receipt.
        
        Validations:
        1. Repair transaction status must be COMPLETED
        2. Amount paid must EQUAL the total repair cost
        """
        try:
            transaction_obj = GadgetRepairTransaction.objects.get(id=transaction_id)
            
            # Validation 1: Check if repair is COMPLETED
            if transaction_obj.status != GadgetRepairTransaction.COMPLETED:
                return {
                    "success": False,
                    "message": "Cannot create receipt. Repair transaction is not completed yet.",
                    "transaction_receipt": None
                }
            
            # Validation 2: Check if amount matches total repair cost
            total_repair_cost = transaction_obj.total_cost
            
            if float(amount) != float(total_repair_cost):
                return {
                    "success": False,
                    "message": f"Amount mismatch! Expected {total_repair_cost}, but received {amount}",
                    "transaction_receipt": None
                }
            
            # Both validations passed - create receipt
            transaction_receipt_obj = GadgetTransactionReceipt.objects.create(
                transaction=transaction_obj,
                amount_paid=amount
            )
            
            return {
                "success": True,
                "message": f"Transaction receipt created successfully with code: {transaction_receipt_obj.receipt_number}",
                "transaction_receipt": transaction_receipt_obj
            }
        
        except GadgetRepairTransaction.DoesNotExist:
            return {
                "success": False,
                "message": "Repair transaction not found",
                "transaction_receipt": None
            }
        except ValueError:
            return {
                "success": False,
                "message": "Invalid amount entered. Please enter a valid number.",
                "transaction_receipt": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "transaction_receipt": None
            }

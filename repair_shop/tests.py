from decimal import Decimal
from datetime import timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from repair_shop.models import (
    Customer, Gadget, GadgetRepairTransaction, GadgetRepairLog,
    Payment, MyUser,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def make_admin(username='admin_user'):
    return MyUser.objects.create_user(
        username=username, password='testpass123',
        email=f'{username}@test.com', first_name='Admin', last_name='User',
        is_superuser=True, is_staff=True, is_admin=True,
    )


def make_customer(first='John', last='Doe', n=0):
    return Customer.objects.create(
        first_name=first, last_name=f'{last}{n}',
        email=f'{first.lower()}{last.lower()}{n}@test.com',
    )


def make_gadget(customer, brand='Samsung', model='Galaxy S10'):
    return Gadget.objects.create(
        customer=customer, gadget_type=Gadget.SMARTPHONE,
        gadget_brand=brand, gadget_model=model,
    )


def make_transaction(gadget, status=GadgetRepairTransaction.PENDING):
    return GadgetRepairTransaction.objects.create(
        gadget=gadget, status=status,
    )


def make_log(transaction, cost):
    return GadgetRepairLog.objects.create(
        transaction=transaction,
        repair_cost=Decimal(str(cost)),
        issue_description='Screen cracked',
    )


def make_payment(transaction, amount, user=None):
    return Payment.objects.create(
        transaction=transaction,
        amount=Decimal(str(amount)),
        payment_type=Payment.CASH,
        recorded_by=user,
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. Model / Business Logic Unit Tests
# ─────────────────────────────────────────────────────────────────────────────

class GadgetRepairTransactionPropertiesTest(TestCase):
    """Tests for model properties: total_cost, total_paid, total_due, is_fully_paid."""

    def setUp(self):
        customer = make_customer()
        gadget = make_gadget(customer)
        self.tx = make_transaction(gadget, GadgetRepairTransaction.PENDING)

    def test_total_cost_no_logs(self):
        self.assertEqual(self.tx.total_cost, 0)

    def test_total_cost_with_logs(self):
        make_log(self.tx, 150)
        make_log(self.tx, 75)
        self.assertEqual(self.tx.total_cost, Decimal('225'))

    def test_total_paid_no_payments(self):
        self.assertEqual(self.tx.total_paid, 0)

    def test_total_paid_with_payments(self):
        make_log(self.tx, 200)
        make_payment(self.tx, 100)
        make_payment(self.tx, 50)
        self.assertEqual(self.tx.total_paid, Decimal('150'))

    def test_total_due(self):
        make_log(self.tx, 200)
        make_payment(self.tx, 80)
        self.assertEqual(self.tx.total_due, Decimal('120'))

    def test_total_due_zero_when_fully_paid(self):
        make_log(self.tx, 100)
        make_payment(self.tx, 100)
        self.assertEqual(self.tx.total_due, Decimal('0'))

    def test_is_fully_paid_false(self):
        make_log(self.tx, 100)
        make_payment(self.tx, 50)
        self.assertFalse(self.tx.is_fully_paid)

    def test_is_fully_paid_true(self):
        make_log(self.tx, 100)
        make_payment(self.tx, 100)
        self.assertTrue(self.tx.is_fully_paid)

    def test_is_fully_paid_overpayment(self):
        """Over-payment should count as fully paid."""
        make_log(self.tx, 100)
        make_payment(self.tx, 120)
        self.assertTrue(self.tx.is_fully_paid)

    def test_has_price_false_when_no_logs(self):
        """has_price should be False when no repair logs exist."""
        self.assertFalse(self.tx.has_price)

    def test_has_price_true_when_logs_exist(self):
        """has_price should be True when at least one repair log exists."""
        make_log(self.tx, 100)
        self.assertTrue(self.tx.has_price)

    def test_is_fully_paid_false_when_no_price_set(self):
        """is_fully_paid should be False even if total_due is 0 when no price is set."""
        # No logs, no payments → total_due = 0, but should NOT be "fully paid"
        self.assertFalse(self.tx.is_fully_paid)


class CustomerCountTest(TestCase):
    """Customer.objects.count() reflects all created customers."""

    def test_no_customers(self):
        self.assertEqual(Customer.objects.count(), 0)

    def test_count_after_creating(self):
        make_customer(n=1)
        make_customer(n=2)
        make_customer(n=3)
        self.assertEqual(Customer.objects.count(), 3)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Dashboard Stats — context values produced by admin_dashboard view
# ─────────────────────────────────────────────────────────────────────────────

class AdminDashboardContextTest(TestCase):
    """
    Verifies that every card on the admin dashboard receives the correct value
    from the view context.  Focuses ONLY on business logic (no UI assertions).
    """

    def setUp(self):
        self.client = Client()
        self.admin = make_admin()
        self.client.login(username='admin_user', password='testpass123')
        self.url = reverse('repair_shop:admin_dashboard')

        # Shared fixtures
        self.customer1 = make_customer(n=1)
        self.customer2 = make_customer(n=2)
        self.gadget1 = make_gadget(self.customer1, brand='Apple', model='iPhone 13')
        self.gadget2 = make_gadget(self.customer2, brand='Samsung', model='A52')

    # ── helper ──────────────────────────────────────────────────────────────

    def _complete_in_month(self, gadget, cost, year, month):
        """Create a COMPLETED transaction with a repair log and fix its updated_at."""
        tx = make_transaction(gadget, GadgetRepairTransaction.COMPLETED)
        make_log(tx, cost)
        # Force updated_at to the desired month so the filter works correctly.
        fake_date = timezone.now().replace(year=year, month=month, day=15)
        GadgetRepairTransaction.objects.filter(pk=tx.pk).update(updated_at=fake_date)
        tx.refresh_from_db()
        return tx

    # ── total_customers ──────────────────────────────────────────────────────

    def test_stats_total_customers_is_present_and_correct(self):
        """stats.total_customers must equal Customer.objects.count()."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        stats = response.context['stats']
        self.assertIn('total_customers', stats,
                      msg="'total_customers' key missing from stats dict in context")
        self.assertEqual(stats['total_customers'], 2)

    def test_stats_total_customers_updates_after_new_customer(self):
        make_customer(n=99)
        response = self.client.get(self.url)
        self.assertEqual(response.context['stats']['total_customers'], 3)

    # ── all-time overview ────────────────────────────────────────────────────

    def test_stats_total_repairs(self):
        make_transaction(self.gadget1)
        make_transaction(self.gadget2)
        response = self.client.get(self.url)
        self.assertEqual(response.context['stats']['total'], 2)

    def test_stats_completed(self):
        make_transaction(self.gadget1, GadgetRepairTransaction.COMPLETED)
        make_transaction(self.gadget2, GadgetRepairTransaction.PENDING)
        response = self.client.get(self.url)
        self.assertEqual(response.context['stats']['completed'], 1)
        self.assertEqual(response.context['stats']['pending'], 1)

    def test_stats_total_revenue_sums_actual_payments_received(self):
        """Total revenue = sum of actual PAYMENTS received (cash collected), not repair costs."""
        tx_done = make_transaction(self.gadget1, GadgetRepairTransaction.COMPLETED)
        make_log(tx_done, 300)
        # Customer pays 200 (partial payment)
        make_payment(tx_done, 200, self.admin)

        # Another completed repair with full payment
        tx_done2 = make_transaction(self.gadget2, GadgetRepairTransaction.COMPLETED)
        make_log(tx_done2, 150)
        make_payment(tx_done2, 150, self.admin)

        # Pending repair with logs but no payment should NOT count
        tx_pending = make_transaction(self.gadget1, GadgetRepairTransaction.PENDING)
        make_log(tx_pending, 999)

        response = self.client.get(self.url)
        # Revenue = 200 + 150 = 350 (actual cash received)
        self.assertEqual(response.context['stats']['total_revenue'], Decimal('350'))

    def test_stats_total_revenue_zero_when_no_payments(self):
        """Revenue is 0 if no payments have been received, even if repairs are completed."""
        tx = make_transaction(self.gadget1, GadgetRepairTransaction.COMPLETED)
        make_log(tx, 500)  # Price set but not paid yet
        response = self.client.get(self.url)
        self.assertEqual(response.context['stats']['total_revenue'], 0)

    # ── monthly stats ────────────────────────────────────────────────────────

    def test_monthly_stats_fixed_key_is_present(self):
        """monthly_stats must have a 'fixed' key (template: monthly_stats.fixed)."""
        response = self.client.get(self.url)
        monthly = response.context['monthly_stats']
        self.assertIn('fixed', monthly,
                      msg="'fixed' key missing from monthly_stats — template will show blank")

    def test_monthly_stats_received_key_is_present(self):
        """monthly_stats must have a 'received' key (template: monthly_stats.received)."""
        response = self.client.get(self.url)
        monthly = response.context['monthly_stats']
        self.assertIn('received', monthly,
                      msg="'received' key missing from monthly_stats — template will show blank")

    def test_monthly_stats_fixed_counts_completions_in_filter_month(self):
        now = timezone.now()
        # Complete one repair this month
        self._complete_in_month(self.gadget1, 200, now.year, now.month)
        # Complete one repair in a different year/month — should not count
        other_month = 1 if now.month != 1 else 2
        other_year = now.year - 1
        self._complete_in_month(self.gadget2, 100, other_year, other_month)

        response = self.client.get(self.url)
        monthly = response.context['monthly_stats']
        self.assertEqual(monthly['fixed'], 1,
                         msg="Only repairs completed in the filter month should be counted")
        self.assertEqual(monthly['completed'], 1)

    def test_monthly_stats_fixed_zero_when_none_completed_this_month(self):
        # Create a PENDING repair this month
        make_transaction(self.gadget1, GadgetRepairTransaction.PENDING)
        response = self.client.get(self.url)
        self.assertEqual(response.context['monthly_stats']['fixed'], 0)

    def test_monthly_stats_received_equals_repairs_brought_in_this_month(self):
        now = timezone.now()
        # Both transactions are created now (this month/year)
        make_transaction(self.gadget1)
        make_transaction(self.gadget2)
        response = self.client.get(
            self.url, {'month': now.month, 'year': now.year}
        )
        self.assertEqual(response.context['monthly_stats']['received'], 2)

    # ── monthly revenue ──────────────────────────────────────────────────────

    def test_monthly_revenue_key_is_present(self):
        response = self.client.get(self.url)
        self.assertIn('revenue', response.context['monthly_stats'])

    def test_monthly_revenue_sums_payments_received_this_month(self):
        """Monthly revenue = actual PAYMENTS received this month (cash collected)."""
        now = timezone.now()
        tx = self._complete_in_month(self.gadget1, 500, now.year, now.month)
        make_log(tx, 75)  # Total cost = 575
        # Payment received this month
        make_payment(tx, 575, self.admin)

        # A payment received last month should NOT be included
        other_month = 1 if now.month != 1 else 2
        other_year = now.year - 1
        tx2 = self._complete_in_month(self.gadget2, 999, other_year, other_month)
        make_log(tx2, 100)
        # Create payment with date in the other month
        from datetime import datetime
        fake_date = datetime(other_year, other_month, 15, 12, 0, 0)
        fake_date = timezone.make_aware(fake_date)
        Payment.objects.filter(id=make_payment(tx2, 100, self.admin).id).update(created_at=fake_date)

        response = self.client.get(self.url)
        # Only payment from this month counts: 575
        self.assertEqual(
            response.context['monthly_stats']['revenue'], Decimal('575'),
            msg="Monthly revenue must only sum payments received in the filter month"
        )

    def test_monthly_revenue_zero_when_no_payments_this_month(self):
        """Revenue is 0 if no payments received this month, even if repairs completed."""
        now = timezone.now()
        tx = self._complete_in_month(self.gadget1, 500, now.year, now.month)
        make_log(tx, 100)  # Price set but not paid yet
        response = self.client.get(self.url)
        self.assertEqual(response.context['monthly_stats']['revenue'], 0)

    def test_monthly_revenue_excludes_pending_repairs(self):
        """Pending repairs (even with payments) should not count toward revenue."""
        now = timezone.now()
        tx_pending = make_transaction(self.gadget1, GadgetRepairTransaction.PENDING)
        make_log(tx_pending, 400)
        make_payment(tx_pending, 400, self.admin)  # Payment exists but repair not completed
        response = self.client.get(
            self.url, {'month': now.month, 'year': now.year}
        )
        # Revenue should still be 0 (repair not completed = no revenue earned)
        self.assertEqual(response.context['monthly_stats']['revenue'], 0)

    # ── filter by month/year params ──────────────────────────────────────────

    def test_filter_by_specific_month_and_year(self):
        """?month=1&year=2025 should only count items from Jan 2025."""
        now = timezone.now()
        # Complete one in Jan 2025 and receive payment in Jan 2025
        tx1 = self._complete_in_month(self.gadget1, 300, 2025, 1)
        from datetime import datetime
        jan_date = timezone.make_aware(datetime(2025, 1, 15, 12, 0, 0))
        Payment.objects.filter(id=make_payment(tx1, 300, self.admin).id).update(created_at=jan_date)
        
        # Complete one this month (different month/year) with payment this month
        tx2 = self._complete_in_month(self.gadget2, 200, now.year, now.month)
        make_payment(tx2, 200, self.admin)

        response = self.client.get(self.url, {'month': 1, 'year': 2025})
        monthly = response.context['monthly_stats']
        self.assertEqual(monthly['fixed'], 1)
        # Revenue = payment received in Jan 2025 (not completion date)
        self.assertEqual(monthly['revenue'], Decimal('300'))

    # ── access control ───────────────────────────────────────────────────────

    def test_non_staff_redirected(self):
        regular = MyUser.objects.create_user(
            username='regular', password='pass', email='reg@test.com',
            first_name='Reg', last_name='User',
        )
        self.client.login(username='regular', password='pass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_unauthenticated_redirected(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

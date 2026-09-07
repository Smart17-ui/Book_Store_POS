from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import Role, User
from apps.inventory.models import Category, Inventory, Product
from apps.payments.models import Payment, PaymentMethod
from apps.reports.models import Receipt


class ProcessSaleTests(TestCase):
	def setUp(self):
		self.client = APIClient()
		role = Role.objects.create(name='Cashier')
		self.cashier = User.objects.create(
			username='cashier',
			password_hash='demo',
			full_name='Test Cashier',
			email='cashier@example.com',
			role=role,
		)
		category = Category.objects.create(name='Books')
		self.product = Product.objects.create(
			sku='BOOK-001',
			name='Test Book',
			category=category,
			unit_price='12.00',
			cost_price='6.00',
		)
		self.inventory = Inventory.objects.create(
			product=self.product,
			quantity_on_hand='3',
			reorder_level='1',
		)
		PaymentMethod.objects.create(name='Cash', type=PaymentMethod.MethodType.CASH)

	def test_process_sale_completes_payment_inventory_and_receipt(self):
		response = self.client.post('/api/sales/process/', {
			'cashier': str(self.cashier.id),
			'items': [{'sku': 'BOOK-001', 'quantity': '2'}],
			'payment_method_type': 'CASH',
			'tendered_amount': '30.00',
		}, format='json')

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['sale']['status'], 'COMPLETED')
		self.assertEqual(response.data['sale']['total_amount'], '24.00')
		self.assertEqual(response.data['change'], '6.00')
		self.inventory.refresh_from_db()
		self.assertEqual(self.inventory.quantity_on_hand, Decimal('1'))
		self.assertTrue(Payment.objects.filter(status='COMPLETED').exists())
		self.assertTrue(Receipt.objects.exists())

	def test_overselling_does_not_change_inventory(self):
		response = self.client.post('/api/sales/process/', {
			'cashier': str(self.cashier.id),
			'items': [{'sku': 'BOOK-001', 'quantity': '4'}],
			'payment_method_type': 'CASH',
			'tendered_amount': '48.00',
		}, format='json')

		self.assertEqual(response.status_code, 400)
		self.inventory.refresh_from_db()
		self.assertEqual(self.inventory.quantity_on_hand, Decimal('3'))
		self.assertFalse(Payment.objects.exists())
		self.assertFalse(Receipt.objects.exists())

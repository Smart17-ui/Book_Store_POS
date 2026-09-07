from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import User
from apps.common.models import UUIDModel
from apps.inventory.models import Product


class Customer(UUIDModel):
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    loyalty_points = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self):
        return self.get_full_name()


class Sale(UUIDModel):
    class SaleStatus(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        COMPLETED = 'COMPLETED', 'Completed'
        VOIDED = 'VOIDED', 'Voided'

    sale_number = models.CharField(max_length=40, unique=True)
    sale_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    status = models.CharField(max_length=20, choices=SaleStatus.choices, default=SaleStatus.DRAFT)

    def calculate_totals(self):
        self.subtotal = sum((item.calculate_line_total() for item in self.items.all()), Decimal('0'))
        self.total_amount = self.subtotal - self.discount_amount + self.tax_amount
        return self.total_amount

    def add_item(self, product, quantity, unit_price=None):
        return self.items.create(product=product, quantity=quantity, unit_price=unit_price or product.unit_price)

    def __str__(self):
        return self.sale_number


class SaleItem(UUIDModel):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=3, validators=[MinValueValidator(Decimal('0.001'))])
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    def calculate_line_total(self):
        self.line_total = self.quantity * self.unit_price - self.discount_amount + self.tax_amount
        return self.line_total

from decimal import Decimal

from django.db import models

from apps.accounts.models import User
from apps.common.models import UUIDModel
from apps.inventory.models import Product
from apps.payments.models import PaymentMethod
from apps.sales.models import Customer, Sale, SaleItem


class Return(UUIDModel):
    class ReturnStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'

    return_number = models.CharField(max_length=40, unique=True)
    sale = models.ForeignKey(Sale, on_delete=models.PROTECT, related_name='returns')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    cashier = models.ForeignKey(User, on_delete=models.PROTECT, related_name='returns')
    return_date = models.DateTimeField(auto_now_add=True)
    total_refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    return_reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.PENDING)

    def calculate_total(self):
        self.total_refund_amount = sum((item.calculate_line_total() for item in self.items.all()), Decimal('0'))
        return self.total_refund_amount


class ReturnItem(UUIDModel):
    return_record = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='items')
    sale_item = models.ForeignKey(SaleItem, on_delete=models.PROTECT, related_name='return_items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='return_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    reason = models.CharField(max_length=255, blank=True)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    def calculate_line_total(self):
        self.line_total = self.quantity * self.unit_price
        return self.line_total


class RefundMethod(UUIDModel):
    class MethodType(models.TextChoices):
        ORIGINAL_PAYMENT = 'ORIGINAL_PAYMENT', 'Original payment'
        STORE_CREDIT = 'STORE_CREDIT', 'Store credit'
        CASH = 'CASH', 'Cash'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank transfer'

    name = models.CharField(max_length=80)
    type = models.CharField(max_length=30, choices=MethodType.choices, unique=True)
    is_active = models.BooleanField(default=True)

    def requires_reference(self):
        return self.type not in {self.MethodType.CASH, self.MethodType.STORE_CREDIT}


class Refund(UUIDModel):
    class RefundStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        DECLINED = 'DECLINED', 'Declined'

    return_record = models.ForeignKey(Return, on_delete=models.CASCADE, related_name='refunds')
    refund_method = models.ForeignKey(RefundMethod, on_delete=models.PROTECT, related_name='refunds')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=RefundStatus.choices, default=RefundStatus.PENDING)
    refund_date = models.DateTimeField(auto_now_add=True)

    def is_successful(self):
        return self.status == self.RefundStatus.COMPLETED

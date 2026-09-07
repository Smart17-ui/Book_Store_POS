from decimal import Decimal

from django.db import models

from apps.common.models import UUIDModel
from apps.sales.models import Sale


class PaymentMethod(UUIDModel):
    class MethodType(models.TextChoices):
        CASH = 'CASH', 'Cash'
        CREDIT_CARD = 'CREDIT_CARD', 'Credit card'
        DEBIT_CARD = 'DEBIT_CARD', 'Debit card'
        GIFT_CARD = 'GIFT_CARD', 'Gift card'
        MOBILE_PAYMENT = 'MOBILE_PAYMENT', 'Mobile payment'
        STORE_CREDIT = 'STORE_CREDIT', 'Store credit'

    name = models.CharField(max_length=80)
    type = models.CharField(max_length=30, choices=MethodType.choices, unique=True)
    is_active = models.BooleanField(default=True)

    def requires_reference(self):
        return self.type != self.MethodType.CASH


class Payment(UUIDModel):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        AUTHORIZED = 'AUTHORIZED', 'Authorized'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.PROTECT, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    reference_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    payment_date = models.DateTimeField(auto_now_add=True)

    def is_successful(self):
        return self.status == self.PaymentStatus.COMPLETED

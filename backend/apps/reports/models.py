from decimal import Decimal

from django.db import models

from apps.common.models import UUIDModel
from apps.sales.models import Sale


class Receipt(UUIDModel):
    sale = models.OneToOneField(Sale, on_delete=models.CASCADE, null=True, blank=True, related_name='receipt')
    return_record = models.OneToOneField(
        'returns.Return', on_delete=models.CASCADE, null=True, blank=True,
        related_name='receipt',
    )
    receipt_number = models.CharField(max_length=40, unique=True)
    receipt_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    printed = models.BooleanField(default=False)
    emailed = models.BooleanField(default=False)

    def print_receipt(self):
        self.printed = True
        self.save(update_fields=['printed', 'updated_at'])

    def email(self, to):
        self.emailed = True
        self.save(update_fields=['emailed', 'updated_at'])

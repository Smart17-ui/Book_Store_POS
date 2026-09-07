from decimal import Decimal
from uuid import uuid4

from django.db import models, transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.inventory.models import Inventory, InventoryAdjustment
from apps.reports.models import Receipt

from .models import Refund, RefundMethod, Return, ReturnItem


@transaction.atomic
def process_return(*, cashier, receipt_number, items, refund_method_type,
                   refund_reference='', return_reason=''):
    cashier = User.objects.get(pk=cashier, is_active=True)
    try:
        original_receipt = Receipt.objects.select_for_update().select_related('sale').get(
            receipt_number=receipt_number,
            sale__isnull=False,
        )
    except Receipt.DoesNotExist as exc:
        raise ValidationError({'receipt_number': 'A completed sale receipt was not found.'}) from exc

    sale = original_receipt.sale
    if sale.status != sale.SaleStatus.COMPLETED:
        raise ValidationError({'receipt_number': 'Only completed sales can be returned.'})
    if not items:
        raise ValidationError({'items': 'At least one return item is required.'})

    try:
        refund_method = RefundMethod.objects.get(type=refund_method_type, is_active=True)
    except RefundMethod.DoesNotExist as exc:
        raise ValidationError({'refund_method_type': 'An active refund method of this type is required.'}) from exc

    return_record = Return.objects.create(
        return_number=f'RETURN-{uuid4().hex[:12].upper()}',
        sale=sale,
        customer=sale.customer,
        cashier=cashier,
        return_reason=return_reason,
        status=Return.ReturnStatus.COMPLETED,
    )
    total_refund = Decimal('0')

    for item_data in items:
        sale_item_id = item_data.get('sale_item_id')
        quantity = Decimal(str(item_data.get('quantity', '0')))
        reason = item_data.get('reason', return_reason)
        if not sale_item_id or quantity <= 0:
            raise ValidationError({'items': 'Each item requires a positive quantity and sale_item_id.'})
        try:
            sale_item = sale.items.select_for_update().get(pk=sale_item_id)
        except Exception as exc:
            raise ValidationError({'items': f'Sale item {sale_item_id} does not belong to the original sale.'}) from exc

        already_returned = ReturnItem.objects.filter(sale_item=sale_item).aggregate(
            total=models.Sum('quantity'),
        )['total'] or Decimal('0')
        if already_returned + quantity > sale_item.quantity:
            raise ValidationError({'items': f'Return quantity exceeds the quantity sold for {sale_item.product.sku}.'})

        return_item = ReturnItem.objects.create(
            return_record=return_record,
            sale_item=sale_item,
            product=sale_item.product,
            quantity=quantity,
            unit_price=sale_item.unit_price,
            reason=reason,
        )
        return_item.calculate_line_total()
        return_item.save(update_fields=('line_total', 'updated_at'))
        total_refund += return_item.line_total

        try:
            inventory = Inventory.objects.select_for_update().get(product=sale_item.product)
        except Inventory.DoesNotExist as exc:
            raise ValidationError({'items': f'Inventory was not found for {sale_item.product.sku}.'}) from exc
        inventory.quantity_on_hand += quantity
        inventory.save(update_fields=('quantity_on_hand', 'last_updated', 'updated_at'))
        InventoryAdjustment.objects.create(
            inventory=inventory,
            adjusted_by=cashier,
            adjustment_type=InventoryAdjustment.AdjustmentType.RETURN,
            quantity_change=quantity,
            reason='Sale return completed',
            reference_number=return_record.return_number,
        )

    return_record.total_refund_amount = total_refund
    return_record.save(update_fields=('total_refund_amount', 'updated_at'))
    Refund.objects.create(
        return_record=return_record,
        refund_method=refund_method,
        amount=total_refund,
        reference_number=refund_reference,
        status=Refund.RefundStatus.COMPLETED,
    )
    receipt = Receipt.objects.create(
        return_record=return_record,
        receipt_number=f'RECEIPT-{return_record.return_number}',
        total_amount=total_refund,
    )
    return return_record, receipt
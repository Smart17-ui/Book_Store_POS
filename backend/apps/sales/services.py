from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.accounts.models import User
from apps.inventory.models import Inventory, InventoryAdjustment
from apps.payments.models import Payment, PaymentMethod
from apps.reports.models import Receipt

from .models import Sale, SaleItem


@transaction.atomic
def process_sale(*, cashier, customer=None, sale_number=None, items, payment_method_type,
                tendered_amount=None, payment_reference='', discount_amount=Decimal('0')):
    cashier = User.objects.get(pk=cashier, is_active=True)
    if customer:
        from .models import Customer
        customer = Customer.objects.get(pk=customer)

    if not items:
        raise ValidationError({'items': 'At least one item is required.'})

    sale_number = sale_number or f'SALE-{uuid4().hex[:12].upper()}'
    sale = Sale.objects.create(
        sale_number=sale_number,
        cashier=cashier,
        customer=customer,
        discount_amount=discount_amount,
    )
    gross_subtotal = Decimal('0')
    item_discount_total = Decimal('0')
    tax_total = Decimal('0')

    for item_data in items:
        sku = item_data.get('sku')
        quantity = Decimal(str(item_data.get('quantity', '0')))
        item_discount = Decimal(str(item_data.get('discount_amount', '0')))
        if not sku:
            raise ValidationError({'items': 'Each item must include an SKU.'})
        if quantity <= 0:
            raise ValidationError({'items': f'Quantity for {sku} must be greater than zero.'})
        if item_discount < 0:
            raise ValidationError({'items': f'Discount for {sku} cannot be negative.'})

        try:
            inventory = Inventory.objects.select_for_update().select_related('product').get(
                product__sku=sku,
                product__is_active=True,
            )
        except Inventory.DoesNotExist as exc:
            raise ValidationError({'items': f'Active inventory was not found for SKU {sku}.'}) from exc

        if inventory.quantity_on_hand < quantity:
            raise ValidationError({
                'items': f'Insufficient stock for SKU {sku}. Available: {inventory.quantity_on_hand}.',
            })

        product = inventory.product
        line_subtotal = quantity * product.unit_price
        taxable_amount = max(line_subtotal - item_discount, Decimal('0'))
        line_tax = taxable_amount * product.tax_rate / Decimal('100')
        sale_item = SaleItem.objects.create(
            sale=sale,
            product=product,
            quantity=quantity,
            unit_price=product.unit_price,
            discount_amount=item_discount,
            tax_amount=line_tax,
        )
        sale_item.calculate_line_total()
        sale_item.save(update_fields=('line_total', 'updated_at'))
        gross_subtotal += line_subtotal
        item_discount_total += item_discount
        tax_total += line_tax

        inventory.quantity_on_hand -= quantity
        inventory.save(update_fields=('quantity_on_hand', 'last_updated', 'updated_at'))
        InventoryAdjustment.objects.create(
            inventory=inventory,
            adjusted_by=cashier,
            adjustment_type=InventoryAdjustment.AdjustmentType.SALE,
            quantity_change=-quantity,
            reason='Sale completed',
            reference_number=sale.sale_number,
        )

    total_discount = item_discount_total + discount_amount
    total_amount = gross_subtotal - total_discount + tax_total
    if total_amount < 0:
        raise ValidationError({'discount_amount': 'Discount cannot exceed the sale subtotal.'})

    try:
        payment_method = PaymentMethod.objects.get(type=payment_method_type, is_active=True)
    except PaymentMethod.DoesNotExist as exc:
        raise ValidationError({'payment_method_type': 'An active payment method of this type is required.'}) from exc

    tendered = Decimal(str(tendered_amount)) if tendered_amount is not None else total_amount
    if payment_method.type == PaymentMethod.MethodType.CASH and tendered < total_amount:
        raise ValidationError({'tendered_amount': f'Cash tendered must be at least {total_amount}.'})
    if payment_method.type != PaymentMethod.MethodType.CASH and tendered != total_amount:
        tendered = total_amount

    payment = Payment.objects.create(
        sale=sale,
        payment_method=payment_method,
        amount=total_amount,
        reference_number=payment_reference,
        status=Payment.PaymentStatus.COMPLETED,
    )
    sale.subtotal = gross_subtotal
    sale.discount_amount = total_discount
    sale.tax_amount = tax_total
    sale.total_amount = total_amount
    sale.status = Sale.SaleStatus.COMPLETED
    sale.save(update_fields=('subtotal', 'discount_amount', 'tax_amount', 'total_amount', 'status', 'updated_at'))
    receipt = Receipt.objects.create(
        sale=sale,
        receipt_number=f'RECEIPT-{sale.sale_number}',
        total_amount=total_amount,
    )
    return sale, payment, receipt, tendered - total_amount

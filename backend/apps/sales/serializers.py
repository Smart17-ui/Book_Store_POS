from django.db import transaction
from rest_framework import serializers

from apps.payments.models import PaymentMethod

from .models import Customer, Sale, SaleItem


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ('id', 'client', 'created_at', 'updated_at')


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = SaleItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'line_total', 'sale')


class SaleSerializer(serializers.ModelSerializer):
    items = SaleItemSerializer(many=True, required=False)

    class Meta:
        model = Sale
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'subtotal', 'total_amount', 'cashier')

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        with transaction.atomic():
            sale = Sale.objects.create(**validated_data)
            for item in items:
                sale_item = SaleItem.objects.create(sale=sale, **item)
                sale_item.calculate_line_total()
                sale_item.save(update_fields=('line_total', 'updated_at'))
            sale.calculate_totals()
            sale.save(update_fields=('subtotal', 'total_amount', 'updated_at'))
        return sale


class ProcessSaleSerializer(serializers.Serializer):
    sale_number = serializers.CharField(max_length=40, required=False)
    cashier = serializers.UUIDField()
    customer = serializers.UUIDField(required=False, allow_null=True)
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    payment_method_type = serializers.ChoiceField(choices=PaymentMethod.MethodType.choices)
    tendered_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, min_value=0)
    payment_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    discount_amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, min_value=0, default=0)
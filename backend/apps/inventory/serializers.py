from rest_framework import serializers

from .models import Category, Inventory, InventoryAdjustment, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('client',)


class InventorySerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)

    class Meta:
        model = Inventory
        fields = ('id', 'product', 'product_name', 'product_sku', 'quantity_on_hand', 'reorder_level', 'reorder_quantity', 'last_updated', 'created_at', 'updated_at')
        read_only_fields = ('id', 'product_name', 'product_sku', 'last_updated', 'created_at', 'updated_at')


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    inventory = InventorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id', 'client', 'created_at', 'updated_at', 'inventory')


class InventoryAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryAdjustment
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'adjustment_date')


class AdjustInventorySerializer(serializers.Serializer):
    adjusted_by = serializers.UUIDField()
    sku = serializers.CharField(max_length=80)
    adjustment_type = serializers.ChoiceField(choices=InventoryAdjustment.AdjustmentType.choices)
    quantity_change = serializers.DecimalField(max_digits=12, decimal_places=3)
    reason = serializers.CharField(max_length=255)
    reference_number = serializers.CharField(max_length=100, required=False, allow_blank=True)


class SetInventorySerializer(serializers.Serializer):
    adjusted_by = serializers.UUIDField()
    sku = serializers.CharField(max_length=80)
    quantity_on_hand = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=0)
    reorder_level = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=0, required=False)
    reorder_quantity = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=0, required=False)
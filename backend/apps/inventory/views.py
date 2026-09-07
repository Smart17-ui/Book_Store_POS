from django.db import transaction
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.models import AuditLog
from apps.accounts.models import User

from .models import Category, Inventory, InventoryAdjustment, Product
from .serializers import AdjustInventorySerializer, CategorySerializer, InventoryAdjustmentSerializer, InventorySerializer, ProductSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related('category', 'inventory').all().order_by('name')
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            product = serializer.save()
            Inventory.objects.create(product=product)

    def get_queryset(self):
        queryset = super().get_queryset()
        active = self.request.query_params.get('active')
        if active in {'true', 'false'}:
            return queryset.filter(is_active=active == 'true')
        return queryset


class InventoryViewSet(ModelViewSet):
    queryset = Inventory.objects.select_related('product').all().order_by('product__name')
    serializer_class = InventorySerializer

    @action(detail=False, methods=['post'], url_path='adjust')
    def adjust(self, request):
        request_serializer = AdjustInventorySerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data
        with transaction.atomic():
            try:
                user = User.objects.get(pk=data['adjusted_by'], is_active=True)
                inventory = Inventory.objects.select_for_update().select_related('product').get(
                    product__sku=data['sku'],
                )
            except (User.DoesNotExist, Inventory.DoesNotExist) as exc:
                raise serializers.ValidationError({'detail': 'Active user and product inventory are required.'}) from exc
            new_quantity = inventory.quantity_on_hand + data['quantity_change']
            if new_quantity < 0:
                raise serializers.ValidationError({'quantity_change': 'Adjustment cannot make stock negative.'})
            inventory.quantity_on_hand = new_quantity
            inventory.save(update_fields=('quantity_on_hand', 'last_updated', 'updated_at'))
            adjustment = InventoryAdjustment.objects.create(
                inventory=inventory,
                adjusted_by=user,
                adjustment_type=data['adjustment_type'],
                quantity_change=data['quantity_change'],
                reason=data['reason'],
                reference_number=data.get('reference_number', ''),
            )
            AuditLog.objects.create(
                user=user,
                action='INVENTORY_ADJUSTMENT',
                entity_type='Inventory',
                entity_id=inventory.id,
                details={
                    'sku': data['sku'],
                    'quantity_change': str(data['quantity_change']),
                    'reason': data['reason'],
                },
            )
        return Response(InventoryAdjustmentSerializer(adjustment).data, status=status.HTTP_201_CREATED)


class InventoryAdjustmentViewSet(ModelViewSet):
    queryset = InventoryAdjustment.objects.select_related('inventory', 'adjusted_by').all().order_by('-adjustment_date')
    serializer_class = InventoryAdjustmentSerializer
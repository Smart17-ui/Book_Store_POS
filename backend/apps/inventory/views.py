from django.db import transaction
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.common.models import AuditLog
from apps.accounts.branch import request_branch
from apps.accounts.models import User
from apps.accounts.permissions import RolePermission

from .models import Category, Inventory, InventoryAdjustment, Product
from .serializers import AdjustInventorySerializer, CategorySerializer, InventoryAdjustmentSerializer, InventorySerializer, ProductSerializer, SetInventorySerializer


class CategoryViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {
        'read': {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER', 'INVENTORY_MANAGER'},
        'write': {'OWNER', 'ADMIN', 'MANAGER', 'INVENTORY_MANAGER'},
    }
    queryset = Category.objects.all().order_by('name')
    serializer_class = CategorySerializer

    def get_queryset(self):
        return super().get_queryset().filter(client_id=self.request.user.client_id)

    def perform_create(self, serializer):
        serializer.save(client_id=self.request.user.client_id)


class ProductViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {
        'read': {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER', 'INVENTORY_MANAGER'},
        'write': {'OWNER', 'ADMIN', 'MANAGER', 'INVENTORY_MANAGER'},
    }
    queryset = Product.objects.select_related('category', 'inventory').all().order_by('name')
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        with transaction.atomic():
            product = serializer.save(client_id=self.request.user.client_id)
            Inventory.objects.create(product=product, branch=request_branch(self.request))

    def get_queryset(self):
        queryset = super().get_queryset().filter(client_id=self.request.user.client_id)
        branch = request_branch(self.request)
        if branch:
            queryset = queryset.filter(inventory__branch=branch)
        active = self.request.query_params.get('active')
        if active in {'true', 'false'}:
            return queryset.filter(is_active=active == 'true')
        return queryset


class InventoryViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'INVENTORY_MANAGER'}
    queryset = Inventory.objects.select_related('product').all().order_by('product__name')
    serializer_class = InventorySerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(product__client_id=self.request.user.client_id)
        branch = request_branch(self.request)
        return queryset.filter(branch=branch) if branch else queryset

    @action(detail=False, methods=['post'], url_path='set-level')
    def set_level(self, request):
        request_serializer = SetInventorySerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        data = request_serializer.validated_data
        with transaction.atomic():
            try:
                user = User.objects.get(pk=data['adjusted_by'], is_active=True)
                inventory = Inventory.objects.select_for_update().get(product__sku=data['sku'], product__client_id=request.user.client_id, branch=request_branch(request))
            except (User.DoesNotExist, Inventory.DoesNotExist) as exc:
                raise serializers.ValidationError({'detail': 'Active user and product inventory are required.'}) from exc
            quantity_change = data['quantity_on_hand'] - inventory.quantity_on_hand
            inventory.quantity_on_hand = data['quantity_on_hand']
            for field in ('reorder_level', 'reorder_quantity'):
                if field in data:
                    setattr(inventory, field, data[field])
            inventory.save()
            InventoryAdjustment.objects.create(
                inventory=inventory,
                adjusted_by=user,
                adjustment_type=InventoryAdjustment.AdjustmentType.MANUAL,
                quantity_change=quantity_change,
                reason='Inventory level set',
            )
        return Response(InventorySerializer(inventory).data, status=status.HTTP_200_OK)

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
                    product__client_id=request.user.client_id,
                    branch=request_branch(request),
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
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'INVENTORY_MANAGER'}
    queryset = InventoryAdjustment.objects.select_related('inventory', 'adjusted_by').all().order_by('-adjustment_date')
    serializer_class = InventoryAdjustmentSerializer

    def get_queryset(self):
        queryset = super().get_queryset().filter(inventory__product__client_id=self.request.user.client_id)
        branch = request_branch(self.request)
        return queryset.filter(inventory__branch=branch) if branch else queryset
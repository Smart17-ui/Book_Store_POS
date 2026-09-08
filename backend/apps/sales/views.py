from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from .services import process_sale
from apps.accounts.permissions import RolePermission
from .models import Customer, Sale, SaleItem
from .serializers import CustomerSerializer, ProcessSaleSerializer, SaleItemSerializer, SaleSerializer


class CustomerViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = Customer.objects.all().order_by('last_name', 'first_name')
    serializer_class = CustomerSerializer

    def get_queryset(self):
        return super().get_queryset().filter(client_id=self.request.user.client_id)

    def perform_create(self, serializer):
        serializer.save(client_id=self.request.user.client_id)


class SaleViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = Sale.objects.prefetch_related('items').select_related('customer', 'cashier').all().order_by('-sale_date')
    serializer_class = SaleSerializer

    def get_queryset(self):
        return super().get_queryset().filter(cashier__client_id=self.request.user.client_id)

    @action(detail=False, methods=['post'], url_path='process')
    def process(self, request):
        request_serializer = ProcessSaleSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        sale_data = request_serializer.validated_data.copy()
        sale_data['cashier'] = request.user.id
        sale, payment, receipt, change = process_sale(**sale_data)
        return Response({
            'sale': SaleSerializer(sale).data,
            'payment_id': payment.id,
            'receipt_id': receipt.id,
            'change': f'{change:.2f}',
        }, status=status.HTTP_201_CREATED)


class SaleItemViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = SaleItem.objects.select_related('sale', 'product').all()
    serializer_class = SaleItemSerializer

    def get_queryset(self):
        return super().get_queryset().filter(sale__cashier__client_id=self.request.user.client_id)
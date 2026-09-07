from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet

from .services import process_sale
from .models import Customer, Sale, SaleItem
from .serializers import CustomerSerializer, ProcessSaleSerializer, SaleItemSerializer, SaleSerializer


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all().order_by('last_name', 'first_name')
    serializer_class = CustomerSerializer


class SaleViewSet(ModelViewSet):
    queryset = Sale.objects.prefetch_related('items').select_related('customer', 'cashier').all().order_by('-sale_date')
    serializer_class = SaleSerializer

    @action(detail=False, methods=['post'], url_path='process')
    def process(self, request):
        request_serializer = ProcessSaleSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        sale, payment, receipt, change = process_sale(**request_serializer.validated_data)
        return Response({
            'sale': SaleSerializer(sale).data,
            'payment_id': payment.id,
            'receipt_id': receipt.id,
            'change': f'{change:.2f}',
        }, status=status.HTTP_201_CREATED)


class SaleItemViewSet(ModelViewSet):
    queryset = SaleItem.objects.select_related('sale', 'product').all()
    serializer_class = SaleItemSerializer
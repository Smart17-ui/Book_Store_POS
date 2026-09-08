from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Refund, Return
from .serializers import ProcessReturnSerializer, RefundSerializer, ReturnSerializer
from .services import process_return
from apps.accounts.permissions import RolePermission


class ReturnViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = Return.objects.prefetch_related('items').select_related('sale', 'customer', 'cashier').all().order_by('-return_date')
    serializer_class = ReturnSerializer

    def get_queryset(self):
        return super().get_queryset().filter(cashier__client_id=self.request.user.client_id)

    @action(detail=False, methods=['post'], url_path='process')
    def process(self, request):
        request_serializer = ProcessReturnSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        return_record, receipt = process_return(**request_serializer.validated_data)
        return Response({
            'return': ReturnSerializer(return_record).data,
            'receipt_id': receipt.id,
        }, status=status.HTTP_201_CREATED)


class RefundViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = Refund.objects.select_related('return_record', 'refund_method').all().order_by('-refund_date')
    serializer_class = RefundSerializer

    def get_queryset(self):
        return super().get_queryset().filter(return_record__cashier__client_id=self.request.user.client_id)
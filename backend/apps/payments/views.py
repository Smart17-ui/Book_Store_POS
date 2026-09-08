from rest_framework.viewsets import ModelViewSet

from .models import Payment, PaymentMethod
from apps.accounts.permissions import RolePermission
from .serializers import PaymentMethodSerializer, PaymentSerializer


class PaymentMethodViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = PaymentMethod.objects.all().order_by('name')
    serializer_class = PaymentMethodSerializer


class PaymentViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = Payment.objects.select_related('sale', 'payment_method').all().order_by('-payment_date')
    serializer_class = PaymentSerializer

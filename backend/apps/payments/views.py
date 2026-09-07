from rest_framework.viewsets import ModelViewSet

from .models import Payment, PaymentMethod
from .serializers import PaymentMethodSerializer, PaymentSerializer


class PaymentMethodViewSet(ModelViewSet):
    queryset = PaymentMethod.objects.all().order_by('name')
    serializer_class = PaymentMethodSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.select_related('sale', 'payment_method').all().order_by('-payment_date')
    serializer_class = PaymentSerializer

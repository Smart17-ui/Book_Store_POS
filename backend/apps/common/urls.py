from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.inventory.views import CategoryViewSet, InventoryAdjustmentViewSet, InventoryViewSet, ProductViewSet
from apps.accounts.urls import urlpatterns as account_urlpatterns
from apps.payments.views import PaymentMethodViewSet, PaymentViewSet
from apps.reports.views import ReceiptViewSet, SalesReportView
from apps.returns.views import RefundViewSet, ReturnViewSet
from apps.sales.views import CustomerViewSet, SaleItemViewSet, SaleViewSet

router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('inventory', InventoryViewSet)
router.register('inventory-adjustments', InventoryAdjustmentViewSet)
router.register('customers', CustomerViewSet)
router.register('sales', SaleViewSet)
router.register('sale-items', SaleItemViewSet)
router.register('returns', ReturnViewSet)
router.register('refunds', RefundViewSet)
router.register('receipts', ReceiptViewSet)
router.register('payment-methods', PaymentMethodViewSet)
router.register('payments', PaymentViewSet)

urlpatterns = [
	path('auth/', include(account_urlpatterns)),
	path('', include(router.urls)),
	path('reports/sales/', SalesReportView.as_view(), name='sales-report'),
]
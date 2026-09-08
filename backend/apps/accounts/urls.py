from django.urls import path

from .views import BranchManagementView, CashierManagementView, CashierPinLoginView, ClientManagementView, LoginView, SignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='account-signup'),
    path('login/', LoginView.as_view(), name='account-login'),
    path('cashier-login/', CashierPinLoginView.as_view(), name='cashier-pin-login'),
    path('client/', ClientManagementView.as_view(), name='client-management'),
    path('branches/', BranchManagementView.as_view(), name='branch-management'),
    path('cashiers/', CashierManagementView.as_view(), name='cashier-management'),
    path('cashiers/<uuid:user_id>/', CashierManagementView.as_view(), name='cashier-detail'),
]

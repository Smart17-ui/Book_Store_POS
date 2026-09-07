from django.urls import path

from .views import LoginView, SignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='account-signup'),
    path('login/', LoginView.as_view(), name='account-login'),
]

from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Role, User
from .serializers import AccountSerializer, LoginSerializer, SignupSerializer


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        role, _ = Role.objects.get_or_create(
            name=User.UserRole.CASHIER,
            defaults={'description': 'Bookstore operations user'},
        )
        user = User.objects.create(
            username=data['username'],
            full_name=data['full_name'],
            email=data['email'],
            password_hash=make_password(data['password']),
            role=role,
        )
        return Response(AccountSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        login = serializer.validated_data['login']
        user = User.objects.filter(username__iexact=login).first() or User.objects.filter(email__iexact=login).first()
        password = serializer.validated_data['password']
        valid_password = False
        legacy_password = False
        if user and user.is_active:
            try:
                identify_hasher(user.password_hash)
                valid_password = check_password(password, user.password_hash)
            except ValueError:
                valid_password = password == user.password_hash
                legacy_password = valid_password
        if not user or not user.is_active or not valid_password:
            return Response({'detail': 'Invalid username/email or password.'}, status=status.HTTP_400_BAD_REQUEST)
        if legacy_password:
            user.password_hash = make_password(password)
        user.last_login = timezone.now()
        user.save(update_fields=('password_hash', 'last_login', 'updated_at'))
        return Response(AccountSerializer(user).data)

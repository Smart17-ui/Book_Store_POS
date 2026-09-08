from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Branch, Client, Role, SessionToken, User
from .serializers import AccountSerializer, BranchSerializer, CashierPinLoginSerializer, CashierSerializer, ClientSerializer, LoginSerializer, SessionAccountSerializer, SignupSerializer


def account_response(user):
    data = AccountSerializer(user).data
    data['token'] = SessionToken.objects.create(user=user).key
    return data


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        with transaction.atomic():
            client = Client.objects.create(
                name=data['company_name'],
                pos_name=data['pos_name'],
            )
            Branch.objects.create(
                client=client,
                name='Main branch',
                code='MAIN',
            )
            role, _ = Role.objects.get_or_create(
                name=User.UserRole.OWNER,
                defaults={'description': 'Client system owner'},
            )
            user = User.objects.create(
                username=data['username'],
                full_name=data['full_name'],
                email=data['email'],
                password_hash=make_password(data['password']),
                role=role,
                client=client,
            )
        return Response(account_response(user), status=status.HTTP_201_CREATED)


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
        return Response(account_response(user))


class CashierPinLoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = CashierPinLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = User.objects.filter(username__iexact=data['username'], role__name=User.UserRole.CASHIER, is_active=True).select_related('role', 'client', 'branch').first()
        if not user or not user.pin_hash or not check_password(data['pin'], user.pin_hash):
            return Response({'detail': 'Invalid cashier username or PIN.'}, status=status.HTTP_400_BAD_REQUEST)
        user.last_login = timezone.now()
        user.save(update_fields=('last_login', 'updated_at'))
        return Response(account_response(user))


class ClientManagementView(APIView):
    def get(self, request):
        client = Client.objects.prefetch_related('branches').filter(id=request.user.client_id).first()
        if not client:
            return Response(None)
        return Response(ClientSerializer(client).data)

    def post(self, request):
        if request.user.client_id:
            return Response({'detail': 'Your account is already linked to a company.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ClientSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        client = serializer.save()
        return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)

    def patch(self, request):
        if request.user.role.name not in (User.UserRole.OWNER, User.UserRole.ADMIN):
            return Response({'detail': 'Only an owner or administrator can update company settings.'}, status=status.HTTP_403_FORBIDDEN)
        client = Client.objects.filter(id=request.user.client_id).first()
        if not client:
            return self.post(request)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(ClientSerializer(serializer.save()).data)


class BranchManagementView(APIView):
    def get(self, request):
        return Response(BranchSerializer(Branch.objects.filter(client_id=request.user.client_id).order_by('name'), many=True).data)

    def post(self, request):
        if request.user.role.name not in (User.UserRole.OWNER, User.UserRole.ADMIN):
            return Response({'detail': 'Only an owner or administrator can manage branches.'}, status=status.HTTP_403_FORBIDDEN)
        if request.data.get('client') != str(request.user.client_id):
            return Response({'detail': 'Branch must belong to your company.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = BranchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CashierManagementView(APIView):
    def get(self, request):
        queryset = User.objects.filter(client_id=request.user.client_id, role__name=User.UserRole.CASHIER).select_related('branch')
        return Response(CashierSerializer(queryset.order_by('full_name'), many=True).data)

    def post(self, request):
        if request.user.role.name not in (User.UserRole.OWNER, User.UserRole.ADMIN):
            return Response({'detail': 'Only an owner or administrator can manage cashiers.'}, status=status.HTTP_403_FORBIDDEN)
        if request.data.get('client') != str(request.user.client_id):
            return Response({'detail': 'Cashier must belong to your company.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CashierSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(CashierSerializer(serializer.save()).data, status=status.HTTP_201_CREATED)

    def patch(self, request, user_id):
        if request.user.role.name not in (User.UserRole.OWNER, User.UserRole.ADMIN):
            return Response({'detail': 'Only an owner or administrator can manage cashiers.'}, status=status.HTTP_403_FORBIDDEN)
        cashier = User.objects.get(id=user_id, client_id=request.user.client_id, role__name=User.UserRole.CASHIER)
        serializer = CashierSerializer(cashier, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        return Response(CashierSerializer(serializer.save()).data)

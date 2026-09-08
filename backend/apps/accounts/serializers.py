from rest_framework import serializers

from .models import Branch, Client, Role, User


class AccountSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source='role.name', read_only=True)
    client_name = serializers.CharField(source='client.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'email', 'role', 'role_name', 'client', 'client_name', 'branch', 'branch_name')


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ('id', 'client', 'name', 'code', 'address', 'is_active')


class ClientSerializer(serializers.ModelSerializer):
    branches = BranchSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = ('id', 'name', 'pos_name', 'primary_color', 'secondary_color', 'is_active', 'branches')


class CashierSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(write_only=True, required=False, min_length=4, max_length=8)
    role_name = serializers.CharField(source='role.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'full_name', 'username', 'email', 'client', 'branch', 'branch_name', 'role_name', 'is_active', 'pin')
        read_only_fields = ('role_name',)

    def create(self, validated_data):
        from django.contrib.auth.hashers import make_password
        pin = validated_data.pop('pin')
        role, _ = Role.objects.get_or_create(name=User.UserRole.CASHIER)
        return User.objects.create(
            **validated_data,
            role=role,
            password_hash=make_password(pin),
            pin_hash=make_password(pin),
        )

    def update(self, instance, validated_data):
        from django.contrib.auth.hashers import make_password
        pin = validated_data.pop('pin', None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if pin:
            instance.pin_hash = make_password(pin)
        instance.save()
        return instance


class SignupSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=160)
    pos_name = serializers.CharField(max_length=160)
    full_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    password_confirmation = serializers.CharField(min_length=8, write_only=True, required=False)

    def validate(self, attrs):
        confirmation = attrs.pop('password_confirmation', None)
        if confirmation is not None and confirmation != attrs['password']:
            raise serializers.ValidationError({'password_confirmation': 'Passwords do not match.'})
        return attrs

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('That username is already in use.')
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('That email is already registered.')
        return value


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField()
    password = serializers.CharField(write_only=True)


class SessionAccountSerializer(AccountSerializer):
    token = serializers.CharField(read_only=True)


class CashierPinLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    pin = serializers.CharField(min_length=4, max_length=8, write_only=True)

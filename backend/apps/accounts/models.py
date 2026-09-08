from django.db import models
import secrets

from apps.common.models import UUIDModel


class Role(UUIDModel):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Client(UUIDModel):
    name = models.CharField(max_length=160)
    pos_name = models.CharField(max_length=160)
    primary_color = models.CharField(max_length=7, default='#236d49')
    secondary_color = models.CharField(max_length=7, default='#d9f0e1')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Branch(UUIDModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=30)
    address = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('client', 'code'), name='unique_branch_code_per_client'),
        ]

    def __str__(self):
        return f'{self.client.name} - {self.name}'


class Permission(UUIDModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class User(UUIDModel):
    class UserRole(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        MANAGER = 'MANAGER', 'Manager'
        CASHIER = 'CASHIER', 'Cashier'
        INVENTORY_MANAGER = 'INVENTORY_MANAGER', 'Inventory manager'
        OWNER = 'OWNER', 'Owner'

    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')
    permissions = models.ManyToManyField(Permission, blank=True, related_name='users')
    is_active = models.BooleanField(default=True)
    pin_hash = models.CharField(max_length=255, blank=True)
    last_login = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

    @property
    def is_authenticated(self):
        return True


class SessionToken(UUIDModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='session_tokens')
    key = models.CharField(max_length=64, unique=True, default=secrets.token_urlsafe)
    last_used_at = models.DateTimeField(null=True, blank=True)

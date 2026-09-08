from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.accounts.models import Branch, Client, User
from apps.common.models import UUIDModel


class Category(UUIDModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children',
    )

    def __str__(self):
        return self.name


class Product(UUIDModel):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    sku = models.CharField(max_length=80, unique=True)
    name = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    edition = models.CharField(max_length=80, blank=True)
    publisher = models.CharField(max_length=160, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    publication_date = models.DateField(null=True, blank=True)
    language = models.CharField(max_length=80, default='English', blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    cost_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    barcode = models.CharField(max_length=80, blank=True, unique=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.sku} - {self.name}'

    def is_low_stock(self):
        return hasattr(self, 'inventory') and self.inventory.is_low_stock()


class Inventory(UUIDModel):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='inventory')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, related_name='inventory')
    quantity_on_hand = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    reorder_level = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    reorder_quantity = models.DecimalField(max_digits=12, decimal_places=3, default=Decimal('0'), validators=[MinValueValidator(Decimal('0'))])
    last_updated = models.DateTimeField(auto_now=True)

    def is_low_stock(self):
        return self.quantity_on_hand <= self.reorder_level


class InventoryAdjustment(UUIDModel):
    class AdjustmentType(models.TextChoices):
        RESTOCK = 'RESTOCK', 'Restock'
        SALE = 'SALE', 'Sale'
        DAMAGED = 'DAMAGED', 'Damaged'
        RETURN = 'RETURN', 'Return'
        MANUAL = 'MANUAL_ADJUSTMENT', 'Manual adjustment'

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name='adjustments')
    adjusted_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inventory_adjustments')
    adjustment_type = models.CharField(max_length=30, choices=AdjustmentType.choices)
    quantity_change = models.DecimalField(max_digits=12, decimal_places=3)
    reason = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, blank=True)
    adjustment_date = models.DateTimeField(auto_now_add=True)

    def get_new_quantity(self):
        return self.inventory.quantity_on_hand + self.quantity_change

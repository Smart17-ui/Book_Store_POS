from django.contrib import admin

from .models import Category, Inventory, InventoryAdjustment, Product

admin.site.register([Category, Inventory, InventoryAdjustment, Product])

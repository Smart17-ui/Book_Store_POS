from django.contrib import admin

from .models import Customer, Sale, SaleItem

admin.site.register([Customer, Sale, SaleItem])

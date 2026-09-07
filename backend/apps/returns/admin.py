from django.contrib import admin

from .models import Refund, RefundMethod, Return, ReturnItem

admin.site.register([Refund, RefundMethod, Return, ReturnItem])

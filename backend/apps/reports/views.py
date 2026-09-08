import csv
from datetime import date, datetime, time, timedelta
from decimal import Decimal

import numpy as np
import pandas as pd
from django.db.models import Sum
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from apps.accounts.permissions import RolePermission

from apps.inventory.models import InventoryAdjustment, Product
from apps.accounts.branch import request_branch
from apps.sales.models import Sale, SaleItem
from .models import Receipt
from .serializers import ReceiptSerializer


class ReceiptViewSet(ModelViewSet):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'CASHIER'}
    queryset = Receipt.objects.select_related('sale').all().order_by('-receipt_date')
    serializer_class = ReceiptSerializer

    def get_queryset(self):
        return super().get_queryset().filter(sale__cashier__client_id=self.request.user.client_id)


class ReportsView(APIView):
    permission_classes = (RolePermission,)
    allowed_roles = {'OWNER', 'ADMIN', 'MANAGER', 'INVENTORY_MANAGER'}
    @staticmethod
    def _parse_dates(request):
        start_raw = request.query_params.get('start_date')
        end_raw = request.query_params.get('end_date')
        if start_raw and end_raw:
            start_date = datetime.strptime(start_raw, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_raw, '%Y-%m-%d').date()
        else:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
        if end_date < start_date:
            raise ValueError('end_date must not be before start_date.')
        return start_date, end_date

    @staticmethod
    def _as_float(value):
        return float(value or 0)

    def get(self, request):
        report_type = request.query_params.get('report_type', 'sales').lower()
        product_name = request.query_params.get('product_name', '').strip()
        try:
            start_date, end_date = self._parse_dates(request)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        start = timezone.make_aware(datetime.combine(start_date, time.min))
        end = timezone.make_aware(datetime.combine(end_date, time.max))

        if report_type == 'sales':
            return self.sales_report(request, start, end, product_name)
        if report_type == 'stock_balance':
            return self.stock_balance_report(request, start, end, product_name)
        if report_type == 'stock_value':
            return self.stock_value_report(request, start, end, product_name)
        return Response({'detail': 'Unsupported report_type. Use sales, stock_balance, or stock_value.'}, status=status.HTTP_400_BAD_REQUEST)

    def sales_report(self, request, start, end, product_name):
        sale_items = SaleItem.objects.filter(
            sale__status=Sale.SaleStatus.COMPLETED,
            sale__sale_date__range=(start, end),
            sale__cashier__client_id=request.user.client_id,
        ).select_related('sale', 'product')
        if product_name:
            sale_items = sale_items.filter(product__name__icontains=product_name)

        rows = [
            {
                'sale_number': item.sale.sale_number,
                'sale_date': item.sale.sale_date.isoformat(),
                'product_name': item.product.name,
                'sku': item.product.sku,
                'quantity': float(item.quantity),
                'unit_price': float(item.unit_price),
                'gross_sales': float(item.quantity * item.unit_price),
                'discount_amount': float(item.discount_amount),
                'tax_amount': float(item.tax_amount),
                'line_total': float(item.line_total),
            }
            for item in sale_items.order_by('sale__sale_date', 'product__name')
        ]
        frame = pd.DataFrame(rows)
        if frame.empty:
            totals = {'gross_sales': 0.0, 'discounts': 0.0, 'taxes': 0.0, 'net_sales': 0.0, 'transaction_count': 0}
        else:
            totals = {
                'gross_sales': float(frame['gross_sales'].sum()),
                'discounts': float(frame['discount_amount'].sum()),
                'taxes': float(frame['tax_amount'].sum()),
                'net_sales': float(frame['line_total'].sum()),
                'transaction_count': int(frame['sale_number'].nunique()),
            }

        data = {
            'report_type': 'sales',
            'start_date': start.date().isoformat(),
            'end_date': end.date().isoformat(),
            'product_name': product_name,
            'rows': rows,
            'totals': totals,
        }
        return self._respond(request, data, 'sales-report')

    def stock_balance_report(self, request, start, end, product_name):
        branch = request_branch(request)
        products = Product.objects.select_related('category', 'inventory').filter(is_active=True, client_id=request.user.client_id)
        if branch:
            products = products.filter(inventory__branch=branch)
        if product_name:
            products = products.filter(name__icontains=product_name)

        movement = {}
        for adjustment in InventoryAdjustment.objects.filter(
            adjustment_date__range=(start, end),
            inventory__product__client_id=request.user.client_id,
            **({'inventory__branch': branch} if branch else {}),
        ).values('inventory__product_id').annotate(total_change=Sum('quantity_change')):
            movement[adjustment['inventory__product_id']] = float(adjustment['total_change'] or 0)

        rows = []
        for product in products.order_by('name'):
            inventory = getattr(product, 'inventory', None)
            quantity = getattr(inventory, 'quantity_on_hand', Decimal('0')) or Decimal('0')
            rows.append({
                'product_name': product.name,
                'sku': product.sku,
                'category': product.category.name,
                'quantity_on_hand': float(quantity),
                'reorder_level': float(getattr(inventory, 'reorder_level', 0) or 0),
                'movement_in_period': movement.get(product.id, 0.0),
                'unit_price': float(product.unit_price),
                'stock_value': float(quantity * product.unit_price),
                'last_updated': inventory.last_updated.isoformat() if inventory else None,
            })

        frame = pd.DataFrame(rows)
        totals = {
            'total_products': int(len(rows)),
            'total_units': float(frame['quantity_on_hand'].sum()) if not frame.empty else 0.0,
            'total_stock_value': float(frame['stock_value'].sum()) if not frame.empty else 0.0,
        }
        data = {
            'report_type': 'stock_balance',
            'start_date': start.date().isoformat(),
            'end_date': end.date().isoformat(),
            'product_name': product_name,
            'rows': rows,
            'totals': totals,
        }
        return self._respond(request, data, 'stock-balance-report')

    def stock_value_report(self, request, start, end, product_name):
        branch = request_branch(request)
        products = Product.objects.select_related('category', 'inventory').filter(is_active=True, client_id=request.user.client_id)
        if branch:
            products = products.filter(inventory__branch=branch)
        if product_name:
            products = products.filter(name__icontains=product_name)

        rows = []
        for product in products.order_by('-unit_price'):
            inventory = getattr(product, 'inventory', None)
            quantity = getattr(inventory, 'quantity_on_hand', Decimal('0')) or Decimal('0')
            value = float(quantity * product.unit_price)
            rows.append({
                'product_name': product.name,
                'sku': product.sku,
                'category': product.category.name,
                'quantity_on_hand': float(quantity),
                'unit_price': float(product.unit_price),
                'stock_value': value,
                'reorder_level': float(getattr(inventory, 'reorder_level', 0) or 0),
            })

        frame = pd.DataFrame(rows)
        totals = {
            'total_products': int(len(rows)),
            'total_units': float(frame['quantity_on_hand'].sum()) if not frame.empty else 0.0,
            'total_stock_value': float(frame['stock_value'].sum()) if not frame.empty else 0.0,
        }
        data = {
            'report_type': 'stock_value',
            'start_date': start.date().isoformat(),
            'end_date': end.date().isoformat(),
            'product_name': product_name,
            'rows': rows,
            'totals': totals,
        }
        return self._respond(request, data, 'stock-value-report')

    @staticmethod
    def _respond(request, data, file_prefix):
        report_format = request.query_params.get('export', 'json').lower()
        if report_format == 'csv':
            return ReportsView.as_csv(data, file_prefix)
        if report_format == 'pdf':
            return ReportsView.as_pdf(data, file_prefix)
        return Response(data)

    @staticmethod
    def as_csv(data, file_prefix):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{file_prefix}.csv"'
        writer = csv.writer(response)
        writer.writerow([data['report_type'].replace('_', ' ').title(), data['start_date'], data['end_date']])
        if data.get('product_name'):
            writer.writerow(['Product filter', data['product_name']])
        writer.writerow([])
        writer.writerow(['Metric', 'Value'])
        for key, value in data['totals'].items():
            writer.writerow([key.replace('_', ' ').title(), value])
        writer.writerow([])
        rows = data.get('rows', [])
        if rows:
            headers = list(rows[0].keys())
            writer.writerow(headers)
            for row in rows:
                writer.writerow([row.get(header, '') for header in headers])
        return response

    @staticmethod
    def as_pdf(data, file_prefix):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{file_prefix}.pdf"'
        document = SimpleDocTemplate(response, pagesize=letter, rightMargin=0.5 * inch, leftMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        elements = [
            Paragraph(data['report_type'].replace('_', ' ').title(), styles['Title']),
            Paragraph(f"{data['start_date']} to {data['end_date']}", styles['Normal']),
            Spacer(1, 12),
        ]
        summary = [['Metric', 'Value']]
        for key, value in data['totals'].items():
            summary.append([key.replace('_', ' ').title(), str(value)])
        table = Table(summary, colWidths=[2.5 * inch, 2 * inch])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        elements.append(table)
        document.build(elements)
        return response


class SalesReportView(ReportsView):
    pass

import csv
from datetime import datetime, time
from decimal import Decimal

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

from apps.sales.models import Sale
from .models import Receipt
from .serializers import ReceiptSerializer


class ReceiptViewSet(ModelViewSet):
    queryset = Receipt.objects.select_related('sale').all().order_by('-receipt_date')
    serializer_class = ReceiptSerializer


class SalesReportView(APIView):
    def get(self, request):
        try:
            start_date = datetime.strptime(request.query_params['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.query_params['end_date'], '%Y-%m-%d').date()
        except (KeyError, ValueError):
            return Response(
                {'detail': 'start_date and end_date are required in YYYY-MM-DD format.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if end_date < start_date:
            return Response({'detail': 'end_date must not be before start_date.'}, status=status.HTTP_400_BAD_REQUEST)

        start = timezone.make_aware(datetime.combine(start_date, time.min))
        end = timezone.make_aware(datetime.combine(end_date, time.max))
        sales = Sale.objects.filter(
            status=Sale.SaleStatus.COMPLETED,
            sale_date__range=(start, end),
        ).prefetch_related('payments__payment_method').order_by('sale_date')
        gross_sales = sum((sale.subtotal for sale in sales), Decimal('0'))
        discounts = sum((sale.discount_amount for sale in sales), Decimal('0'))
        taxes = sum((sale.tax_amount for sale in sales), Decimal('0'))
        net_sales = sum((sale.total_amount for sale in sales), Decimal('0'))
        payment_breakdown = {}
        transactions = []
        for sale in sales:
            transactions.append({
                'sale_number': sale.sale_number,
                'sale_date': sale.sale_date,
                'gross_sales': sale.subtotal,
                'discounts': sale.discount_amount,
                'taxes': sale.tax_amount,
                'net_sales': sale.total_amount,
            })
            for payment in sale.payments.all():
                key = payment.payment_method.type
                payment_breakdown[key] = payment_breakdown.get(key, Decimal('0')) + payment.amount
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'transaction_count': len(transactions),
            'gross_sales': gross_sales,
            'discounts': discounts,
            'taxes': taxes,
            'net_sales': net_sales,
            'payment_breakdown': payment_breakdown,
            'transactions': transactions,
        }
        report_format = request.query_params.get('export', 'json').lower()
        if report_format == 'csv':
            return self.as_csv(data)
        if report_format == 'pdf':
            return self.as_pdf(data)
        return Response(self.as_json(data))

    @staticmethod
    def as_json(data):
        return {
            'start_date': data['start_date'],
            'end_date': data['end_date'],
            'transaction_count': data['transaction_count'],
            'gross_sales': f"{data['gross_sales']:.2f}",
            'discounts': f"{data['discounts']:.2f}",
            'taxes': f"{data['taxes']:.2f}",
            'net_sales': f"{data['net_sales']:.2f}",
            'payment_breakdown': {key: f'{value:.2f}' for key, value in data['payment_breakdown'].items()},
            'transactions': [
                {**row, 'sale_date': row['sale_date'], **{
                    field: f'{row[field]:.2f}' for field in ('gross_sales', 'discounts', 'taxes', 'net_sales')
                }} for row in data['transactions']
            ],
        }

    @staticmethod
    def as_csv(data):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="sales-report.csv"'
        writer = csv.writer(response)
        writer.writerow(['Sales Report', data['start_date'], data['end_date']])
        writer.writerow(['Transaction count', data['transaction_count']])
        writer.writerow(['Gross sales', f"{data['gross_sales']:.2f}"])
        writer.writerow(['Discounts', f"{data['discounts']:.2f}"])
        writer.writerow(['Taxes', f"{data['taxes']:.2f}"])
        writer.writerow(['Net sales', f"{data['net_sales']:.2f}"])
        writer.writerow([])
        writer.writerow(['Payment method', 'Amount'])
        for key, value in data['payment_breakdown'].items():
            writer.writerow([key, f'{value:.2f}'])
        writer.writerow([])
        writer.writerow(['Sale number', 'Sale date', 'Gross', 'Discounts', 'Taxes', 'Net'])
        for row in data['transactions']:
            writer.writerow([row['sale_number'], row['sale_date'], row['gross_sales'], row['discounts'], row['taxes'], row['net_sales']])
        return response

    @staticmethod
    def as_pdf(data):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sales-report.pdf"'
        document = SimpleDocTemplate(response, pagesize=letter, rightMargin=0.5 * inch, leftMargin=0.5 * inch)
        styles = getSampleStyleSheet()
        elements = [Paragraph('Sales Report', styles['Title']), Paragraph(f"{data['start_date']} to {data['end_date']}", styles['Normal']), Spacer(1, 12)]
        summary = [
            ['Metric', 'Amount'],
            ['Transactions', str(data['transaction_count'])],
            ['Gross sales', f"{data['gross_sales']:.2f}"],
            ['Discounts', f"{data['discounts']:.2f}"],
            ['Taxes', f"{data['taxes']:.2f}"],
            ['Net sales', f"{data['net_sales']:.2f}"],
        ]
        table = Table(summary, colWidths=[2.5 * inch, 2 * inch])
        table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)]))
        elements.append(table)
        document.build(elements)
        return response
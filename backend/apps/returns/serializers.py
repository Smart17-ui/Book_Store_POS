from django.db import transaction
from rest_framework import serializers

from .models import Refund, RefundMethod, Return, ReturnItem


class ReturnItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnItem
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'line_total', 'return_record')


class ReturnSerializer(serializers.ModelSerializer):
    items = ReturnItemSerializer(many=True, required=False)

    class Meta:
        model = Return
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'total_refund_amount')

    def create(self, validated_data):
        items = validated_data.pop('items', [])
        with transaction.atomic():
            return_record = Return.objects.create(**validated_data)
            for item in items:
                return_item = ReturnItem.objects.create(return_record=return_record, **item)
                return_item.calculate_line_total()
                return_item.save(update_fields=('line_total', 'updated_at'))
            return_record.calculate_total()
            return_record.save(update_fields=('total_refund_amount', 'updated_at'))
        return return_record


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class ProcessReturnSerializer(serializers.Serializer):
    cashier = serializers.UUIDField()
    receipt_number = serializers.CharField(max_length=40)
    items = serializers.ListField(child=serializers.DictField(), allow_empty=False)
    refund_method_type = serializers.ChoiceField(choices=RefundMethod.MethodType.choices)
    refund_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    return_reason = serializers.CharField(required=False, allow_blank=True)
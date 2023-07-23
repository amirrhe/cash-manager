from django.db import transaction

from rest_framework import serializers
from apps.transaction.models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'transaction_type', 'category', 'created', 'updated']
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class TransactionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'amount', 'transaction_type', 'category', 'created', 'updated']
        read_only_fields = ['user']

    def update(self, instance, validated_data):
        new_amount = validated_data.get('amount')
        old_amount = instance.amount

        if new_amount is not None:
            new_amount = int(new_amount)
        if old_amount is not None:
            old_amount = int(old_amount)

        amount_diff = new_amount - old_amount if new_amount is not None and old_amount is not None else 0
        if instance.transaction_type == 'income':
            instance.user.balance += amount_diff
        elif instance.transaction_type == 'expense':
            instance.user.balance -= amount_diff

        with transaction.atomic():
            instance.user.save()
            instance = super().update(instance, validated_data)

        return instance


class MonthlySummaryReportSerializer(serializers.Serializer):
    month = serializers.IntegerField(min_value=1, max_value=12)
    year = serializers.IntegerField(min_value=1900, max_value=9999)

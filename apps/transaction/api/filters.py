import django_filters
from apps.transaction.models import Transaction


class TransactionFilter(django_filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'transaction_type': ['exact'],
            'category': ['exact'],
            'created': ['date__gte', 'date__lte'],
            'updated': ['date__gte', 'date__lte'],
        }

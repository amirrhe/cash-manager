from django.db import transaction

from rest_framework.generics import (
    CreateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView, RetrieveAPIView)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.transaction.api.serializer import (
    TransactionSerializer, TransactionUpdateSerializer, MonthlySummaryReportSerializer)
from apps.transaction.models import Transaction
from apps.transaction.api.filters import TransactionFilter


class TransactionCreateView(CreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    @transaction.atomic
    def perform_create(self, serializer):
        with transaction.atomic():
            transaction_instance = serializer.save(user=self.request.user)
            transaction_instance.update_user_balance()


class TransactionListView(ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TransactionFilter

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionRetrieveView(RetrieveAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionUpdateView(UpdateAPIView):
    serializer_class = TransactionUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class TransactionDeleteView(DestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    # comment this line beacuse i dont know should balance decrease or increase when transaction deleted
    # @transaction.atomic
    # def perform_destroy(self, instance):
    #     if instance.transaction_type == 'income':
    #         self.request.user.balance -= instance.amount
    #     elif instance.transaction_type == 'expense':
    #         self.request.user.balance += instance.amount

    #     self.request.user.save()

    #     instance.delete()

    #     return Response({"detail": "Transaction deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


class MonthlySummaryReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MonthlySummaryReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        month = serializer.validated_data['month']
        year = serializer.validated_data['year']

        user = request.user
        transactions = Transaction.objects.filter(user=user, created__year=year, created__month=month)

        total_income = sum(
            transaction.amount for transaction in transactions if transaction.transaction_type == 'income')
        total_expense = sum(
            transaction.amount for transaction in transactions if transaction.transaction_type == 'expense')

        return Response({
            'month': month,
            'year': year,
            'total_income': total_income,
            'total_expense': total_expense,
            'net_cash_flow': total_income - total_expense,
        })


class CategoryExpenseReportView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MonthlySummaryReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        month = serializer.validated_data['month']
        year = serializer.validated_data['year']

        user = request.user
        transactions = Transaction.objects.filter(
            user=user,
            transaction_type='expense',
            created__year=year,
            created__month=month)

        category_expenses = {}
        for transaction_obj in transactions:
            category = transaction_obj.category
            amount = transaction_obj.amount
            category_expenses[category] = category_expenses.get(category, 0) + amount

        return Response({
            'month': month,
            'year': year,
            'category_expenses': category_expenses,
        })

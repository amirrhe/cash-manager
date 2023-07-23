from django.urls import path
from apps.transaction.api.views import (
    TransactionCreateView, TransactionListView, TransactionUpdateView,
    TransactionDeleteView, TransactionRetrieveView, MonthlySummaryReportView,
    CategoryExpenseReportView)

urlpatterns = [
    path('transactions/', TransactionCreateView.as_view(), name='create_transaction'),
    path('transactions/list/', TransactionListView.as_view(), name='transaction_list'),
    path('transactions/<int:pk>/', TransactionUpdateView.as_view(), name='transaction_update'),
    path('transactions/<int:pk>/delete/', TransactionDeleteView.as_view(), name='transaction_delete'),
    path('transactions/<int:pk>/retrive/', TransactionRetrieveView.as_view(), name='transaction_retrive'),
    path('reports/monthly-summary/', MonthlySummaryReportView.as_view(), name='monthly_summary_report'),
    path('reports/category-wise-expense/', CategoryExpenseReportView.as_view(), name='category_wise_expense_report'),
]

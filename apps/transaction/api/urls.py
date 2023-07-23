from django.urls import path
from apps.transaction.api.views import TransactionCreateView

urlpatterns = [
    path('transaction/', TransactionCreateView.as_view(), name='create_transaction')
]

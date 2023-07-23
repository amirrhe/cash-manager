from django.db import models
from apps.users.models import CustomUser
from django.db import transaction


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    category = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - {self.amount} - {self.created}"

    class Meta:
        db_table = 'transaction'

    @transaction.atomic
    def update_user_balance(self):
        with transaction.atomic():
            if self.transaction_type == 'income':
                self.user.balance += self.amount
            elif self.transaction_type == 'expense':
                self.user.balance -= self.amount
            self.user.save()

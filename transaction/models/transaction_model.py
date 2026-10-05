from django.contrib.auth.models import User
from django.db import models
from .category_model import Category

class Transaction(models.Model):

    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Income"
        EXPENSE = "EXPENSE", "Expense"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="transactions",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="transactions",
    )
    type = models.CharField(
        max_length=10,
        choices=TransactionType.choices,
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
    )
    description = models.TextField(blank=True)
    transaction_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date"]

    def __str__(self):
        return f"{self.type} - {self.amount}"
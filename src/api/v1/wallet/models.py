from config import settings
from decimal import Decimal
from django.db import models
import uuid


class Wallet(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallets')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Wallet {self.uuid} with Balance: {self.balance}"

    def deposit(self, amount: Decimal) -> None:
        self.balance += amount
        self.save()

    def withdraw(self, amount: Decimal) -> None:
        if self.balance >= amount:
            self.balance -= amount
            self.save()
        else:
            raise ValueError("Insufficient funds for withdrawal")

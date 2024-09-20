from django.contrib import admin
from api.v1.wallet.models import Wallet


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ["uuid", "user", "balance"]
    ordering = "uuid",
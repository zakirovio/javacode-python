from api.v1.wallet.models import Wallet
from django.conf import settings
from rest_framework import serializers


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ["uuid", "balance"]
        read_only_fields = ["uuid"]
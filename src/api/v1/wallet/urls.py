from api.v1.wallet.views import WalletListView, WalletDetailView, WalletOperationView
from django.urls import path


urlpatterns = [
    path("wallets/", WalletListView.as_view(), name="wallet-list"),
    path("wallets/<uuid:uuid>/", WalletDetailView.as_view(), name="wallet-detail"),
    path("wallets/<uuid:uuid>/operation/",WalletOperationView.as_view(), name="wallet-operation")
]
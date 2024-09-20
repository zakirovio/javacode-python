from config.settings import config
from tests.wallet.credentials import valid_operations, invalid_operations
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from api.custom_auth.models import User
from api.v1.wallet.models import Wallet
import uuid


class WalletTest(APITestCase):
    def setUp(self):
        self.signup_data = {"username": "test", "email": "test_1@test.io", "password": "test"}
        self.login_data = {"username": "test_1@test.io", "password": "test"}
        self.auth_headers = {"User-Agent": "TEST", "Accept": "*/*"}
        self.request_headers = {"Content-Type": "application/json", "User-agent": "TEST", "Authorization": ""}

        self.user = User.objects.create_user(**self.signup_data)
        self.wallet = Wallet.objects.create(user=self.user)

       
        response = self.client.post(path=reverse("login"), headers=self.auth_headers, data=self.login_data, format="json")
        
        self.assertEqual(response.status_code, 200, "Failed login")
        self.assertIsNotNone(response.json().get("access_token"), "Access token not returned")
        
        auth = f"{config('SECRET')} {response.json()['access_token']}"
        self.request_headers["Authorization"] = auth

    def test_wallet_create(self):
        url = reverse("wallet-list")
        response = self.client.post(url, headers=self.request_headers, format="json")

        self.assertEqual(response.status_code, 201, "Failed request")
        self.assertEqual(response.json().get("details"), "Wallet created", "Failed created wallet status")
        self.assertIsNotNone(response.json().get("wallet"), "Wallet object does not exist in response body")

        id = response.json().get("wallet").get("uuid")
        balance = response.json().get("wallet").get("balance")

        self.assertEqual(id, str(uuid.UUID(id)), "Response does not contain correct uuid")
        
        wallet = Wallet.objects.filter(uuid=id)
        self.assertEqual(wallet.count(), 1, "Wallet with current uuid does not exist or is not unique")

        self.assertEqual(str(wallet[0].uuid), id, "Response uuid and object uuid are not the same")
        self.assertIsNotNone(balance, "Response does not contain balance entity")

    def test_wallet_list(self):
        url = reverse("wallet-list")
        response = self.client.get(url, headers=self.request_headers, format="json")

        self.assertEqual(response.status_code, 200, "Failed request")
        self.assertIsInstance(response.json(), list, "Wrong response type")

    def test_wallet_detail(self):
        url = reverse("wallet-detail", kwargs={"uuid": self.wallet.uuid})
        response = self.client.get(url, headers=self.request_headers, format="jsom")

        self.assertEqual(response.status_code, 200, "Failed request")
        self.assertEqual(response.json().get("balance"), str(self.wallet.balance), "Returned balance does not match")

    def test_wallet_operation(self):
        url = reverse("wallet-operation", kwargs={"uuid": self.wallet.uuid})

        for operation in valid_operations:
            response = self.client.post(path=url, headers=self.request_headers, data=operation, format="json")
            self.assertEqual(response.status_code, 200, f"Failed {operation.get('operationType')} operation and {response.json()}")
            self.assertEqual(response.json().get("status"), ("Deposited" if operation["operationType"] == "DEPOSIT" else "Withdrawn"), "Invalid status after 200 response")

        self.wallet.refresh_from_db()

        for operation in invalid_operations:
            response = self.client.post(url, headers=self.request_headers, data=operation, format="json")
            self.assertEqual(response.status_code, 400, f"Expected 400 for {operation.get('operationType')} with amount {operation['amount']}")
            self.assertIn("error", response.json(), "Response should contain an error message")

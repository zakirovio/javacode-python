from api.v1.wallet.models import Wallet
from api.v1.wallet.serializers import WalletSerializer
from api.v1.wallet.utils import validate_amount
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import renderers
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class WalletListView(APIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]

    def get(self, request):
        queryset = request.user.wallets
        serializer = self.serializer_class(queryset, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        wallet = Wallet.objects.create(user=request.user)
        serializer = self.serializer_class(wallet)
        return Response({"details": "Wallet created", "wallet": serializer.data}, status=status.HTTP_201_CREATED)


class WalletDetailView(APIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]
    
    def get(self, request, uuid):
        try:
            wallet = Wallet.objects.get(uuid=uuid, user=request.user)
        except Wallet.DoesNotExist:
            return Response({"detail": "Wallet not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(wallet)
        return Response({"balance": serializer.data["balance"]}, status=status.HTTP_200_OK)


class WalletOperationView(APIView):
    permission_classes = [IsAuthenticated]
    renderer_classes = [renderers.JSONRenderer]

    @transaction.atomic
    def post(self, request, uuid):
        try:
            wallet = Wallet.objects.select_for_update().get(uuid=uuid, user=request.user)
        except Wallet.DoesNotExist:
            return Response({"error": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)

        operation_type = request.data.get('operationType')
        amount_string = str(request.data.get('amount'))

        if operation_type is None or amount_string == "None":
            return Response({"error": "Both 'operationType' and 'amount' are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            amount = validate_amount(amount=amount_string)
        except ValidationError as e:
            return Response({"error": str(e.detail[0])}, status=status.HTTP_400_BAD_REQUEST)

        if operation_type == 'DEPOSIT':
            wallet.deposit(amount)
            return Response({'status': 'Deposited'}, status=status.HTTP_200_OK)
        elif operation_type == 'WITHDRAW':
            try:
                wallet.withdraw(amount)
                return Response({'status': 'Withdrawn'}, status=status.HTTP_200_OK)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid operation_type'}, status=status.HTTP_400_BAD_REQUEST)
        
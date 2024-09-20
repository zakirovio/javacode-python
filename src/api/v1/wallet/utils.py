from decimal import Decimal, InvalidOperation
from rest_framework.exceptions import ValidationError
from typing import Union

def validate_amount(amount: str) -> Union[Decimal, None]:
    try:
        decimal_amount = Decimal(amount)
        if decimal_amount.as_tuple().exponent < -2:
            raise ValidationError('Amount must have at most 2 decimal places')
        elif decimal_amount <= 0:
            raise ValidationError("Deposit must be a positive")

        return decimal_amount
    except (TypeError, InvalidOperation, ValueError):
        raise ValidationError('You have provided an invalid amount. It must be a decimal number with at most 2 decimal places after the dot')
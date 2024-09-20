valid_operations = [
        {
            "operationType": "DEPOSIT",
            "amount": 100.00
        },
        {
            "operationType": "WITHDRAW",
            "amount": 50.00
        }
]

invalid_operations = [
    {
        "operationType": "DEPOSIT",
        "amount": -50.00
    },
    {
        "operationType": "WITHDRAW",
        "amount": 200
    },
    {
        "operationType": "WITHDRAW",
        "amount": "invalid_amount"
    },
    {
        "operationType": "INVALID_OPERATION",
        "amount": 50.00
    },
    {
        "amount": -50.00
    }
]

# core/accounting_map.py

ACCOUNT_MAP = {
    "OWNER_INVESTMENT": {
        "debit": "1000",   # Cash
        "credit": "3000",  # Owner Capital
    },
    "CASH_SALE": {
        "debit": "1000",
        "credit": "4000",
    },
    "PAY_RENT": {
        "debit": "6000",
        "credit": "1000",
    },
    "RECEIVE_VENDOR_BILL": {
        "debit": "6000",   # Rent Expense
        "credit": "2000",  # Accounts Payable
    },
}

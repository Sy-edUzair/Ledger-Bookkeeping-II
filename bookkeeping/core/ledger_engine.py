#Scenario 1 – Owner invests cash
# Debit  Cash                    50,000
# Credit Owner Capital           50,000

# Scenario 2 – Cash sale (service)
# Debit  Cash                     3,000
# Credit Service Revenue          3,000

# Scenario 3 – Pay office rent
# Debit  Rent Expense             1,200
# Credit Cash                     1,200


# from django_ledger.io.io_library import IOLibrary, IOBluePrint

# library = IOLibrary(name="bookkeeping")

# @library.register
# def owner_investment(amount):
#     bp = IOBluePrint()
#     bp.debit("1000", amount, "Owner investment")
#     bp.credit("3000", amount, "Owner investment")
#     return bp


# @library.register
# def cash_sale(amount):
#     bp = IOBluePrint()
#     bp.debit("1000", amount, "Service sale")
#     bp.credit("4000", amount, "Service sale")
#     return bp


# @library.register
# def pay_rent(amount):
#     bp = IOBluePrint()
#     bp.debit("6000", amount, "Office rent")
#     bp.credit("1000", amount, "Office rent")
#     return bp


# core/ledger_engine.py

from django_ledger.io.io_library import IOLibrary, IOBluePrint
from core.accounting_map import ACCOUNT_MAP

library = IOLibrary(name="bookkeeping")

def mapped_blueprint(event, amount,debit_acnt,credit_acnt, description):
    bp = IOBluePrint()
    mapping = ACCOUNT_MAP[event]

    bp.debit(debit_acnt, amount, description)
    bp.credit(credit_acnt, amount, description)
    return bp


@library.register
def owner_investment(debit_acnt,credit_acnt,amount):
    return mapped_blueprint(
        "OWNER_INVESTMENT",
        amount,
        debit_acnt,
        credit_acnt,
        "Owner cash contribution",
    )


@library.register
def cash_sale(amount):
    return mapped_blueprint(
        "CASH_SALE",
        amount,
        "Service revenue",
    )


@library.register
def pay_rent(amount):
    return mapped_blueprint(
        "PAY_RENT",
        amount,
        "Office rent",
    )

@library.register
def receive_vendor_bill(amount):
    return mapped_blueprint(
        "RECEIVE_VENDOR_BILL",
        amount,
        "Vendor bill received (rent)",
    )
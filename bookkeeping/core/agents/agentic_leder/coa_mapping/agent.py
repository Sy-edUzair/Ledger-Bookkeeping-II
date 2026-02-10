import logging
from .helper import map_transaction_to_coa

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def coa_mapping_agent(transaction: dict, chart_of_accounts: list[dict]) -> dict:
    """
    COA MAPPING AGENT
    Validated transaction + entity COA JSON → debit & credit accounts (+ alternatives)
    """
    logger.info("STARTING COA MAPPING AGENT")

    result = map_transaction_to_coa(transaction=transaction, chart_of_accounts=chart_of_accounts)

    primary = result["primary"]
    logger.info(
        "COA MAPPING COMPLETED — "
        f"DEBIT: {primary['debit_account']['account_name']} | "
        f"CREDIT: {primary['credit_account']['account_name']}"
    )

    return result


if __name__ == "__main__":
    import json

    txn = {
        "transaction_date": "2026-01-07",
        "amount": 50000.0,
        "currency": "USD",
        "transaction_type": "EQUITY",
        "particular": "Owner Investment",
        "description": "Initial capital investment by owner",
        "payment_method": None,
    }

    coa = [
        {"account_id": 1, "code": "1000", "account_name": "Cash", "role": "ASSET_CA_CASH", "account_class": "ASSET"},
        {"account_id": 2, "code": "3000", "account_name": "Owner Capital", "role": "EQUITY_CAPITAL", "account_class": "EQUITY"},
        {"account_id": 3, "code": "2000", "account_name": "Accounts Payable", "role": "LIABILITY_CL_ACC_PAYABLE", "account_class": "LIABILITY"},
    ]

    print(json.dumps(coa_mapping_agent(txn, coa), indent=2))

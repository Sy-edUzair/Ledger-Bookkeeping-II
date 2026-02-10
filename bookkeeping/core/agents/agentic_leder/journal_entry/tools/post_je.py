from django_ledger.models.accounts import AccountModel
from core.ledger_engine import library

def post_journal_entry(
    *,
    entity,
    user,
    ledger,
    journal_payload: dict,
    timestamp: str,
):
    """
    SIDE-EFFECT TOOL.
    Posts a journal entry using django-ledger cursor.
    """

    cursor = library.get_cursor(
        entity_model=entity,
        user_model=user,
    )

    debit_line = next(l for l in journal_payload["lines"] if l["side"] == "DEBIT")
    credit_line = next(l for l in journal_payload["lines"] if l["side"] == "CREDIT")

    debit_account = AccountModel.objects.get(id=debit_line["account_id"])
    credit_account = AccountModel.objects.get(id=credit_line["account_id"])

    cursor.dispatch(
        "generic_manual",
        ledger,
        debit_account=debit_account,
        credit_account=credit_account,
        amount=debit_line["amount"],
    )

    return cursor.commit(
        post_new_ledgers=False,
        post_journal_entries=True,
        je_timestamp=timestamp,
    )

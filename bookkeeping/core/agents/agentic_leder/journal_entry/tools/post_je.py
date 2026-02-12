from django_ledger.models.accounts import AccountModel
from core.ledger_engine import library, mapped_blueprint

def post_journal_entry(*,entity,user,ledger,journal_payload: dict,timestamp: str,):
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
    
    cursor.dispatch(
        "generic_entry",
        ledger,
        debit_acnt=debit_line["account_code"],
        credit_acnt=credit_line["account_code"],
        amount=debit_line["amount"],
    )

    return cursor.commit(
        post_new_ledgers=False,
        post_journal_entries=True,
        je_timestamp=timestamp,
    )

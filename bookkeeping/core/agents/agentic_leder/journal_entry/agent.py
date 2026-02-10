import logging
from .helper import build_journal_entry
from .tools.post_je import post_journal_entry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def journal_entry_agent(*,entity,user,ledger,transaction: dict,confirmed_mapping: dict,timestamp: str,):
    """
    FINAL STAGE AGENT:
    - Structure journal entry
    - Post using django-ledger
    """
        
    logger.info("STARTING JOURNAL ENTRY AGENT")

    payload = build_journal_entry(
        transaction=transaction,
        debit_account=confirmed_mapping["primary"]["debit_account"],
        credit_account=confirmed_mapping["primary"]["credit_account"],
    )

    ## human review over here before posting
    logger.info("JOURNAL ENTRY STRUCTURED — POSTING")
    result = post_journal_entry(
        entity=entity,
        user=user,
        ledger=ledger,
        journal_payload=payload,
        timestamp=timestamp,
    )

    logger.info("JOURNAL ENTRY POSTED SUCCESSFULLY")
    return result

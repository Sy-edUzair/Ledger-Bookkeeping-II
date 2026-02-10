import json
import os
import django
from datetime import datetime
import sys


def ensure_django():
    from django.conf import settings

    if not getattr(settings, "configured", False):
        
        BASE_DIR = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../../..")
        )
        sys.path.insert(0, BASE_DIR)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bookkeeping.bookkeeping.settings")
        django.setup()

def main():
    ensure_django()

    from django.contrib.auth import get_user_model
    from django_ledger.models.entity import EntityModel
    from django_ledger.models.ledger import LedgerModel

    from bookkeeping.core.agents.agentic_leder.journal_entry.agent import (
        journal_entry_agent,
    )


    mapping_path = r"D:\Django ledger\bookkeeping\coa_mapping.json" 
    transaction_path = r"D:\Django ledger\initial_transaction.json" 

    with open(mapping_path, "r") as f:
        coa_mapping = json.load(f)

    with open(transaction_path, "r") as f:
        validated_transaction = json.load(f)

    User = get_user_model()
    user = User.objects.first()

    entity = EntityModel.objects.get(name="Quick Books LLC")
    ledger = LedgerModel.objects.get(
        entity=entity,
        ledger_xid="january_2026",
    )
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M")
    
    result = journal_entry_agent(
        entity=entity,
        user=user,
        ledger=ledger,
        transaction=validated_transaction,
        confirmed_mapping=coa_mapping,
        timestamp=formatted_time,
    )

    print("\n=== JOURNAL ENTRY POST RESULT ===\n")
    print(result)


if __name__ == "__main__":
    main()

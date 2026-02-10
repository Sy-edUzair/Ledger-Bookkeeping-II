from __future__ import annotations
import os
import sys
import django
import logging
from typing import Dict

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

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
    """
    Manual / CLI / dev entry point for COA Mapping Service.
    This is NOT used in production APIs directly.
    """

    import json
    ensure_django()
    
    from django.contrib.auth import get_user_model
    from django_ledger.models.entity import EntityModel
    from bookkeeping.core.agents.agentic_leder.coa_mapping.agent import (
        map_transaction_for_entity,
    )

    User = get_user_model()
    user = User.objects.first()

    if not user:
        raise RuntimeError("No users found in database")

    entity = EntityModel.objects.filter(name="Quick Books LLC").first()

    # if not entity:
    #     entity = EntityModel.create_entity(
    #         name="Quick Books LLC",
    #         admin=user,
    #         use_accrual_method=True,
    #         fy_start_month=1,
    #     )

    logger.info(f"Using entity: {entity.name}")

    path = r"D:\Django ledger\initial_transaction.json"
    with open(path,"r") as f:
        transaction = json.load(f)
    
    logger.info("Running COA Mapping Service...")

    mapping_result = map_transaction_for_entity(
        entity=entity,
        validated_transaction=transaction,
    )

    print("\n=== COA MAPPING RESULT ===\n")
    print(json.dumps(mapping_result,indent=2))
    with open("coa_mapping.json","w") as f:
        json.dump(mapping_result,f,indent=2)

if __name__ == "__main__":
    main()

from __future__ import annotations
from typing import List, Dict, Any


def fetch_entity_chart_of_accounts(entity) -> List[Dict[str, Any]]:
    """
    READ-ONLY TOOL

    Fetches the active Chart of Accounts for an entity and serializes it
    into agent-safe JSON.

    Returns list of dicts with:
    - account_id
    - code
    - account_name
    - role
    - account_class (one of the 5)
    """
    coa = entity.get_default_coa()

    accounts_qs = (
        coa.accountmodel_set
        .filter(active=True)
        .order_by("code")
    )

    serialized = []
    
    for acc in accounts_qs:
        serialized.append(
            {
                "account_id": acc.uuid,
                "code": acc.code,
                "account_name": acc.name,
                "role": acc.role,
                "account_class": role_to_account_class(acc.role),
            }
        )
    return serialized


def role_to_account_class(role: str) -> str:
    """
    Maps django-ledger role strings to one of the five classes.

    This is intentionally simple and deterministic.
    Adjust if your role naming differs.
    """
    r = (role or "").lower()

    if "asset" in r:
        return "ASSET"
    if "lia" in r or "liability" in r:
        return "LIABILITY"
    if "equity" in r or "capital" in r or "eq" in r:
        return "EQUITY"
    if "income" in r or "revenue" in r or "in" in r:
        return "INCOME"
    if "expense" in r or "ex" in r:
        return "EXPENSE"
    if "cogs" in r:
        return "EXPENSE"

    raise ValueError(f"Unrecognized django-ledger role for class mapping: {role!r}")

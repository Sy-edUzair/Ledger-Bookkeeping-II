def create_real_coa(entity):
    import pandas as pd
    # Lazy import to avoid requiring django_ledger at module-import time.
    from django_ledger.models.entity import EntityModelValidationError

    try:
        coa = entity.get_default_coa()
    except EntityModelValidationError:
        # No default CoA exists yet — create and assign one.
        coa = entity.create_chart_of_accounts(
            coa_name=f"{getattr(entity, 'name', 'Default')} CoA",
            assign_as_default=True,
            commit=True,
        )
        entity.default_coa == coa
    # Use django_ledger role constants for valid roles
    from django_ledger.io.roles import (
        ASSET_CA_CASH,
        ASSET_CA_PREPAID,
        EQUITY_CAPITAL,
        INCOME_OPERATIONAL,
        EXPENSE_OPERATIONAL,
        LIABILITY_CL_ACC_PAYABLE,
    )

    accounts = [
        ("1000", "Cash", ASSET_CA_CASH),
        ("1100", "Prepaid Expenses", ASSET_CA_PREPAID),
        ("2000", "Accounts Payable", LIABILITY_CL_ACC_PAYABLE),
        ("3000", "Owner Capital", EQUITY_CAPITAL),
        ("4000", "Service Revenue", INCOME_OPERATIONAL),
        ("6000", "Rent Expense", EXPENSE_OPERATIONAL),
    ]

    for code, name, role in accounts:
        # ChartOfAccountModel exposes related accounts via `accountmodel_set` and
        # `create_account(code, role, name, balance_type, active, ...)`.
        if not coa.accountmodel_set.filter(code=code).exists():
            # determine balance type: assets/expenses are debit, others credit
            r = role.lower()
            balance_type = 'debit' if ('asset' in r or 'expense' in r) else 'credit'
            coa.create_account(
                code=code,
                role=role,
                name=name,
                balance_type=balance_type,
                active=True,
            )
    return coa
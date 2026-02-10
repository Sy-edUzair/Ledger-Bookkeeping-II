# core/entities.py

from django_ledger.models.entity import EntityModel

def create_entities(user):
    return [
        EntityModel.create_entity(
            name="QuickBooks LLC",
            admin=user,
            use_accrual_method=True,
            fy_start_month=1,
        ),
        EntityModel.create_entity(
            name="Blue Ocean Consulting Inc",
            admin=user,
            use_accrual_method=True,
            fy_start_month=1,
        ),
    ]

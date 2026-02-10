import os
import django

def ensure_django():
    from django.conf import settings

    if not getattr(settings, 'configured', False):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookkeeping.settings')
        django.setup()


def run():
    ensure_django()
    # Delay imports that require Django app registry until after setup
    from django.contrib.auth import get_user_model
    from core.coa import create_real_coa
    from core.ledger_engine import library
    from django_ledger.models.entity import EntityModel
    from django_ledger.models.ledger import LedgerModel
    from core.models import SourceDocument
    from django_ledger.models.journal_entry import JournalEntryModel
    from django_ledger.models.accounts import AccountModel
    from django_ledger.models.bill import BillModel
    from django_ledger.models.vendor import VendorModel
    from django_ledger.io import roles
    
    User = get_user_model()
    user = User.objects.first()

    entity = EntityModel.objects.filter(name="Quick Books LLC").first()

    if entity is None:
        entity = EntityModel.create_entity(
            name="Quick Books LLC",
            admin=user,
            use_accrual_method=True,
            fy_start_month=1,
        )

    create_real_coa(entity)

    ledger = LedgerModel.objects.filter(entity=entity, ledger_xid="january_2026").first()

    if ledger is None:
        ledger = entity.create_ledger(
            name="January 2026 Ledger",
            ledger_xid="january_2026",
            posted=True,
        )
    print(ledger)

    #Owner Investment
    cursor = library.get_cursor(entity_model=entity, user_model=user)
    cursor.dispatch("owner_investment", ledger, amount=50000)
    result = cursor.commit(post_new_ledgers=True, post_journal_entries=True, je_timestamp="2026-01-10 10:00")
    
    cursor = library.get_cursor(entity_model=entity, user_model=user)
    cursor.dispatch("cash_sale", ledger, amount=3000)
    result=cursor.commit(post_new_ledgers=False, post_journal_entries=True, je_timestamp="2026-01-11 10:00")

    cursor = library.get_cursor(entity_model=entity, user_model=user)
    cursor.dispatch("pay_rent", ledger, amount=1200)
    result=cursor.commit(post_new_ledgers=False, post_journal_entries=True, je_timestamp="2026-01-12 10:00")
    
    #Receive Vendor Bill
    cursor = library.get_cursor(entity_model=entity, user_model=user)
    cursor.dispatch("receive_vendor_bill", ledger, amount=1200)
    cursor.commit(post_new_ledgers=False, post_journal_entries=True, je_timestamp="2026-01-13 10:00")
            
    journal_entries = (
        JournalEntryModel.objects
        .filter(
            ledger=ledger,
            posted=True,
        )
        .prefetch_related(
            "transactionmodel_set",
            "transactionmodel_set__account",
        )
        .order_by("timestamp")
    )

    
    print("\n=== LEDGER TRANSACTIONS ===\n")

    for je in journal_entries:
        print(f"\nJE #{je.je_number} | {je.timestamp.date()}")

        for tx in je.transactionmodel_set.all():
            if tx.is_debit():
                debit = tx.amount
                credit = 0
            elif tx.is_credit:
                debit = 0
                credit = tx.amount

            print(
                f"  {tx.account.code} - {tx.account.name} | "
                f"Debit: {debit} | Credit: {credit}"
            )
            
    return entity

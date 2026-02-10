
    #Pay Rent
    # vendor, _ = VendorModel.objects.get_or_create(
    #     entity_model=entity,
    #     vendor_number="V-0000000001",
    #     defaults={
    #         "vendor_name": "ACME Corp"
    #     }
    # )
    # account_model_qs = entity.get_coa_accounts(coa_model=entity.get_default_coa(), active=True)

    # bill = entity.create_bill(
    #     vendor_model=vendor,
    #     terms=BillModel.TERMS_NET_60,
    #     cash_account=account_model_qs.get(role=roles.ASSET_CA_CASH),
    #     prepaid_account=account_model_qs.get(role=roles.ASSET_CA_PREPAID),
    #     payable_account=account_model_qs.get(role=roles.LIABILITY_CL_ACC_PAYABLE),
    # )
    # bill_item_models = bill.get_item_model_qs()
    # print(bill_item_models)
    
    # K = 6
    # import random as r
    # bill_itemtxs = {
    #     im.item_number: {
    #         'unit_cost': round(r.random() * 10, 2),
    #         'quantity': round(r.random() * 100, 2),
    #         'total_amount': None
    #     } for im in r.choices(bill_item_models, k=K)
    # }

    # # Choose operation ITEMIZE_APPEND to append itemtxs...
    # bill_itemtxs = bill.migrate_itemtxs(itemtxs=bill_itemtxs,commit=True,operation=BillModel.ITEMIZE_REPLACE)

    # bill.post_ledger(user_model=user)
    # print(bill.amount_due)
    # je = bill.ce_model   # ← Journal Entry for this bill
    # print(je.je_number)
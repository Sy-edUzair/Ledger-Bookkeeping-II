Business Event (sale, rent, investment)
   ↓
Account Mapping (business → accounting)
   ↓
IOBluePrint (journal logic)
   ↓
Cursor.dispatch()  ← preview point
   ↓
Cursor.commit()    ← validation + atomic write
   ↓
Journal Entry + Lines + Accounts
   ↓
Ledger UI (/ledger/)
   ↓
Source Document linkage (audit)


Yes — **exactly**. You’ve finally hit the key distinction 👍
Let me state it clearly, then show you **what to use instead**.

---

## ✅ Big clarification (this removes the confusion)

### In django-ledger:

| Document         | Used for          | Direction                        |
| ---------------- | ----------------- | -------------------------------- |
| **InvoiceModel** | Sales invoices    | **Customer owes you money (AR)** |
| **BillModel**    | Purchase invoices | **You owe vendor money (AP)**    |
| **ReceiptModel** | Cash receipts     | Money already paid               |
| **Expense / JE** | Immediate expense | No AP / AR                       |

So yes:

> **`InvoiceModel` = invoices you SEND to customers**
> **NOT invoices you RECEIVE**

That’s why:

* Customer is required
* AR is involved
* Revenue accounts are used

This matches **real accounting systems** (QuickBooks, Xero, SAP).

---

## ❌ What you should NOT do

If you receive a vendor invoice (electricity bill, rent, software, etc.):

❌ Do **NOT** use `InvoiceModel`
❌ Do **NOT** fake a “customer = yourself”
❌ Do **NOT** post it as revenue

That would be wrong accounting.

---

## ✅ What to use for your own purchases

You have **three correct options**, depending on the situation.

---

# OPTION 1️⃣ BillModel (MOST COMMON & CORRECT)

Use this when:

* Vendor sends you an invoice
* You will pay later
* You want Accounts Payable (AP)

### Accounting meaning

```
Expense / Asset   DR
Accounts Payable     CR
```

### django-ledger way

```python
from django_ledger.models.bill import BillModel

bill = entity.create_bill(
    vendor_model=vendor,
    terms=BillModel.TERMS_NET_30
)
```

Add items:

```python
bill.bill_items.create(
    description="Office rent – January",
    quantity=1,
    unit_cost=1200,
    account=rent_expense_account
)
```

Post it:

```python
bill.post_ledger(user_model=user)
```

👉 This is the **mirror image** of customer invoices.

---

# OPTION 2️⃣ Direct Expense (no BillModel)

Use this when:

* You paid immediately
* No vendor invoice needed
* Simple expense (cash / card)

### Accounting meaning

```
Expense   DR
Cash         CR
```

### django-ledger way (no invoice / bill)

```python
cursor.dispatch("pay_rent", ledger, amount=1200)
cursor.commit(post_journal_entries=True)
```

No AP, no BillModel, no vendor balance.

---

# OPTION 3️⃣ Asset purchase (capital expense)

Use when:

* Buying equipment
* Laptop, machinery, etc.

### Accounting

```
Asset   DR
Cash / AP   CR
```

Same pattern — just different account.

---

## 🔁 Summary: which document to use?

| Scenario                     | Use            |
| ---------------------------- | -------------- |
| You send invoice to customer | `InvoiceModel` |
| Vendor sends invoice to you  | `BillModel`    |
| You already paid             | Direct JE      |
| No document needed           | Direct JE      |

---

## 🔑 Mental model (lock this in)

```
CUSTOMER FLOW (Money coming in)
Customer → Invoice → AR → Cash

VENDOR FLOW (Money going out)
Vendor → Bill → AP → Cash
```

Invoices are **outgoing** documents.
Bills are **incoming** documents.

---

## ❓ “But my vendor calls it an invoice”

Yes — in real life vendors call it “invoice”.

But in accounting systems:

* **Sales invoice** → Invoice
* **Purchase invoice** → Bill

Same word, different direction.

---

## TL;DR

* ✅ `InvoiceModel` = customer invoices (sales)
* ❌ Not for your own purchases
* ✅ Use `BillModel` for vendor invoices
* ✅ Or post direct expenses if already paid
* This is correct accounting practice

---

If you want next, I can:

* Walk you through **BillModel exactly like InvoiceModel**
* Show **paying a bill**
* Show **AP aging**
* Explain **expense vs bill**
* Help you decide when NOT to use BillModel

Just tell me 👌

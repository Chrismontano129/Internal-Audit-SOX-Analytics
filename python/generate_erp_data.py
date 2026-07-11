import pandas as pd
import numpy as np
from pathlib import Path

np.random.seed(42)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

NUM_POS = 1000

vendors = [f"VENDOR_{i:03d}" for i in range(1, 51)]

# -----------------------------
# PURCHASE ORDERS
# -----------------------------

po_ids = [f"PO{i:05d}" for i in range(1, NUM_POS + 1)]

purchase_orders = pd.DataFrame({
    "po_id": po_ids,
    "vendor_id": np.random.choice(vendors, NUM_POS),
    "po_date": pd.date_range("2025-01-01", periods=NUM_POS, freq="8h"),
    "po_quantity": np.random.randint(1, 101, NUM_POS),
    "unit_price": np.round(np.random.uniform(10, 500, NUM_POS), 2)
})

purchase_orders["po_amount"] = (
    purchase_orders["po_quantity"] * purchase_orders["unit_price"]
).round(2)

# -----------------------------
# GOODS RECEIPTS
# -----------------------------

goods_receipts = purchase_orders[
    ["po_id", "po_quantity", "po_date"]
].copy()

goods_receipts["receipt_id"] = [
    f"GR{i:05d}" for i in range(1, NUM_POS + 1)
]

goods_receipts["receipt_date"] = (
    goods_receipts["po_date"]
    + pd.to_timedelta(np.random.randint(1, 15, NUM_POS), unit="D")
)

goods_receipts["received_quantity"] = goods_receipts["po_quantity"]

# Create quantity receipt exceptions
receipt_exception_idx = np.random.choice(
    goods_receipts.index,
    size=60,
    replace=False
)

goods_receipts.loc[
    receipt_exception_idx,
    "received_quantity"
] -= np.random.randint(1, 5, 60)

goods_receipts["received_quantity"] = goods_receipts[
    "received_quantity"
].clip(lower=0)

goods_receipts = goods_receipts[
    [
        "receipt_id",
        "po_id",
        "receipt_date",
        "received_quantity"
    ]
]

# Remove receipts to create missing GR exceptions
missing_gr_idx = np.random.choice(
    goods_receipts.index,
    size=30,
    replace=False
)

goods_receipts = goods_receipts.drop(missing_gr_idx).reset_index(drop=True)

# -----------------------------
# INVOICES
# -----------------------------

invoices = purchase_orders[
    [
        "po_id",
        "vendor_id",
        "po_date",
        "po_quantity",
        "po_amount"
    ]
].copy()

invoices["invoice_id"] = [
    f"INV{i:05d}" for i in range(1, NUM_POS + 1)
]

invoices["invoice_date"] = (
    invoices["po_date"]
    + pd.to_timedelta(np.random.randint(5, 25, NUM_POS), unit="D")
)

invoices["invoice_quantity"] = invoices["po_quantity"]
invoices["invoice_amount"] = invoices["po_amount"]

# Create invoice amount mismatches
amount_exception_idx = np.random.choice(
    invoices.index,
    size=70,
    replace=False
)

invoices.loc[
    amount_exception_idx,
    "invoice_amount"
] *= np.random.uniform(1.05, 1.25, 70)

invoices["invoice_amount"] = invoices["invoice_amount"].round(2)

# Create invoice quantity mismatches
quantity_exception_idx = np.random.choice(
    invoices.index,
    size=50,
    replace=False
)

invoices.loc[
    quantity_exception_idx,
    "invoice_quantity"
] += np.random.randint(1, 10, 50)

invoices = invoices[
    [
        "invoice_id",
        "po_id",
        "vendor_id",
        "invoice_date",
        "invoice_quantity",
        "invoice_amount"
    ]
]

# Create duplicate payments/invoices
duplicate_invoices = invoices.sample(25, random_state=42).copy()

duplicate_invoices["invoice_id"] = [
    f"DUP{i:05d}" for i in range(1, 26)
]

invoices = pd.concat(
    [invoices, duplicate_invoices],
    ignore_index=True
)

# Create missing PO exceptions
missing_po_invoices = invoices.sample(20, random_state=7).copy()

missing_po_invoices["invoice_id"] = [
    f"NOPO{i:05d}" for i in range(1, 21)
]

missing_po_invoices["po_id"] = [
    f"MISSING_PO_{i:03d}" for i in range(1, 21)
]

invoices = pd.concat(
    [invoices, missing_po_invoices],
    ignore_index=True
)

# -----------------------------
# EXPORT CSV FILES
# -----------------------------

purchase_orders.to_csv(
    OUTPUT_DIR / "purchase_orders.csv",
    index=False
)

goods_receipts.to_csv(
    OUTPUT_DIR / "goods_receipts.csv",
    index=False
)

invoices.to_csv(
    OUTPUT_DIR / "invoices.csv",
    index=False
)

print("ERP dataset generated successfully.")
print(f"Purchase Orders: {len(purchase_orders):,}")
print(f"Goods Receipts: {len(goods_receipts):,}")
print(f"Invoices: {len(invoices):,}")
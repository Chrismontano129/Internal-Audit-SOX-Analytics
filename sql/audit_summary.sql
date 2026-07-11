-- =========================================================
-- POWER BI AUDIT EXCEPTION DATASET
-- One row per flagged invoice
-- =========================================================

CREATE OR REPLACE VIEW audit_exception_summary AS

SELECT
    i.invoice_id,
    i.vendor_id,
    i.po_id,
    i.invoice_date,
    i.invoice_quantity,
    po.po_quantity,
    gr.received_quantity,
    i.invoice_amount,
    po.po_amount,

    CASE
        WHEN po.po_id IS NULL THEN 'MISSING PO'
        WHEN gr.receipt_id IS NULL THEN 'MISSING GOODS RECEIPT'
        WHEN i.invoice_amount <> po.po_amount THEN 'AMOUNT MISMATCH'
        WHEN i.invoice_quantity <> po.po_quantity THEN 'PO QUANTITY MISMATCH'
        WHEN i.invoice_quantity <> gr.received_quantity THEN 'RECEIPT QUANTITY MISMATCH'
        ELSE 'MATCH'
    END AS exception_type,

    CASE
        WHEN po.po_id IS NULL THEN 'HIGH'
        WHEN gr.receipt_id IS NULL THEN 'HIGH'
        WHEN i.invoice_amount <> po.po_amount THEN 'HIGH'
        WHEN i.invoice_quantity <> po.po_quantity THEN 'MEDIUM'
        WHEN i.invoice_quantity <> gr.received_quantity THEN 'MEDIUM'
        ELSE 'LOW'
    END AS risk_category

FROM invoices i

LEFT JOIN purchase_orders po
    ON i.po_id = po.po_id

LEFT JOIN goods_receipts gr
    ON i.po_id = gr.po_id

WHERE
    po.po_id IS NULL
    OR gr.receipt_id IS NULL
    OR i.invoice_amount <> po.po_amount
    OR i.invoice_quantity <> po.po_quantity
    OR i.invoice_quantity <> gr.received_quantity;

-- =========================================================
-- DUPLICATE PAYMENT EXCEPTION VIEW
-- =========================================================

CREATE OR REPLACE VIEW duplicate_payment_exceptions AS

SELECT
    vendor_id,
    po_id,
    invoice_amount,
    COUNT(*) AS invoice_count,
    SUM(invoice_amount) AS total_processed_amount,
    SUM(invoice_amount) - invoice_amount AS potential_duplicate_exposure
FROM invoices
GROUP BY
    vendor_id,
    po_id,
    invoice_amount
HAVING COUNT(*) > 1;
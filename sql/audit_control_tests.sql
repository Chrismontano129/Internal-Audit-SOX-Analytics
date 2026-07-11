-- =========================================================
-- CONTROL TEST 1: DUPLICATE PAYMENT / INVOICE DETECTION
-- Risk:
-- The same vendor, PO, and invoice amount may be processed
-- more than once, creating potential duplicate payment exposure.
-- =========================================================

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
HAVING COUNT(*) > 1
ORDER BY potential_duplicate_exposure DESC;

-- =========================================================
-- CONTROL TEST 2: THREE-WAY MATCH EXCEPTIONS
-- Risk:
-- Invoice details do not agree with the purchase order
-- and/or goods receipt, indicating payment control failures.
-- =========================================================

SELECT
    i.invoice_id,
    i.vendor_id,
    i.po_id,
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
    END AS exception_type

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
    OR i.invoice_quantity <> gr.received_quantity

ORDER BY
    exception_type,
    i.invoice_amount DESC;
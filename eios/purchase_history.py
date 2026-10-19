"""Source-bound purchase history; never derives stock from invoiced quantities."""
from datetime import date
from decimal import Decimal, InvalidOperation


def purchase_history(store, dataset, article, as_of):
    cutoff = date.fromisoformat(as_of)
    invoices = {r["record_id"]: r for r in store.records(dataset, "purchase_invoice")}
    result = []
    for record in store.records(dataset, "purchase_invoice_line"):
        line = record["data"]
        if line.get("article_id") != article["article_id"]:
            continue
        invoice = invoices.get(line.get("invoice_id"))
        if not invoice:
            continue
        header = invoice["data"]
        if line.get("supplier_id") != article["supplier_id"] or header.get("supplier_id") != article["supplier_id"]:
            continue
        try:
            issued = date.fromisoformat(header["issue_date"])
        except (KeyError, ValueError, TypeError):
            continue
        if issued > cutoff:
            continue
        comparable = False
        effective = None
        try:
            quantity = Decimal(str(line["quantity"]))
            net = Decimal(str(line["net_amount"]))
            if quantity.is_finite() and net.is_finite() and quantity > 0 and net > 0:
                effective = str(net / quantity)
                comparable = (line.get("unit_as_documented") == article.get("unit_as_documented")
                              and line.get("currency") == header.get("currency") == "EUR")
        except (KeyError, InvalidOperation, ValueError, TypeError):
            pass
        result.append(dict(invoice_id=line["invoice_id"], invoice_number=header.get("invoice_number", line["invoice_id"]),
                           issue_date=issued.isoformat(), quantity=line.get("quantity"),
                           unit=line.get("unit_as_documented"), unit_price=line.get("unit_price"),
                           net_amount=line.get("net_amount"), currency=line.get("currency"),
                           effective_net_unit_price=effective, comparable=comparable,
                           source_refs=record.get("source_refs", [])))
    return sorted(result, key=lambda r: (r["issue_date"], r["invoice_id"]), reverse=True)

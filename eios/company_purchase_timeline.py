"""Read-only purchase cash timeline, derived from the same declared flows as preview.

No payment confirmation, authority or state mutation is implied.
"""
from collections import defaultdict
from decimal import Decimal


def build_timeline(source, payments, opening, minimum, cutoff, end):
    events = defaultdict(list)
    for item in source:
        row = item["canonical"]
        day = row["due_date"]
        if not cutoff < day <= end:
            continue
        flow = row["flow_type"]
        if flow not in ("PAYMENT", "COLLECTION"):
            continue
        events[day].append({
            "kind": "COLLECTION" if flow == "COLLECTION" else "PAYMENT",
            "amount": str(Decimal(str(row["amount"]))),
            "reference": str(row["flow_id"]),
            "origin": "DECLARED_FORECAST",
        })
    for index, (date_due, amount) in enumerate(payments, start=1):
        events[date_due.isoformat()].append({
            "kind": "PURCHASE_PAYMENT",
            "amount": str(amount),
            "reference": "PURCHASE-DRAFT-" + str(index),
            "origin": "HYPOTHETICAL_PURCHASE",
        })
    balance = Decimal(str(opening))
    minimum = Decimal(str(minimum))
    rows = []
    for day in sorted(events):
        before = balance
        incoming = sum((Decimal(i["amount"]) for i in events[day] if i["kind"] == "COLLECTION"), Decimal(0))
        outgoing = sum((Decimal(i["amount"]) for i in events[day] if i["kind"] != "COLLECTION"), Decimal(0))
        balance += incoming - outgoing
        rows.append({
            "date": day, "balance_before": str(before), "collections": str(incoming),
            "payments": str(outgoing), "balance_after": str(balance),
            "below_minimum": balance < minimum, "movements": events[day],
        })
    return {
        "schema": "PURCHASE-CASH-TIMELINE-01",
        "cutoff": cutoff, "horizon_end": end, "opening_balance": str(opening),
        "treasury_minimum": str(minimum), "rows": rows,
        "closing_balance": str(balance),
        "scope": "SYNTHETIC_DOCUMENTARY_FORECAST",
        "day_netting": True, "decision_authority": False, "operational_path": "FORBIDDEN",
    }

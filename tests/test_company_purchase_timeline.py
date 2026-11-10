"""Regression tests for read-only financial timelines."""
from decimal import Decimal
from datetime import date
from eios.company_purchase_timeline import build_timeline


def flow(ref, day, amount, kind):
    return {"canonical": {"flow_id": ref, "due_date": day,
                          "amount": str(amount), "flow_type": kind}}


def test_timeline_retains_provenance_and_day_netting():
    source = [flow("c-1", "2026-10-04", "300", "COLLECTION"),
              flow("p-1", "2026-10-04", "100", "PAYMENT"),
              flow("p-old", "2026-09-28", "600", "PAYMENT")]
    result = build_timeline(source, [(date(2026, 10, 4), Decimal("250"))],
                            Decimal("1000"), Decimal("800"), "2026-09-30", "2026-10-31")
    assert len(result["rows"]) == 1
    row = result["rows"][0]
    assert row["balance_before"] == "1000"
    assert row["collections"] == "300"
    assert row["payments"] == "350"
    assert row["balance_after"] == "950"
    assert not row["below_minimum"]
    assert {x["reference"] for x in row["movements"]} == {"c-1", "p-1", "PURCHASE-DRAFT-1"}
    assert {x["origin"] for x in row["movements"]} == {"DECLARED_FORECAST", "HYPOTHETICAL_PURCHASE"}
    assert result["decision_authority"] is False
    assert result["operational_path"] == "FORBIDDEN"


def test_proposals_do_not_share_movements_or_balances():
    source = [flow("c-1", "2026-10-05", "200", "COLLECTION")]
    first = build_timeline(source, [(date(2026, 10, 4), Decimal("500"))],
                           "1000", "700", "2026-09-30", "2026-10-31")
    second = build_timeline(source, [(date(2026, 10, 6), Decimal("800"))],
                            "1000", "700", "2026-09-30", "2026-10-31")
    assert first["rows"][-1]["balance_after"] == "700"
    assert second["rows"][-1]["balance_after"] == "400"
    assert first["rows"][0]["date"] == "2026-10-04"
    assert second["rows"][-1]["below_minimum"]
    assert not first["rows"][-1]["below_minimum"]


def test_outside_horizon_excluded():
    source = [flow("future", "2026-12-01", "5000", "COLLECTION")]
    result = build_timeline(source, [], "1000", "500", "2026-09-30", "2026-10-31")
    assert result["rows"] == []
    assert result["closing_balance"] == "1000"

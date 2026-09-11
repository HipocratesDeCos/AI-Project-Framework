"""Deterministic Finance Basic calculations."""
from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from .models import (
    CalculationStatus,
    CashFlow,
    FinanceBasicInput,
    FinanceBasicResult,
    ProjectionPoint,
    ProjectionResult,
    SafetyMarginResult,
    WorkingCapitalResult,
)

_STATUS_PRIORITY: dict[CalculationStatus, int] = {
    "DETERMINED": 0,
    "NOT_EVALUABLE": 1,
    "NOT_EVIDENCED": 2,
    "CONFLICTING_DATA": 3,
}


def _highest_status(statuses: list[CalculationStatus]) -> CalculationStatus:
    if not statuses:
        return "DETERMINED"
    return max(statuses, key=_STATUS_PRIORITY.__getitem__)


def _dedupe(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def _calculate_projection(payload: FinanceBasicInput) -> ProjectionResult:
    snapshot = payload.snapshot
    horizon_end = snapshot.as_of_date + timedelta(days=payload.horizon_days)
    statuses: list[CalculationStatus] = []
    limitations: list[str] = []
    unresolved: list[str] = []
    participants: list[CashFlow] = []

    if snapshot.available_treasury is None:
        statuses.append("NOT_EVIDENCED")
        limitations.append("MISSING_OPENING_TREASURY")

    for flow in payload.cash_flows:
        due_date = flow.due_date

        if flow.evidence_state == "DEMONSTRATED":
            # The model guarantees amount, currency, due_date and source_ref.
            assert due_date is not None
            assert flow.amount is not None
            assert flow.currency is not None

            if due_date <= snapshot.as_of_date:
                statuses.append("NOT_EVALUABLE")
                limitations.append(f"NON_FUTURE_FLOW:{flow.flow_id}")
                continue
            if due_date > horizon_end:
                continue
            if flow.currency != snapshot.currency:
                statuses.append("NOT_EVALUABLE")
                unresolved.append(flow.flow_id)
                limitations.append(f"CURRENCY_INCOMPATIBLE:{flow.flow_id}")
                continue
            participants.append(flow)
            continue

        if flow.evidence_state == "NOT_EVIDENCED":
            if (
                flow.due_date_evidenced
                and due_date is not None
                and due_date > horizon_end
            ):
                # A separately evidenced due date proves exclusion from this horizon.
                continue
            statuses.append("NOT_EVIDENCED")
            unresolved.append(flow.flow_id)
            limitations.append(f"FLOW_NOT_EVIDENCED:{flow.flow_id}")
            continue

        # CONFLICTING_DATA
        if (
            flow.due_date_evidenced
            and due_date is not None
            and due_date > horizon_end
        ):
            limitations.append(f"OUT_OF_HORIZON_CONFLICT:{flow.flow_id}")
            continue
        statuses.append("CONFLICTING_DATA")
        unresolved.append(flow.flow_id)
        limitations.append(f"FLOW_CONFLICTING_DATA:{flow.flow_id}")

    status = _highest_status(statuses)
    opening = snapshot.available_treasury

    if status != "DETERMINED":
        return ProjectionResult(
            status=status,
            horizon_end=horizon_end,
            opening_treasury=opening,
            points=(),
            financial_capacity_forecast=None,
            unresolved_flow_ids=_dedupe(unresolved),
            limitations=_dedupe(limitations),
        )

    # status DETERMINED implies opening treasury is available.
    assert opening is not None

    daily: dict[date, dict[str, Decimal]] = defaultdict(
        lambda: {"collections": Decimal("0"), "payments": Decimal("0")}
    )
    for flow in participants:
        assert flow.due_date is not None
        assert flow.amount is not None
        bucket = daily[flow.due_date]
        if flow.flow_type == "COLLECTION":
            bucket["collections"] += flow.amount
        else:
            bucket["payments"] += flow.amount

    treasury = opening
    capacity = opening
    points: list[ProjectionPoint] = []
    for due_date in sorted(daily):
        collections = daily[due_date]["collections"]
        payments = daily[due_date]["payments"]
        treasury = treasury + collections - payments
        capacity = min(capacity, treasury)
        points.append(
            ProjectionPoint(
                date=due_date,
                collections=collections,
                payments=payments,
                treasury_after=treasury,
            )
        )

    return ProjectionResult(
        status="DETERMINED",
        horizon_end=horizon_end,
        opening_treasury=opening,
        points=tuple(points),
        financial_capacity_forecast=capacity,
        unresolved_flow_ids=(),
        limitations=_dedupe(limitations),
    )


def _calculate_working_capital(payload: FinanceBasicInput) -> WorkingCapitalResult:
    item = payload.working_capital_input
    if item is None:
        return WorkingCapitalResult(
            status="NOT_EVIDENCED",
            value=None,
            limitations=("WORKING_CAPITAL_INPUT_MISSING",),
        )

    missing: list[str] = []
    if item.current_assets is None:
        missing.append("CURRENT_ASSETS_MISSING")
    if item.current_liabilities is None:
        missing.append("CURRENT_LIABILITIES_MISSING")
    if missing:
        return WorkingCapitalResult(
            status="NOT_EVIDENCED",
            value=None,
            limitations=tuple(missing),
        )

    incompatibilities: list[str] = []
    if item.company_scope != payload.snapshot.company_scope:
        incompatibilities.append("WORKING_CAPITAL_SCOPE_INCOMPATIBLE")
    if item.as_of_date != payload.snapshot.as_of_date:
        incompatibilities.append("WORKING_CAPITAL_DATE_INCOMPATIBLE")
    if item.currency != payload.snapshot.currency:
        incompatibilities.append("WORKING_CAPITAL_CURRENCY_INCOMPATIBLE")
    if incompatibilities:
        return WorkingCapitalResult(
            status="NOT_EVALUABLE",
            value=None,
            limitations=tuple(incompatibilities),
        )

    return WorkingCapitalResult(
        status="DETERMINED",
        value=item.current_assets - item.current_liabilities,
        limitations=(),
    )


def _calculate_safety_margin(
    payload: FinanceBasicInput,
    projection: ProjectionResult,
) -> SafetyMarginResult:
    statuses: list[CalculationStatus] = []
    limitations: list[str] = []

    if projection.status != "DETERMINED":
        statuses.append(projection.status)
        limitations.append(f"PROJECTION_{projection.status}")

    minimum = payload.treasury_minimum
    if minimum is None:
        statuses.append("NOT_EVIDENCED")
        limitations.append("TREASURY_MINIMUM_MISSING")
    elif minimum <= 0:
        statuses.append("NOT_EVALUABLE")
        limitations.append("TREASURY_MINIMUM_NOT_POSITIVE")

    status = _highest_status(statuses)
    if status != "DETERMINED":
        return SafetyMarginResult(
            status=status,
            value_pct=None,
            limitations=_dedupe(limitations),
        )

    assert projection.financial_capacity_forecast is not None
    assert minimum is not None and minimum > 0
    value = (
        (projection.financial_capacity_forecast - minimum)
        / minimum
        * Decimal("100")
    )
    return SafetyMarginResult(status="DETERMINED", value_pct=value, limitations=())


def calculate_finance_basic(payload: FinanceBasicInput) -> FinanceBasicResult:
    """Calculate Finance Basic analytical consequences without making a decision."""
    projection = _calculate_projection(payload)
    working_capital = _calculate_working_capital(payload)
    safety_margin = _calculate_safety_margin(payload, projection)

    return FinanceBasicResult(
        decision_id=payload.context.decision_id,
        scenario_id=payload.context.scenario_id,
        data_snapshot_id=payload.context.data_snapshot_id,
        parameters_version=payload.context.parameters_version,
        currency=payload.snapshot.currency,
        projection=projection,
        working_capital=working_capital,
        safety_margin=safety_margin,
        external_liquidity=payload.snapshot.external_liquidity,
    )


__all__ = ["calculate_finance_basic"]

from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from eios.stock.models import (
    ExcessResult,
    ProjectionMovement,
    StockReferenceValue,
    StockResultIdentity,
    StockScope,
)


EVAL = date(2026, 9, 1)
SCOPE = StockScope(company_id="COMP-1", operational_scope_id="WH-1")


def identity():
    return StockResultIdentity(
        decision_id="D-1",
        scenario_id="S-1",
        rules_version="R-1",
        parameters_version="P-1",
        data_snapshot_id="SNAP-1",
        company_id="COMP-1",
        operational_scope_id="WH-1",
        article_id="A-1",
        evaluation_date=EVAL,
        base_unit="unit",
        methodology_version="STK-0.17",
    )


def reference(value="80"):
    return StockReferenceValue(
        identity=identity(),
        reference_kind="CURRENT_AVAILABLE",
        reference_date=EVAL,
        value=Decimal(value),
        unit="unit",
        state="KNOWN",
        source_ref="REF",
    )


def test_not_applicable_projection_movement_requires_exclusion_evidence():
    with pytest.raises(ValidationError, match="exclusión demostrada"):
        ProjectionMovement(
            movement_id="M-NA",
            scope=SCOPE,
            article_id="A-1",
            direction="OUTFLOW",
            state="NOT_APPLICABLE",
            source_kind="OTHER_AUTHORIZED_NEED",
        )


def test_not_applicable_projection_movement_with_evidence_is_representable():
    movement = ProjectionMovement(
        movement_id="M-NA",
        scope=SCOPE,
        article_id="A-1",
        direction="OUTFLOW",
        state="NOT_APPLICABLE",
        source_kind="OTHER_AUTHORIZED_NEED",
        source_ref="EXCLUSION-EVIDENCE",
    )
    assert movement.state == "NOT_APPLICABLE"


def test_excess_result_rejects_threshold_not_equal_maximum_plus_tolerance():
    ref = reference("80")
    with pytest.raises(ValidationError, match="maximum \+ tolerance"):
        ExcessResult(
            identity=identity(),
            stock_reference=ref,
            stock_maximum=Decimal("50"),
            excess_tolerance_quantity=Decimal("5"),
            excess_threshold=Decimal("56"),
            excess_quantity=Decimal("24"),
            state="EXCESS",
            incorporated_confirmed_demand=(),
        )


def test_excess_result_rejects_state_incompatible_with_reference():
    ref = reference("53")
    with pytest.raises(ValidationError, match="ExcessState"):
        ExcessResult(
            identity=identity(),
            stock_reference=ref,
            stock_maximum=Decimal("50"),
            excess_tolerance_quantity=Decimal("5"),
            excess_threshold=Decimal("55"),
            excess_quantity=Decimal("0"),
            state="NO_EXCESS",
            incorporated_confirmed_demand=(),
        )

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from eios.core.decision_input_package import build_decision_input_package
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters.center import (
    Configuration,
    ParameterConfigurationCenter,
    ParameterDefinition,
)
from eios.rotation import (
    SalesActivityWindowEvidence,
    SalesActivityWindowProvenanceError,
    validate_sales_activity_window_evidence,
)


EFFECTIVE = datetime(2026, 9, 23, 8, 0, tzinfo=timezone.utc)
OPERATION_DATE = date(2026, 9, 23)
COMPANY = "COMP-ROT"
PARAMETERS_VERSION = "params-rot-v1"
CONFIGURATION_ID = 7001


def _configuration(
    *,
    parameter_id: str = "P-ROT-001",
    company_id: str = COMPANY,
    value: str = "30",
    unit: str = "días",
    valid_from: datetime = datetime(2026, 9, 1, tzinfo=timezone.utc),
    valid_to: datetime | None = None,
) -> Configuration:
    return Configuration(
        configuration_id=CONFIGURATION_ID,
        parameter_id=parameter_id,
        company_id=company_id,
        value=value,
        value_type="integer",
        unit=unit,
        valid_from=valid_from,
        valid_to=valid_to,
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _configuration_ref(effective_at: datetime = EFFECTIVE) -> str:
    return f"parameter_configuration:{CONFIGURATION_ID}@{effective_at.isoformat()}"


def _package(
    *,
    configuration: Configuration | None = None,
    evidence_state: str = "DEMONSTRATED",
    evidence_source_ref: str | None = None,
    evidence_demonstration_ref: str | None = "config-audit:7001",
    requested: tuple[str, ...] = ("P-ROT-001",),
):
    config = configuration
    configs = {} if config is None else {config.parameter_id: config}

    def get_at(company_id, parameter_id, effective_at):
        return configs.get(parameter_id)

    center = ParameterConfigurationCenter(
        SimpleNamespace(
            get_parameter=lambda pid: ParameterDefinition(pid)
            if pid == "P-ROT-001"
            else None
        ),
        SimpleNamespace(can_modify=lambda *args: False),
        SimpleNamespace(get_at=get_at),
    )

    purchase = PurchaseOperation(
        decision_id="D-ROT-002",
        scenario_id="S-ROT-BASE",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        operation_date=OPERATION_DATE,
    )
    context = DecisionContext(
        decision_id=purchase.decision_id,
        scenario_id=purchase.scenario_id,
        rules_version="rules-v1",
        parameters_version=PARAMETERS_VERSION,
        data_snapshot_id="snapshot-rot-1",
    )

    evidence = ()
    if evidence_state:
        evidence = (
            Evidence(
                evidence_id="E-CFG-ROT-001",
                source_type="configuration-record",
                source_ref=evidence_source_ref or _configuration_ref(),
                captured_at=date(2026, 9, 23),
                state=evidence_state,
                demonstration_ref=(
                    evidence_demonstration_ref
                    if evidence_state == "DEMONSTRATED"
                    else None
                ),
            ),
        )

    return build_decision_input_package(
        purchase=purchase,
        context=context,
        evidence=evidence,
        financial_snapshot=None,
        company_id=COMPANY,
        effective_at=EFFECTIVE,
        requested_parameter_ids=requested,
        center=center,
    )


def _carrier(**overrides) -> SalesActivityWindowEvidence:
    values = dict(
        article_id="ART-001",
        evaluation_date=OPERATION_DATE,
        window_start=date(2026, 8, 25),
        window_end=OPERATION_DATE,
        window_authority_ref=_configuration_ref(),
        source_ref="sales-ledger:ART-001",
        source_semantics_ref="sales-semantics:v1",
        completeness_ref="sales-completeness:ART-001:2026-08-25:2026-09-23",
        activity_state="NOT_DETERMINABLE",
        evidence_refs=("E-CFG-ROT-001",),
        trace_refs=("trace:sales-window:1",),
    )
    values.update(overrides)
    return SalesActivityWindowEvidence(**values)


def test_valid_carrier_revalidates_against_dip_and_p_rot_001() -> None:
    package = _package(configuration=_configuration())
    carrier = _carrier()

    validate_sales_activity_window_evidence(package, carrier)

    assert carrier.activity_state == "NOT_DETERMINABLE"
    assert carrier.window_start == date(2026, 8, 25)
    assert carrier.window_end == OPERATION_DATE


def test_one_day_period_produces_same_start_and_end() -> None:
    package = _package(configuration=_configuration(value="1"))
    carrier = _carrier(window_start=OPERATION_DATE)

    validate_sales_activity_window_evidence(package, carrier)


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "NaN", "Infinity", "abc"])
def test_invalid_period_values_fail_closed(value: str) -> None:
    package = _package(configuration=_configuration(value=value))
    with pytest.raises(SalesActivityWindowProvenanceError):
        validate_sales_activity_window_evidence(package, _carrier())


def test_noncanonical_unit_fails_closed() -> None:
    package = _package(configuration=_configuration(unit="days"))
    with pytest.raises(SalesActivityWindowProvenanceError, match="unidad canónica"):
        validate_sales_activity_window_evidence(package, _carrier())


def test_missing_p_rot_001_fails_closed() -> None:
    package = _package(configuration=None)
    assert package.missing_parameter_ids == ("P-ROT-001",)
    with pytest.raises(SalesActivityWindowProvenanceError, match="ausente"):
        validate_sales_activity_window_evidence(package, _carrier())


def test_p_rot_001_not_requested_fails_closed() -> None:
    package = _package(configuration=None, requested=())
    with pytest.raises(SalesActivityWindowProvenanceError, match="no fue solicitada"):
        validate_sales_activity_window_evidence(package, _carrier())


def test_gap_configuration_evidence_does_not_demonstrate_binding() -> None:
    package = _package(configuration=_configuration(), evidence_state="GAP")
    with pytest.raises(SalesActivityWindowProvenanceError, match="DEMONSTRATED"):
        validate_sales_activity_window_evidence(package, _carrier())


def test_unrelated_demonstrated_evidence_does_not_demonstrate_binding() -> None:
    package = _package(
        configuration=_configuration(),
        evidence_source_ref="other:configuration",
    )
    with pytest.raises(SalesActivityWindowProvenanceError, match="DEMONSTRATED"):
        validate_sales_activity_window_evidence(package, _carrier())


@pytest.mark.parametrize(
    "override,match",
    [
        ({"article_id": "ART-OTHER"}, "article_id"),
        ({"evaluation_date": date(2026, 9, 22)}, "evaluation_date"),
        ({"window_end": date(2026, 9, 22)}, "window_end"),
        ({"window_start": date(2026, 8, 26)}, "window_start"),
        ({"window_authority_ref": "parameter_configuration:other"}, "window_authority_ref"),
    ],
)
def test_carrier_binding_mismatches_fail_closed(override, match: str) -> None:
    package = _package(configuration=_configuration())
    with pytest.raises(SalesActivityWindowProvenanceError, match=match):
        validate_sales_activity_window_evidence(package, _carrier(**override))


def test_carrier_must_preserve_configuration_evidence_id() -> None:
    package = _package(configuration=_configuration())
    carrier = _carrier(evidence_refs=("E-SALES-ONLY",))
    with pytest.raises(SalesActivityWindowProvenanceError, match="conservar evidence_id"):
        validate_sales_activity_window_evidence(package, carrier)


def test_activity_state_is_canonical_field_not_state() -> None:
    values = _carrier().model_dump()
    values["state"] = values.pop("activity_state")
    with pytest.raises(ValidationError):
        SalesActivityWindowEvidence(**values)


@pytest.mark.parametrize(
    "activity_state",
    [
        "SALES_ACTIVITY_PRESENT",
        "ZERO_VALID_SALES_DEMONSTRATED",
        "NOT_EVIDENCED",
        "CONFLICTING_DATA",
        "NOT_DETERMINABLE",
    ],
)
def test_only_authorized_track_a_states_are_supported(activity_state: str) -> None:
    carrier = _carrier(activity_state=activity_state)
    assert carrier.activity_state == activity_state


def test_unknown_activity_state_is_rejected() -> None:
    with pytest.raises(ValidationError):
        _carrier(activity_state="ZERO_SALES")


def test_window_invariants_and_unique_refs_are_enforced() -> None:
    with pytest.raises(ValidationError, match="window_start"):
        _carrier(window_start=date(2026, 9, 24))
    with pytest.raises(ValidationError, match="window_end"):
        _carrier(window_end=date(2026, 9, 24))
    with pytest.raises(ValidationError, match="evidence_refs"):
        _carrier(evidence_refs=("E-CFG-ROT-001", "E-CFG-ROT-001"))
    with pytest.raises(ValidationError, match="trace_refs"):
        _carrier(trace_refs=("trace:1", "trace:1"))


def test_validator_does_not_promote_activity_state_to_rule_result() -> None:
    package = _package(configuration=_configuration())
    carrier = _carrier(activity_state="ZERO_VALID_SALES_DEMONSTRATED")
    validate_sales_activity_window_evidence(package, carrier)
    payload = carrier.model_dump()
    assert "assessment" not in payload
    assert "outcome" not in payload
    assert "result" not in payload

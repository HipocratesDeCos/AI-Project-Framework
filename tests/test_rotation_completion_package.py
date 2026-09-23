from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

import pytest

from eios.core.decision_input_package import build_decision_input_package
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.parameters.center import Configuration, ParameterConfigurationCenter, ParameterDefinition
from eios.rotation import (
    ROT002_MVP_EXCEPTION_TYPES,
    RotationExceptionDetermination,
    RotationExceptionEvidence,
    SalesActivitySourceEvidence,
    SalesActivityWindowEvidence,
    produce_sales_activity_window_evidence,
)
from eios.rules.catalog import authorized_rule, authorized_rule_metadata
from eios.rules.orchestrator import RotationRuleInputs, run_domain_rules
from eios.rules.rotation import R_ROT_002, evaluate_r_rot_002


EFFECTIVE = datetime(2026, 9, 23, 8, 0, tzinfo=timezone.utc)
OPERATION_DATE = date(2026, 9, 23)
WINDOW_START = date(2026, 8, 25)
COMPANY = "COMP-ROT"
PARAMETERS_VERSION = "params-rot-v1"
CONFIGURATION_ID = 7001


def _purchase() -> PurchaseOperation:
    return PurchaseOperation(
        decision_id="D-ROT-002",
        scenario_id="S-ROT-BASE",
        article_id="ART-001",
        supplier_id="SUP-001",
        quantity=Decimal("10"),
        unit_price=Decimal("5"),
        operation_date=OPERATION_DATE,
    )


def _context() -> DecisionContext:
    return DecisionContext(
        decision_id="D-ROT-002",
        scenario_id="S-ROT-BASE",
        rules_version="rules-v1",
        parameters_version=PARAMETERS_VERSION,
        data_snapshot_id="snapshot-rot-1",
    )


def _configuration() -> Configuration:
    return Configuration(
        configuration_id=CONFIGURATION_ID,
        parameter_id="P-ROT-001",
        company_id=COMPANY,
        value="30",
        value_type="integer",
        unit="días",
        valid_from=datetime(2026, 9, 1, tzinfo=timezone.utc),
        valid_to=None,
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )


def _configuration_ref() -> str:
    return f"parameter_configuration:{CONFIGURATION_ID}@{EFFECTIVE.isoformat()}"


def _evidence(
    evidence_id: str,
    demonstration_ref: str,
    *,
    source_ref: str = "rot:test",
    state: str = "DEMONSTRATED",
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type="rotation-test",
        source_ref=source_ref,
        captured_at=OPERATION_DATE,
        state=state,
        demonstration_ref=demonstration_ref if state == "DEMONSTRATED" else None,
    )


def _package(extra_evidence: tuple[Evidence, ...] = ()):
    config = _configuration()
    center = ParameterConfigurationCenter(
        SimpleNamespace(
            get_parameter=lambda pid: ParameterDefinition(pid)
            if pid == "P-ROT-001"
            else None
        ),
        SimpleNamespace(can_modify=lambda *args: False),
        SimpleNamespace(
            get_at=lambda company_id, parameter_id, effective_at: config
            if parameter_id == "P-ROT-001"
            else None
        ),
    )
    cfg = _evidence(
        "E-CFG-ROT",
        "config-audit:7001",
        source_ref=_configuration_ref(),
    )
    # Existing P-ROT-001 authority binds source_ref rather than demonstration_ref.
    cfg = cfg.model_copy(update={"source_ref": _configuration_ref()})
    return build_decision_input_package(
        purchase=_purchase(),
        context=_context(),
        evidence=(cfg, *extra_evidence),
        financial_snapshot=None,
        company_id=COMPANY,
        effective_at=EFFECTIVE,
        requested_parameter_ids=("P-ROT-001",),
        center=center,
    )


def _source(
    *,
    coverage_state: str = "COMPLETE",
    valid_sale_evidence_refs: tuple[str, ...] = (),
) -> SalesActivitySourceEvidence:
    return SalesActivitySourceEvidence(
        article_id="ART-001",
        window_start=WINDOW_START,
        window_end=OPERATION_DATE,
        source_ref="sales-ledger:ART-001",
        source_semantics_ref="sales-semantics:v1",
        completeness_ref="sales-completeness:ART-001:window",
        valid_sale_evidence_refs=valid_sale_evidence_refs,
        trace_refs=("trace:sales:1",),
        coverage_state=coverage_state,
    )


def _window(state: str = "ZERO_VALID_SALES_DEMONSTRATED") -> SalesActivityWindowEvidence:
    return SalesActivityWindowEvidence(
        article_id="ART-001",
        evaluation_date=OPERATION_DATE,
        window_start=WINDOW_START,
        window_end=OPERATION_DATE,
        window_authority_ref=_configuration_ref(),
        source_ref="sales-ledger:ART-001",
        source_semantics_ref="sales-semantics:v1",
        completeness_ref="sales-completeness:ART-001:window",
        activity_state=state,
        evidence_refs=("E-ACTIVITY",),
        trace_refs=("trace:sales:1",),
    )


def _exception_evidences(
    states: dict[str, str] | None = None,
) -> tuple[RotationExceptionEvidence, tuple[Evidence, ...]]:
    states = states or {item: "NOT_PRESENT" for item in ROT002_MVP_EXCEPTION_TYPES}
    determinations = []
    evidences = [
        _evidence("E-EXC-SCOPE", "rot-exception-scope:ART-001"),
    ]
    carrier_refs = ["E-EXC-SCOPE"]
    for idx, exception_type in enumerate(states, start=1):
        evidence_id = f"E-EXC-{idx}"
        state = states[exception_type]
        refs = (evidence_id,) if state in {"PRESENT", "NOT_PRESENT"} else ()
        determinations.append(
            RotationExceptionDetermination(
                exception_type=exception_type,
                state=state,
                evidence_refs=refs,
            )
        )
        if refs:
            evidences.append(
                _evidence(evidence_id, f"rot-exception:{exception_type}:{state}")
            )
            carrier_refs.append(evidence_id)
    carrier = RotationExceptionEvidence(
        article_id="ART-001",
        evaluation_date=OPERATION_DATE,
        exception_scope_ref="rot-exception-scope:ART-001",
        determinations=tuple(determinations),
        evidence_refs=tuple(carrier_refs),
        trace_refs=("trace:exceptions:1",),
    )
    return carrier, tuple(evidences)


def test_producer_demonstrates_positive_sales_without_complete_coverage() -> None:
    semantic = _evidence("E-SEM", "sales-semantics:v1")
    sale = _evidence("E-SALE-1", "sale-event:1")
    package = _package((semantic, sale))
    result = produce_sales_activity_window_evidence(
        package,
        _source(coverage_state="PARTIAL", valid_sale_evidence_refs=("E-SALE-1",)),
    )
    assert result.activity_state == "SALES_ACTIVITY_PRESENT"


def test_producer_demonstrates_zero_only_with_complete_coverage() -> None:
    semantic = _evidence("E-SEM", "sales-semantics:v1")
    complete = _evidence("E-COMP", "sales-completeness:ART-001:window")
    package = _package((semantic, complete))
    result = produce_sales_activity_window_evidence(package, _source())
    assert result.activity_state == "ZERO_VALID_SALES_DEMONSTRATED"
    assert {"E-CFG-ROT", "E-SEM", "E-COMP"}.issubset(result.evidence_refs)


@pytest.mark.parametrize(
    ("coverage", "expected"),
    [
        ("PARTIAL", "NOT_EVIDENCED"),
        ("NOT_DEMONSTRATED", "NOT_EVIDENCED"),
        ("CONFLICTING", "CONFLICTING_DATA"),
    ],
)
def test_producer_preserves_non_conclusive_coverage(coverage: str, expected: str) -> None:
    package = _package((_evidence("E-SEM", "sales-semantics:v1"),))
    result = produce_sales_activity_window_evidence(
        package,
        _source(coverage_state=coverage),
    )
    assert result.activity_state == expected


def test_r_rot_002_true_requires_zero_sales_and_four_negative_exceptions() -> None:
    exceptions, exception_evidence = _exception_evidences()
    evidences = (
        _evidence("E-ACTIVITY", "sales-window:zero"),
        *exception_evidence,
    )
    result = evaluate_r_rot_002(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_ROT_002, "rules-v1"),
        sales_activity=_window(),
        exceptions=exceptions,
        evidences=evidences,
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "TRUE"


@pytest.mark.parametrize("present_type", ROT002_MVP_EXCEPTION_TYPES)
def test_each_authorized_exception_mitigates_r_rot_002(present_type: str) -> None:
    states = {item: "NOT_PRESENT" for item in ROT002_MVP_EXCEPTION_TYPES}
    states[present_type] = "PRESENT"
    exceptions, exception_evidence = _exception_evidences(states)
    result = evaluate_r_rot_002(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_ROT_002, "rules-v1"),
        sales_activity=_window(),
        exceptions=exceptions,
        evidences=(
            _evidence("E-ACTIVITY", "sales-window:zero"),
            *exception_evidence,
        ),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"
    assert "exceptuada" in result.reason


def test_incomplete_exception_universe_is_not_evaluable() -> None:
    states = {
        "CONFIRMED_ORDER": "NOT_PRESENT",
        "PLANNED_CAMPAIGN": "NOT_PRESENT",
        "STRATEGIC_OPERATION": "NOT_PRESENT",
    }
    exceptions, exception_evidence = _exception_evidences(states)
    result = evaluate_r_rot_002(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_ROT_002, "rules-v1"),
        sales_activity=_window(),
        exceptions=exceptions,
        evidences=(
            _evidence("E-ACTIVITY", "sales-window:zero"),
            *exception_evidence,
        ),
    )
    assert result.status == "NOT_EVALUABLE"
    assert result.outcome is None


def test_conflicting_exception_is_not_evaluable() -> None:
    states = {item: "NOT_PRESENT" for item in ROT002_MVP_EXCEPTION_TYPES}
    states["PLANNED_CAMPAIGN"] = "CONFLICTING"
    exceptions, exception_evidence = _exception_evidences(states)
    result = evaluate_r_rot_002(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_ROT_002, "rules-v1"),
        sales_activity=_window(),
        exceptions=exceptions,
        evidences=(
            _evidence("E-ACTIVITY", "sales-window:zero"),
            *exception_evidence,
        ),
    )
    assert result.status == "NOT_EVALUABLE"


def test_sales_activity_present_is_false_without_needing_negative_exception_proof() -> None:
    exceptions = RotationExceptionEvidence(
        article_id="ART-001",
        evaluation_date=OPERATION_DATE,
        exception_scope_ref="rot-exception-scope:ART-001",
        determinations=(),
        evidence_refs=(),
        trace_refs=(),
    )
    result = evaluate_r_rot_002(
        purchase=_purchase(),
        context=_context(),
        rule=authorized_rule(R_ROT_002, "rules-v1"),
        sales_activity=_window("SALES_ACTIVITY_PRESENT"),
        exceptions=exceptions,
        evidences=(_evidence("E-ACTIVITY", "sales-window:present"),),
    )
    assert result.status == "EVALUABLE"
    assert result.outcome == "FALSE"


def test_r_rot_002_metadata_preserves_r1_but_active_result_no_comprar() -> None:
    metadata = authorized_rule_metadata(R_ROT_002, "rules-v1")
    assert metadata.effect == "R1"
    assert metadata.severity == "ALTA"
    assert metadata.active_result == "NO COMPRAR"


def test_orchestrator_crc_preserves_no_comprar_for_active_r_rot_002() -> None:
    exceptions, exception_evidence = _exception_evidences()
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
        rotation=RotationRuleInputs(
            sales_activity=_window(),
            rotation_exceptions=exceptions,
            evidences=(
                _evidence("E-ACTIVITY", "sales-window:zero"),
                *exception_evidence,
            ),
        ),
    )
    assert R_ROT_002 in result.executed_rule_ids
    assert result.crc_result.consolidated_result == "NO COMPRAR"


def test_orchestrator_omits_rotation_when_bundle_absent() -> None:
    result = run_domain_rules(
        purchase=_purchase(),
        context=_context(),
        base_result="COMPRAR",
    )
    assert R_ROT_002 in result.omitted_rule_ids

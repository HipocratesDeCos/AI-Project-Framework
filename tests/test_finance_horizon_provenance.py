from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from eios.core.models import DecisionContext
from eios.finance import (
    FinanceBasicInput,
    FinanceHorizonProvenanceError,
    FinancialSnapshot,
    ProvenancedFinanceBasicExecution,
    run_provenanced_finance_basic,
    validate_provenanced_finance_basic_execution,
)
from eios.parameters import ResolvedConfiguration, resolve_configuration_for_context
from eios.parameters.center import Configuration


AS_OF = date(2026, 9, 11)
EFFECTIVE = datetime(2026, 9, 11, 12, 0, tzinfo=timezone.utc)
PARAMS = "params-v1"
COMPANY = "COMP-1"


def _context(*, parameters_version: str = PARAMS) -> DecisionContext:
    return DecisionContext(
        decision_id="D-FIN-PROV",
        scenario_id="S-FIN-PROV",
        rules_version="rules-v1",
        parameters_version=parameters_version,
        data_snapshot_id="snapshot-v1",
    )


def _input(*, horizon_days: int = 30) -> FinanceBasicInput:
    context = _context()
    return FinanceBasicInput(
        context=context,
        snapshot=FinancialSnapshot(
            company_scope=COMPANY,
            as_of_date=AS_OF,
            data_snapshot_id=context.data_snapshot_id,
            currency="EUR",
            available_treasury=Decimal("100"),
            treasury_evidence_ref="bank:snapshot",
        ),
        horizon_days=horizon_days,
        treasury_minimum=Decimal("50"),
    )


def _configuration(
    *,
    parameter_id: str = "P-FIN-001",
    company_id: str = COMPANY,
    value: str = "30",
    unit: str = "días",
    valid_from: datetime = datetime(2026, 9, 1, tzinfo=timezone.utc),
    valid_to: datetime | None = None,
) -> Configuration:
    return Configuration(
        configuration_id=2001,
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


def _resolved(
    *,
    configuration: Configuration | None = None,
    effective_at: datetime = EFFECTIVE,
) -> ResolvedConfiguration:
    result = resolve_configuration_for_context(
        configuration or _configuration(),
        _context(),
        effective_at,
    )
    assert result is not None
    return result


def test_provenanced_finance_execution_binds_p_fin_001_and_recomputes() -> None:
    payload = _input()
    resolved = _resolved()

    execution = run_provenanced_finance_basic(payload, resolved)

    assert execution.finance_input == payload
    assert execution.finance_input is not payload
    assert execution.horizon_resolution == resolved
    assert execution.horizon_resolution is not resolved
    assert execution.horizon_configuration_ref == resolved.configuration_ref
    assert execution.finance_result.projection.horizon_end == date(2026, 10, 11)
    validate_provenanced_finance_basic_execution(execution)


def test_provenance_rejects_parameter_other_than_p_fin_001() -> None:
    resolved = _resolved(configuration=_configuration(parameter_id="P-FIN-002"))
    with pytest.raises(FinanceHorizonProvenanceError, match="requiere P-FIN-001"):
        run_provenanced_finance_basic(_input(), resolved)


def test_provenance_rejects_other_parameters_version() -> None:
    resolved = replace(_resolved(), parameters_version="params-other")
    with pytest.raises(FinanceHorizonProvenanceError, match="parameters_version"):
        run_provenanced_finance_basic(_input(), resolved)


def test_provenance_rejects_other_company_scope() -> None:
    resolved = _resolved(configuration=_configuration(company_id="COMP-OTHER"))
    with pytest.raises(FinanceHorizonProvenanceError, match="company_scope"):
        run_provenanced_finance_basic(_input(), resolved)


def test_provenance_rejects_resolution_for_other_snapshot_date() -> None:
    resolved = _resolved(effective_at=datetime(2026, 9, 12, 12, 0, tzinfo=timezone.utc))
    with pytest.raises(FinanceHorizonProvenanceError, match="fecha del snapshot"):
        run_provenanced_finance_basic(_input(), resolved)


def test_provenance_revalidates_configuration_validity_interval() -> None:
    expired = _configuration(valid_to=datetime(2026, 9, 11, 10, 0, tzinfo=timezone.utc))
    manually_resolved = ResolvedConfiguration(
        configuration=expired,
        parameters_version=PARAMS,
        effective_at=EFFECTIVE,
    )
    with pytest.raises(FinanceHorizonProvenanceError, match="no está vigente"):
        run_provenanced_finance_basic(_input(), manually_resolved)


def test_provenance_rejects_incompatible_temporal_semantics() -> None:
    naive = _configuration(valid_from=datetime(2026, 9, 1))
    manually_resolved = ResolvedConfiguration(
        configuration=naive,
        parameters_version=PARAMS,
        effective_at=EFFECTIVE,
    )
    with pytest.raises(FinanceHorizonProvenanceError, match="semántica temporal"):
        run_provenanced_finance_basic(_input(), manually_resolved)


@pytest.mark.parametrize("value", ["0", "-1", "1.5", "NaN", "Infinity", "abc"])
def test_provenance_rejects_invalid_horizon_values(value: str) -> None:
    resolved = _resolved(configuration=_configuration(value=value))
    with pytest.raises(FinanceHorizonProvenanceError):
        run_provenanced_finance_basic(_input(), resolved)


def test_provenance_rejects_noncanonical_unit() -> None:
    resolved = _resolved(configuration=_configuration(unit="days"))
    with pytest.raises(FinanceHorizonProvenanceError, match="unidad canónica 'días'"):
        run_provenanced_finance_basic(_input(), resolved)


def test_provenance_rejects_horizon_not_matching_resolved_value() -> None:
    with pytest.raises(FinanceHorizonProvenanceError, match="no coincide"):
        run_provenanced_finance_basic(_input(horizon_days=60), _resolved())


def test_revalidation_rejects_manually_forged_detached_result() -> None:
    execution = run_provenanced_finance_basic(_input(), _resolved())
    forged_result = execution.finance_result.model_copy(
        update={"parameters_version": "params-forged"}
    )
    forged = ProvenancedFinanceBasicExecution(
        finance_input=execution.finance_input,
        finance_result=forged_result,
        horizon_resolution=execution.horizon_resolution,
    )

    with pytest.raises(FinanceHorizonProvenanceError, match="recomputación"):
        validate_provenanced_finance_basic_execution(forged)

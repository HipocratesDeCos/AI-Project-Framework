from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest

from eios.parameters.center import (
    ChangeRequest,
    Configuration,
    ConfigurationAuthorization,
    ConfigurationRepository,
    HistoryEntry,
    ParameterCatalogue,
    ParameterConfigurationCenter,
    ParameterConfigurationError,
    ParameterDefinition,
)


NOW = datetime(2026, 8, 31, 10, 0, tzinfo=timezone.utc)


@dataclass
class FakeCatalogue(ParameterCatalogue):
    definitions: dict[str, ParameterDefinition]

    def get_parameter(self, parameter_id: str) -> ParameterDefinition | None:
        return self.definitions.get(parameter_id)


@dataclass
class FakeAuthorization(ConfigurationAuthorization):
    allowed: bool = True

    def can_modify(self, company_id: str, parameter_id: str, actor: str) -> bool:
        return self.allowed


class FakeRepository(ConfigurationRepository):
    def __init__(self) -> None:
        self.configurations: list[Configuration] = []
        self.history: list[HistoryEntry] = []
        self.next_id = 1

    @staticmethod
    def overlaps(start: datetime, end: datetime | None, other_start: datetime, other_end: datetime | None) -> bool:
        left = end is None or other_start < end
        right = other_end is None or start < other_end
        return left and right

    def get_current(self, company_id: str, parameter_id: str) -> Configuration | None:
        candidates = [
            item for item in self.configurations
            if item.company_id == company_id and item.parameter_id == parameter_id
            and item.valid_from <= NOW
            and (item.valid_to is None or NOW < item.valid_to)
        ]
        return max(candidates, key=lambda item: item.valid_from, default=None)

    def get_at(self, company_id: str, parameter_id: str, effective_at: datetime) -> Configuration | None:
        candidates = [
            item for item in self.configurations
            if item.company_id == company_id and item.parameter_id == parameter_id
            and item.valid_from <= effective_at
            and (item.valid_to is None or effective_at < item.valid_to)
        ]
        return max(candidates, key=lambda item: item.valid_from, default=None)

    def get_history(self, company_id: str, parameter_id: str) -> tuple[HistoryEntry, ...]:
        return tuple(
            item for item in self.history
            if item.company_id == company_id and item.parameter_id == parameter_id
        )

    def has_overlapping_configuration(
        self,
        company_id: str,
        parameter_id: str,
        valid_from: datetime,
        valid_to: datetime | None,
    ) -> bool:
        return any(
            item.company_id == company_id
            and item.parameter_id == parameter_id
            and self.overlaps(valid_from, valid_to, item.valid_from, item.valid_to)
            for item in self.configurations
        )

    def apply_change_atomically(self, request: ChangeRequest) -> Configuration:
        if self.has_overlapping_configuration(
            request.company_id, request.parameter_id, request.valid_from, request.valid_to
        ):
            raise ParameterConfigurationError(
                "CONFLICTING_ACTIVE_CONFIGURATION", "intervalo solapado"
            )
        current = self.get_current(request.company_id, request.parameter_id)
        configuration = Configuration(
            configuration_id=self.next_id,
            parameter_id=request.parameter_id,
            company_id=request.company_id,
            value=request.value,
            value_type="DECIMAL",
            unit="EUR",
            valid_from=request.valid_from,
            valid_to=request.valid_to,
            created_at=NOW,
            updated_at=NOW,
        )
        self.next_id += 1
        self.configurations.append(configuration)
        self.history.append(
            HistoryEntry(
                configuration_id=configuration.configuration_id,
                parameter_id=request.parameter_id,
                company_id=request.company_id,
                previous_value=current.value if current else None,
                new_value=request.value,
                changed_by=request.actor,
                changed_at=NOW,
                change_reason=request.reason,
            )
        )
        return configuration


def make_center(
    *,
    allowed: bool = True,
    restricted: bool = False,
    validator=None,
) -> tuple[ParameterConfigurationCenter, FakeRepository]:
    catalogue = FakeCatalogue(
        {"PRE-001": ParameterDefinition(
            parameter_id="PRE-001",
            value_type="DECIMAL",
            unit="EUR",
            validate_value=validator,
            restricted=restricted,
        )}
    )
    repository = FakeRepository()
    return (
        ParameterConfigurationCenter(
            catalogue, FakeAuthorization(allowed), repository
        ),
        repository,
    )


def request(**overrides) -> ChangeRequest:
    values = {
        "company_id": "COMP-001",
        "parameter_id": "PRE-001",
        "value": "12.50",
        "valid_from": NOW,
        "valid_to": NOW + timedelta(days=30),
        "actor": "USER-001",
        "reason": "Ajuste autorizado",
    }
    values.update(overrides)
    return ChangeRequest(**values)


def test_unknown_parameter_is_rejected():
    center, _ = make_center()
    with pytest.raises(ParameterConfigurationError) as exc:
        center.validate_change(request(parameter_id="XXX-999"))
    assert exc.value.code == "PARAMETER_NOT_FOUND"


def test_invalid_company_scope_is_rejected():
    center, _ = make_center()
    with pytest.raises(ParameterConfigurationError) as exc:
        center.validate_change(request(company_id=""))
    assert exc.value.code == "INVALID_COMPANY_SCOPE"


def test_unauthorized_change_is_rejected():
    center, _ = make_center(allowed=False)
    with pytest.raises(ParameterConfigurationError) as exc:
        center.validate_change(request())
    assert exc.value.code == "UNAUTHORIZED_CHANGE"


def test_restricted_parameter_uses_distinct_error_code():
    center, _ = make_center(allowed=False, restricted=True)
    with pytest.raises(ParameterConfigurationError) as exc:
        center.validate_change(request())
    assert exc.value.code == "RESTRICTED_PARAMETER"


def test_invalid_type_is_rejected_by_catalogue_validator():
    center, _ = make_center(validator=lambda value: "INVALID_TYPE" if "." not in value else None)
    with pytest.raises(ParameterConfigurationError) as exc:
        center.validate_change(request(value="abc"))
    assert exc.value.code == "INVALID_TYPE"


def test_invalid_validity_is_rejected():
    center, _ = make_center()
    with pytest.raises(ParameterConfigurationError) as exc:
        center.validate_change(request(valid_to=NOW))
    assert exc.value.code == "INVALID_VALIDITY"


def test_apply_change_creates_configuration_and_history():
    center, repository = make_center()
    configuration = center.apply_change(request())
    assert configuration.parameter_id == "PRE-001"
    assert configuration.company_id == "COMP-001"
    assert len(repository.history) == 1
    assert repository.history[0].previous_value is None
    assert repository.history[0].new_value == "12.50"
    assert repository.history[0].changed_by == "USER-001"


def test_company_isolation_is_preserved():
    center, repository = make_center()
    center.apply_change(request(company_id="COMP-001"))
    assert center.get_current_configuration("COMP-002", "PRE-001") is None
    assert repository.get_history("COMP-002", "PRE-001") == ()


def test_temporal_lookup_returns_configuration_for_effective_time():
    center, _ = make_center()
    center.apply_change(request(valid_from=NOW - timedelta(days=10), valid_to=NOW + timedelta(days=10)))
    found = center.get_configuration_at("COMP-001", "PRE-001", NOW)
    assert found is not None
    assert found.value == "12.50"


def test_overlapping_configuration_is_rejected():
    center, _ = make_center()
    center.apply_change(request())
    with pytest.raises(ParameterConfigurationError) as exc:
        center.apply_change(request(value="13.00"))
    assert exc.value.code == "CONFLICTING_ACTIVE_CONFIGURATION"


def test_apply_change_does_not_evaluate_rules_or_make_decisions():
    center, _ = make_center()
    configuration = center.apply_change(request())
    assert not hasattr(configuration, "decision")
    assert not hasattr(configuration, "rule_result")

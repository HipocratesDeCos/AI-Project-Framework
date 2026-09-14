from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from eios.frontend.application_boundary import present_configuration_center_snapshot
from eios.frontend.visual.configuration_center import (
    AuthorizedConfigurationUIContext,
    ConfigurationCenterUIController,
)
from eios.frontend.visual.configuration_center_components import ConfigurationChangeForm
from eios.frontend.visual.configuration_center_workflow import (
    ConfigurationCenterSelectedWorkflow,
)
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


EFFECTIVE_NOW = datetime(2026, 9, 14, 8, 0, tzinfo=timezone.utc)
VALID_TO = EFFECTIVE_NOW + timedelta(days=30)
COMPANY_ID = "COMP-001"
PARAMETER_ID = "PRE-001"
ACTOR = "USER-001"


@dataclass
class E2ECatalogue(ParameterCatalogue):
    definition: ParameterDefinition

    def get_parameter(self, parameter_id: str) -> ParameterDefinition | None:
        if parameter_id == self.definition.parameter_id:
            return self.definition
        return None


@dataclass
class MutableAuthorization(ConfigurationAuthorization):
    allowed: bool = True

    def can_modify(self, company_id: str, parameter_id: str, actor: str) -> bool:
        return self.allowed


class E2ERepository(ConfigurationRepository):
    def __init__(self, effective_now: datetime) -> None:
        self.effective_now = effective_now
        self.configurations: list[Configuration] = []
        self.history: list[HistoryEntry] = []
        self.next_id = 1
        self.atomic_apply_calls = 0

    @staticmethod
    def overlaps(
        start: datetime,
        end: datetime | None,
        other_start: datetime,
        other_end: datetime | None,
    ) -> bool:
        left = end is None or other_start < end
        right = other_end is None or start < other_end
        return left and right

    def get_current(self, company_id: str, parameter_id: str) -> Configuration | None:
        return self.get_at(company_id, parameter_id, self.effective_now)

    def get_at(
        self, company_id: str, parameter_id: str, effective_at: datetime
    ) -> Configuration | None:
        candidates = [
            item
            for item in self.configurations
            if item.company_id == company_id
            and item.parameter_id == parameter_id
            and item.valid_from <= effective_at
            and (item.valid_to is None or effective_at < item.valid_to)
        ]
        return max(candidates, key=lambda item: item.valid_from, default=None)

    def get_history(
        self, company_id: str, parameter_id: str
    ) -> tuple[HistoryEntry, ...]:
        return tuple(
            item
            for item in self.history
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
        self.atomic_apply_calls += 1
        if self.has_overlapping_configuration(
            request.company_id,
            request.parameter_id,
            request.valid_from,
            request.valid_to,
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
            created_at=self.effective_now,
            updated_at=self.effective_now,
        )
        self.next_id += 1
        self.configurations.append(configuration)
        self.history.append(
            HistoryEntry(
                configuration_id=configuration.configuration_id,
                parameter_id=request.parameter_id,
                company_id=request.company_id,
                previous_value=current.value if current is not None else None,
                new_value=request.value,
                changed_by=request.actor,
                changed_at=self.effective_now,
                change_reason=request.reason,
            )
        )
        return configuration

    def inject_external_configuration(
        self,
        *,
        value: str,
        valid_from: datetime,
        valid_to: datetime | None,
    ) -> Configuration:
        configuration = Configuration(
            configuration_id=900,
            parameter_id=PARAMETER_ID,
            company_id=COMPANY_ID,
            value=value,
            value_type="DECIMAL",
            unit="EUR",
            valid_from=valid_from,
            valid_to=valid_to,
            created_at=self.effective_now,
            updated_at=self.effective_now,
        )
        self.configurations.append(configuration)
        return configuration


def _build_stack() -> tuple[
    ConfigurationCenterSelectedWorkflow,
    ConfigurationCenterUIController,
    E2ERepository,
    MutableAuthorization,
]:
    catalogue = E2ECatalogue(
        ParameterDefinition(
            parameter_id=PARAMETER_ID,
            value_type="DECIMAL",
            unit="EUR",
            restricted=False,
        )
    )
    authorization = MutableAuthorization()
    repository = E2ERepository(EFFECTIVE_NOW)
    center = ParameterConfigurationCenter(catalogue, authorization, repository)
    context = AuthorizedConfigurationUIContext(
        company_id=COMPANY_ID,
        parameter_id=PARAMETER_ID,
        actor=ACTOR,
    )
    controller = ConfigurationCenterUIController(center, context)
    workflow = ConfigurationCenterSelectedWorkflow(controller)
    return workflow, controller, repository, authorization


def _form(*, value: str = "12.50", reason: str = "Ajuste autorizado") -> ConfigurationChangeForm:
    return ConfigurationChangeForm(
        value=value,
        valid_from=EFFECTIVE_NOW,
        valid_to=VALID_TO,
        reason=reason,
    )


def test_selected_context_e2e_first_configuration_refreshes_real_history() -> None:
    workflow, controller, repository, _ = _build_stack()

    initial = workflow.refresh()
    initial_payload = present_configuration_center_snapshot(initial)

    assert initial.data_ready is True
    assert initial.history_stale is False
    assert initial_payload["status"] == {"state": "VIEWING", "error_code": None}
    assert initial_payload["detail"]["company_id"] == COMPANY_ID
    assert initial_payload["detail"]["parameter_id"] == PARAMETER_ID
    assert initial_payload["detail"]["actor"] == ACTOR
    assert initial_payload["detail"]["configuration"] is None
    assert initial_payload["history"] == []
    json.dumps(initial_payload)

    prepared = workflow.prepare(_form())
    prepared_payload = present_configuration_center_snapshot(prepared)
    assert prepared_payload["status"]["state"] == "AWAITING_CONFIRMATION"
    assert prepared_payload["confirmation"] is not None
    assert prepared_payload["confirmation"]["detail"]["company_id"] == COMPANY_ID
    assert prepared_payload["confirmation"]["detail"]["parameter_id"] == PARAMETER_ID
    assert controller.has_pending_confirmation is True

    applied = workflow.confirm()
    applied_payload = present_configuration_center_snapshot(applied)

    assert applied_payload["status"] == {"state": "APPLIED", "error_code": None}
    assert applied.history_stale is True
    assert repository.atomic_apply_calls == 1
    assert len(repository.configurations) == 1
    assert len(repository.history) == 1
    assert applied_payload["detail"]["configuration"]["value"] == "12.50"
    assert applied_payload["detail"]["configuration"]["company_id"] == COMPANY_ID
    assert applied_payload["detail"]["configuration"]["parameter_id"] == PARAMETER_ID
    assert applied_payload["history"] == []
    assert applied_payload["confirmation"] is None
    assert controller.has_pending_confirmation is False
    json.dumps(applied_payload)

    refreshed = workflow.refresh()
    refreshed_payload = present_configuration_center_snapshot(refreshed)

    assert refreshed.data_ready is True
    assert refreshed.history_stale is False
    assert refreshed_payload["status"] == {"state": "VIEWING", "error_code": None}
    assert refreshed_payload["detail"]["configuration"]["value"] == "12.50"
    assert len(refreshed_payload["history"]) == 1
    history_item = refreshed_payload["history"][0]
    assert history_item["company_id"] == COMPANY_ID
    assert history_item["parameter_id"] == PARAMETER_ID
    assert history_item["previous_value"] is None
    assert history_item["new_value"] == "12.50"
    assert history_item["changed_by"] == ACTOR
    assert history_item["change_reason"] == "Ajuste autorizado"
    json.dumps(refreshed_payload)


def test_selected_context_e2e_authorization_revocation_writes_nothing() -> None:
    workflow, controller, repository, authorization = _build_stack()

    workflow.refresh()
    workflow.prepare(_form(value="13.25", reason="Cambio aún no aplicado"))
    authorization.allowed = False

    rejected = workflow.confirm()
    payload = present_configuration_center_snapshot(rejected)

    assert payload["status"] == {
        "state": "FORBIDDEN",
        "error_code": "UNAUTHORIZED_CHANGE",
    }
    assert repository.atomic_apply_calls == 0
    assert repository.configurations == []
    assert repository.history == []
    assert controller.has_pending_confirmation is False
    assert workflow.has_local_proposal is False
    assert payload["confirmation"] is None
    assert payload["form"] is not None
    assert payload["form"]["value"] == "13.25"
    assert payload["detail"]["company_id"] == COMPANY_ID
    assert payload["detail"]["parameter_id"] == PARAMETER_ID
    assert payload["detail"]["actor"] == ACTOR
    json.dumps(payload)


def test_selected_context_e2e_concurrent_conflict_rejects_eios_write() -> None:
    workflow, controller, repository, _ = _build_stack()

    workflow.refresh()
    workflow.prepare(_form(value="14.00", reason="Solicitud EIOS"))
    atomic_calls_before_confirm = repository.atomic_apply_calls

    external = repository.inject_external_configuration(
        value="99.00",
        valid_from=EFFECTIVE_NOW,
        valid_to=VALID_TO,
    )

    rejected = workflow.confirm()
    payload = present_configuration_center_snapshot(rejected)

    assert payload["status"] == {
        "state": "CONFLICT",
        "error_code": "CONFLICTING_ACTIVE_CONFIGURATION",
    }
    assert atomic_calls_before_confirm == 0
    assert repository.atomic_apply_calls == atomic_calls_before_confirm
    assert repository.configurations == [external]
    assert repository.history == []
    assert controller.has_pending_confirmation is False
    assert workflow.has_local_proposal is False
    assert payload["confirmation"] is None
    assert payload["form"] is not None
    assert payload["form"]["value"] == "14.00"
    assert payload["detail"]["company_id"] == COMPANY_ID
    assert payload["detail"]["parameter_id"] == PARAMETER_ID
    assert payload["detail"]["actor"] == ACTOR
    json.dumps(payload)

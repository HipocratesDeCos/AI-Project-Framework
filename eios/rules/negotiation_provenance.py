"""Provenance-safe producers for Negotiation Intelligence and Negotiation Ladder."""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from eios.core.capability_adapters import adapt_ni, adapt_nl
from eios.core.models import DecisionContext, Evidence, PurchaseOperation
from eios.core.negotiation_intelligence import (
    NIAssertion,
    NIContextReferences,
    NegotiationContent,
    NegotiationIntelligenceResult,
)
from eios.core.negotiation_ladder import (
    LadderContextReferences,
    LadderRoute,
    LadderStep,
    LadderTransition,
    NegotiationLadderResult,
)
from eios.core.orchestration import CapabilityExecution
from eios.core.validation import validate_evidence

from .provenance import AssessmentTraceBinding, validate_assessment_trace_binding


AuthorityState = Literal["AUTHORIZED", "NOT_AUTHORIZED", "NOT_DETERMINABLE", "CONFLICTING"]


class NegotiationContentEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    decision_id: str = Field(min_length=1, max_length=64)
    scenario_id: str | None = Field(default=None, max_length=64)
    authority_ref: str = Field(min_length=1, max_length=256)
    decision_twin_reference: str | None = Field(default=None, max_length=128)
    viability_reference: str | None = Field(default=None, max_length=128)
    negotiation_content: NegotiationContent
    justification: tuple[NIAssertion, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    trace_refs: tuple[str, ...] = ()
    authority_state: AuthorityState

    @model_validator(mode="after")
    def validate_refs(self) -> "NegotiationContentEvidence":
        if len(self.evidence_refs) != len(set(self.evidence_refs)):
            raise ValueError("evidence_refs no puede contener duplicados")
        if len(self.trace_refs) != len(set(self.trace_refs)):
            raise ValueError("trace_refs no puede contener duplicados")
        if not self.trace_refs:
            raise ValueError("trace_refs no puede estar vacío")
        return self


def _canon(value):
    if hasattr(value, "model_dump"):
        value = value.model_dump(mode="python")
    if isinstance(value, dict):
        return {k: _canon(value[k]) for k in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_canon(v) for v in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _fingerprint(payload: dict) -> str:
    raw = json.dumps(_canon(payload), ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
    return sha256(raw).hexdigest()


def _demonstrated(evidences: tuple[Evidence, ...], ref: str) -> bool:
    return any(
        item.state == "DEMONSTRATED"
        and item.demonstration_ref == ref
        and validate_evidence(item).status == "VALID"
        for item in evidences
    )


def produce_negotiation_intelligence(
    *,
    purchase: PurchaseOperation,
    context: DecisionContext,
    content_evidence: NegotiationContentEvidence,
    evidences: tuple[Evidence, ...],
) -> NegotiationIntelligenceResult:
    if purchase.decision_id != context.decision_id or purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation incompatible con DecisionContext")
    if content_evidence.decision_id != context.decision_id:
        raise ValueError("NegotiationContentEvidence.decision_id incompatible")
    if content_evidence.scenario_id is not None and content_evidence.scenario_id != context.scenario_id:
        raise ValueError("NegotiationContentEvidence.scenario_id incompatible")
    if content_evidence.authority_state != "AUTHORIZED":
        raise ValueError("contenido negociador no autorizado")
    if not _demonstrated(evidences, content_evidence.authority_ref):
        raise ValueError("authority_ref no demostrada")

    by_id = {item.evidence_id: item for item in evidences}
    if len(by_id) != len(evidences):
        raise ValueError("evidence_id duplicado")
    for ref in content_evidence.evidence_refs:
        item = by_id.get(ref)
        if item is None or item.state != "DEMONSTRATED" or validate_evidence(item).status != "VALID":
            raise ValueError("evidence_ref no demostrada")

    payload = {
        "context": context.model_dump(mode="python"),
        "authority_ref": content_evidence.authority_ref,
        "negotiation_content": content_evidence.negotiation_content.model_dump(mode="python"),
        "justification": [item.model_dump(mode="python") for item in content_evidence.justification],
        "evidence_refs": content_evidence.evidence_refs,
        "trace_refs": content_evidence.trace_refs,
    }
    fp = _fingerprint(payload)
    scenario_part = content_evidence.scenario_id or "none"
    result_id = f"ni:{context.decision_id}:{scenario_part}:{fp}"

    return NegotiationIntelligenceResult(
        negotiation_result_id=result_id,
        context_references=NIContextReferences(
            decision_id=context.decision_id,
            scenario_id=content_evidence.scenario_id,
            rules_version=context.rules_version,
            parameters_version=context.parameters_version,
            data_snapshot_id=context.data_snapshot_id,
            viability_reference=content_evidence.viability_reference,
            decision_twin_reference=content_evidence.decision_twin_reference,
            evidence_references=content_evidence.evidence_refs,
        ),
        negotiation_content=deepcopy(content_evidence.negotiation_content),
        justification=tuple(deepcopy(content_evidence.justification)),
        traceability_references=content_evidence.trace_refs,
    )


def _append_steps(result: NegotiationIntelligenceResult) -> tuple[LadderStep, ...]:
    content = result.negotiation_content
    specs: list[tuple[str, str, str, int]] = []
    if content.objective:
        specs.append(("OBJECTIVE", "objective", content.objective, 0))
    if content.opening_request:
        specs.append(("OPENING_REQUEST", "opening_request", content.opening_request, 0))
    for i, value in enumerate(content.moves):
        specs.append(("MOVE", "moves", value, i))
    for i, value in enumerate(content.concessions):
        specs.append(("CONCESSION", "concessions", value, i))
    for i, value in enumerate(content.counterpart_requirements):
        specs.append(("COUNTERPART_CONSIDERATION", "counterpart_requirements", value, i))
    for i, value in enumerate(content.conditions):
        specs.append(("CONDITION", "conditions", value, i))
    for i, value in enumerate(content.alternatives):
        specs.append(("ALTERNATIVE", "alternatives", value, i))
    if content.fallback:
        specs.append(("FALLBACK", "fallback", content.fallback, 0))

    steps = []
    for position, (step_type, field, _value, idx) in enumerate(specs, start=1):
        source_ref = f"ni:{result.negotiation_result_id}:content:{field}:{idx}"
        steps.append(
            LadderStep(
                step_id=f"step:{position}:{_fingerprint({'ref': source_ref})[:16]}",
                step_type=step_type,
                source_content_reference=source_ref,
                position=position,
            )
        )
    return tuple(steps)


def produce_negotiation_ladder(
    *,
    negotiation_result: NegotiationIntelligenceResult,
    purchase: PurchaseOperation,
    context: DecisionContext,
) -> NegotiationLadderResult:
    refs = negotiation_result.context_references
    if purchase.decision_id != context.decision_id or purchase.scenario_id != context.scenario_id:
        raise ValueError("PurchaseOperation incompatible con DecisionContext")
    if refs.decision_id != context.decision_id:
        raise ValueError("NI decision_id incompatible")
    if refs.scenario_id is not None and refs.scenario_id != context.scenario_id:
        raise ValueError("NI scenario_id incompatible")
    if not negotiation_result.traceability_references:
        raise ValueError("NI sin traceability_references")

    steps = _append_steps(negotiation_result)
    if not steps:
        raise ValueError("contenido NI no representable en Ladder v0.1")

    transitions = tuple(
        LadderTransition(
            transition_id=f"transition:{i}",
            from_step_id=steps[i - 1].step_id,
            to_step_id=steps[i].step_id,
            trigger_reference=None,
        )
        for i in range(1, len(steps))
    )
    routes = ()
    if len(steps) >= 2:
        routes = (
            LadderRoute(
                route_id="route:linear:1",
                step_references=tuple(step.step_id for step in steps),
            ),
        )

    structure_fp = _fingerprint({
        "negotiation_result_id": negotiation_result.negotiation_result_id,
        "steps": [step.model_dump(mode="python") for step in steps],
        "transitions": [item.model_dump(mode="python") for item in transitions],
        "routes": [item.model_dump(mode="python") for item in routes],
    })

    return NegotiationLadderResult(
        ladder_id=(
            f"ladder:{negotiation_result.negotiation_result_id}:"
            f"{structure_fp[:max(1, 128 - len('ladder:') - len(negotiation_result.negotiation_result_id) - 1)]}"
        ),
        context_references=LadderContextReferences(
            negotiation_result_id=negotiation_result.negotiation_result_id,
            decision_id=context.decision_id,
            scenario_id=refs.scenario_id,
            source_references=negotiation_result.traceability_references,
        ),
        steps=steps,
        transitions=transitions,
        routes=routes,
        traceability_references=negotiation_result.traceability_references,
    )


def build_provenanced_negotiation_intelligence_invoker(
    *,
    content_evidence: NegotiationContentEvidence,
    evidences: tuple[Evidence, ...],
):
    content_snapshot = content_evidence.model_copy(deep=True)
    evidence_snapshot = tuple(item.model_copy(deep=True) for item in evidences)

    def invoke(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        result = produce_negotiation_intelligence(
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
            content_evidence=content_snapshot.model_copy(deep=True),
            evidences=tuple(item.model_copy(deep=True) for item in evidence_snapshot),
        )
        return adapt_ni(result)

    return invoke


def build_provenanced_ni_ladder_invokers(
    *,
    content_evidence: NegotiationContentEvidence,
    evidences: tuple[Evidence, ...],
) -> tuple:
    content_snapshot = content_evidence.model_copy(deep=True)
    evidence_snapshot = tuple(item.model_copy(deep=True) for item in evidences)

    def ni_invoker(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        result = produce_negotiation_intelligence(
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
            content_evidence=content_snapshot.model_copy(deep=True),
            evidences=tuple(item.model_copy(deep=True) for item in evidence_snapshot),
        )
        return adapt_ni(result)

    def ladder_invoker(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        ni_result = produce_negotiation_intelligence(
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
            content_evidence=content_snapshot.model_copy(deep=True),
            evidences=tuple(item.model_copy(deep=True) for item in evidence_snapshot),
        )
        ladder = produce_negotiation_ladder(
            negotiation_result=ni_result,
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
        )
        return adapt_nl(ladder)

    return ni_invoker, ladder_invoker


def build_c0_bound_ni_ladder_invokers(
    *,
    content_evidence: NegotiationContentEvidence,
    evidences: tuple[Evidence, ...],
    bindings: tuple[AssessmentTraceBinding, ...],
) -> tuple:
    """Revalidate exact C0 provenance before producing NI or Ladder.

    The binding proves each claimed trace against the runtime purchase/context.
    It does not claim that NI content was derived from C0 or that a separate
    C0 capability was executed in the same plan.
    """
    content_snapshot = content_evidence.model_copy(deep=True)
    evidence_snapshot = tuple(item.model_copy(deep=True) for item in evidences)
    binding_snapshots = tuple(item.model_copy(deep=True) for item in bindings)
    if not binding_snapshots:
        raise ValueError("NI requiere bindings C0 no vacíos")
    trace_ids = tuple(item.trace.trace_id for item in binding_snapshots)
    if len(trace_ids) != len(set(trace_ids)):
        raise ValueError("NI no acepta trace_id C0 duplicado")
    if set(content_snapshot.trace_refs) != set(trace_ids) or len(content_snapshot.trace_refs) != len(trace_ids):
        raise ValueError("NI trace_refs no coincide con bindings C0")

    def validated_result(
        purchase: PurchaseOperation, context: DecisionContext,
    ) -> NegotiationIntelligenceResult:
        purchase_snapshot = purchase.model_copy(deep=True)
        context_snapshot = context.model_copy(deep=True)
        for binding in binding_snapshots:
            validate_assessment_trace_binding(
                purchase=purchase_snapshot,
                context=context_snapshot,
                binding=binding,
            )
        return produce_negotiation_intelligence(
            purchase=purchase_snapshot,
            context=context_snapshot,
            content_evidence=content_snapshot.model_copy(deep=True),
            evidences=tuple(item.model_copy(deep=True) for item in evidence_snapshot),
        )

    def ni_invoker(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        return adapt_ni(validated_result(purchase, context))

    def ladder_invoker(purchase: PurchaseOperation, context: DecisionContext) -> CapabilityExecution:
        result = validated_result(purchase, context)
        return adapt_nl(produce_negotiation_ladder(
            negotiation_result=result,
            purchase=purchase.model_copy(deep=True),
            context=context.model_copy(deep=True),
        ))

    return ni_invoker, ladder_invoker


__all__ = [
    "NegotiationContentEvidence",
    "build_provenanced_negotiation_intelligence_invoker",
    "build_provenanced_ni_ladder_invokers",
    "build_c0_bound_ni_ladder_invokers",
    "produce_negotiation_intelligence",
    "produce_negotiation_ladder",
]

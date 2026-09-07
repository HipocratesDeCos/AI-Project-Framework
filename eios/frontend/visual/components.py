"""U1.1 visual component boundaries.

These components are presentation-only adapters. They do not calculate,
rank, recommend, approve, persist, or call EIOS engines.
"""

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class AppShell:
    content: Any


@dataclass(frozen=True)
class ExecutiveDashboard:
    content: Any


@dataclass(frozen=True)
class OperationForm:
    fields: Mapping[str, Any]


@dataclass(frozen=True)
class EvidencePanel:
    evidence: Any


@dataclass(frozen=True)
class DecisionContextPanel:
    context: Any


@dataclass(frozen=True)
class ExecutionStatus:
    status: Any


@dataclass(frozen=True)
class ExecutiveResult:
    result: Any


@dataclass(frozen=True)
class ScenarioList:
    scenarios: Any


@dataclass(frozen=True)
class TwinComparison:
    comparison: Any

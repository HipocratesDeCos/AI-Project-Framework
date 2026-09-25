"""Private single-use capture shared by synthetic reference capability invokers."""
from __future__ import annotations

from collections.abc import Callable
from threading import Lock
from typing import Generic, TypeVar

from pydantic import BaseModel

from .models import DecisionContext, PurchaseOperation
from .orchestration import CapabilityExecution


Result = TypeVar("Result", bound=BaseModel)
Capture = TypeVar("Capture")


class SingleUseObservedInvoker(Generic[Result, Capture]):
    def __init__(self, *, label: str, reference_case_id: str,
                 producer: Callable[[PurchaseOperation, DecisionContext], Result],
                 adapter: Callable[[Result], CapabilityExecution],
                 capture_factory: Callable[[Result, CapabilityExecution], Capture]) -> None:
        if not isinstance(reference_case_id, str) or not reference_case_id.strip() \
                or reference_case_id != reference_case_id.strip():
            raise ValueError("reference_case_id is required")
        self.reference_case_id = reference_case_id
        self._label = label
        self._producer = producer
        self._adapter = adapter
        self._capture_factory = capture_factory
        self._lock = Lock()
        self._used = False
        self._result: Result | None = None
        self._capability: CapabilityExecution | None = None

    def __call__(self, purchase: PurchaseOperation,
                 context: DecisionContext) -> CapabilityExecution:
        with self._lock:
            if self._used:
                raise ValueError(f"Observed {self._label} invoker is single-use")
            self._used = True
            result = self._producer(purchase.model_copy(deep=True),
                                    context.model_copy(deep=True))
            capability = self._adapter(result)
            self._result = result.model_copy(deep=True)
            self._capability = capability.model_copy(deep=True)
            return capability

    def capture(self) -> Capture:
        with self._lock:
            if self._result is None or self._capability is None:
                raise ValueError(
                    f"{self._label} observation is unavailable before successful invocation"
                )
            return self._capture_factory(
                self._result.model_copy(deep=True),
                self._capability.model_copy(deep=True),
            )

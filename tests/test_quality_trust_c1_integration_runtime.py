"""Runtime contract tests for QTG -> C1 integration.

These tests verify gate behavior without changing QTG or C1.
"""

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from eios.quality.gate import QualityCheck, QualityStatus, evaluate_quality


@dataclass(frozen=True)
class _FakePriceResult:
    value: str = "EXECUTED"


def _check(status: QualityStatus, *, critical: bool = True) -> QualityCheck:
    return QualityCheck(
        check_id="IT-QTG-001",
        description="integration fixture",
        satisfied=status == QualityStatus.APTO,
        critical=critical,
    )


def _gate_then_c1(checks, c1):
    qtg = evaluate_quality(checks)
    if qtg.status == QualityStatus.NO_APTO:
        return qtg, None
    return qtg, c1()


def test_apto_executes_c1_and_preserves_qtg():
    c1 = Mock(return_value=_FakePriceResult())
    qtg, price = _gate_then_c1((_check(QualityStatus.APTO),), c1)

    assert qtg.status == QualityStatus.APTO
    assert price == _FakePriceResult()
    c1.assert_called_once_with()


def test_apto_con_advertencias_executes_c1_and_preserves_qtg():
    warning = QualityCheck(
        check_id="IT-QTG-002",
        description="integration warning fixture",
        satisfied=False,
        critical=False,
    )
    c1 = Mock(return_value=_FakePriceResult())
    qtg, price = _gate_then_c1((warning,), c1)

    assert qtg.status == QualityStatus.APTO_CON_ADVERTENCIAS
    assert price == _FakePriceResult()
    c1.assert_called_once_with()


def test_no_apto_blocks_c1_and_does_not_fabricate_price_result():
    blocking = QualityCheck(
        check_id="IT-QTG-003",
        description="blocking integration fixture",
        satisfied=False,
        critical=True,
    )
    c1 = Mock(return_value=_FakePriceResult())
    qtg, price = _gate_then_c1((blocking,), c1)

    assert qtg.status == QualityStatus.NO_APTO
    assert price is None
    c1.assert_not_called()


def test_qtg_permissive_status_does_not_determine_c1_result():
    c1 = Mock(return_value=_FakePriceResult(value="PR_NOT_JUSTIFIABLE"))
    qtg, price = _gate_then_c1((_check(QualityStatus.APTO),), c1)

    assert qtg.status == QualityStatus.APTO
    assert price.value == "PR_NOT_JUSTIFIABLE"
    c1.assert_called_once_with()

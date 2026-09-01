"""Runtime contract tests for QTG -> C1 integration."""

from dataclasses import dataclass
from unittest.mock import Mock

from eios.quality.gate import QualityCheck, evaluate_quality


@dataclass(frozen=True)
class _FakePriceResult:
    value: str = "EXECUTED"


def _gate_then_c1(checks, c1):
    qtg = evaluate_quality(checks)
    if qtg.status == "NO_APTO":
        return qtg, None
    return qtg, c1()


def test_apto_executes_c1_and_preserves_qtg():
    c1 = Mock(return_value=_FakePriceResult())
    qtg, price = _gate_then_c1(
        (QualityCheck(control="IT-QTG-001", satisfied=True),), c1
    )

    assert qtg.status == "APTO"
    assert qtg.confidence == "ALTA"
    assert price == _FakePriceResult()
    c1.assert_called_once_with()


def test_apto_con_advertencias_executes_c1_and_preserves_qtg():
    warning = QualityCheck(
        control="IT-QTG-002",
        satisfied=False,
        critical=False,
    )
    c1 = Mock(return_value=_FakePriceResult())
    qtg, price = _gate_then_c1((warning,), c1)

    assert qtg.status == "APTO_CON_ADVERTENCIAS"
    assert qtg.confidence == "MEDIA"
    assert price == _FakePriceResult()
    c1.assert_called_once_with()


def test_no_apto_blocks_c1_and_does_not_fabricate_price_result():
    blocking = QualityCheck(
        control="IT-QTG-003",
        satisfied=False,
        critical=True,
    )
    c1 = Mock(return_value=_FakePriceResult())
    qtg, price = _gate_then_c1((blocking,), c1)

    assert qtg.status == "NO_APTO"
    assert qtg.confidence == "BAJA"
    assert price is None
    c1.assert_not_called()


def test_qtg_permissive_status_does_not_determine_c1_result():
    c1 = Mock(return_value=_FakePriceResult(value="PR_NOT_JUSTIFIABLE"))
    qtg, price = _gate_then_c1(
        (QualityCheck(control="IT-QTG-004", satisfied=True),), c1
    )

    assert qtg.status == "APTO"
    assert price.value == "PR_NOT_JUSTIFIABLE"
    c1.assert_called_once_with()

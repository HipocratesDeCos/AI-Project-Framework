"""Contract-level integration tests for QTG -> C1.

These tests are intentionally structural/contractual. They do not alter QTG or C1.
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "08_Implementacion" / "Quality_Trust_C1_Integration_Contract.md"


def test_qtg_c1_integration_contract_exists():
    assert CONTRACT.is_file()


def test_qtg_c1_integration_contract_preserves_boundaries():
    text = CONTRACT.read_text(encoding="utf-8")
    assert "`NO_APTO` impide ejecutar C1." in text
    assert "`APTO` permite ejecutar C1." in text
    assert "`APTO_CON_ADVERTENCIAS` permite ejecutar C1." in text
    assert "no modifica C0" in text
    assert "no convierte estados QTG en estados de Price Intelligence" in text
    assert "QualityTrustResult" in text


def test_qtg_c1_integration_contract_has_minimum_execution_cases():
    text = CONTRACT.read_text(encoding="utf-8")
    for case in (
        "`APTO → C1 ejecutado`.",
        "`APTO_CON_ADVERTENCIAS → C1 ejecutado`.",
        "`NO_APTO → C1 no ejecutado`.",
    ):
        assert case in text

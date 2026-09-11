from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "08_Implementacion" / "STK_Implementation_Contract.md"
CLOSURE = ROOT / "08_Implementacion" / "STK_Implementation_Contract_Closure_v0.17.md"
FINAL_AUDIT = ROOT / "07_Pruebas" / "STK_Implementation_Contract_Audit_2_Final_v0.16.md"


def test_stk_contract_v017_is_closed_by_audited_closure_record():
    contract = CONTRACT.read_text(encoding="utf-8")
    closure = CLOSURE.read_text(encoding="utf-8")
    audit = FINAL_AUDIT.read_text(encoding="utf-8")

    assert "**Versión:** 0.17" in contract
    assert "DemandProjectionSchedule" in contract
    assert "**AUDIT 2 FINAL: SUPERADA.**" in audit
    assert "bloqueos → **0**" in audit
    assert "**STK IMPLEMENTATION CONTRACT v0.17: 🔒 CERRADO.**" in closure
    assert "ad1868d43076d9d063232ba31fcff6af0ee8d207" in closure


def test_stk_contract_close_authorizes_implementation_without_defaults_or_decision_authority():
    closure = CLOSURE.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "implementación ejecutable `eios/stock`" in closure
    assert "no autoriza" in closure.lower()
    assert "forecasting interno" in closure
    assert "ventas → demanda" in closure
    assert "decisión automática" in closure
    assert "C0" in closure

    for forbidden_default in (
        "15 %",
        "30/90 días",
        "10 %",
        "12 meses",
        "90 días",
        "15 días",
    ):
        assert forbidden_default in contract


def test_stk_contract_keeps_demand_projection_calendar_external_and_authorized():
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "STK **no** convierte por sí mismo `DemandRateResult` en salidas fechadas" in contract
    assert "`transformation_ref`" in contract
    assert "`reconciliation_ref`" in contract
    assert "Si falta transformación o reconciliación autorizada" in contract
    assert "sin calendarización automática de tasa" in contract


def test_stk_contract_preserves_human_authority_and_module_boundaries():
    closure = CLOSURE.read_text(encoding="utf-8")
    contract = CONTRACT.read_text(encoding="utf-8")

    assert "Rules conserva `R-STK-001…004`" in contract
    assert "CRC conserva resolución de conflictos" in contract
    assert "la decisión final permanece en la persona autorizada" in contract
    assert "STK no decide" in contract
    assert "cambios de C0" in closure

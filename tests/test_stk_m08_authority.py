from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M08_Confirmed_Demand_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"


def test_m08_requires_complete_confirmed_order_evidence():
    text = AUTHORITY.read_text(encoding="utf-8")
    for clause in ("`Pedido_ID`", "cliente", "artículo", "cantidad comprometida", "fecha del pedido", "fecha de confirmación", "estado vigente", "fecha prevista de entrega", "fuente de la evidencia"):
        assert clause in text
    assert "`Pedido_Confirmado = Sí` no constituye evidencia suficiente" in text


def test_m08_limits_applicable_quantity_and_prevents_reuse():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "mismo artículo normalizado" in text
    assert "permanece pendiente de servir" in text
    assert "aplicable al horizonte temporal evaluado" in text
    assert "no puede asignarse más de una vez" in text


def test_m08_materializes_absorption_relations_without_rewriting_excess():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`absorbed_excess = min(excess_quantity, confirmed_order_quantity_applicable)`" in text
    assert "`residual_excess = max(0, excess_quantity - absorbed_excess)`" in text
    assert "No elimina, modifica ni recalcula retroactivamente el exceso original" in text
    assert "Se preservan conjuntamente `excess_quantity`, `absorbed_excess` y `residual_excess`" in text


def test_m08_defines_required_business_states():
    text = AUTHORITY.read_text(encoding="utf-8")
    for state in ("`NO_EXISTE`", "`NO_APLICABLE`", "`APLICABLE_Y_VALIDADA`", "`NO_VERIFICABLE`"):
        assert state in text
    assert "Ninguno puede reducir el exceso" in text


def test_m08_changes_and_partial_deliveries_are_traceable():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "Cancelaciones, modificaciones, entregas parciales" in text
    assert "cantidad aplicable es siempre la pendiente de servir" in text
    assert "no se reutiliza como absorción futura" in text


def test_m08_preserves_human_authority_and_stk_boundary():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    assert "STK-M08 — Pedido confirmado — CERRADO" in matrix
    assert "No equivale a autorización de compra, cancelación, reducción de stock" in authority
    assert "autoridad decisional humana" in authority
    assert "`STK-M09…M10` permanecen pendientes" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

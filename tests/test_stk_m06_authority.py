from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M06_Logistics_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"
CATALOG = ROOT / "02_Parametros" / "Catalogo_Parametros_MVP_v0.3.md"


def test_m06_defines_distinct_exclusive_logistics_states():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`PENDING_ORDER`" in text
    assert "`IN_TRANSIT`" in text
    assert "mutuamente excluyentes" in text
    assert "unidad base normalizada del artículo" in text


def test_m06_requires_identity_evidence_and_noninvented_date():
    text = AUTHORITY.read_text(encoding="utf-8")
    for clause in ("pedido u origen documental", "proveedor", "estado", "fecha prevista de recepción", "evidencia disponible"):
        assert clause in text
    assert "Sin identidad o referencia suficiente no se suman como entradas independientes" in text
    assert "Nunca se inventa a partir de ausencia de información" in text


def test_m06_excludes_current_stock_and_prevents_double_counting():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "no forman parte del stock físico disponible actual" in text
    assert "una sola representación vigente de cada cantidad" in text
    assert "no pueden producir dos incrementos proyectivos" in text
    assert "parte recibida sale de STK-M06" in text


def test_m06_missing_or_conflicting_inputs_remain_explicit():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "la entrada es `UNKNOWN / NOT_EVIDENCED`" in text
    assert "`UNKNOWN / NOT_EVIDENCED ≠ 0`" in text
    assert "no se incorpora silenciosamente" in text
    assert "se cerrará en `STK-M10`" in text


def test_m06_preserves_parameter_and_human_authority_boundaries():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    assert "STK-M06 — Pedidos pendientes y tránsito — CERRADO" in matrix
    assert "no valida los valores iniciales “Sí” de `PYE-002` y `PYE-003`" in authority
    assert "| PYE-002 | Considerar pedidos pendientes | Sí | Sí/No | Pendiente de validación |" in catalog
    assert "| PYE-003 | Considerar compras en tránsito | Sí | Sí/No | Pendiente de validación |" in catalog
    assert "No constituye por sí mismo autorización de compra" in authority
    assert "`STK-M07…M10` permanecen pendientes" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

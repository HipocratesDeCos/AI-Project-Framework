from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M07_Excess_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"
CATALOG = ROOT / "02_Parametros" / "Catalogo_Parametros_MVP_v0.3.md"


def test_m07_materializes_threshold_and_quantity_relations():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`excess_threshold = stock_maximum + excess_tolerance`" in text
    assert "`excess_quantity = max(0, stock_reference - excess_threshold)`" in text
    assert "unidad base normalizada del artículo" in text


def test_m07_defines_complete_boundary_states():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`stock_reference ≤ stock_maximum`" in text and "`NO_EXCESS`" in text
    assert "`stock_maximum < stock_reference ≤ excess_threshold`" in text and "`WITHIN_TOLERANCE`" in text
    assert "`stock_reference > excess_threshold`" in text and "`EXCESS`" in text
    assert "resultados calculados con entradas conocidas y evidenciadas" in text


def test_m07_future_reference_reuses_m05_without_recounting_m06():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "consume la proyección autorizada de STK-M05" in text
    assert "no vuelve a sumar pedidos pendientes o tránsito de STK-M06" in text
    assert "STK-M07 no la añade de nuevo ni presume su aprobación" in text


def test_m07_percentage_tolerance_is_dimensionally_converted():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`excess_tolerance_quantity = stock_maximum * authorized_tolerance_rate`" in text
    assert "normalizada antes del cálculo" in text
    assert "no infiere su significado" in text


def test_m07_missing_inputs_never_default_to_no_excess():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "resultado es `UNKNOWN / NOT_EVIDENCED`" in text
    assert "`UNKNOWN / NOT_EVIDENCED ≠ NO_EXCESS`" in text
    assert "dimensionalmente incompatibles" in text


def test_m07_preserves_catalog_and_human_authority_boundaries():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    assert "STK-M07 — Exceso — CERRADO" in matrix
    assert "10 % de `STK-005` permanece pendiente de validación" in authority
    assert "90 días de `STK-004` permanecen pendientes de validación" in authority
    assert "| STK-004 | Cobertura máxima | 90 | días | Exceso de stock | Pendiente de validación |" in catalog
    assert "| STK-005 | Tolerancia de exceso | 10 | % | Alerta | Pendiente de validación |" in catalog
    assert "No autoriza automáticamente cancelaciones" in authority
    assert "`STK-M08…M10` permanecen pendientes" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

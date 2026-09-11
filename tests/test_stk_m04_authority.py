from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M04_Coverage_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"
CATALOG = ROOT / "02_Parametros" / "Catalogo_Parametros_MVP_v0.3.md"


def test_m04_materializes_formula_dimensions_and_standard_unit():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "tiempo estimado durante el cual el stock disponible" in text
    assert "`coverage = stock_available / authorized_average_demand_or_consumption_per_time_unit`" in text
    assert "misma unidad base del artículo por unidad de tiempo" in text
    assert "unidad estándar es días de cobertura" in text


def test_m04_requires_authorized_evidenced_unmixed_source():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "datos históricos o previsiones explícitamente autorizadas" in text
    assert "No se mezclan fuentes sin una regla documentada" in text
    assert "no valida por sí misma los 12 meses de `STK-006`" in text


def test_m04_distinguishes_confirmed_zero_from_missing_inputs():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`UNBOUNDED / NOT_APPLICABLE`" in text
    assert "no representa artificialmente un número infinito" in text
    assert "`UNKNOWN / NOT_EVIDENCED ≠ 0`" in text
    assert "La ausencia no puede clasificarse como cero confirmado" in text


def test_m04_preserves_as_of_date_and_stock_composition_boundaries():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "fecha explícita `as_of_date`" in text
    assert "reservado a `STK-M06`" in text
    assert "sin crear fechas paralelas o ambiguas" in text


def test_m04_does_not_validate_catalog_thresholds_or_automate_decision():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    assert "STK-M04 — Cobertura — CERRADO" in matrix
    assert "30 y 90 días consignados en el catálogo continúan pendientes de validación" in authority
    assert "| STK-003 | Cobertura mínima | 30 | días | Compras | Pendiente de validación |" in catalog
    assert "| STK-004 | Cobertura máxima | 90 | días | Exceso de stock | Pendiente de validación |" in catalog
    assert "no constituye por sí misma una decisión automática" in authority
    assert "`STK-M05…M10` permanecen pendientes" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

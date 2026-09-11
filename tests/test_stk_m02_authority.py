from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M02_Minimum_Stock_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"


def test_m02_materializes_the_authorized_minimum_stock_definition():
    text = AUTHORITY.read_text(encoding="utf-8")
    required = (
        "cantidad mínima de existencias",
        "proteger la continuidad operativa",
        "unidad base normalizada del artículo",
        "política o cálculo explícito, trazable y autorizado",
        "demanda esperada",
        "`lead_time`",
        "variabilidad",
        "nivel de protección requerido",
    )
    for clause in required:
        assert clause in text


def test_m02_preserves_distinct_safety_stock_coverage_and_demand_roles():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "ambos conceptos no son equivalentes" in text
    assert "permite expresar cuántos días o periodos de consumo" in text
    assert "Una variación de demanda no modifica automáticamente el valor vigente" in text


def test_m02_absence_never_becomes_zero_or_implicit_estimate():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`UNKNOWN / NOT_EVIDENCED ≠ 0`" in text
    assert "No se sustituye por cero ni por una estimación implícita" in text


def test_m02_closure_does_not_authorize_formula_or_automatic_replenishment():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    assert "STK-M02 — Stock mínimo — CERRADO" in matrix
    assert "no constituye por sí mismo una orden de reposición" in authority
    assert "una fórmula concreta de `stock_minimum`" in authority
    assert "`STK-M03…M10` permanecen pendientes" in authority
    assert "**Estado actual:** APTO PARA DISEÑO DE CONTRATO TÉCNICO STK." in matrix
    assert "**No constituye por sí misma implementación ejecutable.**" in matrix

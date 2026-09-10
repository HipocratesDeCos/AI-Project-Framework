from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M01_Consumption_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"


def test_m01_authority_materializes_human_decision_without_substitution():
    text = AUTHORITY.read_text(encoding="utf-8")
    required = (
        "cantidad real consumida",
        "unidad base normalizada del artículo",
        "suma de los consumos registrados durante periodos mensuales",
        "`UNKNOWN` y nunca como consumo cero salvo evidencia explícita",
        "desde la puesta en producción de EIOS",
        "de forma retrospectiva a los datos históricos incorporados",
    )
    for clause in required:
        assert clause in text


def test_m01_keeps_sales_and_forecast_demand_separate():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "No equivale por defecto" in text
    assert "- ventas;" in text
    assert "- demanda prevista;" in text
    assert "`UNKNOWN ≠ 0`" in text


def test_monthly_period_does_not_invent_calendar_boundaries_or_window():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "no determina que el periodo deba coincidir con el mes natural" in text
    assert "no fija todavía el número de meses" in text
    assert "`STK-006` permanece pendiente de validación" in text


def test_m01_closure_does_not_authorize_stk_implementation():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    assert "STK-M01 — Consumo — CERRADO" in matrix
    assert "STK-M02…STK-M10" in authority
    assert "implementar el motor cuantitativo STK" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

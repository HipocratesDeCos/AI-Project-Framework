from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M03_Safety_Stock_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"
CATALOG = ROOT / "02_Parametros" / "Catalogo_Parametros_MVP_v0.3.md"

def test_m03_authorized_definition():
    text = AUTHORITY.read_text(encoding="utf-8")
    for clause in ("cantidad adicional de existencias", "unidad base normalizada del artículo", "política o método explícito, documentado, trazable y autorizado", "variabilidad de demanda", "variabilidad del `lead_time`", "nivel de servicio o protección requerido", "calidad de evidencia disponible"):
        assert clause in text

def test_m03_evidence_and_distinction():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "datos históricos y previsiones válidas, normalizadas y suficientemente evidenciadas" in text
    assert "demanda y/o del plazo y fiabilidad de reposición" in text
    assert "son conceptos distintos y no deben asumirse equivalentes" in text

def test_m03_absence_and_vigency():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`UNKNOWN / NOT_EVIDENCED ≠ 0`" in text
    assert "Nunca se sustituye por cero ni por un valor inferido automáticamente" in text
    assert "solo entra en vigor desde su aprobación o materialización correspondiente" in text

def test_m03_keeps_quantitative_boundary():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    assert "STK-M03 — Stock de seguridad — CERRADO" in matrix
    assert "`STK-002` sea el 15 % del consumo" in authority
    assert "| STK-002 | Stock de seguridad | 15 | % del consumo | Riesgo | Pendiente de validación |" in catalog
    assert "`STK-M04…M10` permanecen pendientes" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

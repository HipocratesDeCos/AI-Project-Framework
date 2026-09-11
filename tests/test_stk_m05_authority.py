from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M05_Projection_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"
CATALOG = ROOT / "02_Parametros" / "Catalogo_Parametros_MVP_v0.3.md"


def test_m05_materializes_projection_relation_and_dimensions():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "evolución proyectada del stock de un artículo" in text
    assert "`projected_stock = current_available_stock + expected_inflows - expected_outflows`" in text
    assert "unidad base normalizada del artículo" in text
    assert "horizonte temporal explícito" in text


def test_m05_requires_evidenced_inflows_and_restricts_lead_time():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "existencia, cantidad y fecha están suficientemente evidenciadas" in text
    assert "Nunca convierte por sí mismo una compra no confirmada en entrada prevista" in text
    assert "permanecen en `STK-M06`" in text


def test_m05_preserves_authorized_outflow_sources_without_mixing():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "demanda, consumo, reservas u otras necesidades futuras" in text
    assert "no se mezcla o sustituye por otra sin una regla documentada" in text


def test_m05_missing_elements_remain_visible_and_nonzero():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "el elemento correspondiente es `UNKNOWN / NOT_EVIDENCED`" in text
    assert "`UNKNOWN / NOT_EVIDENCED ≠ 0`" in text
    assert "no puede omitirse silenciosamente" in text
    assert "se cerrará en `STK-M09`" in text


def test_m05_preserves_parameter_and_human_authority_boundaries():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    catalog = CATALOG.read_text(encoding="utf-8")
    assert "STK-M05 — Proyección — CERRADO" in matrix
    assert "no constituye por sí misma una decisión de compra ni autoriza una reposición" in authority
    assert "no valida automáticamente los 90 días de `PYE-001`" in authority
    assert "Tampoco valida el umbral de 15 días de `PYE-006`" in authority
    assert "| PYE-001 | Horizonte de proyección | 90 | días | Pendiente de validación |" in catalog
    assert "| PYE-006 | Umbral de riesgo de rotura | 15 | días | Pendiente de validación |" in catalog
    assert "`STK-M06…M10` permanecen pendientes" in authority
    assert "**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA." in matrix

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M10_Contradictions_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"


def test_m10_defines_material_contradiction_and_comparability():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "dos o más datos o evidencias suficientemente identificados" in text
    assert "no pueden considerarse simultáneamente ciertos" in text
    for dimension in ("identidad del artículo", "variable representada", "unidad de medida", "normalización aplicada", "fecha de referencia", "ámbito operativo", "versión del dato", "contexto"):
        assert dimension in text
    assert "Una diferencia entre fuentes no constituye automáticamente una contradicción" in text


def test_m10_excludes_legitimate_differences():
    text = AUTHORITY.read_text(encoding="utf-8")
    for difference in ("diferencias temporales", "unidades convertibles", "ámbitos distintos", "versiones sucesivas correctamente trazadas"):
        assert difference in text
    assert "permanecen separados conforme a su contexto" in text


def test_m10_preserves_evidence_and_forbids_implicit_resolution():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "conserva todas las evidencias implicadas sin sobrescribir ninguna" in text
    assert "`CONFLICTING_DATA / UNRESOLVED_CONTRADICTION`" in text
    for heuristic in ("más reciente", "mayor", "menor", "aparentemente más probable", "promedio", "score", "prioridad arbitraria"):
        assert heuristic in text
    assert "política de autoridad documental previamente autorizada" in text


def test_m10_propagates_and_records_authorized_resolution():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "propaga la incertidumbre y bloquea la conclusión" in text
    for record in ("contradicción detectada", "evidencia no utilizada", "regla o política de autoridad aplicada", "justificación de la resolución", "versión y fecha efectiva"):
        assert record in text
    assert "se escala a autoridad humana" in text
    assert "no reescribe retroactivamente" in text


def test_m10_preserves_authority_boundaries_and_distinguishes_missing_data():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "pertenecen exclusivamente a la Capa de Resolución de Conflictos" in text
    assert "Mat​riz de Autoridad Documental".replace("​", "") in text
    assert "`contradiction ≠ missing_data`" in text
    assert "En STK-M09 falta evidencia suficiente" in text
    assert "En STK-M10 existen dos o más datos o evidencias suficientemente identificados" in text


def test_m10_closes_methodology_without_authorizing_implementation_or_decision():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    assert "STK-M10 — Contradicciones — CERRADO" in matrix
    assert "`STK-M01…M10` quedan metodológicamente cerrados" in authority
    assert "no constituye por sí mismo un contrato técnico ni autoriza la implementación cuantitativa" in authority
    assert "no constituye una decisión de compra" in authority
    assert "autoridad decisional final permanece en la persona autorizada" in authority
    assert "**Estado actual:** APTO PARA DISEÑO DE CONTRATO TÉCNICO STK." in matrix
    assert "**No constituye por sí misma implementación ejecutable.**" in matrix

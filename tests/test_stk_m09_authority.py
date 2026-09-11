from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_M09_Missing_Data_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"


def test_m09_defines_missing_data_without_normalizing_uncertainty():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "imposibilidad de determinar de forma suficientemente evidenciada" in text
    assert "no equivale a cero, inexistencia, normalidad ni ausencia de riesgo" in text
    assert "no esté disponible, no sea verificable, esté desactualizado" in text


def test_m09_defines_minimum_states_and_limits_not_applicable():
    text = AUTHORITY.read_text(encoding="utf-8")
    for state in ("`UNKNOWN`", "`NOT_EVIDENCED`", "`NOT_APPLICABLE`", "`CONFLICTING_DATA`"):
        assert state in text
    assert "`NOT_APPLICABLE` exige evidencia de que el dato no aplica" in text


def test_m09_forbids_implicit_substitution_and_governs_imputation():
    text = AUTHORITY.read_text(encoding="utf-8")
    for replacement in ("cero", "medias históricas", "valores anteriores", "estimaciones", "valores por defecto"):
        assert replacement in text
    assert "política empresarial específica" in text
    assert "documentada, versionada y es trazable" in text
    assert "nunca se presenta como observación original" in text


def test_m09_propagates_uncertainty_without_inventing_criticality():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "STK-M01…M08" in text
    assert "propaga el estado de incertidumbre" in text
    assert "evita emitir como cierta una conclusión" in text
    assert "no declara por inferencia nuevas criticidades ni tratamientos parciales" in text
    assert "permanece `PENDING` conforme a la matriz de dependencias" in text


def test_m09_records_traceability_and_versions_reevaluation():
    text = AUTHORITY.read_text(encoding="utf-8")
    for field in ("dato ausente", "fuente esperada", "fecha de referencia", "causa conocida", "módulos afectados"):
        assert field in text
    assert "trazabilidad entre la evaluación anterior y la nueva versión" in text
    assert "no reescribe retroactivamente la anterior" in text


def test_m09_preserves_human_authority_and_stk_boundary():
    authority = AUTHORITY.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    assert "STK-M09 — Ausencia de datos — CERRADO" in matrix
    assert "no constituye por sí mismo una decisión de compra" in authority
    assert "autoridad decisional final permanece en la persona autorizada" in authority
    assert "`STK-M10` permanece pendiente" in authority
    assert "**Estado actual:** APTO PARA DISEÑO DE CONTRATO TÉCNICO STK." in matrix
    assert "**No constituye por sí misma implementación ejecutable.**" in matrix

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "01_Modelo" / "STK_Contract_Entry_Authority.md"
MATRIX = ROOT / "01_Modelo" / "Stock_Demand_Methodological_Matrix.md"
AUDIT = ROOT / "07_Pruebas" / "STK_Contract_Entry_Audit_v0.2.md"
PARAM_RULE = ROOT / "02_Parametros" / "Matriz_Parametros_Reglas_MVP.md"
RDM = ROOT / "04_Reglas" / "Rule_Dependency_Matrix.md"
CATALOG = ROOT / "02_Parametros" / "Catalogo_Parametros_MVP_v0.3.md"


def test_contract_entry_gate_is_go_for_contract_design_only():
    matrix = MATRIX.read_text(encoding="utf-8")
    audit = AUDIT.read_text(encoding="utf-8")
    assert "**Estado actual:** APTO PARA DISEÑO DE CONTRATO TÉCNICO STK." in matrix
    assert "**No constituye por sí misma implementación ejecutable.**" in matrix
    assert "**DICTAMEN: GO A DISEÑO DE CONTRATO TÉCNICO STK.**" in audit
    assert "La implementación ejecutable seguirá bloqueada" in audit


def test_approved_stock_availability_semantics_are_materialized():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "`stock_on_hand` representa la **cantidad física evidenciada" in text
    assert "`stock_committed` representa la **parte de `stock_on_hand` reservada o asignada" in text
    assert "`stock_available = max(0, stock_on_hand - stock_committed)`" in text
    assert "`availability_deficit = stock_committed - stock_on_hand`" in text
    assert "no produce stock disponible negativo" in text


def test_approved_demand_policy_keeps_sales_separate_and_window_complete():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "Previsión externa/autorizada" in text
    assert "Base histórica derivada de `consumption`" in text
    assert "`historical_daily_demand = total_evidenced_consumption / evidenced_days_in_window`" in text
    assert "no se reduce silenciosamente la ventana" in text
    assert "Las ventas históricas no se convierten automáticamente" in text
    assert "`P-PYE-005 — Considerar ventas históricas` no autoriza por sí mismo" in text


def test_stk_parameter_rule_mapping_confirms_only_demonstrated_relations():
    mapping = PARAM_RULE.read_text(encoding="utf-8")
    rdm = RDM.read_text(encoding="utf-8")
    for relation in (
        "`P-STK-004 → R-STK-002`",
        "`P-STK-004 → R-STK-003`",
        "`P-STK-005 → R-STK-003`",
    ):
        assert relation in mapping
    for dependency_id in (
        "DEP-STK-004-RSTK-002",
        "DEP-STK-004-RSTK-003",
        "DEP-STK-005-RSTK-003",
    ):
        assert dependency_id in rdm
    assert "P-PYE-001…006" in rdm
    assert "`REJECTED` como relación directa" in rdm


def test_catalog_initial_values_remain_pending_not_normative_defaults():
    catalog = CATALOG.read_text(encoding="utf-8")
    authority = AUTHORITY.read_text(encoding="utf-8")
    for row in (
        "| STK-002 | Stock de seguridad | 15 | % del consumo | Riesgo | Pendiente de validación |",
        "| STK-003 | Cobertura mínima | 30 | días | Compras | Pendiente de validación |",
        "| STK-004 | Cobertura máxima | 90 | días | Exceso de stock | Pendiente de validación |",
        "| STK-005 | Tolerancia de exceso | 10 | % | Alerta | Pendiente de validación |",
        "| STK-006 | Periodo para calcular consumo | 12 | meses | Proyección | Pendiente de validación |",
        "| PYE-001 | Horizonte de proyección | 90 | días | Pendiente de validación |",
        "| PYE-006 | Umbral de riesgo de rotura | 15 | días | Pendiente de validación |",
    ):
        assert row in catalog
    assert "no valida los valores iniciales del catálogo" in authority
    assert "no convertir esos valores iniciales en defaults normativos" in authority


def test_contract_entry_authority_does_not_expand_c0_or_decide_purchase():
    text = AUTHORITY.read_text(encoding="utf-8")
    assert "no modifica C0" in text
    assert "no autoriza reposición automática" in text
    assert "no convierte una métrica en una decisión" in text
    assert "La autoridad decisional final permanece en la persona autorizada" in text

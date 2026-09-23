# EIOS — Reference Business Case 001 · Supplier Risk/Value Extension Audit v0.1

**Baseline:** `main @ 560769510ec127907710d60c1f8e3faca673d60b`  
**Fecha:** 23/09/2026  
**Estado:** MATERIALIZADO EN RAMA / CI PENDIENTE

## 1. Propósito

Ampliar `REF-BUSINESS-001` desde:

```text
QTG → PRICE → TCO → C0
```

hasta:

```text
QTG → PRICE → TCO → SUPPLIER_RISK_VALUE → C0
```

sin introducir scoring, ranking, preferencia de proveedor ni recomendación.

## 2. Supplier Evidence Core

La identidad factual del proveedor se construye mediante el motor público:

`evaluate_supplier_evidence(SupplierEvidenceInput(...))`

El input queda ligado a:

- PurchaseOperation exacta;
- DecisionContext exacto;
- company_scope del caso de referencia;
- evaluation_date exacta de la operación.

En esta primera extensión no se declaran candidatos alternativos, observaciones
comparativas, métricas externas ni comparaciones estructurales.

El resultado factual conserva exclusivamente al proveedor actual.

## 3. Evaluación Risk/Value

Se aporta una única dimensión sintética:

```text
supplier_id = proveedor actual
dimension   = RELIABILITY
state       = FAVORABLE
```

La dimensión dispone de:

- authority_ref demostrada mediante Evidence;
- assessment evidence demostrada;
- methodology_ref explícita;
- assessment_ref explícita;
- trace_ref explícita.

No se publica ninguna dimensión Value porque no existe candidato alternativo en
esta extensión.

## 4. Invoker

La capacidad entra exclusivamente por:

`build_provenanced_supplier_risk_value_invoker(...)`

El builder:

- congela SupplierEvidenceResult;
- congela assessments y evidences;
- revalida identidad contra PurchaseOperation/DecisionContext runtime;
- exige authority_ref demostrada;
- exige evidence_refs válidas;
- produce CapabilityExecution sin score ni selección.

## 5. Resultado esperado

```text
QTG
→ PRICE
→ TCO
→ SUPPLIER_RISK_VALUE
→ C0
```

La capacidad Supplier Risk/Value debe resultar:

```text
status           = COMPLETED
result_available = true
unresolved_items = ()
```

La ejecución global técnica debe permanecer `COMPLETED`.

## 6. Salvaguardas

La extensión no altera:

- QTG `NO_APTO/BAJA`;
- `material_nature=SYNTHETIC`;
- `operational_path=FORBIDDEN`;
- `operational_effect=false`;
- `decision_authority=false`.

Un estado Risk `FAVORABLE` describe únicamente la evaluación sintética de una
dimensión. No equivale a aprobación del proveedor ni recomendación de compra.

## 7. Fuera de alcance

No se introducen todavía:

- proveedor alternativo;
- comparación Value;
- score;
- ranking;
- preferred supplier;
- selected supplier;
- recomendación;
- R-PROV;
- decisión empresarial.

## 8. Materialización

Se modifica únicamente:

- `tests/test_reference_business_case_001.py`;

y se añade este documento.

No se modifica código de producción.

## 9. Criterio de cierre

CI deberá demostrar:

- Supplier Evidence Core construido desde inputs físicos tipados;
- Risk assessment ligada a autoridad/evidencia sintéticas demostradas;
- invoker provenance-safe;
- orden canónico `QTG → PRICE → TCO → SUPPLIER_RISK_VALUE → C0`;
- Supplier Risk/Value `COMPLETED`;
- QTG desfavorable preservado;
- ausencia de efecto operacional y autoridad decisional.

## 10. Continuidad

El siguiente frente será Scenario/VF. Antes de integrarlo en el caso de
referencia se auditará la frontera de Scenario Coordination para distinguir la
reconstrucción provenance-safe de Stage 2 de la actual fachada interna de
presentación, que no certifica por sí sola el origen del orchestration result.

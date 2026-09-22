# EIOS — R-PROV-001 / R-PROV-002 Provenance-Safe Core Implementation Audit v0.1

**Baseline de integración:** `main @ a4d31e7731e1dffb51f7f375afe91d77b36d48c9`  
**Fecha:** 22/09/2026  
**Estado:** CERRADO / MATERIALIZADO / CI VALIDATED  
**Autoridad:** `01_Modelo/PROV_Supplier_Alternatives_Authority_v0.1.md`  
**Contrato:** `08_Implementacion/R_PROV_001_002_Provenance_Safe_Core_Technical_Contract_v0.1.md`

## A1 — Frontera Supplier Evidence

Los bridges públicos consumen `SupplierEvidenceInput` y reconstruyen internamente:

```text
SupplierEvidenceInput
→ evaluate_supplier_evidence
→ SupplierEvidenceResult
```

No aceptan `SupplierEvidenceResult` desprendido.

**Resultado:** CONFORME.

## A2 — Identidad contextual

Se verifican:

- `decision_id`;
- `scenario_id`;
- `rules_version`;
- `parameters_version`;
- `data_snapshot_id`;
- `article_id`;
- proveedor actual;
- `purchase_operation_ref`;
- `supplier_evidence_ref`;
- `candidate_id`;
- `supplier_id`.

Mismatch falla cerrado.

**Resultado:** CONFORME.

## A3 — Cobertura

`COMPLETE` requiere evidencia explícita demostrada y vinculada al carrier exacto.

`PARTIAL` y `NOT_DETERMINABLE` no permiten demostrar FALSE.

**Resultado:** CONFORME.

## A4 — R-PROV-001

TRUE requiere:

```text
EVIDENCED_CANDIDATE
+
POTENTIALLY_BETTER
```

para el mismo candidato.

FALSE requiere:

```text
COMPLETE
+
todas las candidaturas EVIDENCED_CANDIDATE
+
determinación para todo candidato
+
todas NOT_POTENTIALLY_BETTER
```

**Resultado:** CONFORME.

## A5 — R-PROV-002

TRUE requiere el mismo candidato:

```text
EVIDENCED_CANDIDATE
+
COMPARABLE
+
SIGNIFICANT_IMPROVEMENT
```

FALSE requiere cobertura completa, universo resuelto, ambas determinaciones concluyentes por candidato y ausencia de la combinación positiva.

**Resultado:** CONFORME.

## A6 — Independencia

Existen bundles separados:

- `SupplierAlternativeOpportunityRuleInputs`;
- `SupplierAlternativeComparisonRuleInputs`.

Cada regla reconstruye Supplier Evidence de forma independiente.

No existe dependencia Assessment→Assessment.

**Resultado:** CONFORME.

## A7 — Evidencia

Los carriers concluyentes requieren `Evidence.state = DEMONSTRATED` vinculada mediante `demonstration_ref` al hash exacto del carrier.

Se rechaza:

- evidence_id desconocido;
- source_type incompatible;
- demonstration_ref falsificado;
- evidencia adicional no referenciada.

**Resultado:** CONFORME.

## A8 — No promoción estructural

La API R-PROV-002 no recibe:

- `StructuralComparisonResult`;
- `difference_decimal`;
- resultado PRICE desprendido.

La comparabilidad y la mejora significativa deben llegar como carriers explícitos autorizados.

**Resultado:** CONFORME.

## A9 — No ranking / scoring

No se materializan:

- score;
- weight;
- rank;
- winner;
- best supplier;
- provider recommendation;
- cambio automático.

**Resultado:** CONFORME.

## A10 — Catálogo y CRC

Metadata:

```text
R-PROV-001 → R2 / MEDIA → NEGOCIAR
R-PROV-002 → R2 / ALTA  → NEGOCIAR
```

No se crea ningún resultado CRC nuevo.

**Resultado:** CONFORME.

## A11 — Pruebas añadidas

La suite específica cubre:

- TRUE con cobertura parcial;
- FALSE exhaustivo;
- universo COMPLETE vacío;
- candidato no evidenciado;
- carrier indeterminado;
- refs falsificados;
- supplier/candidate mismatch;
- evidencia falsificada;
- ausencia de API de resultado desprendido;
- no promoción de comparación estructural;
- metadata;
- integración de orchestrator.

## A12 — Validación CI e integración

PR #305 (`feat(prov): materialize provenance-safe supplier alternatives rules`) fue validada por CI #1158: **SUCCESS**.

La PR se integró sin deriva sobre el baseline esperado:

```text
main @ a4d31e7731e1dffb51f7f375afe91d77b36d48c9
```

La CI post-merge #1159 ejecutó y superó:

- suite Python completa;
- validación SQL Server C0;
- validación Decision Versioning;
- validación Parameter Configuration.

**Resultado:** CONFORME.

## Dictamen

```text
DISEÑAR       ✅
AUDITAR       ✅
DEPURAR       ✅
AUDITAR 2     ✅
CERRAR        ✅
MATERIALIZAR  ✅
CI PR         ✅ #1158
MERGE         ✅ PR #305
CI MAIN       ✅ #1159
```

**DICTAMEN: R-PROV-001 / R-PROV-002 PROVENANCE-SAFE CORE v0.1 — CERRADO / MATERIALIZADO / CI VALIDATED EN SU ALCANCE AUTORIZADO.**

Persisten fuera del alcance los productores empresariales que determinen `POTENTIALLY_BETTER`, `COMPARABLE` o `SIGNIFICANT_IMPROVEMENT`; su ausencia no invalida el core y debe conservarse como `NOT_DETERMINABLE / NOT_EVALUABLE` cuando proceda.

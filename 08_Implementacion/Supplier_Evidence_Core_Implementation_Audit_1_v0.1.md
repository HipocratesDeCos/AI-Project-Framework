# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION AUDIT 1 v0.1

**Estado:** COMPLETADA — 3 HALLAZGOS OBJETIVOS  
**Fecha:** 11/09/2026  
**Baseline de implementación:** `main @ 18558b5759ca181d8fe234623440341211163a8a`  
**Contrato de partida:** v0.3.2 🔒

---

## 1. Alcance auditado

Implementación real inicial:

- `eios/supplier/models.py`;
- `eios/supplier/engine.py`;
- `eios/supplier/__init__.py`;
- `tests/test_supplier_evidence_core.py`.

La auditoría revisa representabilidad, pérdida de información, determinismo, autoridad, tipos, temporalidad, comparación, agregados y ausencia de funciones decisionales.

---

## 2. Dictamen

La implementación respeta la frontera no decisional y no introduce scoring, ranking, R-PROV ni cálculo de riesgo.

Sin embargo, se identifican **tres hallazgos físicos** que deben resolverse antes de CI/cierre.

Ninguno requiere política empresarial nueva.

---

## 3. Hallazgos

### PROV-IMPL-A1-01 — El resultado no conserva la candidatura factual completa

`SupplierEvidenceResult` devuelve `candidate_resolutions`, pero no conserva los objetos `SupplierCandidateEvidence`.

`CandidateResolution` conserva IDs de evidencia/issues/traces, pero pierde del resultado:

- `source_ref`;
- `captured_at`;
- `applicability_ref`;
- `valid_from`;
- `valid_to`;
- `object_id`.

La metodología cerrada exige salida factual y trazable de candidatos y source references. El input seguiría existiendo en memoria, pero el resultado aislado no permitiría reconstruir completamente la evidencia de candidatura.

**Corrección:** `SupplierEvidenceResult` debe conservar:

```text
candidates: tuple[SupplierCandidateEvidence, ...]
```

en el mismo orden de entrada, además de `candidate_resolutions`.

Esto no añade valoración ni autoridad; evita pérdida de trazabilidad.

---

### PROV-IMPL-A1-02 — Deduplicar issues solo por issue_id puede causar pérdida de datos

El engine inicial usa:

```text
issue_id
```

como única clave de deduplicación de `SupplierDataIssueRef`.

El contrato no impone unicidad global de `issue_id` entre todos los registros del sobre. Por tanto, dos observaciones distintas podrían contener:

```text
issue_id = "I-1"
issue_record_ref distinto
evidence_refs distintas
```

La comparación perdería silenciosamente la segunda incidencia.

**Corrección:** deduplicar únicamente issues **exactamente iguales** en todos sus campos contractuales, preservando incidencias distintas aunque compartan `issue_id`.

No se introduce prioridad entre issues.

---

### PROV-IMPL-A1-03 — `dimension` singular es ambigua cuando las dimensiones son incompatibles

En el engine inicial, una comparación:

```text
current.dimension   = PRICE_REFERENCE
candidate.dimension = LEAD_TIME
```

produce correctamente:

```text
NOT_STRUCTURALLY_COMPARABLE
DIMENSION_INCOMPATIBLE
```

pero `StructuralComparisonResult.dimension` se rellena con `current.dimension`.

Eso representa el resultado como si la comparación tuviera una única dimensión PRICE, cuando precisamente se ha demostrado una incompatibilidad dimensional.

**Corrección física mínima:** sustituir en el resultado:

```text
dimension
```

por:

```text
current_dimension
candidate_dimension
```

La igualdad de ambas sigue siendo condición para `STRUCTURALLY_COMPARABLE`.

Esto es una corrección de representabilidad; no cambia la semántica empresarial ni la precedencia del algoritmo.

---

## 4. Verificaciones superadas

Audit 1 confirma que la implementación inicial sí preserva:

- DecisionContext canónico;
- PurchaseOperation como ancla;
- company_scope separado;
- estados de candidatura;
- GAP ≠ FALSE;
- contradicciones explícitas;
- strict bool antes de coerción numérica;
- métricas externas sin autoautorización;
- PRICE authority ref;
- ausencia de cross-product;
- diferencia Decimal descriptiva;
- SupplierItemRef namespaced;
- orden de entrada;
- no mutación;
- ausencia de scoring/ranking;
- ausencia de Assessment/CRC/recomendación/decisión.

---

## 5. Consecuencia contractual

Los hallazgos A1-01 y A1-03 revelan dos defectos de representabilidad del contrato v0.3.2 que solo se hacen observables al materializar el resultado físico.

Se justifica una **corrección técnica estrecha v0.3.3**, sin reabrir metodología v0.3 ni gaps PROV.

A1-02 requiere únicamente depuración del engine/tests.

---

## 6. Decisión

**IMPLEMENTACIÓN INICIAL: NO CERRABLE.**

Secuencia requerida:

```text
corrección contractual técnica v0.3.3
→ depuración de models/engine/tests
→ Audit 2 de implementación
→ CI
```

# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION CONTRACT v0.3.3

**Estado:** 🔒 CERRADO — AUDIT 2 + CI SUPERADOS  
**Fecha:** 11/09/2026  
**Base normativa:** `Supplier_Evidence_Core_Implementation_Contract_v0.3.2.md` 🔒  
**Causa:** hallazgos objetivos `PROV-IMPL-A1-01` y `PROV-IMPL-A1-03`

---

## 1. Naturaleza de esta versión

v0.3.3 es una **corrección técnica estrecha de representabilidad** descubierta durante la materialización física.

No reabre:

- metodología Supplier Evidence Core v0.3;
- gaps PROV-G02…G09;
- Rules;
- parámetros;
- C0;
- PRICE/TCO/STK/Finance/Q&T;
- CRC;
- autoridad decisional.

Salvo los dos overrides definidos a continuación, **todo el contrato v0.3.2 permanece vigente sin cambios**.

---

## 2. Override TC-3.3-01 — Preservación completa de candidaturas en el resultado

### Problema

`SupplierEvidenceResult` v0.3.2 conservaba `candidate_resolutions`, pero no los objetos `SupplierCandidateEvidence` completos.

Esto podía perder del resultado aislado:

- `source_ref`;
- `captured_at`;
- `applicability_ref`;
- `valid_from` / `valid_to`;
- `object_id`;
- referencias originales de issues/traces de candidatura.

### Contrato corregido

`SupplierEvidenceResult` deberá contener:

```text
identity: SupplierResultIdentity
current_supplier_id
candidates: tuple[SupplierCandidateEvidence, ...]
candidate_resolutions: tuple[CandidateResolution, ...]
observations
historical_facts
external_metrics
signals
structural_comparisons
unresolved_items
conflicting_items
limitations
```

### Invariantes

1. `candidates` conserva exactamente el orden de `SupplierEvidenceInput.candidates`.
2. El engine no modifica los objetos de candidatura.
3. `candidate_resolutions[i]` corresponde a `candidates[i]` por `candidate_id`.
4. Conservar `candidates` no otorga autoridad adicional ni crea una segunda fuente; es preservación del input factual en la salida normalizada.

---

## 3. Override TC-3.3-02 — Dimensiones explícitas en StructuralComparisonResult

### Problema

El campo singular:

```text
dimension
```

es ambiguo cuando las observaciones solicitadas pertenecen a dimensiones distintas y el resultado es `NOT_STRUCTURALLY_COMPARABLE`.

### Contrato corregido

`StructuralComparisonResult` sustituye `dimension` por:

```text
current_dimension: SupplierDimension
candidate_dimension: SupplierDimension
```

El resto permanece:

```text
comparison_id
current_observation_id
candidate_observation_id
current_dimension
candidate_dimension
state
difference_decimal
comparison_authority_ref
issue_refs
limitations
```

### Invariantes

1. `current_dimension` se copia de `current_observation.dimension`.
2. `candidate_dimension` se copia de `candidate_observation.dimension`.
3. `STRUCTURALLY_COMPARABLE` exige `current_dimension == candidate_dimension` por la precedencia ya definida en v0.3.2.
4. La discrepancia dimensional se representa sin elegir una dimensión como dominante.
5. Este cambio no modifica la autoridad PRICE ni la semántica `STRUCTURALLY_COMPARABLE ≠ RULE_COMPARABLE`.

---

## 4. Corrección de implementación asociada — identidad de issues

El hallazgo `PROV-IMPL-A1-02` no cambia el esquema contractual.

La deduplicación estable de `issue_refs` se interpretará de forma conservadora:

> Solo dos `SupplierDataIssueRef` exactamente iguales en todos sus campos contractuales se consideran duplicados.

Compartir únicamente `issue_id` **no es suficiente** para descartar una incidencia.

Esto evita pérdida de información cuando IDs locales se reutilicen en registros diferentes.

---

## 5. Tests adicionales obligatorios

Añadir como mínimo:

1. resultado conserva candidatura completa (`source_ref`, vigencia, aplicabilidad);
2. dos issues con mismo `issue_id` pero distinto `issue_record_ref/evidence_refs` se preservan ambos;
3. comparación de dimensiones incompatibles devuelve ambas dimensiones explícitas;
4. comparación compatible devuelve dimensiones iguales;
5. orden candidato ↔ resolución permanece alineado.

---

## 6. Evidencia de cierre

- Audit 1 de implementación: completada y depurada.
- Audit 2 final estática: **SUPERADA — 0 bloqueos**.
- Snapshot ejecutable certificado: `d45ed1ca9d557d8d4cebd121c13eed79d182992d`.
- GitHub Actions `EIOS Tests` **#586: SUCCESS**.
- Suite Python completa: **SUCCESS**.
- Validación SQL transversal: **SUCCESS**.
- No existen cambios ejecutables posteriores al snapshot certificado en el momento de cierre.

---

## 7. Estado final

**v0.3.3 queda 🔒 CERRADA.**

La implementación física Supplier Evidence Core v0.1 es apta para cierre documental, CI del HEAD final y reconciliación pre-merge.

Los gaps PROV-G02…G09 permanecen fuera de alcance y no se consideran resueltos por este cierre.

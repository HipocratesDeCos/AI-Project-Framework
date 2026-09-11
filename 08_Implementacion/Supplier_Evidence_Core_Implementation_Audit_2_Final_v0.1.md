# EIOS — SUPPLIER EVIDENCE CORE · IMPLEMENTATION AUDIT 2 FINAL v0.1

**Estado:** SUPERADA — 0 BLOQUEOS ESTÁTICOS · CI PENDIENTE  
**Fecha:** 11/09/2026  
**Rama:** `prov/supplier-evidence-core-implementation-v0.1`  
**Baseline:** `main @ 18558b5759ca181d8fe234623440341211163a8a`  
**Autoridad:** Supplier Evidence Core methodology v0.3 + Implementation Contract v0.3.2 + correction v0.3.3

---

## 1. Objeto

Revisar la implementación física depurada tras Audit 1, verificando que el paquete `eios/supplier` materializa únicamente Supplier Evidence Core factual y no amplía autoridad hacia scoring, ranking, Rules, CRC o decisión.

Archivos ejecutables auditados:

- `eios/supplier/models.py`
- `eios/supplier/engine.py`
- `eios/supplier/__init__.py`
- `tests/test_supplier_evidence_core.py`

---

## 2. Resultado de los hallazgos Audit 1

### PROV-IMPL-A1-01 — preservación de candidatura completa
**RESUELTO.**

`SupplierEvidenceResult.candidates` conserva los objetos `SupplierCandidateEvidence` originales, en orden de entrada, junto con `candidate_resolutions` alineadas por `candidate_id`.

### PROV-IMPL-A1-02 — deduplicación de incidencias
**RESUELTO.**

El engine solo considera duplicadas dos `SupplierDataIssueRef` exactamente iguales en todos sus campos contractuales. Compartir `issue_id` no elimina incidencias diferentes.

### PROV-IMPL-A1-03 — dimensiones de comparación incompatibles
**RESUELTO.**

`StructuralComparisonResult` conserva `current_dimension` y `candidate_dimension`. Una comparación incompatible no elige una dimensión dominante.

---

## 3. Audit 2 — invariantes de entrada

Verificado:

- `DecisionContext` y `PurchaseOperation` comparten `decision_id/scenario_id`;
- metodología fijada a `0.3`;
- IDs únicos por colección;
- candidato alternativo distinto del proveedor actual;
- objeto/candidato/observación ligados al artículo evaluado;
- observación alternativa ligada a `candidate_id` existente y mismo proveedor;
- hechos, señales y métricas limitados al conjunto de proveedores evaluado;
- temporalidad futura rechazada conforme al contrato;
- requests con observaciones existentes, lados current/candidate correctos y sin autocomparación.

No se añade ninguna inferencia de candidatura.

---

## 4. Audit 2 — tipado y estados

Verificado:

- modelos Pydantic `extra=forbid`, `frozen=True`;
- `bool` rechazado antes de coerción a INTEGER/DECIMAL;
- BOOLEAN requiere bool real;
- Decimal determinado finito;
- KNOWN publica exactamente el valor de su `value_kind`;
- estados no KNOWN no fabrican valores;
- CONFLICTING_DATA exige contradicción demostrada;
- DATE/TEXT/BOOLEAN no aceptan unidad;
- Supplier no convierte unidades;
- métricas externas autorizadas requieren dato KNOWN y `usage_authority_ref`.

---

## 5. Audit 2 — algoritmo de comparación

La precedencia implementada coincide con el contrato:

1. candidatura actual demostrada;
2. estado de evidencia de observaciones;
3. vigencia;
4. compatibilidad estructural básica;
5. autoridad PRICE;
6. `STRUCTURALLY_COMPARABLE`;
7. diferencia descriptiva Decimal.

Se confirma:

- solo se procesan `comparison_requests` explícitos;
- no existe cross-product;
- incompatibilidad dimensional precede a autoridad PRICE;
- PRICE sin authority ref no se autoautoriza;
- diferencia = candidate − current solo en Decimal compatible;
- diferencia no produce mejor/peor;
- `STRUCTURALLY_COMPARABLE ≠ RULE_COMPARABLE`.

---

## 6. Audit 2 — resultado y trazabilidad

Verificado:

- identidad derivada de `DecisionContext`, scope, artículo y fecha;
- candidaturas originales preservadas;
- orden de candidatos/resoluciones y demás colecciones preservado;
- `SupplierItemRef` usa namespace `(item_type, item_id)`;
- unresolved/conflicting se agregan de forma estable;
- issues se deduplican solo por igualdad contractual completa;
- inputs no se mutan;
- colecciones vacías no se interpretan como inexistencia empresarial.

---

## 7. Fronteras negativas

No aparecen en modelos ni engine:

- `supplier_score`;
- ranking;
- preferred supplier;
- supplier risk level;
- reliability/compliance score calculado;
- concentración calculada;
- `RULE_COMPARABLE`;
- R-PROV-001/002;
- Assessment;
- effect/severity;
- CRC;
- recomendación;
- purchase decision.

No se recalculan PRICE, TCO, STK, Finance ni Quality & Trust.

---

## 8. Gaps deliberadamente fuera de alcance

Permanecen abiertos y **no son bloqueos del Supplier Evidence Core factual**:

- PROV-G02 fiabilidad cuantitativa;
- PROV-G03 cumplimiento cuantitativo;
- PROV-G04 valoración comparativa de disponibilidad;
- PROV-G05 concentración;
- PROV-G06 “potencialmente mejores”;
- PROV-G07 “mejora significativamente”;
- PROV-G08 trade-offs;
- PROV-G09 impacto de señales críticas.

Su existencia no autoriza defaults, scores ni heurísticas.

---

## 9. Dictamen

**AUDIT 2 ESTÁTICA: SUPERADA — 0 BLOQUEOS.**

La implementación es apta para validación dinámica en CI.

El cierre técnico definitivo queda condicionado a:

1. CI sobre el HEAD exacto de esta implementación;
2. suite Python completa verde;
3. validación SQL transversal verde;
4. ausencia de cambios posteriores en código sin nueva auditoría.

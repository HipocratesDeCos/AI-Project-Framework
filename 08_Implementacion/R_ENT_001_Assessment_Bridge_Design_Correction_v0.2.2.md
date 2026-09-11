# EIOS — R-ENT-001 · Assessment Bridge Design Correction v0.2.2

**Estado:** CORREGIDO — CANDIDATO A AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Extiende:** v0.2 + correction v0.2.1

---

## 1. Coherencia de versiones y snapshot

La proyección STK que sostiene `BaselineStockoutQualification` debe pertenecer al mismo contexto reproducible de la evaluación, salvo `scenario_id`, cuya semántica no se reinterpreta como baseline.

Se exige:

```text
projection.identity.decision_id == context.decision_id
projection.identity.rules_version == context.rules_version
projection.identity.parameters_version == context.parameters_version
projection.identity.data_snapshot_id == context.data_snapshot_id
```

No se exige:

```text
projection.identity.scenario_id == context.scenario_id
```

porque la metodología ENT prohíbe usar `scenario_id` como prueba de baseline y no autoriza inferir equivalencia entre escenario base y escenario de compra.

---

## 2. Binding de estados no concluyentes

Para permitir que un objeto C0 `Evidence(state=DEMONSTRATED)` represente trazablemente la existencia de una contradicción, gap cualificado o indeterminación conservada por ENT, los conjuntos role-specific se amplían sin mezclar roles.

### Baseline refs

```text
baseline.evidence_refs
∪ baseline.trace_refs
∪ baseline.issue_refs
∪ baseline.unresolved_refs
∪ {baseline_relation_ref if not null}
∪ {projection_provenance_ref if not null}
∪ {purchase_exclusion_ref if not null}
```

### Delivery refs

```text
delivery.evidence_refs
∪ delivery.trace_refs
∪ delivery.issue_refs
∪ {delivery_semantic_ref if not null}
∪ {purchase_applicability_ref if not null}
∪ {source_ref if not null}
```

Esto solo vincula provenance. No convierte una contradicción o indeterminación en una evaluación booleana.

La precedencia permanece:

```text
ENT NOT_EVIDENCED / CONFLICTING_DATA / NOT_DETERMINABLE
→ Assessment NOT_EVALUABLE / None
```

incluso cuando el objeto C0 Evidence que documenta el estado sea `DEMONSTRATED`.

---

## 3. Fronteras preservadas

- no comparación de `scenario_id` como baseline;
- no creación de componente RDM;
- no cambio a Evidence Contract;
- no cambio a Assessment;
- no nuevo parámetro;
- no lógica decisional.

---

## 4. Estado

Correcciones defensivas incorporadas.  
Procede **AUDIT 2 FINAL** sobre el diseño compuesto v0.2 + v0.2.1 + v0.2.2.

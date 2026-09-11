# EIOS — R-ENT-001 · Assessment Bridge Audit 2 Final v0.2.2

**Estado:** SUPERADA — 0 BLOQUEADORES  
**Fecha:** 11/09/2026  
**Objeto:** diseño compuesto v0.2 + corrections v0.2.1 + v0.2.2

---

## 1. Dictamen ejecutivo

El diseño compuesto del bridge `R-ENT-001 → Assessment` queda coherente con la condición normativa, las dependencias RDM, Evidence Contract, Assessment C0 y las fronteras cerradas de ENT/STK/Supplier.

**Bloqueadores:** 0.  
**Política empresarial nueva:** 0.  
**Parámetros nuevos:** 0.  
**Dependencias RDM nuevas:** 0.

---

## 2. Regla normativa

SUPERADA.

La única condición booleana evaluada sigue siendo:

```text
expected_delivery_date > depletion_date
```

El bridge no produce `NEGOCIAR`; únicamente determina el resultado individual de `R-ENT-001`.

---

## 3. Mapeo ENT → Assessment

SUPERADO.

```text
LATE_DELIVERY_DEMONSTRATED
→ EVALUABLE / TRUE

NOT_LATE_DEMONSTRATED
→ EVALUABLE / FALSE

NOT_LATE_WITHIN_EVIDENCED_HORIZON
→ EVALUABLE / FALSE

NOT_EVIDENCED
→ NOT_EVALUABLE / None

CONFLICTING_DATA
→ NOT_EVALUABLE / None

NOT_DETERMINABLE
→ NOT_EVALUABLE / None
```

`NOT_LATE_WITHIN_EVIDENCED_HORIZON` permanece limitado al horizonte ya demostrado por ENT; no hay extrapolación.

---

## 4. GAP / evidencia inválida

SUPERADA.

Un resultado ENT concluyente solo produce `EVALUABLE` cuando ambas dependencias C0 resultan `VALID`.

```text
GAP / INVALID
→ NOT_EVALUABLE
```

Nunca se transforma ausencia o insuficiencia en `FALSE`.

---

## 5. Identidad C0

SUPERADA.

Se demuestra compatibilidad de:

```text
PurchaseOperation ↔ DecisionContext
Rule.version ↔ DecisionContext.rules_version
PurchaseOperation.article_id ↔ ENT article_id
PurchaseOperation.supplier_id ↔ ENT supplier_id
```

Las incompatibilidades son errores de contrato y no resultados empresariales.

---

## 6. Versiones y snapshot STK

SUPERADA.

La proyección factual utilizada debe compartir con C0:

```text
decision_id
rules_version
parameters_version
data_snapshot_id
```

No se exige igualdad de `scenario_id`, preservando la prohibición de usarlo como prueba de baseline.

---

## 7. Copy integrity

SUPERADA.

Sin volver a ejecutar ENT, el bridge verifica igualdad exacta de:

```text
expected_delivery_date
depletion_date
horizon_end
baseline_projection_ref
```

entre el resultado ENT y su provenance input correspondiente.

---

## 8. Evidence role binding

SUPERADA.

Los roles permanecen separados:

```text
BaselineStockoutQualification
PurchaseSpecificDeliveryTimingEvidence
```

`demonstration_ref` se vincula únicamente a referencias pertenecientes a su dependencia original.

No existe validación contra un pool agregado que permita cruzar refs entre roles.

---

## 9. Estados no concluyentes

SUPERADA.

Una contradicción o indeterminación puede estar documentada mediante un objeto C0 `Evidence(state=DEMONSTRATED)` sin que ello convierta la regla en evaluable.

La suficiencia del resultado procede de ENT + evidencia requerida, no del estado `DEMONSTRATED` aislado.

---

## 10. SAME_DAY

SUPERADA.

Igualdad de fecha no satisface `delivery > depletion`:

```text
EVALUABLE / FALSE
```

con reason explícito que conserva que el orden intradía no está demostrado.

---

## 11. Assessment contract

SUPERADA.

Salida limitada a:

```text
rule_id
status
outcome
evidence_ids
reason
```

No se incorporan:

```text
effect
severity
recommendation
decision
priority
CRC
score
confidence
```

---

## 12. evidence_ids

SUPERADA.

Solo se publican IDs de objetos C0 `Evidence`, en orden baseline → delivery.

Refs ENT permanecen como provenance y no se convierten en IDs C0.

---

## 13. RDM

SUPERADA.

Se consumen únicamente:

```text
DEP-ENT-BSQ-RENT-001
DEP-ENT-DTE-RENT-001
```

Permanecen sin alteración:

```text
Criticality = PENDING
Evaluability_Impact = PENDING
Fallback = NONE
Affected_Component = NONE
```

La importación técnica de modelos ENT no se registra por inferencia como dependencia COMPONENT.

---

## 14. Fronteras de componentes

| Componente | Dictamen |
|---|---|
| C0 | preservado |
| ENT analyzer | preservado |
| STK | preservado |
| Supplier | preservado |
| Evidence Contract | preservado |
| Rules | propietario del bridge |
| CRC | fuera de alcance |
| decisión humana | preservada |

---

## 15. Alcance autorizado de materialización

Se autoriza exclusivamente:

```text
eios/rules/delivery.py
tests/test_r_ent_001_assessment_bridge.py
```

Puede actualizarse `eios/rules/__init__.py` únicamente para exportar la función pública, sin lógica adicional.

No se autorizan cambios en C0, ENT, STK, Supplier, RDM, Rule Matrix, parámetros ni SQL.

---

## 16. Resultado

**AUDIT 2 FINAL: SUPERADA.**  
**Bloqueadores:** 0.  
**Procede:** CERRAR diseño → MATERIALIZAR → CI.

# EIOS — Commercial COM001/COM002 Completion Package Proposal v0.1

**Baseline:** `main @ 169e50771c9f2dafbb316dab60a9d2866a398534`  
**Fecha:** 23/09/2026  
**Estado:** 🔒 AUTORIZADO — VIGENTE  
**Reglas:** `R-COM-001`, `R-COM-002`

## 1. Objetivo

Cerrar en un único paquete:

- COM001-G01…G05;
- COM002-G01…G06;
- carriers provenance-safe;
- semántica factual;
- semántica económica mínima;
- bridges Rules;
- metadata CRC;
- orchestrator;
- RDM y tests.

No se reutiliza automáticamente `COMMERCIAL_CONDITION`, `P-PAG-005` ni `P-MGE-006`.

## 2. Principio transversal

```text
mención comercial ≠ descuento demostrado
rappel potencial ≠ beneficio cierto
condición no resuelta ≠ beneficio económico aplicable
```

Solo Evidence explícita y vinculada puede convertir una condición comercial en un hecho concluyente.

## 3. R-COM-001 — descuento disponible

### 3.1 Carrier propuesto

```text
DiscountOpportunityEvidence
├── article_id
├── supplier_id
├── evaluation_date
├── opportunity_ref
├── applicability_ref
├── opportunity_state
├── applicability_state
├── evidence_refs
└── trace_refs
```

`opportunity_state`:

```text
AVAILABLE
NOT_AVAILABLE
NOT_DETERMINABLE
CONFLICTING
```

`applicability_state`:

```text
CONFIRMED
CONDITIONAL
NOT_CONFIRMED
NOT_DETERMINABLE
CONFLICTING
```

### 3.2 Semántica COM001

Se considera `R-COM-001 TRUE` únicamente cuando:

```text
opportunity_state == AVAILABLE
+
applicability_state == CONFIRMED
+
opportunity_ref DEMONSTRATED
+
applicability_ref DEMONSTRATED
+
article/supplier/fecha coinciden con PurchaseOperation
```

Mapping:

```text
AVAILABLE + CONFIRMED
→ EVALUABLE / TRUE

NOT_AVAILABLE + evidencia concluyente
→ EVALUABLE / FALSE

AVAILABLE + CONDITIONAL
→ NOT_EVALUABLE

NOT_CONFIRMED / NOT_DETERMINABLE / CONFLICTING
→ NOT_EVALUABLE
```

Esto resuelve la frase oficial:

> No debe modificar automáticamente la recomendación si no se conoce su aplicación real.

Una posibilidad genérica o condicionada puede conservarse como contexto, pero no activa la Rule.

### 3.3 CRC COM001

```text
effect = R2
severity = MEDIA
active_result = NEGOCIAR
```

Solo un TRUE ya confirmado y aplicable activa `NEGOCIAR`.

No escala a R1/R0.

## 4. R-COM-002 — rappel disponible

### 4.1 Alcance económico MVP

Se autoriza únicamente un rappel:

- confirmado;
- atribuible a la operación evaluada;
- con porcentaje único explícito;
- con base económica explícita;
- sin escalados;
- sin retroactividad;
- sin combinación de tramos;
- sin proyección de cumplimiento futuro.

Los demás casos → `NOT_EVALUABLE`.

### 4.2 Carrier factual/económico

```text
RappelApplicabilityEvidence
├── article_id
├── supplier_id
├── evaluation_date
├── agreement_ref
├── applicability_ref
├── economic_basis_ref
├── applicability_state
├── eligible_base_amount
├── rebate_rate_pct
├── currency
├── evidence_refs
└── trace_refs
```

`applicability_state`:

```text
CONFIRMED
CONDITIONAL
NOT_APPLICABLE
NOT_DETERMINABLE
CONFLICTING
```

### 4.3 Fórmula MVP

Para `CONFIRMED`:

```text
rebate_amount =
eligible_base_amount * rebate_rate_pct / 100

effective_cost_after_rappel =
purchase_gross_amount - rebate_amount
```

donde:

```text
purchase_gross_amount =
PurchaseOperation.quantity * PurchaseOperation.unit_price
```

Condiciones:

- `eligible_base_amount >= 0`;
- `rebate_rate_pct > 0`;
- `rebate_rate_pct <= 100`;
- moneda del carrier = moneda de PurchaseOperation;
- `rebate_amount <= purchase_gross_amount`;
- `effective_cost_after_rappel >= 0`.

Se usa `Decimal`, sin redondeo decisional implícito.

### 4.4 Carrier derivado

```text
RappelEffectiveCostEvidence
├── article_id
├── supplier_id
├── evaluation_date
├── agreement_ref
├── purchase_gross_amount
├── eligible_base_amount
├── rebate_rate_pct
├── rebate_amount
├── effective_cost_after_rappel
├── currency
├── evidence_refs
└── trace_refs
```

No se acepta coste efectivo desprendido.

### 4.5 Rule COM002

```text
CONFIRMED
+
rebate_amount > 0
+
effective_cost_after_rappel < purchase_gross_amount
→ EVALUABLE / TRUE

NOT_APPLICABLE con evidencia concluyente
→ EVALUABLE / FALSE

CONDITIONAL / NOT_DETERMINABLE / CONFLICTING
→ NOT_EVALUABLE
```

### 4.6 CRC COM002

La regla es:

```text
R3 / MEDIA
```

Se propone que **no modifique el resultado consolidado**.

COM002 aporta Assessment, Evidence, Trace y el cálculo económico derivado, pero no cambia `COMPRAR / NEGOCIAR / NO COMPRAR` por sí sola.

Por tanto, su metadata se mantiene `R3 / MEDIA` sin `active_result` comercial específico.

## 5. Relación con CEA/TCO

Los documentos archivados de CEA/TCO se consideran antecedentes no vigentes.

Este paquete **no convierte CEA/TCO en autoridad activa** y no propaga automáticamente el rappel o descuento a otros motores.

COM002 calcula un efecto económico local de la Rule.

Una futura integración CEA/TCO/Scenario requerirá contrato propio.

## 6. Supplier Evidence

`COMMERCIAL_CONDITION` puede ser fuente upstream, pero nunca se promociona automáticamente.

Debe existir una autoridad/adaptador explícito que produzca:

- `DiscountOpportunityEvidence`; o
- `RappelApplicabilityEvidence`.

## 7. Evidence binding

Todo ref concluyente debe estar respaldado por C0 `Evidence(state=DEMONSTRATED)`.

GAP nunca demuestra:

- descuento disponible;
- aplicabilidad;
- rappel;
- base económica;
- porcentaje.

Contradicciones → `NOT_EVALUABLE`.

## 8. Parámetros

No se crean parámetros COM en v0.1.

No se reutilizan:

- `P-PAG-005`;
- `P-MGE-006`.

Los valores económicos vienen de evidencia comercial explícita aplicable a la operación, no del Parameter Center.

## 9. Orchestrator

Bundles propuestos:

```text
CommercialDiscountRuleInputs
├── discount
└── evidences

CommercialRappelRuleInputs
├── rappel
└── evidences
```

Ambos opcionales.

Ausencia de bundle → rule en `omitted_rule_ids`.

## 10. Tests consolidados

COM001:
1. AVAILABLE+CONFIRMED → TRUE;
2. NOT_AVAILABLE demostrado → FALSE;
3. AVAILABLE+CONDITIONAL → NOT_EVALUABLE;
4. NOT_CONFIRMED → NOT_EVALUABLE;
5. CONFLICTING → NOT_EVALUABLE;
6. supplier/article/date mismatch → fail closed;
7. GAP no demuestra refs;
8. metadata R2/MEDIA/NEGOCIAR.

COM002:
9. confirmed linear rappel → TRUE;
10. cálculo Decimal exacto;
11. NOT_APPLICABLE → FALSE;
12. CONDITIONAL → NOT_EVALUABLE;
13. CONFLICTING → NOT_EVALUABLE;
14. rate <=0 o >100 rechazado;
15. currency mismatch → NOT_EVALUABLE;
16. rebate > gross → NOT_EVALUABLE;
17. no tiers;
18. no retroactive;
19. metadata R3/MEDIA;
20. COM002 no altera CRC por sí sola.

Integración:
21. orchestrator bundles;
22. omitted sin bundle;
23. no promoción desde COMMERCIAL_CONDITION;
24. no reutilización P-PAG-005/P-MGE-006.

## 11. No alcance

No autoriza:

- discounts automáticos desde texto libre;
- inferencia LLM de condiciones;
- rappel escalonado;
- rappel retroactivo;
- cálculo de cumplimiento futuro;
- acumulación multioperación;
- CEA transversal;
- TCO transversal;
- Scenario Engine;
- modificación automática de precio de PurchaseOperation;
- scoring/ranking;
- nuevos parámetros COM.

## 12. Efecto de autorización única

```text
AUTORIZAR
→ AUDITAR
→ MATERIALIZAR
   - carriers COM001/002
   - evaluadores
   - cálculo lineal COM002
   - catalog metadata
   - orchestrator
   - RDM
   - tests
→ CI
→ merge
→ CI main
```

Sin micro-gates intermedios dentro de este alcance.

## 13. Autorización humana

Autorizado expresamente el 23/09/2026 como paquete único de cierre COM001/COM002.

La autorización comprende la semántica factual de descuento, la aplicabilidad confirmada, el rappel lineal confirmado, la fórmula económica local, metadata CRC y límites de no alcance definidos en este documento.

**COMMERCIAL COM001/COM002 COMPLETION PACKAGE v0.1 — 🔒 AUTORIZADO / VIGENTE.**

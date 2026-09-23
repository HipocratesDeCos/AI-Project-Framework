# EIOS — ROT002 Completion Package Proposal v0.1

**Baseline:** `main @ 5e9f80565906b336191924349c0740eb9f9dc703`  
**Fecha:** 23/09/2026  
**Estado:** PROPUESTA CONSOLIDADA — NO AUTORIZADA / NO VIGENTE  
**Objetivo:** cerrar de una sola vez la arquitectura restante de `R-ROT-002`.

---

## 1. Alcance

Este paquete consolida en una única autorización:

1. productor factual upstream de actividad de ventas;
2. contrato mínimo de completitud;
3. contrato de excepciones MVP;
4. bridge factual hacia `R-ROT-002`;
5. metadata CRC de `R-ROT-002`;
6. política fail-closed;
7. límites explícitos de no alcance.

No modifica `R-ROT-001`.

---

## 2. Upstream factual autorizado propuesto

Se adopta el carrier:

```text
SalesActivitySourceEvidence
├── article_id
├── window_start
├── window_end
├── source_ref
├── source_semantics_ref
├── completeness_ref
├── valid_sale_evidence_refs
├── trace_refs
└── coverage_state
```

`coverage_state`:

```text
COMPLETE
PARTIAL
NOT_DEMONSTRATED
CONFLICTING
```

Invariantes:

- `source_ref` no equivale a autoridad semántica;
- `source_semantics_ref` identifica la autoridad que ya calificó eventos como ventas válidas;
- ROT no recalifica facturas, pedidos, albaranes, tickets, asientos, devoluciones o abonos;
- `valid_sale_evidence_refs` contiene referencias de eventos ya calificados upstream;
- `COMPLETE` exige cobertura demostrada de toda la ventana y scope;
- ausencia de filas no demuestra ausencia de ventas;
- suma neta cero no demuestra ausencia de ventas.

---

## 3. Derivación a SalesActivityWindowEvidence

### 3.1 Presencia

```text
valid_sale_evidence_refs != vacío
+
binding article/window correcto
+
source_semantics_ref válido
→ SALES_ACTIVITY_PRESENT
```

No se exige cobertura COMPLETE para demostrar presencia positiva.

### 3.2 Ausencia

```text
coverage_state == COMPLETE
+
valid_sale_evidence_refs == vacío
+
completeness_ref demostrado
+
binding article/window correcto
+
source_semantics_ref válido
→ ZERO_VALID_SALES_DEMONSTRATED
```

### 3.3 Casos no concluyentes

```text
PARTIAL
NOT_DEMONSTRATED
→ NOT_EVIDENCED o NOT_DETERMINABLE
```

```text
CONFLICTING
→ CONFLICTING_DATA
```

según el motivo factual preservado.

---

## 4. Evidencia upstream

La implementación deberá exigir Evidence vinculada a los refs factuales utilizados.

No se crea un nuevo sistema de Evidence.

Para una referencia concluyente:

```text
Evidence.state == DEMONSTRATED
Evidence.demonstration_ref == referencia factual exacta aplicable
```

Los estados GAP nunca demuestran presencia, ausencia ni completitud.

---

## 5. Universo de excepciones MVP propuesto

La Matriz de Reglas documenta como excepciones posibles:

```text
CONFIRMED_ORDER
PLANNED_CAMPAIGN
STRATEGIC_OPERATION
EXPLICIT_BUSINESS_DECISION
```

Se propone convertir **exactamente estas cuatro** en el universo de excepciones MVP de `R-ROT-002`.

Esto no declara que sean universales fuera del MVP.

---

## 6. Carrier de excepciones propuesto

```text
RotationExceptionEvidence
├── article_id
├── evaluation_date
├── exception_scope_ref
├── determinations
├── evidence_refs
└── trace_refs
```

Cada determination:

```text
exception_type
state
evidence_refs
```

Estados permitidos:

```text
PRESENT
NOT_PRESENT
NOT_DETERMINABLE
CONFLICTING
```

---

## 7. Semántica de excepciones

### 7.1 Excepción presente

Si al menos una de las cuatro categorías está:

```text
PRESENT
```

con Evidence DEMONSTRATED válida y vinculada:

```text
R-ROT-002 no debe activar NO COMPRAR
```

La regla puede quedar evaluable como condición mitigada por excepción o como FALSE técnico del bridge, pero la implementación deberá conservar trazabilidad de la excepción aplicada.

### 7.2 Ausencia demostrada de excepción

Solo se considera ausencia de excepción cuando las cuatro categorías están explícitamente:

```text
NOT_PRESENT
```

y el `exception_scope_ref` demuestra cobertura completa del universo MVP.

Ausencia de evidencias no equivale a ausencia de excepción.

### 7.3 Excepción indeterminada

Si cualquier categoría está:

```text
NOT_DETERMINABLE
CONFLICTING
```

o falta cobertura suficiente:

```text
R-ROT-002 → NOT_EVALUABLE
```

No se aplica NO COMPRAR.

---

## 8. Bridge propuesto R-ROT-002

Inputs mínimos:

```text
PurchaseOperation
DecisionContext
Rule(R-ROT-002)
SalesActivityWindowEvidence
RotationExceptionEvidence
Evidence asociadas
```

### 8.1 Condición factual activa sin excepción

```text
SalesActivityWindowEvidence.activity_state
== ZERO_VALID_SALES_DEMONSTRATED
+
NO_EXCEPTION_DEMONSTRATED
→ Assessment(
    status = EVALUABLE,
    outcome = TRUE
)
```

### 8.2 Actividad presente

```text
SALES_ACTIVITY_PRESENT
→ Assessment(
    status = EVALUABLE,
    outcome = FALSE
)
```

### 8.3 Excepción presente

```text
ZERO_VALID_SALES_DEMONSTRATED
+
EXCEPTION_PRESENT
→ Assessment(
    status = EVALUABLE,
    outcome = FALSE
)
```

La razón debe indicar que la condición factual existe pero queda exceptuada.

### 8.4 Estados insuficientes

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
→ Assessment(
    status = NOT_EVALUABLE,
    outcome = None
)
```

Lo mismo cuando la excepción no pueda resolverse.

---

## 9. Metadata normativa propuesta

Se materializa exactamente la metadata ya documentada:

```text
rule_id      = R-ROT-002
effect       = R1
severity     = ALTA
active_result = NO COMPRAR
```

Razón:

la Matriz de Reglas establece simultáneamente:

```text
Resultado: NO COMPRAR
Efecto / severidad: R1 / ALTA
```

Por tanto se propone usar `active_result = "NO COMPRAR"` para evitar que el mapping genérico R1 del CRC lo degrade a `COMPRAR CONDICIONADO`.

---

## 10. Escalada R0

NO se autoriza escalada automática R1 → R0.

Permanece:

```text
R-ROT-002 = R1 / ALTA
```

hasta que exista una política específica que establezca bloqueo.

---

## 11. Fail-closed

Se propone que cualquier mismatch de:

- article_id;
- decision_id;
- scenario_id;
- rules_version;
- ventana;
- autoridad temporal;
- source semantics;
- completeness;
- exception scope;
- evidence binding;

impida una evaluación concluyente.

No existen fallbacks.

---

## 12. Orchestrator

Tras materialización:

```text
RotationRuleInputs
├── sales_activity
├── rotation_exceptions
└── evidences
```

se incorpora como bundle opcional a `run_domain_rules(...)`.

Si no se suministra:

```text
R-ROT-002
```

permanece en `omitted_rule_ids`.

No se fuerza evaluación incompleta.

---

## 13. RDM

Tras autorización se reconciliarán explícitamente:

```text
R-ROT-002 ← SalesActivityWindowEvidence
R-ROT-002 ← RotationExceptionEvidence
R-ROT-002 ← Evidence bindings
R-ROT-002 ← P-ROT-001
```

No se introduce dependencia a STK, consumo, demanda ni stock.

---

## 14. Tests consolidados

La materialización deberá cubrir en un único paquete:

1. venta válida presente → FALSE;
2. ausencia demostrada + cuatro excepciones NOT_PRESENT → TRUE;
3. ausencia demostrada + confirmed order PRESENT → FALSE;
4. ausencia demostrada + planned campaign PRESENT → FALSE;
5. ausencia demostrada + strategic operation PRESENT → FALSE;
6. ausencia demostrada + explicit business decision PRESENT → FALSE;
7. excepción incompleta → NOT_EVALUABLE;
8. excepción conflictiva → NOT_EVALUABLE;
9. coverage PARTIAL → NOT_EVALUABLE;
10. coverage NOT_DEMONSTRATED → NOT_EVALUABLE;
11. coverage CONFLICTING → NOT_EVALUABLE;
12. GAP no demuestra presencia;
13. GAP no demuestra ausencia;
14. ausencia de filas no demuestra cero ventas;
15. net quantity no forma parte del contrato;
16. mismatch article/window → fail closed;
17. metadata R1/ALTA/NO COMPRAR;
18. prohibición de escalada R0;
19. integración orchestrator;
20. integración CRC sin degradar NO COMPRAR a COMPRAR CONDICIONADO.

---

## 15. No alcance

Este paquete no autoriza:

- `R-ROT-001`;
- fórmula de rotación;
- umbral de baja rotación;
- clasificación automática de documentos comerciales;
- ERP adapter concreto;
- inferencia de devoluciones/abonos;
- scoring;
- ranking;
- excepción adicional;
- R0 automático;
- decisión humana final.

---

## 16. Efecto de la autorización

Una única autorización humana de este paquete permitirá ejecutar:

```text
AUTORIZAR
→ AUDITAR implementación
→ MATERIALIZAR:
   - SalesActivitySourceEvidence
   - RotationExceptionEvidence
   - producer Track A
   - evaluate_r_rot_002
   - catalog metadata
   - orchestrator
   - RDM reconciliation
   - tests
→ CI
→ merge
→ CI main
```

sin solicitar nuevas aprobaciones intermedias mientras la implementación no exceda este contrato.

---

## 17. Estado

**ROT002 COMPLETION PACKAGE v0.1 — PROPUESTA CONSOLIDADA / NO VIGENTE.**

# EIOS — RENTABILIDAD / MARGEN · DISEÑO METODOLÓGICO v0.2

**Estado:** DEPURADO — PENDIENTE DE AUDIT 2  
**Fecha:** 11/09/2026  
**Base:** v0.1 + Audit 1

---

## 1. Propósito depurado

Definir una capacidad analítica de Rentabilidad/Margen dividida en dos fronteras:

```text
A. PROFITABILITY EVIDENCE
   representa bases económicas, evidencia, estados y trazas

B. AUTHORIZED MARGIN CALCULATION
   calcula margen únicamente cuando existe una política MGE autorizada
```

No se crea una nueva capa arquitectónica y no se ejecutan reglas MGE.

---

## 2. Autoridad y fronteras

La capacidad se subordina a Especificación Funcional, MED, Matriz de Reglas, Catálogo/Parametrización, RDM, Evidence Contract y contratos cerrados PRICE/TCO.

Invariantes:

```text
purchase_price ≠ reference_price
purchase_price ≠ TCO
TCO ≠ margin_cost_basis por defecto
sale_price ≠ economic_sale_basis por defecto
margin_percentage ≠ markup
calculation ≠ rule evaluation
```

---

## 3. MGE-E01 — Identidad

Toda evidencia/resultado MGE conserva:

```text
decision_id
scenario_id
rules_version
parameters_version
data_snapshot_id
company_scope
article_id
evaluation_date
methodology_version
```

Se reutiliza `DecisionContext`; no se crea un contexto paralelo.

---

## 4. MGE-E02 — Magnitud económica evidenciada

Una magnitud económica debe conservar conceptualmente:

```text
concept
value | null
currency
unit_or_basis
state
source_ref
captured_at
valid_from / valid_to
normalization_ref
issue_refs
trace_refs
```

Estados mínimos conceptuales:

```text
KNOWN
NOT_EVIDENCED
CONFLICTING_DATA
NOT_APPLICABLE
NOT_DETERMINABLE
```

Un estado no `KNOWN` no publica un valor determinado.

---

## 5. MGE-E03 — Profitability Evidence

El envelope puede preservar, sin decidir su uso en una fórmula:

```text
sale_price_evidence
purchase_price_evidence
tco_reference
discount_evidence
rebate_evidence
other_authorized_economic_bases
```

Conservar evidencia no equivale a seleccionarla como base de margen.

---

## 6. MGE-E04 — Precio/base de venta

Se distinguen:

```text
sale_price_evidence
        ≠
economic_sale_basis
```

`sale_price_evidence` puede representarse si tiene fuente, vigencia, moneda y unidad/basis.

`economic_sale_basis` solo puede quedar `KNOWN` cuando una política autorizada identifica qué evidencia de venta se utiliza y qué ajustes son aplicables.

No existe selección automática por último/promedio/tarifa/histórico.

---

## 7. MGE-E05 — Base de coste

Se distinguen:

```text
purchase_price_evidence
tco_reference
        ≠
margin_cost_basis
```

`margin_cost_basis` exige política explícita que determine:

- concepto fuente;
- componentes incluidos/excluidos;
- regla de atribución;
- unidad/basis;
- moneda;
- transformación autorizada.

No existe fallback automático TCO→purchase price ni purchase price→TCO.

---

## 8. MGE-E06 — Descuentos

Un descuento se representa separadamente con:

```text
amount_or_rate
basis
condition
applicability
source_ref
state
```

No se aplica al ingreso o coste hasta que la política MGE determine su atribución.

Una condición no demostrada no se considera cumplida.

---

## 9. MGE-E07 — Rappels

Un rappel se representa separadamente y debe conservar, cuando proceda:

```text
scope
period
threshold/condition
attributable_amount_or_rate
source_ref
state
```

No se prorratea ni se anticipa automáticamente.

Rappel esperado ≠ rappel devengado/evidenciado.

---

## 10. MGE-C01 — Policy Gate

No existe cálculo de margen si falta cualquiera de:

```text
authorized_margin_policy
economic_sale_basis KNOWN
margin_cost_basis KNOWN
currency/unit compatibility
```

La ausencia de una política produce:

```text
NOT_DETERMINABLE
```

no error, cero ni fallback.

---

## 11. MGE-C02 — Margen en importe

La estructura de cálculo queda reservada como:

```text
margin_amount = authorized_sale_basis - authorized_cost_basis
```

Esta expresión solo es operativa después de que una autoridad empresarial defina qué representan ambas bases.

No autoriza escoger esas bases por inferencia.

---

## 12. MGE-C03 — Margen porcentual

La ratio exige un `percentage_denominator` explícitamente autorizado.

Hasta entonces:

```text
margin_percentage = NOT_DETERMINABLE
```

No se sustituye por markup.

---

## 13. MGE-C04 — Compatibilidad monetaria y de unidad

Si las bases autorizadas no son comparables:

```text
margin = NOT_DETERMINABLE
```

No existe:

- FX implícito;
- conversión de unidad implícita;
- redondeo usado como reconciliación;
- selección arbitraria de una fuente.

Puede consumirse una normalización externa únicamente con referencia trazable de autoridad.

**MGE-G10 queda cerrado en su parte MGE:** no motor FX/conversión propio.

---

## 14. MGE-C05 — Temporalidad

Las bases deben ser aplicables a `evaluation_date` conforme a su política de vigencia.

No se selecciona automáticamente el último dato disponible.

Un dato futuro no constituye por sí mismo la base vigente.

---

## 15. MGE-C06 — Parámetros MGE

Relaciones confirmadas y preservadas:

```text
P-MGE-001 → R-MGE-001
P-MGE-002 → R-MGE-003
P-MGE-003 → R-MGE-002
```

MGE puede transportar referencias a la configuración vigente, pero **no ejecuta las reglas**.

No se hardcodean los valores de catálogo.

`P-MGE-004/005/006` permanecen fuera de consumo hasta que exista relación funcional demostrada.

---

## 16. MGE-C07 — Resultado analítico

Salida conceptual:

```text
identity
profitability_evidence
authorized_policy_ref
economic_sale_basis
margin_cost_basis
margin_amount
margin_percentage
calculation_state
unresolved_items
conflicting_items
limitations
trace_refs
```

No contiene:

```text
Assessment
rule_outcome
effect
severity
CRC
recommendation
purchase_decision
```

---

## 17. Gaps después de Audit 1

### Requieren autoridad empresarial

| Gap | Materia |
|---|---|
| MGE-G01 | base económica de venta |
| MGE-G02 | base de coste |
| MGE-G03 | denominador porcentual |
| MGE-G04 | fuente/aplicabilidad de venta |
| MGE-G05 | atribución de descuentos |
| MGE-G06 | atribución de rappels |

### Deuda documental/paramétrica, no bloqueante del core si no se consume

| Gap | Materia |
|---|---|
| MGE-G07 | P-MGE-004 |
| MGE-G08 | P-MGE-005 |
| MGE-G09 | P-MGE-006 |

### Cerrado negativamente

```text
MGE-G10 → MGE no crea FX ni conversión propia.
```

---

## 18. Criterios de Audit 2

Audit 2 deberá comprobar que:

1. no haya fórmula ejecutable sin policy gate;
2. sale evidence y sale basis estén separadas;
3. TCO/purchase price y cost basis estén separadas;
4. descuento/rappel no se apliquen sin atribución;
5. margin percentage no presuponga denominador;
6. parámetros iniciales no se hardcodeen;
7. MGE no ejecute Rules;
8. no se cree nueva capa arquitectónica;
9. no exista fallback silencioso;
10. la parte cerrable sea suficiente para redactar un único paquete de autoridad G01…G06.

---

## 19. Estado

**v0.2 DEPURADO — PENDIENTE DE AUDIT 2.**

No autoriza implementación cuantitativa.

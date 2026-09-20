# EIOS — MGE Rules Readiness Audit v0.1

**Baseline:** `main @ c4be1f405c9f9043441d7d39aa5f36e2a16ee25a`  
**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA — RULES NO AUTORIZADAS PARA MATERIALIZACIÓN

## 1. Objeto

Determinar si, después de cerrar:

- `MGE-AUTH v0.1`;
- `Profitability Core v0.1`;
- `Profitability Provenance Boundary v0.1`;

existe autoridad y semántica suficiente para materializar `R-MGE-001/002/003`.

Esta auditoría no ejecuta Rules y no modifica CRC.

## 2. Autoridad MGE ya cerrada

La cadena analítica queda físicamente disponible:

```text
AuthorizedSaleBasis
+
AuthorizedCostBasis
        ↓
ProfitabilityInput
        ↓
calculate_profitability
        ↓
ProfitabilityResult
        ↓
ProvenancedProfitabilityExecution
```

El resultado aporta, con provenance revalidable:

- `margin_amount`;
- `margin_percentage`;
- estado de cálculo;
- identidad completa;
- bases autorizadas;
- trazas.

## 3. Frontera de autorización

`MGE-AUTH v0.1` autorizó expresamente el cálculo analítico y excluyó:

- ejecución R-MGE;
- valores empresariales definitivos de parámetros;
- selección automática de fuentes;
- CRC/recomendación/decisión.

Por tanto:

```text
Profitability Core autorizado
≠
R-MGE autorizadas para ejecución
```

Una autorización de la metodología de margen no debe promoverse por inferencia a autorización de efectos de regla.

## 4. R-MGE-001 — Margen inferior al mínimo

### Autoridad existente

Matriz de Reglas:

> margen previsto inferior al margen mínimo configurado.

Relación documental:

```text
P-MGE-001 → R-MGE-001
```

Efecto ordinario documentado:

```text
R1 — CONDICIONANTE / ALTA
```

La Matriz menciona una posible escalada R0 cuando el margen negativo o el límite empresarial aplicable constituya bloqueo no resoluble.

### Readiness

La condición booleana básica puede expresarse sin ambigüedad una vez exista una configuración válida:

```text
profitability.margin_percentage < resolved(P-MGE-001)
```

Pero no puede materializarse todavía porque:

1. MGE-AUTH no autorizó ejecución R-MGE;
2. el valor inicial del catálogo figura `Pendiente de validación` y no puede hardcodearse;
3. debe consumirse `ResolvedConfiguration(P-MGE-001)` con evidence/provenance;
4. la escalada R1→R0 no dispone de política ejecutable cerrada y debe quedar fuera incluso en una futura primera versión.

**Estado:** `CONDITION_READY / EXECUTION_AUTHORITY_BLOCKED`.

## 5. R-MGE-003 — Margen objetivo alcanzado

### Autoridad existente

Condición:

> margen cumple o supera el objetivo.

Relación:

```text
P-MGE-002 → R-MGE-003
```

Efecto:

```text
R3 — INFORMATIVA / INFORMATIVA
```

### Readiness

La condición booleana es físicamente clara:

```text
profitability.margin_percentage >= resolved(P-MGE-002)
```

pero permanece bloqueada por:

1. ausencia de autorización explícita para ejecutar R-MGE;
2. prohibición de hardcodear el valor inicial de P-MGE-002;
3. necesidad de resolution/evidence provenance-safe.

**Estado:** `CONDITION_READY / EXECUTION_AUTHORITY_BLOCKED`.

## 6. R-MGE-002 — Margen dentro de tolerancia

### Autoridad existente

Condición textual:

> margen ligeramente por debajo del objetivo, pero dentro de la tolerancia configurada.

Relación:

```text
P-MGE-003 → R-MGE-002
```

P-MGE-003 está expresado en puntos porcentuales.

### Gap objetivo

No existe en las fuentes contrastadas una transformación ejecutable que determine de forma inequívoca si la condición es:

```text
target - tolerance <= margin < target
```

u otra frontera posible.

Tampoco está formalizada la prioridad/interacción cuando el margen pudiera simultáneamente estar:

- por debajo de `P-MGE-001`;
- dentro de la tolerancia del objetivo;
- en otra relación entre mínimo, objetivo y tolerancia.

No es legítimo inferir una banda matemática únicamente por el nombre “tolerancia”.

**Estado:** `SEMANTIC_TRANSFORM_BLOCKED`.

## 7. Provenance del resultado MGE

Este gap sí queda cerrado técnicamente:

```text
MGE-RULES-PROV-01 → CERRADO
```

Una futura Rule bridge debe aceptar:

```text
ProvenancedProfitabilityExecution
```

y llamar primero a:

```python
validate_provenanced_profitability_execution(...)
```

No debe aceptar un `ProfitabilityResult` desprendido.

## 8. Parámetros

Una futura Rule bridge deberá utilizar el patrón cerrado de configuración EIOS:

- `ResolvedConfiguration`;
- misma `parameters_version` que `DecisionContext`;
- empresa/contexto aplicable;
- vigencia para la fecha evaluada;
- unidad exacta;
- `Evidence` del parámetro;
- `configuration_ref` concordante.

No se validan mediante este documento los valores iniciales:

- 20 %;
- 30 %;
- 3 puntos porcentuales.

## 9. Estados no determinados

Si `ProfitabilityResult.calculation_state != DETERMINED`, cualquier R-MGE que dependa de `margin_percentage` debe ser:

```text
Assessment.status = NOT_EVALUABLE
Assessment.outcome = null
```

No puede interpretar:

- porcentaje null como 0;
- ausencia como FALSE;
- conflicto como FALSE;
- venta cero como margen 0 %.

## 10. Gates de apertura Rules MGE

### MGE-RULES-G01 — autoridad de ejecución

Autorización explícita para que EIOS evalúe `R-MGE-001/002/003` desde el resultado provenance-safe de Profitability Core.

### MGE-RULES-G02 — política de R-MGE-002

Definición matemática exacta de la banda de tolerancia y fronteras inclusivas/exclusivas.

### MGE-RULES-G03 — interacción mínimo/objetivo/tolerancia

Definición que impida solapamientos o contradicciones entre R-MGE-001, R-MGE-002 y R-MGE-003.

### MGE-RULES-G04 — parámetros físicos

Binding de `P-MGE-001/002/003` mediante `ResolvedConfiguration + Evidence`, sin defaults.

### MGE-RULES-G05 — metadata de Rule/CRC

Para una primera materialización conservadora:

- R-MGE-001 solo podría usar su efecto ordinario R1/ALTA;
- no se autoriza escalada R0 por inferencia;
- R-MGE-002 permanece R2/MEDIA;
- R-MGE-003 permanece R3/INFORMATIVA.

Cualquier política adicional requiere fuente específica.

## 11. Audit 2

Se verifica que esta auditoría:

- no implementa Rules;
- no añade R-MGE al catálogo ejecutable;
- no valida defaults del catálogo;
- no inventa la fórmula P-MGE-003;
- no autoriza R0;
- no modifica CRC;
- no reabre Profitability Core;
- preserva provenance-safe execution.

**AUDIT 2: SUPERADA — 0 contradicciones documentales.**

## 12. Dictamen

```text
Profitability Core          → CERRADO
Profitability provenance    → CERRADO
R-MGE-001 condition         → TÉCNICAMENTE DEFINIBLE
R-MGE-003 condition         → TÉCNICAMENTE DEFINIBLE
R-MGE-002 transform         → BLOQUEADO
R-MGE execution authority   → BLOQUEADA
```

**NO-GO para materializar R-MGE en este momento.**

El siguiente avance requiere autorización específica de Rules MGE y cierre semántico de G02/G03; la autorización previa de MGE-AUTH v0.1 no se extiende automáticamente a esta frontera.


## 13. Reconciliación posterior — 20/09/2026

Tras autorización humana explícita:

```text
Autorizo Rules MGE y la semántica propuesta
```

se cierran documentalmente:

- MGE-RULES-G01 — autoridad de ejecución;
- MGE-RULES-G02 — fórmula exacta R-MGE-002;
- MGE-RULES-G03 — interacción mínimo/objetivo/tolerancia;
- MGE-RULES-G05 — metadata conservadora sin R0.

La semántica autorizada es:

```text
R-MGE-001: m < minimum
R-MGE-002: m >= minimum AND m >= target - tolerance AND m < target
R-MGE-003: m >= target
```

`MGE-RULES-G04` queda diseñado técnicamente mediante binding de las tres `ResolvedConfiguration + Evidence` dentro de un único bundle coherente y está listo para materialización.

**Readiness actualizado: GO documental para materialización, condicionado a CI y a no ampliar el alcance autorizado.**


## 14. Cierre físico posterior — PR #244

La materialización de Rules MGE quedó integrada en:

```text
main @ b3fdb6275a6cc6a33ecca55bbd9af49816ce5776
```

mediante PR #244.

Se materializaron:

- `eios/rules/profitability.py`;
- metadata de catálogo para R-MGE-001/002/003;
- `ProfitabilityRuleInputs` en el orquestador;
- tests dedicados de fórmulas, fronteras, provenance, parámetros y omisión.

`MGE-RULES-G04` queda **CERRADO FÍSICAMENTE** mediante:

```text
ResolvedConfiguration(P-MGE-001/002/003)
+
ParameterConfigurationEvidence
+
ProvenancedProfitabilityExecution
+
ProfitabilityResultEvidence
        ↓
R-MGE-001/002/003
```

CI inicial #1006 detectó exclusivamente cuatro expectativas históricas del catálogo/orquestador. Tras reconciliarlas sin modificar lógica MGE, CI #1007 resultó:

```text
1686 passed
8 warnings
SQL validations SUCCESS
```

**Readiness final: CLOSED / MATERIALIZED / CI VALIDATED.**

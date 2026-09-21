# EIOS — PRE002 Critical Price Authority Proposal v0.1

**Baseline:** `main @ 5bba5b6c6219dc6ecc55db038bfc7eff48bb8e11`  
**Fecha:** 21/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA  
**Ámbito:** `R-PRE-002 — Precio superior al límite crítico`

## 1. Propósito

Cerrar únicamente la semántica mínima necesaria para evaluar:

```text
purchase.unit_price
vs.
critical_price_limit
```

donde `critical_price_limit` se deriva de un baseline crítico explícito y del parámetro `P-PRE-005`.

No se reutiliza por analogía:

- `ComparablePriceReference` de R-PRE-001;
- `RecommendedPriceCeiling` de R-PRE-003;
- `PriceIntelligenceResult.pr_value`.

## 2. Autoridad existente

La Matriz de Reglas define:

> El precio supera el umbral crítico configurado.

La Matriz de Parámetros/RDM confirma:

```text
P-PRE-005 → R-PRE-002
```

P-PRE-005 se denomina:

```text
Diferencia para alerta crítica de precio
```

con unidad `%`.

Su valor inicial de 10% permanece pendiente de validación y no puede convertirse en default.

## 3. Gap actual

La documentación no determina el precio base sobre el que debe aplicarse P-PRE-005.

Por tanto no es válido inferir:

```text
critical baseline = PRE001 comparable reference
critical baseline = PRE003 PMR
critical baseline = Price Intelligence PR
critical baseline = last purchase
```

sin autoridad expresa.

## 4. Carrier factual propuesto

Se define un carrier independiente:

`CriticalPriceBaseline`

Campos mínimos:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
currency
purchase_operation_ref
state
baseline_price
source_ref
authority_ref
methodology_ref
trace_refs
```

Estados:

```text
AVAILABLE
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

Si AVAILABLE:

- baseline_price obligatorio;
- Decimal finito;
- baseline_price > 0;
- moneda explícita.

Otros estados → baseline_price = null.

## 5. Binding a la operación

El carrier debe estar ligado a:

```text
decision_id
scenario_id
data_snapshot_id
company_scope
article_id
evaluation_date
currency
purchase_operation_ref
```

`purchase_operation_ref` será SHA-256 determinista de la PurchaseOperation completa.

## 6. Evidence

Se exige:

```text
CriticalPriceBaselineEvidence
```

Si DEMONSTRATED:

```text
demonstration_ref == critical_price_baseline_ref(carrier)
```

Evidence GAP/INVALID → NOT_EVALUABLE.

Reference forjada/ajena → error estructural.

## 7. P-PRE-005

Se consume solo mediante:

```text
ResolvedConfiguration(P-PRE-005)
+
ParameterConfigurationEvidence
```

Validaciones:

- parameter_id exacto;
- parameters_version;
- company_id;
- vigencia;
- fecha aplicable;
- unit == `%`;
- Decimal finito y >= 0;
- Evidence ligada a configuration_ref.

No se hardcodea 10%.

## 8. Fórmula propuesta

```text
critical_price_limit =
baseline_price * (1 + P-PRE-005 / 100)
```

No se redondea antes de comparar.

## 9. Frontera propuesta

La Matriz dice “el precio supera el umbral crítico”.

Por tanto se propone:

```text
triggered =
purchase.unit_price > critical_price_limit
```

Fronteras:

```text
purchase.unit_price < critical_limit  → FALSE
purchase.unit_price == critical_limit → FALSE
purchase.unit_price > critical_limit  → TRUE
```

La igualdad NO activa R-PRE-002.

Esta frontera es distinta de PRE001, donde la autoridad ya aprobó `>=`.

## 10. Evaluabilidad

R-PRE-002 devuelve NOT_EVALUABLE cuando:

- baseline no AVAILABLE;
- Evidence del baseline no VALID;
- baseline_price <= 0;
- moneda incompatible;
- P-PRE-005 ausente/no válida/no evidenciada;
- identity/provenance incompatible.

Ausencia de baseline nunca equivale a cero ni a FALSE.

## 11. Metadata propuesta

La Matriz vigente autoriza ordinariamente:

```text
R-PRE-002 → R1 / ALTA
```

La frase:

> pudiendo escalar a R0 si el límite es no negociable

NO autoriza una escalada automática sin una fuente adicional que demuestre esa condición empresarial.

v0.1 materializaría únicamente:

```text
R1 / ALTA
```

Sin R0.

## 12. Separación respecto a otras reglas

### PRE001

PRE001 evalúa una referencia comparable reciente y P-PRE-004.

PRE002 no reutiliza automáticamente ese carrier.

### PRE003

PRE003 consume PMR independiente.

PMR no se usa como baseline crítico salvo futura autoridad.

### Price Intelligence

PR no se usa como baseline crítico por defecto.

## 13. No-alcance

No se autoriza:

- elegir baseline dentro de Rules;
- usar PRE001/PRE003/PR por analogía;
- hardcodear 10%;
- FX;
- normalización implícita;
- R0 automático;
- modificar R-PRE-001/003;
- modificar Price Intelligence;
- decisión empresarial automática.

## 14. Gates que resolvería la aprobación

Si se autoriza expresamente:

```text
PRE-G03 → semántica ejecutable P-PRE-005 CERRADA
PRE-G05 → provenance del precio crítico CERRADA para R-PRE-002
PRE002-G01 → CriticalPriceBaseline DEFINIDO
PRE002-G02 → Evidence/provenance DEFINIDA
PRE002-G03 → fórmula critical limit CERRADA
PRE002-G04 → frontera estricta > CERRADA
PRE002-G05 → fail-closed CERRADO
PRE002-G06 → metadata ordinaria R1/ALTA CERRADA
```

## 15. Estado

**PRE002 Critical Price Authority v0.1 — PROPUESTA / NO AUTORIZADA.**

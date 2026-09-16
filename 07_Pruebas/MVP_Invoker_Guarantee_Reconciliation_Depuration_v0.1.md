# EIOS — MVP Invoker Guarantee Reconciliation · Depuración v0.1

## Estado

**DEPURACIÓN COMPLETADA**

Unidad: `MVP-INVOKER-GUARANTEE-RECON-01`

Base: Diseño v0.1 + Audit 1 SUPERADA.

## 1. Objetivo

Fijar una redacción exacta para `run_mvp_execution(...)` que describa la frontera genérica sin atribuir automáticamente garantías provenance-safe a cualquier `CapabilityInvoker`.

## 2. Texto actual incorrecto

El docstring vigente contiene conceptualmente:

```text
PRICE, TCO, Decision Twin, Scenario Coordination, Negotiation Intelligence
and Negotiation Ladder must arrive through explicit provenance-safe invokers
```

El adjetivo global `provenance-safe` contradice las cuarentenas cerradas de Scenario Coordination y NI/Ladder y excede lo que puede demostrar el tipo genérico `CapabilityInvoker`.

## 3. Texto objetivo depurado

La parte común quedará conceptualmente:

```text
PRICE, TCO, Decision Twin, Scenario Coordination, Negotiation Intelligence
and Negotiation Ladder must arrive through explicit invokers; this service
never re-labels detached raw results for those capabilities into the current
context. Invoker presence alone is not provenance proof.
```

A continuación se conservará sin cambio semántico la cláusula QTG:

```text
QTG remains in the canonical architecture order but is deliberately not
accepted by this generic boundary until a provenance-safe producer from the
authorized Decision Input Package exists.
```

## 4. Razón de esta formulación

La redacción separa cuatro conceptos que no deben confundirse:

1. **forma de composición**: invocador explícito;
2. **prohibición de raw result desprendido**: responsabilidad del generic boundary;
3. **procedencia positiva**: responsabilidad de contratos/builders especializados;
4. **capacidad no habilitada**: QTG permanece explícitamente en cuarentena.

## 5. PRICE / TCO

No se cambia ni cuestiona que sus builders especializados sean provenance-safe.

La frase genérica simplemente deja de afirmar que cualquier callable suministrado al parámetro correspondiente hereda esa garantía automáticamente.

## 6. Scenario / NI / Ladder

Se restaura literalmente el principio autorizado por sus contratos de cuarentena:

**Invoker presence alone is not provenance proof.**

No se crea builder, rerun, bundle, metadata ni validación adicional.

## 7. Decision Twin

El texto no declara disponibilidad actual. Solo describe el contrato estructural del slot genérico si se utiliza.

La cuarentena pública Stage 2/VF permanece fuera de esta unidad e intacta.

## 8. QTG

La cláusula actual se conserva. No reaparece `quality_invoker`.

## 9. Materialización prevista

Único cambio funcional/documental embebido:

- sustituir el párrafo del docstring en `eios/core/mvp_execution.py`.

No cambiar:

- imports;
- tipos;
- parámetros;
- ramas `if`;
- `MVP_CAPABILITY_ORDER`;
- `ExecutionPlan`;
- tests funcionales.

## 10. Resultado

**DEPURACIÓN COMPLETADA.**

La unidad puede pasar a **AUDITAR 2**.
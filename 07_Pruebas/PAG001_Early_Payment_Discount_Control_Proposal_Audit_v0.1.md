# EIOS — PAG001 Early-Payment Discount Control Proposal Audit v0.1

**Baseline:** `main @ 39c61b6f8185ba4441163e696c39631bb809abaf`  
**Fecha:** 22/09/2026  
**Estado:** AUDIT 2 DE PROPUESTA — SUPERADA / NO AUTORIZA IMPLEMENTACIÓN

## A1 — Conflicto identificado

Catálogo:

```text
P-PAG-005 = Considerar descuento por pronto pago
Unidad = Sí/No
```

Especificación:

```text
P-PAG-005 = factor económico / cálculo coste-beneficio
```

La interpretación literal conjunta es inconsistente.

## A2 — Resolución mínima

Se conserva el contrato tipado del catálogo:

```text
P-PAG-005 = control booleano
```

y se separa el dato económico real como futura dependencia factual/metodológica.

## A3 — R-PAG-001 no depende del descuento para su condición base

La condición de regla documentada es plazo ofrecido frente al objetivo/umbral.

No existe evidencia de que un descuento sea necesario para determinar TRUE/FALSE.

Por tanto, hacer P-PAG-005 obligatorio para evaluabilidad introduciría una dependencia más fuerte que la documentada.

## A4 — COMMERCIAL_CONDITION no basta

Supplier Evidence Core conserva hechos por dimensión, pero no otorga semántica especializada de descuento por pronto pago ni fórmula económica.

## A5 — No se inventa fórmula

La propuesta no define porcentaje, importe, TAE, coste efectivo ni equivalencia días/precio.

## A6 — Consecuencia

Si se autoriza:

- P-PAG-005 deja de bloquear el core R-PAG-001;
- sigue abierto un módulo/contexto económico futuro;
- se podrá auditar el ensamblaje completo del comparador PAG001 sin inventar economía.

## Dictamen

```text
DISEÑAR   → SUPERADA
AUDITAR   → SUPERADA
DEPURAR   → SUPERADA
AUDIT 2   → SUPERADA
CERRAR    → BLOQUEADO POR AUTORIZACIÓN HUMANA
IMPLEMENT → BLOQUEADO
```

**0 bloqueadores documentales para someter PAG001 Early-Payment Discount Control Authority v0.1 a autorización humana.**

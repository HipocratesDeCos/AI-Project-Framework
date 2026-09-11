# EIOS — RENTABILIDAD / MARGEN · AUDIT 2 METODOLÓGICA v0.2

**Estado:** SUPERADA ESTRUCTURALMENTE — POLICY GATE EMPRESARIAL PENDIENTE  
**Fecha:** 11/09/2026  
**Objeto:** `Profitability_Margin_Methodological_Design_v0.2.md`

---

## 1. Dictamen

La depuración v0.2 corrige los hallazgos estructurales de Audit 1:

- MGE no se presenta como nueva capa arquitectónica;
- PRICE/TCO/MGE permanecen separados;
- evidencia económica ≠ base autorizada;
- base de venta ≠ precio de venta por defecto;
- base de coste ≠ purchase price/TCO por defecto;
- descuentos/rappels no se aplican por inferencia;
- porcentaje no presupone denominador;
- no existe FX/conversión implícita;
- cálculo ≠ regla;
- no se hardcodean parámetros.

No quedan bloqueos estructurales para definir un **Profitability Core condicionado a bases autorizadas**.

---

## 2. Hallazgo A2-01 — TCO físico confirma que no puede reutilizarse sin autoridad

La implementación TCO calcula:

```text
TCO total = quantity × unit_price + costes atribuibles
```

`TCOResult.value` representa el total monetario de la propuesta.

Convertirlo en una base unitaria mediante:

```text
TCO / quantity
```

sería una transformación nueva desde la perspectiva de MGE y no está autorizada como política de margen.

**Resultado:** mantener TCO como referencia posible, nunca como base implícita.

---

## 3. Hallazgo A2-02 — La selección de bases debe permanecer fuera del algoritmo MGE

Para evitar que el engine MGE se convierta en un selector económico oculto, el core debe recibir objetos conceptuales equivalentes a:

```text
AuthorizedSaleBasis
AuthorizedCostBasis
```

Cada uno debe aportar:

```text
value
currency
unit_or_basis
state
authority_ref
source_ref
transformation_ref (si aplica)
validity/evaluation context
trace_refs
```

MGE valida compatibilidad y autoridad, pero no decide qué fuente ganó entre varias posibles.

Esto permite mantener fuera del core:

- selección de tarifa/venta histórica;
- selección purchase price/TCO;
- atribución de descuentos;
- atribución de rappels;
- FX/conversión.

---

## 4. Hallazgo A2-03 — MGE-G04/G05/G06 pueden dejar de bloquear el core

Si el core exige bases ya autorizadas:

- `MGE-G04` fuente/selección de venta pasa a autoridad upstream;
- `MGE-G05` descuentos se aplican solo si la autoridad de la base ya los incorpora explícitamente;
- `MGE-G06` rappels se aplican solo si la autoridad de la base ya los incorpora explícitamente.

MGE no los recalcula ni los prorratea.

Por tanto, esos gaps siguen abiertos en el sistema, pero **no bloquean un core de cálculo sobre bases autorizadas**.

`P-MGE-005/006` permanecen sin consumidor directo demostrado y no se implementan como switches.

---

## 5. Hallazgo A2-04 — Política mínima realmente necesaria

El core solo necesita autoridad empresarial sobre:

1. semántica de `AuthorizedSaleBasis`;
2. semántica de `AuthorizedCostBasis`;
3. fórmula de `margin_amount`;
4. denominador de `margin_percentage`;
5. tratamiento de `sale_basis = 0`.

No necesita elegir ERP, tarifa, TCO, descuento o rappel específico si las bases llegan con autoridad/traza explícita.

---

## 6. Fórmula todavía NO autorizada

Audit 2 no convierte en política la propuesta siguiente:

```text
margin_amount = authorized_sale_basis - authorized_cost_basis
margin_percentage = margin_amount / authorized_sale_basis × 100
```

Es una candidata coherente con la distinción margen vs markup, pero requiere autorización empresarial expresa.

---

## 7. Parámetros

Se preserva:

```text
P-MGE-001 → R-MGE-001
P-MGE-002 → R-MGE-003
P-MGE-003 → R-MGE-002
```

El core MGE puede producir `margin_percentage`; la comparación normativa y el outcome pertenecen a Rules.

No se autoriza:

```text
P-MGE-004
P-MGE-005
P-MGE-006
```

como consumidores del core mientras su relación no esté demostrada.

---

## 8. Casos límite que deberá cerrar la autoridad

### Base de venta cero

Puede existir `margin_amount` determinado, pero una división por cero no produce porcentaje válido.

La opción conservadora propuesta es:

```text
sale_basis = 0
→ margin_amount puede calcularse
→ margin_percentage = NOT_DETERMINABLE
```

### Moneda/unidad incompatible

```text
→ margin_amount = NOT_DETERMINABLE
→ margin_percentage = NOT_DETERMINABLE
```

salvo normalización externa autorizada.

### Base ausente/contradictoria

No existe fallback a purchase price ni TCO.

---

## 9. Fronteras limpias

Audit 2 confirma:

- MGE no redefine PRICE;
- MGE no redefine TCO;
- MGE no modifica C0;
- MGE no selecciona precio de venta;
- MGE no selecciona coste de margen;
- MGE no ejecuta R-MGE;
- MGE no produce Assessment;
- MGE no produce CRC ni recomendación;
- MGE no crea una nueva capa 6;
- ausencia/contradicción no generan cero.

---

## 10. Estado de gaps tras Audit 2

| Gap | Estado |
|---|---|
| MGE-G01 base venta | REDUCIDO a semántica de AuthorizedSaleBasis |
| MGE-G02 base coste | REDUCIDO a semántica de AuthorizedCostBasis |
| MGE-G03 denominador | REQUIERE AUTORIDAD |
| MGE-G04 selección venta | FUERA DEL CORE / autoridad upstream |
| MGE-G05 descuentos | FUERA DEL CORE salvo base autorizada |
| MGE-G06 rappels | FUERA DEL CORE salvo base autorizada |
| MGE-G07 MGE-004 | OPEN, no consumidor |
| MGE-G08 MGE-005 | OPEN, no consumidor |
| MGE-G09 MGE-006 | OPEN, no consumidor |
| MGE-G10 FX/conversión | CERRADO NEGATIVAMENTE en MGE |

---

## 11. Dictamen

**AUDIT 2 ESTRUCTURAL: SUPERADA.**

No procede aún cerrar metodología cuantitativa ni redactar contrato técnico hasta autorizar el **Margin Calculation Policy** mínimo.

Siguiente paso: materializar una única propuesta empresarial conservadora, sin defaults de parámetros y sin apropiarse de PRICE/TCO.

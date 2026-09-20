# EIOS — RENTABILIDAD / MARGEN · MGE-AUTH v0.1

**Estado:** PROPUESTA — NO AUTORIZADA  
**Fecha:** 11/09/2026  
**Objeto:** política mínima para habilitar el cálculo de margen sobre bases económicas previamente autorizadas

---

## 1. Propósito

Cerrar únicamente la semántica empresarial necesaria para que EIOS pueda calcular margen sin decidir por sí mismo qué fuente de venta o coste debe utilizar.

Esta propuesta no autoriza:

- seleccionar tarifas o precios históricos;
- convertir TCO automáticamente en coste de margen;
- aplicar descuentos/rappels por inferencia;
- hardcodear parámetros MGE;
- ejecutar R-MGE;
- emitir recomendación o decisión.

---

## 2. MGE-AUTH-01 — AuthorizedSaleBasis

La base de venta utilizada por el cálculo debe llegar al core como una magnitud económica **previamente autorizada**:

```text
AuthorizedSaleBasis
├── value
├── currency
├── economic_basis_ref
├── state
├── authority_ref
├── source_ref
├── transformation_ref (si aplica)
├── validity/evaluation context
└── trace_refs
```

Semántica propuesta:

> `AuthorizedSaleBasis` representa el importe de venta económicamente aplicable al mismo objeto/basis sobre el que se calculará el margen.

MGE no selecciona la fuente.

No se presume que una tarifa, último precio, promedio, promoción o forecast sea la base autorizada.

---

## 3. MGE-AUTH-02 — AuthorizedCostBasis

La base de coste debe llegar igualmente autorizada:

```text
AuthorizedCostBasis
├── value
├── currency
├── economic_basis_ref
├── state
├── authority_ref
├── source_ref
├── transformation_ref (si aplica)
├── validity/evaluation context
└── trace_refs
```

Semántica propuesta:

> `AuthorizedCostBasis` representa el coste económicamente atribuible al mismo objeto/basis utilizado por `AuthorizedSaleBasis`, conforme a una autoridad externa identificable.

MGE no decide si esa base procede de:

- purchase price;
- purchase price neto;
- TCO;
- TCO transformado a otra base;
- otra fuente contable/económica.

No existe fallback entre esas fuentes.

---

## 4. MGE-AUTH-03 — Compatibilidad obligatoria

Solo se calcula margen si:

```text
sale.state = KNOWN
cost.state = KNOWN
sale.currency = cost.currency
sale.economic_basis_ref = cost.economic_basis_ref
```

y ambas magnitudes son aplicables al contexto de evaluación.

Si se requiere FX o conversión de basis/unidad, debe existir una transformación externa previamente autorizada y trazable.

MGE no convierte por sí mismo.

---

## 5. MGE-AUTH-04 — Margen en importe

Fórmula empresarial propuesta:

```text
margin_amount = AuthorizedSaleBasis.value - AuthorizedCostBasis.value
```

`margin_amount`:

- conserva la moneda;
- conserva `economic_basis_ref`;
- puede ser positivo, cero o negativo;
- no se redondea para cambiar clasificación económica;
- conserva referencias a ambas bases.

---

## 6. MGE-AUTH-05 — Margen porcentual

Se propone definir **margen porcentual**, no markup, como:

```text
margin_percentage =
    margin_amount / AuthorizedSaleBasis.value × 100
```

cuando:

```text
AuthorizedSaleBasis.value > 0
```

Esta definición fija explícitamente el denominador en la base de venta.

Por tanto:

```text
margin_percentage ≠ markup
```

El porcentaje puede ser negativo cuando el coste supera la venta.

No se clampa artificialmente a 0–100.

---

## 7. MGE-AUTH-06 — Base de venta cero

Cuando:

```text
AuthorizedSaleBasis.value = 0
```

se propone:

```text
margin_amount = 0 - AuthorizedCostBasis.value
margin_percentage = NOT_DETERMINABLE
```

No se divide por cero ni se sustituye el porcentaje por 0.

---

## 8. MGE-AUTH-07 — Descuentos y rappels

MGE Core **no aplica descuentos ni rappels directamente** en v0.1.

Si un descuento o rappel debe afectar al margen, su efecto debe estar ya incorporado en una de las bases autorizadas mediante una transformación/atribución trazable.

Reglas:

1. no doble cómputo;
2. descuento/rappel no evidenciado no se anticipa;
3. una condición futura no demostrada no se considera cumplida;
4. MGE-005/MGE-006 no se usan como switches mientras no tengan consumidor funcional demostrado.

---

## 9. MGE-AUTH-08 — Relación con TCO

TCO puede ser una fuente upstream de una base de coste **solo si una autoridad externa lo transforma/declara expresamente como `AuthorizedCostBasis` compatible**.

MGE no ejecuta automáticamente:

```text
TCO.value / quantity
```

ni ninguna otra transformación TCO→margen.

Así se conserva la autoridad del dominio TCO y se evita asumir una base unitaria no autorizada.

---

## 10. MGE-AUTH-09 — Parámetros y Rules

MGE Core produce únicamente:

```text
margin_amount
margin_percentage
calculation_state
trazabilidad
```

Las reglas consumen posteriormente esos resultados conforme a autoridad propia.

Relaciones vigentes preservadas:

```text
P-MGE-001 → R-MGE-001
P-MGE-002 → R-MGE-003
P-MGE-003 → R-MGE-002
```

Los valores iniciales del catálogo no se convierten mediante esta autoridad en valores empresariales definitivos.

`P-MGE-004/005/006` permanecen sin consumidor directo demostrado.

---

## 11. MGE-AUTH-10 — Estados de insuficiencia

Si falta cualquiera de las bases o existe contradicción material no resuelta:

```text
margin_amount = null
margin_percentage = null
calculation_state = NOT_EVIDENCED / CONFLICTING_DATA / NOT_DETERMINABLE
```

según la causa.

No existe fallback silencioso.

---

## 12. Consecuencia de aprobación

Si esta propuesta se autoriza, permitirá:

1. cerrar metodología MGE v0.3;
2. diseñar contrato técnico de `Profitability Core`;
3. implementar un core determinista sobre bases autorizadas;
4. mantener fuera del core la selección de fuentes y los gaps `P-MGE-004/005/006`;
5. avanzar después hacia Rules sin inventar margen/markup.

---

## 13. Estado

**MGE-AUTH v0.1 — PROPUESTA / NO AUTORIZADA.**

No debe utilizarse como autoridad hasta aprobación humana explícita.

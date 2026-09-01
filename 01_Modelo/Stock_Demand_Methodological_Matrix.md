# EIOS — STOCK & DEMAND METHODOLOGICAL MATRIX

**Versión:** 0.1  
**Estado:** DISEÑO — PENDIENTE DE AUTORIDAD CUANTITATIVA  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 01/09/2026

---

## 1. Propósito

Esta matriz formaliza el perímetro metodológico de Stock & Demand Intelligence sin introducir fórmulas o criterios cuantitativos no demostrados por la documentación vigente.

Su finalidad es preparar la posterior implementación técnica de STK mediante la secuencia:

`metodología → regla → parámetro → contrato → implementación → tests`

La matriz no crea reglas, parámetros, excepciones ni valores empresariales nuevos.

---

## 2. Autoridad utilizada

Fuentes actualmente demostradas:

- `01_Modelo/Especificacion_funcional.md` — alcance funcional de stock y demanda.
- `04_Reglas/Matriz_Reglas_MVP.md` v2.1 — reglas `R-STK-001…004`, reglas de rotación y `R-ENT-001`.
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` — parámetros `STK-001…006` y `PYE-001…006`.
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` — estado de los parámetros y relaciones parámetro-regla.
- `04_Reglas/Rule_Dependency_Matrix.md` v1.3 — gobierno de dependencias.

Ninguna de estas fuentes autoriza por sí sola una fórmula cuantitativa completa para STK.

---

## 3. Perímetro funcional demostrado

EIOS puede considerar, cuando exista información suficiente:

- stock actual;
- stock comprometido;
- pedidos pendientes;
- compras en tránsito;
- consumo/demanda histórica;
- demanda prevista;
- plazo de entrega;
- fecha prevista de recepción;
- cantidad propuesta.

El análisis puede identificar:

- riesgo de rotura;
- exceso de stock;
- compra potencialmente innecesaria;
- compra necesaria para atender demanda prevista.

---

## 4. Reglas STK demostradas

| Rule_ID | Regla | Condición documental | Resultado | Estado metodológico |
|---|---|---|---|---|
| `R-STK-001` | Riesgo de rotura | La proyección indica agotamiento antes de nueva recepción | COMPRAR / COMPRAR CONDICIONADO | Fórmula de proyección pendiente |
| `R-STK-002` | Compra innecesaria por stock suficiente | Cobertura supera ampliamente nivel configurado sin necesidad justificada | NO COMPRAR / NEGOCIAR CANTIDAD | Definición cuantitativa de cobertura pendiente |
| `R-STK-003` | Exceso de stock | Stock posterior a compra supera máximo configurado | NEGOCIAR / NO COMPRAR | Fórmula y horizonte temporal pendientes |
| `R-STK-004` | Excepción por pedido confirmado | Pedido confirmado absorbe total/parcialmente el exceso | COMPRAR / COMPRAR CONDICIONADO | Mecánica de absorción pendiente |

---

## 5. Parámetros STK demostrados

El catálogo vigente define:

| ID | Definición vigente | Estado |
|---|---|---|
| `STK-001` | Stock mínimo | Pendiente de datos |
| `STK-002` | Stock de seguridad | 15 % del consumo; pendiente de validación |
| `STK-003` | Cobertura mínima | 30 días; pendiente de validación |
| `STK-004` | Cobertura máxima | 90 días; pendiente de validación |
| `STK-005` | Tolerancia de exceso | 10 %; pendiente de validación |
| `STK-006` | Periodo para calcular consumo | 12 meses; pendiente de validación |

Estos valores son valores iniciales de trabajo, no autoridad cuantitativa definitiva.

---

## 6. Parámetros de proyección relacionados

| ID | Definición vigente | Estado |
|---|---|---|
| `PYE-001` | Horizonte de proyección | Pendiente de validación |
| `PYE-002` | Considerar pedidos pendientes | Pendiente de validación |
| `PYE-003` | Considerar compras en tránsito | Pendiente de validación |
| `PYE-004` | Considerar plazo de entrega | Pendiente de validación |
| `PYE-005` | Considerar ventas históricas | Pendiente de validación |
| `PYE-006` | Umbral de riesgo de rotura | Pendiente de validación |

La existencia de estos parámetros no demuestra todavía qué regla los consume ni qué transformación aplica.

---

## 7. Variables canónicas requeridas

Antes de implementar STK deben quedar definidas, con unidad y fecha de referencia inequívocas:

1. `stock_on_hand` — stock físico disponible en la fecha de evaluación.
2. `stock_committed` — stock comprometido cuya semántica debe ser confirmada.
3. `pending_orders` — pedidos pendientes relevantes.
4. `in_transit` — compras en tránsito relevantes.
5. `consumption` — consumo histórico utilizado por la metodología.
6. `demand` — demanda utilizada para proyección.
7. `lead_time` — plazo de entrega aplicable.
8. `expected_receipt_date` — fecha prevista de recepción.
9. `proposed_quantity` — cantidad de la propuesta.
10. `evaluation_date` — fecha canónica de evaluación.

La lista anterior define variables de entrada necesarias para el diseño; no define todavía sus fórmulas de agregación.

---

## 8. Puntos metodológicos que deben resolverse antes del código

### STK-M01 — Consumo

Debe determinarse si `consumption` corresponde a consumo real, ventas, demanda o una transformación documentada de estas fuentes.

### STK-M02 — Stock mínimo

Debe determinarse cómo `STK-001` se relaciona con stock de seguridad, cobertura y demanda.

### STK-M03 — Stock de seguridad

Debe determinarse si `STK-002` se aplica sobre consumo medio, demanda u otra magnitud autorizada.

### STK-M04 — Cobertura

Debe definirse formalmente el numerador, denominador, unidad temporal y tratamiento de consumo/demanda nulos.

### STK-M05 — Proyección

Debe definirse cómo se incorpora el plazo de entrega y la fecha prevista de recepción.

### STK-M06 — Pedidos pendientes y tránsito

Debe determinarse si se incorporan como aumentos de disponibilidad futura y en qué fecha, evitando doble contabilización.

### STK-M07 — Exceso

Debe definirse la relación entre `STK-004` y `STK-005`, especialmente si la tolerancia modifica el umbral o solo la clasificación.

### STK-M08 — Pedido confirmado

Debe definirse cómo se demuestra la absorción del exceso por un pedido confirmado y cómo se evita convertir una expectativa en hecho.

### STK-M09 — Ausencia de datos

Debe definirse qué entradas son críticas y qué resultado produce su ausencia. Nunca debe sustituirse ausencia por cero sin autoridad explícita.

### STK-M10 — Contradicciones

Debe definirse el tratamiento de datos de stock/demanda temporalmente incompatibles o contradictorios, sin resolverlos mediante heurística no autorizada.

---

## 9. Regla de no invención

Hasta que `STK-M01…STK-M10` estén resueltos documentalmente:

- no se implementan fórmulas cuantitativas de STK;
- no se asignan consumidores definitivos a `P-STK-*` o `PYE-*` por inferencia nominal;
- no se crean parámetros adicionales;
- no se crean reglas adicionales;
- no se convierten valores iniciales del catálogo en política empresarial definitiva.

---

## 10. Criterio de entrada a implementación

STK podrá pasar a contrato técnico cuando exista evidencia suficiente para determinar, como mínimo:

- entradas canónicas;
- unidad de cada magnitud;
- fecha de referencia;
- fórmula de consumo/demanda;
- fórmula de cobertura;
- regla de proyección;
- tratamiento de recepción futura;
- tratamiento de ausencia;
- tratamiento de contradicción;
- relación demostrada regla ↔ parámetro.

**Estado actual:** NO APTO PARA IMPLEMENTACIÓN CUANTITATIVA.

---

## 11. Estado

**STK Methodological Matrix v0.1**  
**Estado:** DISEÑO — PENDIENTE DE AUTORIDAD CUANTITATIVA  
**No constituye contrato de implementación.**

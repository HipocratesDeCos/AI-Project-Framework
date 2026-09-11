# EIOS — ROTACIÓN · METHODOLOGICAL DESIGN v0.1

**Estado:** DISEÑO INICIAL — PENDIENTE DE AUDIT 1  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Rama:** `rot/rotation-methodology-v0.1`

---

## 1. Propósito

Delimitar la metodología de Rotación necesaria para sostener `R-ROT-001` y `R-ROT-002` sin inventar una fórmula, umbral, periodo, fuente o excepción no autorizada.

Este documento no implementa Rules ni crea parámetros nuevos.

---

## 2. Autoridad disponible

### Matriz de Reglas MVP

`R-ROT-001 — Producto de baja rotación`

- condición: la rotación está por debajo del umbral establecido;
- resultado: NEGOCIAR / NO COMPRAR;
- efecto/severidad: R2 / ALTA.

`R-ROT-002 — Producto sin rotación`

- condición: no existen ventas durante el periodo configurado;
- resultado: NO COMPRAR salvo excepción;
- efecto/severidad: R1 / ALTA, escalable a R0 si una política aplicable establece bloqueo;
- excepciones posibles: pedido confirmado, campaña prevista, operación estratégica, decisión empresarial explícita.

### Stock & Demand

La metodología STK cerrada distingue explícitamente:

- consumo real;
- demanda autorizada;
- ventas históricas.

Ventas históricas no sustituyen consumo o demanda por defecto.

Por tanto Rotación no puede apropiarse de `consumption` o `demand` por semejanza semántica.

---

## 3. Hallazgos de entrada

El baseline no demuestra todavía:

1. definición canónica de `rotation`;
2. fórmula de rotación;
3. numerador y denominador;
4. unidad de la métrica;
5. ventana temporal aplicable a `R-ROT-001`;
6. umbral configurable de baja rotación;
7. parámetro del periodo de `R-ROT-002`;
8. dependencia DATA/EVIDENCE de `R-ROT-001/002` en la RDM;
9. consumidor funcional parametrizado para ROT;
10. mecanismo formal de las excepciones no STK.

La ausencia de estos elementos impide implementar cuantitativamente Rotación.

---

## 4. Separación semántica obligatoria

El diseño distingue cuatro conceptos:

```text
sales_activity
rotation_metric
consumption
stock_coverage
```

No son equivalentes.

### 4.1 `sales_activity`

Representa evidencia de ventas del artículo dentro de una ventana explícita.

No autoriza por sí misma una fórmula de rotación.

### 4.2 `rotation_metric`

Representa la métrica empresarial que, una vez autorizada, permitirá comparar contra el umbral de `R-ROT-001`.

Su fórmula queda PENDING.

### 4.3 `consumption`

Permanece bajo STK-M01 y no se convierte en ventas o rotación.

### 4.4 `stock_coverage`

Permanece bajo STK-M04 y no se utiliza como sustituto de rotación.

---

## 5. Evidencia mínima conceptual

La futura evaluación de rotación deberá poder conservar, cuando corresponda:

```text
article_id
evaluation_date
window_start
window_end
sales_quantity_or_sales_events
sales_evidence_refs
sales_source_ref
unit_or_basis
rotation_metric_value (solo si autoridad permite calcularla)
rotation_methodology_ref
trace_refs
```

La lista es un contrato conceptual de evidencia, no una definición de fórmula.

---

## 6. Regla R-ROT-002 — cero ventas

La condición documental permite afirmar únicamente:

> No existen ventas durante el periodo configurado.

Para evaluarla de forma legítima deberán estar demostrados:

1. periodo configurado vigente;
2. fuente de ventas aplicable;
3. artículo/scope correcto;
4. completitud suficiente de la ventana;
5. evidencia de cero ventas, no mera ausencia de registros.

### Invariante

```text
sin registros de venta != ventas = 0
```

Si la ventana está incompleta o la fuente no puede demostrar cero, el resultado no puede tratarse como “sin rotación”.

---

## 7. Regla R-ROT-001 — baja rotación

La regla exige dos autoridades que hoy no están demostradas:

```text
rotation_metric methodology
+
rotation_threshold
```

Hasta cerrarlas:

```text
R-ROT-001 = NOT EVALUABLE QUANTITATIVELY
```

No se usará como sustituto:

- ventas por día;
- ventas mensuales;
- consumo;
- cobertura;
- stock turnover contable;
- días de inventario;
- frecuencia de pedidos;
- cualquier score de movimiento.

---

## 8. Excepciones de R-ROT-002

Las excepciones listadas en la Matriz de Reglas son posibilidades documentales, no autorizaciones automáticas.

### Pedido confirmado

Puede existir una relación conceptual con STK-M08, pero no se declarará dependencia formal hasta que la autoridad de Rules la demuestre.

### Campaña prevista

Requiere evidencia y autoridad específicas aún no demostradas.

### Operación estratégica

Requiere definición y autoridad explícitas; no puede inferirse.

### Decisión empresarial explícita

Es una intervención humana trazable; no constituye una regla automática de Rotación.

---

## 9. Estados metodológicos propuestos

Sin crear todavía un contrato físico, el análisis deberá distinguir como mínimo:

```text
EVIDENCED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

La ausencia de ventas demostradas y la ausencia de datos no deben compartir estado.

---

## 10. Relación con Rules y CRC

Rotación produce evidencia/resultado analítico; no produce una decisión final.

```text
ROT evidence / metric
        ↓
R-ROT-001 / R-ROT-002
        ↓
Assessment
        ↓
CRC
        ↓
recomendación
        ↓
decisor humano
```

Rotación no:

- selecciona el resultado entre NEGOCIAR y NO COMPRAR;
- escala por sí misma R1→R0;
- aplica excepciones no formalizadas;
- ejecuta CRC;
- decide compra.

---

## 11. Parámetros

El catálogo MVP vigente no contiene una familia `ROT-*` demostrada.

No se crearán parámetros por inferencia durante esta fase.

Los elementos funcionales pendientes son, como mínimo:

- umbral de baja rotación;
- periodo de evaluación de cero ventas;
- posible ventana/metodología de cálculo de la métrica.

Audit 1 deberá determinar si alguno ya existe bajo otra autoridad o si constituyen gaps reales de parametrización.

---

## 12. Criterio de entrada a contrato técnico

Rotación no será apta para contrato técnico cuantitativo hasta que se cierre documentalmente:

1. semántica de `rotation_metric`;
2. fórmula/metodología;
3. unidad/basis;
4. ventana temporal;
5. umbral de `R-ROT-001`;
6. periodo de `R-ROT-002`;
7. relación parámetro↔regla;
8. dependencias mínimas DATA/EVIDENCE;
9. tratamiento de ausencia vs cero;
10. excepciones que deban ser operativas.

---

## 13. Estado

**ROT v0.1 — DISEÑO INICIAL.**  
**Implementación cuantitativa:** NO AUTORIZADA.  
**Nuevos parámetros:** 0.  
**Fórmulas inventadas:** 0.

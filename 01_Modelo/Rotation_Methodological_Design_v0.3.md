# EIOS — ROTACIÓN · METHODOLOGICAL DESIGN v0.3

**Estado:** DEPURADO TRAS AUDIT 2 — PENDIENTE DE AUDIT 2 FINAL  
**Fecha:** 11/09/2026  
**Base:** `Rotation_Methodological_Audit_2_v0.2.md`

---

## 1. Corrección ROT-A2-01

Se elimina cualquier interpretación basada únicamente en:

```text
sum(sales_quantity) == 0
```

como prueba de “no existen ventas”.

La condición factual de inactividad se sustenta exclusivamente mediante evidencia de actividad de ventas sobre una ventana completa y semánticamente definida.

---

## 2. ROT-TRACK-A — Sales Activity Window

### 2.1 Objeto conceptual

```text
SalesActivityWindowEvidence
├── article_id
├── evaluation_date
├── window_start
├── window_end
├── window_authority_ref
├── source_ref
├── source_semantics_ref
├── completeness_ref
├── activity_state
├── evidence_refs
└── trace_refs
```

### 2.2 `source_semantics_ref`

Debe identificar la autoridad o semántica de la fuente que permite determinar qué registros constituyen ventas válidas.

ROT no define por sí mismo:

- qué documento comercial equivale a venta;
- si una devolución revierte o no una venta histórica;
- tratamiento de anulaciones;
- tratamiento de notas de abono;
- netting contable;
- reconocimiento temporal de ingresos.

### 2.3 `completeness_ref`

Debe permitir demostrar que la ventana evaluada está cubierta de forma suficiente para concluir actividad o inactividad.

Una ventana parcialmente disponible no se presume completa.

### 2.4 Estados conceptuales

```text
SALES_ACTIVITY_PRESENT
ZERO_VALID_SALES_DEMONSTRATED
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

### 2.5 Semántica cerrada

`ZERO_VALID_SALES_DEMONSTRATED` significa:

> La fuente autorizada, conforme a su semántica identificada y con cobertura suficiente de toda la ventana aplicable, demuestra que no existió ningún evento de venta válido del artículo dentro de esa ventana.

No significa:

- suma neta = 0;
- ausencia de filas;
- ausencia de factura encontrada en una búsqueda incompleta;
- consumo = 0;
- demanda = 0;
- cobertura infinita;
- stock sin movimiento.

`SALES_ACTIVITY_PRESENT` significa que al menos una venta válida queda demostrada dentro de la misma ventana y scope.

---

## 3. Relación con R-ROT-002

La condición factual se entrega a Rules de forma no decisional:

```text
ZERO_VALID_SALES_DEMONSTRATED
→ soporte factual para “no existen ventas durante el periodo configurado”

SALES_ACTIVITY_PRESENT
→ soporte factual para que la condición no se cumpla
```

Los restantes estados no autorizan TRUE/FALSE concluyente.

ROT no produce `Assessment` ni el resultado `NO COMPRAR`.

---

## 4. Ventana temporal

Permanece obligatorio:

```text
window_start <= window_end <= evaluation_date
window_authority_ref != null
```

La fuente del periodo configurado sigue siendo un gap de parametrización.

No se crean ni reutilizan parámetros por inferencia.

---

## 5. Excepciones

Track A no resuelve ni aplica excepciones.

Las posibilidades documentadas en `R-ROT-002` permanecen fuera del análisis factual hasta especificación de Rules/autoridad correspondiente.

---

## 6. ROT-TRACK-B — Rotation Metric

Sin cambios respecto de v0.2.

Permanece bloqueado hasta que una autoridad especializada defina:

```text
rotation_metric_definition
rotation_formula
rotation_numerator
rotation_denominator
rotation_unit_or_basis
rotation_window
rotation_threshold
```

No se adopta ninguna fórmula estándar por inferencia.

---

## 7. Gaps controlados

### ROT-G01 — Periodo configurable R-ROT-002

No existe parámetro demostrado.

### ROT-G02 — Métrica de R-ROT-001

No existe metodología demostrada.

### ROT-G03 — Umbral R-ROT-001

No existe parámetro demostrado.

### ROT-G04 — Dependencias canónicas

RDM no contiene aún DATA/EVIDENCE/PARAMETER para `R-ROT-001/002`.

### ROT-G05 — Excepciones operativas R-ROT-002

La enumeración de excepciones posibles no constituye contrato ejecutable.

---

## 8. Criterio de cierre parcial

Track A podrá cerrarse metodológicamente cuando Audit 2 final confirme:

1. cero ventas se basa en ausencia demostrada de eventos válidos;
2. semántica de fuente explícita;
3. completitud explícita;
4. ventana autorizada obligatoria;
5. ausencia != cero;
6. no netting implícito;
7. no conversión STK→ROT;
8. no aplicación de excepciones;
9. no decisión.

El cierre parcial no autoriza implementación hasta resolver `ROT-G01` y `ROT-G04`.

Track B permanece abierto por `ROT-G02/03/04`.

---

## 9. Estado

**ROT v0.3 — DEPURADO.**  
**Track A:** candidato a cierre metodológico parcial.  
**Track B:** bloqueado.  
**Implementación:** NO AUTORIZADA.  
**Política empresarial nueva:** 0.

# DECISION LOG — PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 20/08/2026

---

# 1. PROPÓSITO

Este documento registra las decisiones necesarias para cerrar la definición funcional de `02_Parametros` sin modificar silenciosamente la autoridad de `01_Modelo`, `04_Reglas` o la CRC.

Actúa como documento de decisión y no sustituye al Centro de Parametrización, al Catálogo de Parámetros ni a la Matriz de Reglas.

---

# 2. DECISIONES APROBADAS

## D-01 — Datos insuficientes

**Elemento:** `DAT-004 — Permitir evaluación con datos incompletos`

**Decisión:** No incluirlo como capacidad configurable del MVP.

**Motivo:** La Especificación Funcional v2.0 establece que cuando falte información crítica para una evaluación fiable EIOS deberá identificar la insuficiencia y utilizar `INFORMACIÓN INSUFICIENTE` cuando corresponda.

**Consecuencia:** La ausencia de evidencia crítica no podrá convertirse mediante un parámetro ordinario en una recomendación favorable.

**Estado:** APROBADO.

---

## D-02 — Parámetros críticos

**Elemento:** parámetros cuyo cambio pueda afectar a bloqueos, salvaguardas o restricciones críticas.

**Decisión:** Los parámetros críticos no podrán ser modificados mediante una parametrización ordinaria sin controles específicos de autorización, trazabilidad y vigencia.

**Motivo:** La parametrización no debe convertirse en un mecanismo indirecto para desactivar salvaguardas.

**Estado:** APROBADO.

---

## D-03 — Activación/desactivación de reglas

**Elementos:** `RGL-001` a `RGL-006`.

**Decisión:** Los parámetros ordinarios no podrán desactivar reglas críticas, anular restricciones no anulables ni habilitar excepciones no autorizadas. Las reglas no críticas podrán ser configurables cuando su autoridad documental lo permita. Toda modificación deberá quedar trazada.

**Motivo:** Activar, desactivar o permitir excepciones puede alterar el comportamiento de reglas y salvaguardas. La autoridad no debe quedar implícita en el catálogo de parámetros.

**Estado:** APROBADO.

---

## D-04 — Prioridad frente a autoridad

**Elemento:** prioridades configurables.

**Decisión:** La prioridad de un parámetro o regla no constituye por sí misma autoridad de resolución.

**Motivo:** La resolución de conflictos corresponde a la CRC. El catálogo de parámetros no debe duplicar ni sustituir dicha autoridad.

**Estado:** APROBADO.

---

## D-05 — Datos de presentación y trazabilidad

**Elementos:** `DAT-005 — Mostrar fecha de actualización` y `DAT-006 — Mostrar nivel de fiabilidad`.

**Decisión:** Reclasificar estos elementos fuera del catálogo de parámetros empresariales ordinarios cuando no modifiquen la lógica de decisión, tratándolos como capacidades de presentación, calidad o trazabilidad según corresponda.

**Motivo:** Un elemento informativo no debe confundirse con una variable que modifique el comportamiento del motor.

**Estado:** APROBADO.

---

## D-06 — Valores iniciales

**Elemento:** valores económicos y operativos incluidos en el catálogo.

**Decisión:** Mantenerlos como valores iniciales de trabajo hasta su validación con datos empresariales y casos reales.

**Motivo:** El catálogo actual identifica estos valores como pendientes de validación.

**Estado:** APROBADO.

---

## D-07 — Parámetro sin consumidor

**Elemento:** cualquier parámetro que no pueda vincularse documentalmente a una regla o función MVP.

**Decisión:** No considerarlo parámetro MVP confirmado hasta identificar su consumidor funcional.

**Motivo:** Evitar un catálogo sobredimensionado y parámetros sin efecto real en el sistema.

**Estado:** APROBADO.

---

## D-08 — Regla sin parámetro

**Elemento:** regla que requiera un valor configurable y no disponga del parámetro correspondiente.

**Decisión:** Registrar la carencia como gap de parametrización antes de cerrar el catálogo MVP.

**Motivo:** El catálogo debe ser suficiente para soportar las reglas configurables del MVP.

**Estado:** APROBADO.

---

# 3. CRITERIO DE CIERRE DE 02_PARAMETROS

La carpeta no se considerará cerrada hasta que:

1. cada parámetro MVP tenga consumidor funcional o justificación explícita;
2. cada regla parametrizable tenga sus parámetros identificados;
3. los parámetros críticos tengan controles de modificación adecuados;
4. los valores que se declaren oficiales hayan sido validados;
5. se diferencien claramente parámetros, reglas, presentación y trazabilidad;
6. la matriz de parámetros y reglas quede coherente con `04_Reglas` y la CRC.

Las decisiones D-01 a D-08 están aprobadas y deberán trasladarse de forma controlada a los documentos afectados.

---

# 4. PRINCIPIO DE NO ALTERACIÓN DE AUTORIDAD

Este Decision Log no modifica por sí mismo documentos aprobados.

Una decisión aprobada que afecte a `04_Reglas`, la CRC, `01_Modelo` o la Arquitectura deberá materializarse mediante la actualización controlada del documento que tenga autoridad sobre la materia.

---

# 5. ESTADO

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP

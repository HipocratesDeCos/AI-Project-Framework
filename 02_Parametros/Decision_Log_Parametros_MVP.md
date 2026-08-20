# DECISION LOG — PARÁMETROS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.1  
**Estado:** PROPUESTA — pendiente de aprobación  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 20/08/2026

---

# 1. PROPÓSITO

Este documento registra las decisiones necesarias para cerrar la definición funcional de `02_Parametros` sin modificar silenciosamente la autoridad de `01_Modelo`, `04_Reglas` o la CRC.

Actúa como documento de decisión y no sustituye al Centro de Parametrización, al Catálogo de Parámetros ni a la Matriz de Reglas.

---

# 2. DECISIONES

## D-01 — Datos insuficientes

**Elemento:** `DAT-004 — Permitir evaluación con datos incompletos`

**Decisión propuesta:** No incluirlo como capacidad configurable del MVP.

**Motivo:** La Especificación Funcional v2.0 establece que cuando falte información crítica para una evaluación fiable EIOS deberá identificar la insuficiencia y utilizar `INFORMACIÓN INSUFICIENTE` cuando corresponda.

**Consecuencia:** La ausencia de evidencia crítica no podrá convertirse mediante un parámetro ordinario en una recomendación favorable.

**Estado:** PROPUESTA.

---

## D-02 — Parámetros críticos

**Elemento:** parámetros cuyo cambio pueda afectar a bloqueos, salvaguardas o restricciones críticas.

**Decisión propuesta:** Los parámetros críticos no podrán ser modificados mediante una parametrización ordinaria sin controles específicos de autorización, trazabilidad y vigencia.

**Motivo:** La parametrización no debe convertirse en un mecanismo indirecto para desactivar salvaguardas.

**Estado:** PROPUESTA.

---

## D-03 — Activación/desactivación de reglas

**Elementos:** `RGL-001` a `RGL-006`.

**Decisión propuesta:** No considerar estos elementos como simples parámetros ordinarios del MVP hasta definir su autoridad documental.

**Motivo:** Activar, desactivar o permitir excepciones puede alterar el comportamiento de reglas y salvaguardas. La autoridad no debe quedar implícita en el catálogo de parámetros.

**Estado:** PROPUESTA.

---

## D-04 — Prioridad frente a autoridad

**Elemento:** prioridades configurables.

**Decisión propuesta:** La prioridad de un parámetro o regla no constituye por sí misma autoridad de resolución.

**Motivo:** La resolución de conflictos corresponde a la CRC. El catálogo de parámetros no debe duplicar ni sustituir dicha autoridad.

**Estado:** PROPUESTA.

---

## D-05 — Datos de presentación y trazabilidad

**Elementos:** `DAT-005 — Mostrar fecha de actualización` y `DAT-006 — Mostrar nivel de fiabilidad`.

**Decisión propuesta:** Revisar su clasificación como parámetros. Si no modifican la lógica de decisión, deberán considerarse capacidades de presentación, calidad o trazabilidad y no parámetros empresariales ordinarios.

**Motivo:** Un elemento informativo no debe confundirse con una variable que modifique el comportamiento del motor.

**Estado:** PROPUESTA.

---

## D-06 — Valores iniciales

**Elemento:** valores económicos y operativos incluidos en el catálogo.

**Decisión propuesta:** Mantenerlos como valores iniciales de trabajo hasta su validación con datos empresariales y casos reales.

**Motivo:** El catálogo actual identifica estos valores como pendientes de validación.

**Estado:** PROPUESTA.

---

## D-07 — Parámetro sin consumidor

**Elemento:** cualquier parámetro que no pueda vincularse documentalmente a una regla o función MVP.

**Decisión propuesta:** No considerarlo parámetro MVP confirmado hasta identificar su consumidor funcional.

**Motivo:** Evitar un catálogo sobredimensionado y parámetros sin efecto real en el sistema.

**Estado:** PROPUESTA.

---

## D-08 — Regla sin parámetro

**Elemento:** regla que requiera un valor configurable y no disponga del parámetro correspondiente.

**Decisión propuesta:** Registrar la carencia como gap de parametrización antes de cerrar el catálogo MVP.

**Motivo:** El catálogo debe ser suficiente para soportar las reglas configurables del MVP.

**Estado:** PROPUESTA.

---

# 3. CRITERIO DE CIERRE DE 02_PARAMETROS

La carpeta no se considerará aprobable hasta que:

1. se resuelvan D-01 a D-08;
2. cada parámetro MVP tenga consumidor funcional o justificación explícita;
3. cada regla parametrizable tenga sus parámetros identificados;
4. los parámetros críticos tengan controles de modificación adecuados;
5. los valores que se declaren oficiales hayan sido validados;
6. se diferencien claramente parámetros, reglas, presentación y trazabilidad;
7. la matriz de parámetros y reglas quede coherente con `04_Reglas` y la CRC.

---

# 4. PRINCIPIO DE NO ALTERACIÓN DE AUTORIDAD

Este Decision Log no modifica por sí mismo documentos aprobados.

Una decisión aprobada que afecte a `04_Reglas`, la CRC, `01_Modelo` o la Arquitectura deberá materializarse mediante la actualización controlada del documento que tenga autoridad sobre la materia.

---

# 5. ESTADO

**PROPUESTA — pendiente de aprobación.**

Una vez aprobadas las decisiones, deberán trasladarse de forma controlada al Centro de Parametrización, al Catálogo y a la Matriz de Parámetros-Reglas que corresponda.

# MATRIZ DE PARÁMETROS Y REGLAS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 20/08/2026

---

# 1. PROPÓSITO

Esta matriz establece el vínculo funcional entre los parámetros configurables de EIOS y las reglas empresariales que los utilizan.

Su finalidad es determinar, para cada parámetro:

- qué regla lo utiliza;
- qué función cumple;
- si es crítico;
- si puede ser editable;
- si es específico de empresa;
- si pertenece realmente al MVP;
- si requiere validación adicional.

La matriz no sustituye a la Matriz de Reglas ni al Catálogo de Parámetros. Actúa como documento de enlace entre ambas capas.

---

# 2. PRINCIPIO DE AUTORIDAD

Esta matriz no define por sí misma la autoridad de resolución de conflictos.

La prioridad funcional de una regla no equivale necesariamente a su autoridad.

La resolución de resultados incompatibles corresponde a la Capa de Resolución de Conflictos (CRC) y a los documentos que tengan autoridad sobre dicha materia.

Ningún parámetro ordinario puede desactivar una regla crítica, anular una restricción no anulable ni habilitar una excepción no autorizada.

---

# 3. ESTADO DE LA EVIDENCIA

La matriz se construye a partir de los parámetros definidos en el catálogo y de la documentación de reglas disponible.

Cuando no exista evidencia documental suficiente para afirmar que un parámetro está conectado a una regla concreta, se marcará como:

**PENDIENTE DE CRUCE CON REGLAS**

No se inventarán relaciones parámetro-regla.

---

# 4. CRITERIOS

| Campo | Significado |
|---|---|
| Parámetro | Identificador oficial del catálogo |
| Regla | Regla que consume el parámetro |
| Función | Papel funcional del parámetro |
| Crítico | Si su modificación puede afectar a una salvaguarda o bloqueo relevante |
| Editable | Si puede ser modificado mediante parametrización ordinaria |
| Empresa | Si puede variar por empresa |
| MVP | Si debe formar parte del MVP |
| Estado | Situación de validación |

---

# 5. MATRIZ DE PARÁMETROS

| ID | Área | Regla | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|
| PRE-001 a PRE-006 | Precios | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| STK-001 a STK-006 | Stock | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| PYE-001 a PYE-006 | Proyección | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| MGE-001 a MGE-006 | Rentabilidad | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| FIN-001 | Finanzas | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| FIN-002 | Finanzas | Regla financiera aplicable | Sí | Restringida | Sí | Sí | Pendiente de autoridad/validación |
| FIN-003 | Finanzas | Regla financiera aplicable | Sí | Restringida | Sí | Sí | Pendiente de autoridad/validación |
| FIN-004 a FIN-006 | Finanzas | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| PAG-001 a PAG-005 | Pagos | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| RGL-001 a RGL-006 | Reglas | Activación/excepción | Según regla | Restringida | Sí | Revisar | Pendiente de autoridad |
| RGL-007 | Reglas | Compra condicionada | Pendiente | Sí, sujeto a autoridad | Sí | Sí | Pendiente de cruce |
| DAT-001 a DAT-003 | Calidad | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| DAT-004 | Calidad | Ninguna en MVP | Sí | No | No aplica | No | Excluido del MVP |
| DAT-005 | Presentación/trazabilidad | No es parámetro de decisión | No | No aplica | No aplica | No | Reclasificado |
| DAT-006 | Calidad/explicabilidad | No es parámetro de decisión | No | No aplica | No aplica | No | Reclasificado |
| DAT-007 | Calidad | Pendiente de identificación documental individual | Sí | Restringida | Sí | Sí | Pendiente de cruce |

---

# 6. REGLAS DE GOBIERNO DERIVADAS

## G-01 — Parámetro crítico

Un parámetro cuyo cambio pueda afectar a un bloqueo, salvaguarda o restricción crítica no puede modificarse mediante parametrización ordinaria sin controles específicos de autorización, trazabilidad y vigencia.

## G-02 — Regla crítica

Un parámetro ordinario no puede desactivar una regla crítica ni anular una restricción no anulable.

## G-03 — Excepciones

Un parámetro ordinario no puede habilitar una excepción no autorizada.

## G-04 — Prioridad

La prioridad de una regla no constituye autoridad de resolución. La CRC mantiene la función de resolución de conflictos conforme a su documentación aplicable.

## G-05 — Evidencia

No se asignará una regla concreta a un parámetro si la documentación disponible no demuestra dicha relación.

## G-06 — Consumidor funcional

Un parámetro sin consumidor funcional o justificación explícita no se considerará parámetro MVP confirmado.

## G-07 — Gap

Una regla que requiera un valor configurable sin disponer del parámetro correspondiente constituye un gap de parametrización.

---

# 7. HALLAZGOS RESUELTOS POR EL DECISION LOG

- `DAT-004` queda fuera del MVP configurable.
- `DAT-005` se reclasifica como presentación/trazabilidad.
- `DAT-006` se reclasifica como calidad/explicabilidad.
- `RGL-001` a `RGL-006` quedan sujetos a autoridad y no son parámetros ordinarios sin más.
- La prioridad no se utiliza como sustituto de autoridad.
- Los valores económicos y operativos siguen siendo valores iniciales hasta su validación empresarial.

---

# 8. PENDIENTES DE VALIDACIÓN

1. Identificar documentalmente cada regla consumidora de cada parámetro.
2. Confirmar los parámetros realmente necesarios para el MVP.
3. Validar los valores empresariales definitivos.
4. Determinar los parámetros específicos de cada empresa.
5. Confirmar la editabilidad individual.
6. Resolver los gaps de parametrización que aparezcan al completar el cruce.

---

# 9. ESTADO

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP

La aprobación de esta matriz significa que el modelo de gobierno y clasificación queda aprobado. No significa que las relaciones Parámetro → Regla pendientes de evidencia hayan sido inventadas o cerradas.

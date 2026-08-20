# MATRIZ DE PARÁMETROS Y REGLAS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.4  
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

# 4. CONVENCIÓN DE IDENTIFICADORES

Se utiliza la convención establecida para distinguir las entidades entre capas:

- `P-XXX-NNN` → parámetro.
- `R-XXX-NNN` → regla.

La numeración funcional se conserva; el prefijo identifica el tipo de entidad.

---

# 5. CRITERIOS

| Campo | Significado |
|---|---|
| Parámetro | Identificador oficial del catálogo (`P-*`) |
| Regla | Regla consumidora (`R-*`) |
| Función | Papel funcional del parámetro |
| Crítico | Si su modificación puede afectar a una salvaguarda o bloqueo relevante |
| Editable | Si puede ser modificado mediante parametrización ordinaria |
| Empresa | Si puede variar por empresa |
| MVP | Si debe formar parte del MVP |
| Estado | Situación de validación |

---

# 6. MATRIZ DE PARÁMETROS

| ID | Área | Regla | Crítico | Editable | Empresa | MVP | Estado |
|---|---|---|---|---|---|---|---|
| P-PRE-001 a P-PRE-006 | Precios | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-STK-001 a P-STK-006 | Stock | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-PYE-001 a P-PYE-006 | Proyección | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-MGE-001 a P-MGE-006 | Rentabilidad | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-FIN-001 | Finanzas | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| P-FIN-002 | Finanzas | Regla financiera aplicable | Sí | Restringida | Sí | Sí | Pendiente de autoridad/validación |
| P-FIN-003 | Finanzas | Regla financiera aplicable | Sí | Restringida | Sí | Sí | Pendiente de autoridad/validación |
| P-FIN-004 a P-FIN-006 | Finanzas | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| P-PAG-001 a P-PAG-005 | Pagos | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-RGL-001 a P-RGL-006 | Reglas | Activación/excepción | Según regla | Restringida | Sí | Revisar | Pendiente de autoridad |
| P-RGL-007 | Reglas | Compra condicionada | Pendiente | Sí, sujeto a autoridad | Sí | Sí | Pendiente de cruce |
| P-DAT-001 a P-DAT-003 | Calidad | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| P-DAT-004 | Calidad | Ninguna en MVP | Sí | No | No aplica | No | Excluido del MVP |
| P-DAT-005 | Presentación/trazabilidad | No es parámetro de decisión | No | No aplica | No aplica | No | Reclasificado |
| P-DAT-006 | Calidad/explicabilidad | No es parámetro de decisión | No | No aplica | No aplica | No | Reclasificado |
| P-DAT-007 | Calidad | Pendiente de identificación documental individual | Sí | Restringida | Sí | Sí | Pendiente de cruce |

---

# 7. REGLAS DE GOBIERNO DERIVADAS

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

# 8. RELACIONES CONFIRMADAS

Actualmente no se mantienen relaciones parámetro → regla adicionales como `CONFIRMADO` en esta sección.

Las relaciones que figuraban anteriormente para `PAG-001/PAG-002 → CON-001` se eliminan porque no existe evidencia documental suficiente para sostenerlas y `CON-001` no constituye aquí un identificador válido de regla de pago.

Los casos `C-01` a `C-06` se mantienen como criterios, metodologías, evaluaciones o cálculos sin parámetro directo confirmado.

---

# 9. HALLAZGOS RESUELTOS POR EL DECISION LOG

- `P-DAT-004` queda fuera del MVP configurable.
- `P-DAT-005` se reclasifica como presentación/trazabilidad.
- `P-DAT-006` se reclasifica como calidad/explicabilidad.
- `P-RGL-001` a `P-RGL-006` quedan sujetos a autoridad y no son parámetros ordinarios sin más.
- La prioridad no se utiliza como sustituto de autoridad.
- Los valores económicos y operativos siguen siendo valores iniciales hasta su validación empresarial.
- `GAP-01 / PRO-001` queda tratado como dato del proveedor, no como nuevo parámetro empresarial.

---

# 10. PENDIENTES DE VALIDACIÓN

1. Completar la migración documental de los IDs de `02_Parametros` a `P-*`.
2. Completar la migración documental de los IDs de `04_Reglas` a `R-*`.
3. Identificar documentalmente cada regla consumidora de cada parámetro.
4. Confirmar los parámetros realmente necesarios para el MVP.
5. Validar los valores empresariales definitivos.
6. Determinar los parámetros específicos de cada empresa.
7. Confirmar la editabilidad individual.
8. Resolver los gaps de parametrización que aparezcan al completar el cruce.

---

# 11. ESTADO

**Versión:** 0.4  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP

La aprobación de esta matriz significa que el modelo de gobierno y clasificación queda aprobado. Las relaciones no demostradas permanecen pendientes y no se consideran cerradas por inferencia.

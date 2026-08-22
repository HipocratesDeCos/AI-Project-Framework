# MATRIZ DE PARÁMETROS Y REGLAS — MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.7  
**Estado:** APROBADO — CIERRE FUNCIONAL F3 / C-07  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 22/08/2026

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
| P-PRE-001 | Precios | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-PRE-002 | Precios | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| **P-PRE-003** | Precios | **Criterio/metodología histórica — no parámetro directo (C-01); R-HIS-001 utiliza P-DAT-002** | Según regla | No aplica como parámetro directo | Sí | Sí | **RESUELTO / C-01** |
| **P-PRE-004** | Precios | **R-PRE-001** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO** |
| **P-PRE-005** | Precios | **R-PRE-002** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO** |
| **P-PRE-006** | Precios | **R-HIS-002** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO** |
| P-STK-001 a P-STK-006 | Stock | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-PYE-001 a P-PYE-006 | Proyección | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| **P-MGE-001** | Rentabilidad | **R-MGE-001** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO** |
| **P-MGE-002** | Rentabilidad | **R-MGE-003** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO** |
| **P-MGE-003** | Rentabilidad | **R-MGE-002** | Según regla | Sí | Sí | Sí | **CONFIRMADO** |
| P-MGE-004 a P-MGE-006 | Rentabilidad | Pendiente de identificación documental individual | Según regla | Sí, sujeto a control | Sí | Sí | Pendiente de cruce |
| P-FIN-001 | Finanzas | Pendiente de identificación documental individual | Alta | Restringida | Sí | Sí | Pendiente de cruce |
| P-FIN-002 | Finanzas | R-FIN-001 — capacidad financiera prevista, como parte del cálculo | Sí | Restringida | Sí | Sí | CONFIRMADO — relación compuesta |
| P-FIN-003 | Finanzas | R-FIN-002 | Sí | Restringida | Sí | Sí | CONFIRMADO |
| P-FIN-004 | Finanzas | R-FIN-003 | Alta | Restringida | Sí | Sí | CONFIRMADO |
| P-FIN-005 | Finanzas | R-FIN-001 — cálculo de capacidad financiera prevista | Alta | Restringida | Sí | Sí | CONFIRMADO — relación compuesta |
| P-FIN-006 | Finanzas | R-FIN-001 — cálculo de capacidad financiera prevista | Alta | Restringida | Sí | Sí | CONFIRMADO — relación compuesta |
| **P-PAG-001** | Pagos | **R-PAG-002** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO — directa** |
| **P-PAG-002** | Pagos | **R-PAG-001** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO — directa** |
| **P-PAG-003** | Pagos | **R-PAG-001** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO — derivada** |
| **P-PAG-004** | Pagos | **R-PAG-001 / R-PAG-002** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO — control funcional** |
| **P-PAG-005** | Pagos | **R-PAG-001 / R-PAG-002** | Según regla | Sí, sujeto a control | Sí | Sí | **CONFIRMADO — indirecta / derivada** |
| P-RGL-001 a P-RGL-006 | Reglas | Activación/excepción | Según regla | Restringida | Sí | Revisar | Pendiente de autoridad |
| P-RGL-007 | Reglas | Compra condicionada | Pendiente | Sí, sujeto a autoridad | Sí | Sí | Pendiente de cruce |
| P-DAT-001 | Calidad | R-DAT-001 | Alta | Restringida | Sí | Sí | CONFIRMADO |
| P-DAT-002 | Calidad | R-HIS-001 — antigüedad máxima de referencia de precio | Alta | Restringida | Sí | Sí | CONFIRMADO |
| P-DAT-003 | Calidad | Sin consumidor directo de regla MVP demostrado; no sustituye P-PRE-006 | Alta | Restringida | Sí | Sí | SIN CONSUMIDOR DIRECTO DEMOSTRADO |
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

Las siguientes relaciones quedan confirmadas por el cruce documental realizado y, para los parámetros de pago, por la especificación especializada `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` y su incorporación a la Matriz de Reglas MVP v2.1:

| Parámetro | Regla consumidora | Tipo | Estado |
|---|---|---|---|
| `P-PRE-004` | `R-PRE-001` | Directa | CONFIRMADO |
| `P-PRE-005` | `R-PRE-002` | Directa | CONFIRMADO |
| `P-MGE-001` | `R-MGE-001` | Directa | CONFIRMADO |
| `P-MGE-002` | `R-MGE-003` | Directa | CONFIRMADO |
| `P-MGE-003` | `R-MGE-002` | Directa | CONFIRMADO |
| `P-FIN-002` | `R-FIN-001` | Compuesta | CONFIRMADO |
| `P-FIN-003` | `R-FIN-002` | Directa | CONFIRMADO |
| `P-FIN-004` | `R-FIN-003` | Directa | CONFIRMADO |
| `P-FIN-005` | `R-FIN-001` | Compuesta | CONFIRMADO |
| `P-FIN-006` | `R-FIN-001` | Compuesta | CONFIRMADO |
| `P-PAG-001` | `R-PAG-002` | Directa | CONFIRMADO |
| `P-PAG-002` | `R-PAG-001` | Directa | CONFIRMADO |
| `P-PAG-003` | `R-PAG-001` | Derivada | CONFIRMADO |
| `P-PAG-004` | `R-PAG-001 / R-PAG-002` | Control funcional | CONFIRMADO |
| `P-PAG-005` | `R-PAG-001 / R-PAG-002` | Indirecta / derivada | CONFIRMADO |
| `P-DAT-001` | `R-DAT-001` | Directa | CONFIRMADO |
| `P-DAT-002` | `R-HIS-001` | Directa | CONFIRMADO |
| `P-PRE-006` | `R-HIS-002` | Directa | CONFIRMADO |

### Nota de resolución histórica

`P-PRE-003` no se considera parámetro directo de `R-HIS-001`: C-01 lo mantiene como criterio/metodología. `R-HIS-001` utiliza `P-DAT-002` como parámetro configurable de antigüedad de referencia.

`P-DAT-003` no sustituye a `P-PRE-006`: el primero representa un criterio de disponibilidad/registro histórico, mientras el segundo representa el mínimo de operaciones comparables exigido por `R-HIS-002`.

---

# 9. HALLAZGOS RESUELTOS POR EL DECISION LOG

- `P-DAT-004` queda fuera del MVP configurable.
- `P-DAT-005` se reclasifica como presentación/trazabilidad.
- `P-DAT-006` se reclasifica como calidad/explicabilidad.
- `P-RGL-001` a `P-RGL-006` quedan sujetos a autoridad y no son parámetros ordinarios sin más.
- La prioridad no se utiliza como sustituto de autoridad.
- Los valores económicos y operativos siguen siendo valores iniciales hasta su validación empresarial.
- `GAP-01 / PRO-001` queda tratado como dato del proveedor, no como nuevo parámetro empresarial.
- `C-07` queda documentalmente satisfecho para `P-PAG-001…005` mediante `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` y su incorporación a `Matriz_Reglas_MVP v2.1`.

---

# 10. PENDIENTES DE VALIDACIÓN

1. Completar la migración documental de los IDs de `02_Parametros` a `P-*`.
2. Completar la migración documental de los IDs de `04_Reglas` a `R-*`.
3. Identificar documentalmente cada regla consumidora de cada parámetro que permanece pendiente.
4. Confirmar los parámetros realmente necesarios para el MVP.
5. Validar los valores empresariales definitivos.
6. Determinar los parámetros específicos de cada empresa.
7. Confirmar la editabilidad individual.
8. Resolver los gaps de parametrización que aparezcan al completar el cruce.

Estos pendientes son de alcance general del MVP y **no mantienen abierto C-07**.

---

# 11. ESTADO

**Versión:** 0.7  
**Estado:** APROBADO — CIERRE FUNCIONAL F3 / C-07  
**Baseline:** EIOS Vertical MVP

La relación `P-PAG-001…005 → R-PAG-*` queda incorporada a la matriz con tipo funcional explícito y evidencia documental especializada. `C-07` deja de ser un pendiente de evidencia para este conjunto de parámetros.

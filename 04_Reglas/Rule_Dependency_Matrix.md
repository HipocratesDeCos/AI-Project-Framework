# RULE DEPENDENCY MATRIX

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** APROBADO — ESTRUCTURA CANÓNICA; COBERTURA INICIAL PARCIAL  
**Baseline:** EIOS Vertical MVP  
**Ubicación:** `04_Reglas/Rule_Dependency_Matrix.md`

---

# 1. Propósito

La `Rule_Dependency_Matrix.md` constituye el mapa canónico transversal de dependencias de las reglas de EIOS.

Su finalidad es representar, de forma reproducible y trazable, qué elementos necesita una regla para poder evaluarse y qué componentes quedan afectados por esas dependencias.

La matriz conecta, sin sustituir su autoridad, las siguientes capas:

```text
REGLA
  │
  ├── datos
  ├── parámetros
  ├── evidencia
  ├── componentes
  └── condiciones de evaluabilidad
```

La matriz no define por sí misma nuevas reglas, nuevos parámetros ni nuevos criterios de evidencia.

---

# 2. Autoridad y límites

La autoridad de esta matriz deriva de `00_Gobierno/Matriz_Autoridad_Documental.md`.

La `Rule_Dependency_Matrix.md` es la **fuente canónica transversal de dependencias**.

No sustituye a:

- `02_Parametros/Catalogo_Parametros_MVP_v0.2.md` para la definición de parámetros;
- `02_Parametros/Centro_Parametrizacion.md` para los valores y gobierno de configuración;
- `04_Reglas/Matriz_Reglas_MVP.md` para condiciones, evaluación y resultados de reglas;
- `04_Reglas/Evidence_Contract.md` para el contrato general de evidencia;
- `05_Motor/Capa_resolucion_conflictos.md` para la resolución de resultados incompatibles.

Tampoco sustituye a las especificaciones especializadas que aporten evidencia o detalle funcional sobre relaciones concretas.

---

# 3. Principio fundamental

> **Una dependencia solo puede considerarse canónica cuando su relación está demostrada, identificada y trazable.**

La coincidencia de nombres, prefijos, unidades, valores o similitud semántica no constituye por sí sola evidencia suficiente.

Cuando una relación no esté demostrada deberá conservarse explícitamente como pendiente.

No se inferirán dependencias para completar artificialmente la matriz.

---

# 4. Tipos de dependencia

La matriz distingue como mínimo los siguientes tipos:

| Tipo | Significado |
|---|---|
| `DATA` | La regla necesita un dato o hecho de entrada |
| `PARAMETER` | La regla consume un parámetro configurable |
| `EVIDENCE` | La regla requiere evidencia para poder evaluarse |
| `COMPONENT` | La regla depende de otro componente del sistema |
| `DERIVED` | La dependencia procede de una relación derivada documentada |
| `CONTROL` | El elemento controla si una evaluación debe realizarse |
| `CONTEXT` | El elemento aporta contexto sin constituir por sí mismo un criterio decisorio |

Una relación puede tener más de un tipo cuando la evidencia documental lo justifique.

---

# 5. Estados de dependencia

| Estado | Significado |
|---|---|
| `CONFIRMED` | Relación demostrada mediante evidencia documental suficiente |
| `PARTIAL` | Existe evidencia, pero falta completar algún aspecto de la relación |
| `PENDING` | Relación todavía no demostrada |
| `REJECTED` | La relación fue analizada y descartada |
| `SUPERSEDED` | La relación existió, pero ha sido sustituida por otra vigente |

Solo `CONFIRMED` constituye dependencia canónica operativa.

`PARTIAL` y `PENDING` no deben utilizarse para ejecutar una dependencia como si estuviera confirmada.

---

# 6. Estructura canónica del registro

Cada dependencia deberá poder expresarse mediante los siguientes campos:

| Campo | Descripción |
|---|---|
| `Dependency_ID` | Identificador único de la dependencia |
| `Rule_ID` | Regla consumidora |
| `Dependency_Type` | Tipo de dependencia |
| `Source_ID` | Elemento del que depende la regla |
| `Source_Domain` | Dominio del elemento fuente |
| `Function` | Función concreta de la dependencia |
| `Criticality` | Importancia para la evaluabilidad |
| `Evidence_Source` | Documento que demuestra la relación |
| `Evidence_Status` | Estado de demostración |
| `Evaluability_Impact` | Efecto de la ausencia de la dependencia |
| `Fallback` | Tratamiento permitido cuando proceda |
| `Affected_Component` | Componente afectado |
| `Notes` | Observaciones de trazabilidad |

---

# 7. Reglas de autoridad sobre dependencias

## RD-01 — No invención

No se añadirá una dependencia por inferencia semántica o conveniencia de diseño.

## RD-02 — Fuente de autoridad

La fuente especializada que demuestra una relación conserva autoridad sobre el detalle que documenta.

La `Rule_Dependency_Matrix.md` consolida esa relación dentro del mapa transversal.

## RD-03 — No redefinición

La matriz no puede modificar una regla, redefinir un parámetro ni alterar el contrato general de evidencia.

## RD-04 — Evidencia insuficiente

Si una dependencia crítica no está demostrada, la regla no puede tratarla como disponible.

## RD-05 — Evaluabilidad explícita

La ausencia de una dependencia debe tener un tratamiento explícito: `BLOCKED`, `INSUFFICIENT_DATA`, `NOT_EVALUABLE` u otro estado formalmente autorizado por la documentación aplicable.

## RD-06 — No sustitución silenciosa

Una dependencia no puede ser sustituida por otra por similitud conceptual sin evidencia documental de dicha sustitución.

## RD-07 — Trazabilidad

Toda dependencia `CONFIRMED` debe poder remontarse a una fuente documental identificable.

---

# 8. Relación con Evidence Contract

`Evidence_Contract.md` establece el contrato general de evidencia.

La `Rule_Dependency_Matrix.md` determina qué evidencia concreta necesita cada regla en función de sus dependencias documentadas.

La relación es:

```text
Evidence Contract
      │
      ├── qué significa evidencia suficiente
      ├── admisibilidad
      └── trazabilidad mínima
               │
               ▼
Rule Dependency Matrix
      │
      └── qué evidencia necesita cada regla
```

La matriz no puede convertir una evidencia insuficiente en suficiente.

---

# 9. Relación con Matriz de Parámetros y Reglas

`02_Parametros/Matriz_Parametros_Reglas_MVP.md` conserva su función como **vista especializada parámetro ↔ regla**.

Sus relaciones confirmadas deben poder incorporarse a esta matriz cuando constituyan dependencias de regla.

La incorporación no modifica el significado de la relación en la fuente especializada.

La diferencia de función es:

```text
Matriz Parámetros ↔ Reglas
        │
        └── vista especializada del vínculo P → R

Rule Dependency Matrix
        │
        └── grafo transversal de dependencias de R
            ├── P
            ├── DATA
            ├── EVIDENCE
            ├── COMPONENT
            └── EVALUABILITY
```

---

# 10. Relaciones especializadas incorporadas

Las relaciones siguientes se incorporan inicialmente porque ya disponen de evidencia documental aprobada.

| Dependency_ID | Rule_ID | Type | Source_ID | Function | Status | Evidence_Source |
|---|---|---|---|---|---|---|
| DEP-PRE-004-RPRE-001 | `R-PRE-001` | `PARAMETER` | `P-PRE-004` | Parámetro consumidor de la regla | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-PRE-005-RPRE-002 | `R-PRE-002` | `PARAMETER` | `P-PRE-005` | Parámetro consumidor de la regla | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-MGE-001-RMGE-001 | `R-MGE-001` | `PARAMETER` | `P-MGE-001` | Parámetro consumidor de margen | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-MGE-002-RMGE-003 | `R-MGE-003` | `PARAMETER` | `P-MGE-002` | Parámetro consumidor de margen objetivo | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-MGE-003-RMGE-002 | `R-MGE-002` | `PARAMETER` | `P-MGE-003` | Parámetro consumidor de tolerancia | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-FIN-002-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-002` | Parte del cálculo de capacidad financiera prevista | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-FIN-003-RFIN-002 | `R-FIN-002` | `PARAMETER` | `P-FIN-003` | Parámetro consumidor de fondo de maniobra | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-FIN-004-RFIN-003 | `R-FIN-003` | `PARAMETER` | `P-FIN-004` | Parámetro consumidor de riesgo financiero | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-FIN-005-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-005` | Parte del cálculo de capacidad financiera prevista | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-FIN-006-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-006` | Parte del cálculo de capacidad financiera prevista | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-PAG-001-RPAG-002 | `R-PAG-002` | `PARAMETER` | `P-PAG-001` | Plazo mínimo aceptable | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-PAG-002-RPAG-001 | `R-PAG-001` | `PARAMETER` | `P-PAG-002` | Plazo objetivo | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-PAG-003-RPAG-001 | `R-PAG-001` | `DERIVED` | `P-PAG-003` | Modulación del objetivo de pago | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-PAG-004-RPAG-001 | `R-PAG-001` | `CONTROL` | `P-PAG-004` | Control de consideración del plazo | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-PAG-004-RPAG-002 | `R-PAG-002` | `CONTROL` | `P-PAG-004` | Control de consideración del plazo | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-PAG-005-RPAG-001 | `R-PAG-001` | `DERIVED` | `P-PAG-005` | Contexto económico de negociación | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-PAG-005-RPAG-002 | `R-PAG-002` | `DERIVED` | `P-PAG-005` | Contexto económico de negociación | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` |
| DEP-DAT-001-RDAT-001 | `R-DAT-001` | `PARAMETER` | `P-DAT-001` | Parámetro consumidor de calidad de datos | `CONFIRMED` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` |
| DEP-HIS-002-RHIS-001 | `R-HIS-001` | `PARAMETER` | `P-DAT-002` | Antigüedad máxima de referencia | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` |
| DEP-HIS-006-RHIS-002 | `R-HIS-002` | `PARAMETER` | `P-PRE-006` | Mínimo de operaciones comparables | `CONFIRMED` | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` |

---

# 11. Relaciones expresamente no demostradas

Las siguientes relaciones no deben inferirse:

| Elemento | No demostrado | Tratamiento |
|---|---|---|
| `P-PRE-003` | `P-PRE-003 → R-HIS-001` | `REJECTED` como consumidor directo; el consumidor demostrado es `P-DAT-002` |
| `P-DAT-003` | `P-DAT-003 → R-HIS-002` | `REJECTED` como consumidor directo; el consumidor demostrado es `P-PRE-006` |
| `P-DAT-003` | `P-DAT-003 → P-PRE-006` maestro → derivado | `REJECTED` por falta de transformación documentada |
| `P-PRE-003` | `P-PRE-003 → P-DAT-002` maestro → derivado | `REJECTED` por falta de transformación documentada |

Estas determinaciones se apoyan en la documentación histórica especializada y no deben reabrirse por similitud semántica.

---

# 12. Cobertura inicial y pendientes

La cobertura inicial se limita a relaciones ya demostradas documentalmente.

Quedan pendientes de cruce, entre otros:

- dependencias `DATA` no identificadas individualmente;
- dependencias `EVIDENCE` específicas por regla;
- dependencias `COMPONENT` cuando no exista evidencia documental directa;
- impactos concretos de evaluabilidad ante ausencia de cada dependencia;
- relaciones adicionales de parámetros marcadas como pendientes en la matriz de parámetros.

Estos pendientes no constituyen defectos de la matriz: representan **gaps de evidencia/dependencia aún no resueltos**.

---

# 13. Regla de evaluabilidad

Una regla solo puede considerarse evaluable cuando se cumplen las dependencias que su documentación declare críticas para esa evaluación.

La ausencia de una dependencia crítica no autoriza a:

- asumir un valor;
- reutilizar otro parámetro sin evidencia;
- convertir ausencia de evidencia en resultado positivo;
- omitir silenciosamente la regla.

El estado concreto producido por una dependencia ausente deberá alinearse con la autoridad de la regla, del Evidence Contract y de la capa de resolución aplicable.

---

# 14. Regla de actualización

Cuando se confirme una nueva dependencia:

1. debe identificarse la fuente que la demuestra;
2. debe determinarse su tipo;
3. debe registrarse su estado;
4. debe evaluarse su impacto sobre la evaluabilidad;
5. debe incorporarse a esta matriz;
6. deben actualizarse las vistas especializadas que correspondan.

La incorporación a esta matriz no permite modificar silenciosamente la fuente que tiene autoridad sobre el concepto dependiente.

---

# 15. No regresión

No se debe:

- eliminar una dependencia `CONFIRMED` sin documentar su sustitución;
- cambiar el tipo de una dependencia sin evidencia;
- convertir una relación `PENDING` en `CONFIRMED` sin fuente demostrable;
- crear una segunda autoridad transversal de dependencias;
- utilizar una dependencia `REJECTED` como si estuviera vigente;
- modificar las condiciones de una regla desde esta matriz.

---

# 16. Estado

**Versión:** 1.0  
**Estado:** APROBADO — ESTRUCTURA CANÓNICA; COBERTURA INICIAL PARCIAL  
**Ámbito:** Dependencias transversales de reglas EIOS  
**Autoridad:** `00_Gobierno/Matriz_Autoridad_Documental.md`

La matriz queda preparada para ampliar progresivamente la cobertura de dependencias sin crear nuevas fuentes de autoridad paralelas.

# MATRIZ CANÓNICA DE DEPENDENCIAS DE REGLAS

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.1  
**Estado:** BORRADOR DEPURADO — PENDIENTE DE AUDITORÍA DE CIERRE  
**Baseline:** EIOS Vertical MVP  
**Autoridad:** `00_Gobierno/Matriz_Autoridad_Documental.md`

---

# 1. Propósito

`Rule_Dependency_Matrix.md` constituye el mapa canónico transversal de dependencias de las reglas de EIOS.

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

La matriz no define por sí misma nuevas reglas, nuevos parámetros ni nuevos criterios generales de evidencia.

---

# 2. Autoridad y límites

La autoridad de esta matriz deriva de `00_Gobierno/Matriz_Autoridad_Documental.md`.

La `Rule_Dependency_Matrix.md` es la **fuente canónica transversal del mapa de dependencias**.

No sustituye a:

- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md` para la definición de parámetros;
- `02_Parametros/Centro_Parametrizacion.md` para los valores y gobierno de configuración;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md` como vista especializada del vínculo parámetro ↔ regla;
- `04_Reglas/Matriz_Reglas_MVP.md` para condiciones, evaluación y resultados de reglas;
- `04_Reglas/Evidence_Contract.md` para el contrato general de evidencia;
- `04_Reglas/Capa_resolucion_conflictos.md` para la resolución de resultados incompatibles.

Las especificaciones especializadas pueden demostrar relaciones concretas, pero no constituyen una autoridad paralela sobre el mapa transversal de dependencias.

---

# 3. Principio fundamental

> **Una dependencia solo puede considerarse canónica cuando su relación está demostrada, identificada y trazable.**

La coincidencia de nombres, prefijos, unidades, valores o similitud semántica no constituye por sí sola evidencia suficiente.

Cuando una relación no esté demostrada deberá conservarse explícitamente como pendiente o rechazada, según corresponda.

No se inferirán dependencias para completar artificialmente la matriz.

---

# 4. Tipos de dependencia

Cada registro tiene **un único `Dependency_Type` primario**.

| Tipo | Significado |
|---|---|
| `DATA` | La regla necesita un dato o hecho de entrada. |
| `PARAMETER` | La regla consume un parámetro configurable. |
| `EVIDENCE` | La regla requiere evidencia para poder evaluarse. |
| `COMPONENT` | La regla depende de otro componente del sistema. |
| `DERIVED` | La dependencia procede de una relación derivada documentada. |
| `CONTROL` | El elemento controla si una evaluación debe realizarse. |
| `CONTEXT` | El elemento aporta contexto sin constituir por sí mismo un criterio decisorio. |

No se permite registrar varios tipos primarios en un mismo registro.

Cuando una relación tenga características adicionales, estas deberán expresarse mediante `Notes` o mediante una futura extensión contractual explícita, sin alterar el tipo primario.

---

# 5. Estados de dependencia

| Estado | Significado |
|---|---|
| `CONFIRMED` | Relación demostrada mediante evidencia documental suficiente. |
| `PARTIAL` | Existe evidencia, pero falta completar algún aspecto de la relación. No constituye dependencia operativa confirmada. |
| `PENDING` | Relación todavía no demostrada. |
| `REJECTED` | La relación fue analizada y descartada. |
| `SUPERSEDED` | Relación histórica sustituida por otra vigente; no constituye dependencia operativa vigente. |

Solo `CONFIRMED` constituye dependencia canónica operativa.

---

# 6. Estructura canónica del registro

Cada dependencia canónica se representa mediante los siguientes campos:

| Campo | Obligatorio | Definición |
|---|---:|---|
| `Dependency_ID` | Sí | Identificador único de la dependencia. |
| `Rule_ID` | Sí | Regla consumidora. |
| `Dependency_Type` | Sí | Tipo primario de dependencia. |
| `Source_ID` | Sí | Elemento del que depende la regla. |
| `Source_Domain` | Sí | Dominio del elemento fuente. |
| `Function` | Sí | Función concreta de la dependencia. |
| `Criticality` | Sí | Importancia de la dependencia para la evaluabilidad. No es severidad de la regla. |
| `Evidence_Source` | Sí | Documento o autoridad que demuestra la relación. |
| `Evidence_Status` | Sí | Estado de demostración de la relación documental. |
| `Evaluability_Impact` | Sí | Impacto previsto de la ausencia de la dependencia sobre la capacidad de evaluación. |
| `Fallback` | Sí | Tratamiento de contingencia autorizado, o `NONE`. Nunca contiene lógica de sustitución inventada. |
| `Affected_Component` | Sí | Componente afectado cuando exista evidencia de esa dependencia; en otro caso `NONE` o valor controlado pendiente. |
| `Notes` | Sí | Información explicativa o de trazabilidad que no crea nueva autoridad. |

La obligatoriedad del campo no implica que siempre deba contener una afirmación positiva. Cuando un aspecto aún no esté establecido, debe utilizarse un valor controlado inequívoco, no una inferencia.

---

# 7. Criticality

`Criticality` expresa la importancia de una dependencia respecto de la **capacidad de evaluar la regla**.

No representa:

- severidad de la regla;
- efecto de la regla;
- prioridad de la regla;
- impacto económico de la operación;
- prioridad de resolución del CRC.

La severidad y el efecto permanecen bajo la autoridad de `Matriz_Reglas_MVP.md`.

---

# 8. Evaluability_Impact

`Evaluability_Impact` describe el impacto de la ausencia de una dependencia sobre la capacidad de evaluación de la regla.

Valores controlados:

| Valor | Significado |
|---|---|
| `NO_IMPACT` | La ausencia no impide la evaluación. |
| `WARNING` | La ausencia permite continuar solo bajo un tratamiento explícitamente autorizado. |
| `INSUFFICIENT_DATA` | La ausencia deja insuficiente la información necesaria. |
| `BLOCKED` | La dependencia es necesaria y su ausencia impide continuar con la evaluación. |

`NOT_EVALUABLE` **no es un valor producido por la RDM**.

Es un resultado del proceso de evaluación y pertenece al contrato de `Assessment`.

La cadena conceptual es:

```text
Dependency unavailable
        ↓
Evaluability_Impact
        ↓
Rule evaluation
        ↓
Assessment
        ↓
EVALUABLE / NOT_EVALUABLE
```

---

# 9. Fallback

`Fallback` no constituye una regla de sustitución.

Solo puede contener:

- `NONE`;
- una referencia a un mecanismo de contingencia ya autorizado por otra fuente de autoridad;
- una referencia a un tratamiento explícitamente definido por la regla o por la arquitectura aplicable.

No puede contener instrucciones creadas por la RDM como:

```text
si falta X → utilizar Y
```

salvo que esa sustitución esté previamente definida y demostrada por la autoridad correspondiente.

La RDM no crea valores por defecto.

---

# 10. Evidence_Source y Evidence_Status

`Evidence_Source` identifica el documento, especificación, contrato o autoridad que demuestra la relación.

`Evidence_Status` describe el estado de la **relación documental**, no el estado operativo de un objeto `Evidence`.

Valores mínimos:

```text
CONFIRMED
PARTIAL
PENDING
REJECTED
SUPERSEDED
```

Esto es distinto de:

```text
Evidence.state
→ DEMONSTRATED / GAP

EvidenceValidation.status
→ VALID / INVALID
```

La RDM no redefine ninguno de esos estados.

---

# 11. DERIVED

Una dependencia `DERIVED` exige que la transformación que conecta la fuente con la regla esté explícitamente documentada.

No es suficiente que los nombres o significados parezcan relacionados.

Por tanto:

```text
Source A
   ↓
transformación documentada
   ↓
Rule dependency
```

Una relación sin transformación demostrable no puede clasificarse como `CONFIRMED / DERIVED`.

---

# 12. DATA

Una dependencia `DATA` representa una entrada de datos que la regla necesita.

El nombre conceptual de una información mencionada en `Matriz_Reglas_MVP.md` no constituye automáticamente una dependencia `DATA` confirmada.

La relación debe demostrarse mediante la documentación correspondiente.

Por tanto:

```text
Regla menciona “stock”
        ≠
RDM puede inventar DATA → stock
```

El cruce `Rule × DATA` debe construirse de forma demostrable.

---

# 13. EVIDENCE

Una dependencia `EVIDENCE` identifica evidencia que una regla concreta necesita para sustentar su evaluación.

La RDM determina la relación:

```text
Rule → Evidence requirement
```

pero no redefine qué hace admisible o suficiente una evidencia.

Eso corresponde a `Evidence_Contract.md`.

Las condiciones específicas de comparabilidad, temporalidad, cantidad u otras características pertenecen a la regla y/o a la especificación de dependencias correspondiente; no se convierten en criterios generales del Evidence Contract.

---

# 14. COMPONENT

Una dependencia `COMPONENT` solo se confirma cuando existe evidencia de que la regla requiere un componente o servicio concreto.

No debe inferirse una dependencia directa porque un componente produzca datos que finalmente utiliza la regla.

Debe distinguirse:

```text
Rule → Data
```

de:

```text
Rule → Component
```

La segunda requiere evidencia específica.

---

# 15. CONTEXT

`CONTEXT` representa información contextual que puede intervenir en la interpretación de una evaluación, pero que no constituye por sí misma un criterio decisorio.

No puede utilizarse para introducir una regla implícita.

Cada registro conserva un único tipo primario.

---

# 16. Relaciones confirmadas actualmente

La cobertura de esta versión se limita deliberadamente a relaciones cuya existencia ya está documentada.

| Dependency_ID | Rule_ID | Dependency_Type | Source_ID | Source_Domain | Function | Criticality | Evidence_Source | Evidence_Status | Evaluability_Impact | Fallback | Affected_Component | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DEP-PRE-004-RPRE-001 | `R-PRE-001` | `PARAMETER` | `P-PRE-004` | PARAMETER | Parámetro consumidor de la regla | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación directa documentada. |
| DEP-PRE-005-RPRE-002 | `R-PRE-002` | `PARAMETER` | `P-PRE-005` | PARAMETER | Parámetro consumidor de la regla | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación directa documentada. |
| DEP-MGE-001-RMGE-001 | `R-MGE-001` | `PARAMETER` | `P-MGE-001` | PARAMETER | Parámetro consumidor de margen | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación directa documentada. |
| DEP-MGE-002-RMGE-003 | `R-MGE-003` | `PARAMETER` | `P-MGE-002` | PARAMETER | Parámetro consumidor de margen objetivo | MEDIUM | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | INSUFFICIENT_DATA | NONE | NONE | Relación documentada. |
| DEP-MGE-003-RMGE-002 | `R-MGE-002` | `PARAMETER` | `P-MGE-003` | PARAMETER | Parámetro consumidor de tolerancia | MEDIUM | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | INSUFFICIENT_DATA | NONE | NONE | Relación documentada. |
| DEP-FIN-002-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-002` | PARAMETER | Parte del cálculo de capacidad financiera prevista | CRITICAL | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación documentada. |
| DEP-FIN-003-RFIN-002 | `R-FIN-002` | `PARAMETER` | `P-FIN-003` | PARAMETER | Parámetro consumidor de fondo de maniobra | CRITICAL | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación directa documentada. |
| DEP-FIN-004-RFIN-003 | `R-FIN-003` | `PARAMETER` | `P-FIN-004` | PARAMETER | Parámetro consumidor de riesgo financiero | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación documentada. |
| DEP-FIN-005-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-005` | PARAMETER | Parte del cálculo de capacidad financiera prevista | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación documentada. |
| DEP-FIN-006-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-006` | PARAMETER | Parte del cálculo de capacidad financiera prevista | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación documentada. |
| DEP-PAG-001-RPAG-002 | `R-PAG-002` | `PARAMETER` | `P-PAG-001` | PARAMETER | Plazo mínimo aceptable | HIGH | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación directa. |
| DEP-PAG-002-RPAG-001 | `R-PAG-001` | `PARAMETER` | `P-PAG-002` | PARAMETER | Plazo objetivo | HIGH | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación directa. |
| DEP-PAG-003-RPAG-001 | `R-PAG-001` | `DERIVED` | `P-PAG-003` | PARAMETER | Modulación del objetivo de pago | HIGH | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Naturaleza derivada documentada. |
| DEP-PAG-004-RPAG-001 | `R-PAG-001` | `CONTROL` | `P-PAG-004` | PARAMETER | Control de consideración del plazo | HIGH | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Control funcional. |
| DEP-PAG-004-RPAG-002 | `R-PAG-002` | `CONTROL` | `P-PAG-004` | PARAMETER | Control de consideración del plazo | HIGH | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Control funcional. |
| DEP-PAG-005-RPAG-001 | `R-PAG-001` | `DERIVED` | `P-PAG-005` | PARAMETER | Contexto económico de negociación | MEDIUM | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | INSUFFICIENT_DATA | NONE | NONE | Naturaleza derivada documentada. |
| DEP-PAG-005-RPAG-002 | `R-PAG-002` | `DERIVED` | `P-PAG-005` | PARAMETER | Contexto económico de negociación | MEDIUM | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | INSUFFICIENT_DATA | NONE | NONE | Naturaleza derivada documentada. |
| DEP-DAT-001-RDAT-001 | `R-DAT-001` | `PARAMETER` | `P-DAT-001` | PARAMETER | Parámetro consumidor de calidad de datos | HIGH | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | BLOCKED | NONE | NONE | Relación documentada. |
| DEP-HIS-002-RHIS-001 | `R-HIS-001` | `PARAMETER` | `P-DAT-002` | PARAMETER | Antigüedad máxima de referencia | MEDIUM | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` | CONFIRMED | INSUFFICIENT_DATA | NONE | NONE | Relación documentada. |
| DEP-HIS-006-RHIS-002 | `R-HIS-002` | `PARAMETER` | `P-PRE-006` | PARAMETER | Mínimo de operaciones comparables | MEDIUM | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` | CONFIRMED | INSUFFICIENT_DATA | NONE | NONE | Relación documentada. |

---

# 17. Relaciones expresamente no demostradas

Las siguientes relaciones no deben inferirse:

| Dependency_ID | Rule_ID | Dependency_Type | Source_ID | Evidence_Source | Evidence_Status | Reason |
|---|---|---|---|---|---|---|
| REJ-PRE-001 | `R-HIS-001` | `PARAMETER` | `P-PRE-003` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | REJECTED | `P-PRE-003` es criterio/metodología de comparación; no se ha demostrado como parámetro operativo de antigüedad. |
| REJ-DAT-001 | `R-HIS-002` | `PARAMETER` | `P-DAT-003` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | REJECTED | No existe evidencia de que `P-DAT-003` sea el parámetro del mínimo de operaciones históricas. |
| REJ-DER-001 | `R-HIS-002` | `DERIVED` | `P-PRE-003` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | REJECTED | No existe transformación documental que permita derivar el mínimo histórico desde `P-PRE-003`. |
| REJ-DER-002 | `R-HIS-002` | `DERIVED` | `P-DAT-003` | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | REJECTED | No existe transformación documental que permita derivar el mínimo histórico desde `P-DAT-003`. |

---

# 18. Cobertura inicial y pendientes

La cobertura inicial se limita a relaciones ya demostradas documentalmente.

Quedan pendientes de cruce, entre otros:

- dependencias `DATA` no identificadas individualmente;
- dependencias `EVIDENCE` específicas por regla;
- dependencias `COMPONENT` cuando no exista evidencia documental directa;
- impactos concretos de evaluabilidad ante ausencia de cada dependencia;
- relaciones adicionales de parámetros marcadas como pendientes en la matriz de parámetros.

Estos pendientes no constituyen una autorización para inferir dependencias. Son **gaps de evidencia/dependencia aún no resueltos**.

---

# 19. Criterios para confirmar una dependencia

Antes de marcar una relación como `CONFIRMED` deben responderse afirmativamente estas preguntas:

1. ¿Existe una `Rule_ID` real y vigente?
2. ¿Existe un `Source_ID` identificable?
3. ¿La relación está documentada por una autoridad válida?
4. ¿El tipo primario de dependencia es inequívoco?
5. ¿La función de la dependencia está demostrada?
6. ¿La criticidad se refiere a evaluabilidad y no a severidad?
7. ¿El impacto de ausencia está definido sin producir `Assessment`?
8. ¿El fallback, si existe, está autorizado externamente?
9. ¿No se está redefiniendo la fuente de autoridad?
10. ¿La relación puede reproducirse documentalmente?

Si alguna respuesta crítica es negativa, la relación no debe marcarse `CONFIRMED`.

---

# 20. Invariantes

La RDM debe preservar:

```text
I-01  Una dependencia tiene un único Dependency_Type primario.

I-02  CONFIRMED requiere evidencia documental suficiente.

I-03  PARTIAL y PENDING no pueden utilizarse como dependencias operativas confirmadas.

I-04  REJECTED y SUPERSEDED no pueden utilizarse como dependencias operativas vigentes.

I-05  Criticality ≠ Rule Severity.

I-06  Evaluability_Impact ≠ Assessment outcome.

I-07  Fallback ≠ nueva lógica de negocio.

I-08  Evidence Contract ≠ Rule Dependency Matrix.

I-09  Rule Dependency Matrix ≠ Rule definition.

I-10  Rule Dependency Matrix ≠ CRC.

I-11  La ausencia de una dependencia no puede transformarse directamente en FALSE.

I-12  No se confirma una dependencia por inferencia semántica.
```

---

# 21. Compatibilidad con C0

La RDM no modifica el contrato físico C0.

En particular, no altera:

```text
Evidence
→ DEMONSTRATED / GAP

EvidenceValidation
→ VALID / INVALID

Assessment
→ EVALUABLE / NOT_EVALUABLE
```

La RDM únicamente declara dependencias que deberán estar disponibles para que las reglas correspondientes puedan evaluarse.

---

# 22. Relación con Assessment

La RDM no genera `Assessment`.

La secuencia física permanece:

```text
Evidence
   ↓
EvidenceValidation
   ↓
Rule
   ↓
Assessment
```

La RDM aporta el mapa de dependencias que permite conocer qué necesita la `Rule`.

---

# 23. Relación con Trace

La RDM no sustituye `Trace`.

`Trace` conserva el contexto reproducible de la ejecución y los identificadores de evidencia correspondientes.

La RDM solo proporciona el mapa declarativo de dependencias.

---

# 24. Relación con F3

La trazabilidad F3 puede constituir evidencia de una dependencia.

Pero F3 no queda absorbido por la RDM.

La relación es:

```text
F3
→ demuestra relaciones

RDM
→ registra la dependencia demostrada
```

---

# 25. Estado del documento

**BORRADOR DEPURADO — PENDIENTE DE AUDITORÍA DE CIERRE**

Esta versión corrige las ambigüedades contractuales detectadas en la auditoría inicial, pero **no declara cerrada la cobertura de dependencias del MVP**.

El siguiente paso obligatorio es la **segunda auditoría formal de cierre** contra:

```text
Matriz_Autoridad_Documental
Matriz_Reglas_MVP
Matriz_Parametros_Reglas_MVP
Evidence_Contract
Especificacion_Reglas_Configuracion_Pagos_MVP
Especificacion_Reglas_Historico_MVP
Capa_resolucion_conflictos
modelos C0
Assessment Contract
Trace
```

Solo después de superar esa auditoría podrá determinarse si la RDM queda cerrada o requiere una nueva depuración.

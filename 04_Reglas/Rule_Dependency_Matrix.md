# MATRIZ CANÓNICA DE DEPENDENCIAS DE REGLAS

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.5  
**Estado:** CERRADO  
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

Las características adicionales de una relación se expresan mediante `Notes` o mediante una futura extensión contractual explícita, sin alterar el tipo primario.

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
| `Evaluability_Impact` | Sí | Impacto de la ausencia de la dependencia sobre la capacidad de evaluación, solo cuando esté documentalmente determinado. |
| `Fallback` | Sí | Tratamiento de contingencia autorizado, o `NONE`. Nunca contiene lógica de sustitución inventada. |
| `Affected_Component` | Sí | Componente afectado cuando exista evidencia de esa dependencia; en otro caso `NONE`. |
| `Notes` | Sí | Información explicativa o de trazabilidad que no crea nueva autoridad. |

La obligatoriedad del campo no autoriza a inferir su contenido. Cuando un aspecto no esté determinado por una fuente competente se utiliza el valor controlado `PENDING`.

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

Valores controlados:

```text
CRITICAL
HIGH
MEDIUM
LOW
PENDING
```

`CRITICAL`, `HIGH`, `MEDIUM` o `LOW` solo pueden utilizarse cuando la criticidad de la dependencia esté documentalmente determinada. En ausencia de esa determinación, el valor obligatorio es `PENDING`.

---

# 8. Evaluability_Impact

`Evaluability_Impact` describe el impacto de la ausencia de una dependencia sobre la capacidad de evaluación de la regla.

Valores controlados:

| Valor | Significado |
|---|---|
| `NO_IMPACT` | La ausencia no impide la evaluación, cuando así esté documentado. |
| `WARNING` | La ausencia permite continuar bajo un tratamiento explícitamente autorizado. |
| `INSUFFICIENT_DATA` | La ausencia deja insuficiente la información necesaria. |
| `BLOCKED` | La dependencia es necesaria y su ausencia impide continuar con la evaluación. |
| `PENDING` | El impacto de ausencia todavía no está documentalmente determinado. |

`NOT_EVALUABLE` **no es un valor producido por la RDM**. Es un resultado del proceso de evaluación y pertenece al contrato de `Assessment`.

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

La RDM no produce ni redefine el resultado `Assessment`.

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

```text
Regla menciona “stock”
        ≠
RDM puede inventar DATA → stock
```

El cruce `Rule × DATA` se construirá únicamente de forma demostrable. No se amplía en esta versión.

---

# 13. EVIDENCE

Una dependencia `EVIDENCE` identifica evidencia que una regla concreta necesita para sustentar su evaluación.

La RDM determina la relación:

```text
Rule → Evidence requirement
```

pero no redefine qué hace admisible o suficiente una evidencia. Eso corresponde a `Evidence_Contract.md`.

Las condiciones específicas de comparabilidad, temporalidad, cantidad u otras características pertenecen a la regla y/o a la especificación de dependencias correspondiente; no se convierten en criterios generales del Evidence Contract.

No se incorporan relaciones `EVIDENCE` en esta versión sin una fuente demostrable.

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

No se incorporan relaciones `COMPONENT` en esta versión sin una fuente demostrable.

---

# 15. CONTEXT

`CONTEXT` representa información contextual que puede intervenir en la interpretación de una evaluación, pero que no constituye por sí misma un criterio decisorio.

No puede utilizarse para introducir una regla implícita.

Cada registro conserva un único tipo primario.

---

# 16. Relaciones confirmadas actualmente

La cobertura de esta versión se limita deliberadamente a relaciones cuya **existencia** ya está documentada. La confirmación de la relación no implica que `Criticality` o `Evaluability_Impact` hayan sido determinados; cuando no exista autoridad documental suficiente ambos se mantienen como `PENDING`.

| Dependency_ID | Rule_ID | Dependency_Type | Source_ID | Source_Domain | Function | Criticality | Evidence_Source | Evidence_Status | Evaluability_Impact | Fallback | Affected_Component | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| DEP-PRE-004-RPRE-001 | `R-PRE-001` | `PARAMETER` | `P-PRE-004` | PARAMETER | Parámetro consumidor de la regla | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa documentada. |
| DEP-PRE-005-RPRE-002 | `R-PRE-002` | `PARAMETER` | `P-PRE-005` | PARAMETER | Parámetro consumidor de la regla | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa documentada. |
| DEP-STK-004-RSTK-002 | `R-STK-002` | `PARAMETER` | `P-STK-004` | PARAMETER | Umbral máximo de cobertura consumido por la condición de cobertura elevada | PENDING | `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa demostrada por R-STK-002 + M04. |
| DEP-STK-004-RSTK-003 | `R-STK-003` | `DERIVED` | `P-STK-004` | PARAMETER | Conversión de coverage_maximum a cantidad máxima cuando el máximo se gobierna por cobertura | PENDING | `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Transformación documentada por M04/M07. |
| DEP-STK-005-RSTK-003 | `R-STK-003` | `DERIVED` | `P-STK-005` | PARAMETER | Tolerancia incorporada al umbral cuantitativo de exceso | PENDING | `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Transformación documentada por M07. |
| DEP-MGE-001-RMGE-001 | `R-MGE-001` | `PARAMETER` | `P-MGE-001` | PARAMETER | Parámetro consumidor de margen | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa documentada. |
| DEP-MGE-002-RMGE-003 | `R-MGE-003` | `PARAMETER` | `P-MGE-002` | PARAMETER | Parámetro consumidor de margen objetivo | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-MGE-003-RMGE-002 | `R-MGE-002` | `PARAMETER` | `P-MGE-003` | PARAMETER | Parámetro consumidor de tolerancia | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-FIN-002-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-002` | PARAMETER | Parte del cálculo de capacidad financiera prevista | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-FIN-003-RFIN-002 | `R-FIN-002` | `PARAMETER` | `P-FIN-003` | PARAMETER | Parámetro consumidor de fondo de maniobra | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa documentada. |
| DEP-FIN-004-RFIN-003 | `R-FIN-003` | `PARAMETER` | `P-FIN-004` | PARAMETER | Parámetro consumidor de riesgo financiero | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-FIN-005-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-005` | PARAMETER | Parte del cálculo de capacidad financiera prevista | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-FIN-006-RFIN-001 | `R-FIN-001` | `PARAMETER` | `P-FIN-006` | PARAMETER | Parte del cálculo de capacidad financiera prevista | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-PAG-001-RPAG-002 | `R-PAG-002` | `PARAMETER` | `P-PAG-001` | PARAMETER | Plazo mínimo aceptable | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa. |
| DEP-PAG-002-RPAG-001 | `R-PAG-001` | `PARAMETER` | `P-PAG-002` | PARAMETER | Plazo objetivo | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación directa. |
| DEP-PAG-003-RPAG-001 | `R-PAG-001` | `DERIVED` | `P-PAG-003` | PARAMETER | Modulación del objetivo de pago | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Naturaleza derivada documentada. |
| DEP-PAG-004-RPAG-001 | `R-PAG-001` | `CONTROL` | `P-PAG-004` | PARAMETER | Control de consideración del plazo | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Control documentado. |
| DEP-PAG-004-RPAG-002 | `R-PAG-002` | `CONTROL` | `P-PAG-004` | PARAMETER | Control de consideración del plazo | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Control documentado. |
| DEP-PAG-005-RPAG-001 | `R-PAG-001` | `DERIVED` | `P-PAG-005` | PARAMETER | Contexto económico de negociación | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Naturaleza derivada documentada. |
| DEP-PAG-005-RPAG-002 | `R-PAG-002` | `DERIVED` | `P-PAG-005` | PARAMETER | Contexto económico de negociación | PENDING | `04_Reglas/Especificacion_Reglas_Configuracion_Pagos_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Naturaleza derivada documentada. |
| DEP-DAT-001-RDAT-001 | `R-DAT-001` | `PARAMETER` | `P-DAT-001` | PARAMETER | Parámetro consumidor de calidad de datos | PENDING | `02_Parametros/Matriz_Parametros_Reglas_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-HIS-002-RHIS-001 | `R-HIS-001` | `PARAMETER` | `P-DAT-002` | PARAMETER | Antigüedad máxima de referencia | PENDING | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-HIS-006-RHIS-002 | `R-HIS-002` | `PARAMETER` | `P-PRE-006` | PARAMETER | Mínimo de operaciones comparables | PENDING | `04_Reglas/Especificacion_Reglas_Historico_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Relación documentada. |
| DEP-ENT-BSQ-RENT-001 | `R-ENT-001` | `EVIDENCE` | `BaselineStockoutQualification` | STK / ENT METHODOLOGY | Timing de agotamiento cualificado desde escenario base sin la compra evaluada | PENDING | `04_Reglas/Especificacion_Reglas_Entrega_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Exige provenance de baseline y exclusión de la compra; no implica dependencia COMPONENT directa a STK. |
| DEP-ENT-DTE-RENT-001 | `R-ENT-001` | `EVIDENCE` | `PurchaseSpecificDeliveryTimingEvidence` | DELIVERY / SUPPLIER EVIDENCE ADAPTER | Fecha prevista de entrega aplicable específicamente a la propuesta evaluada | PENDING | `04_Reglas/Especificacion_Reglas_Entrega_MVP.md` | CONFIRMED | PENDING | NONE | NONE | Supplier DELIVERY_DATE es fuente opcional adaptada, no dependencia COMPONENT obligatoria. |

---

# 17. Relaciones expresamente no demostradas

Las siguientes relaciones no deben inferirse:

| Elemento | Relación no demostrada | Tratamiento |
|---|---|---|
| `P-PRE-003` | `P-PRE-003 → R-HIS-001` | `REJECTED` como consumidor directo; el consumidor demostrado es `P-DAT-002`. |
| `P-DAT-003` | `P-DAT-003 → R-HIS-002` | `REJECTED` como consumidor directo; el consumidor demostrado es `P-PRE-006`. |
| `P-DAT-003` | `P-DAT-003 → P-PRE-006` maestro → derivado | `REJECTED` por falta de transformación documentada. |
| `P-PRE-003` | `P-PRE-003 → P-DAT-002` maestro → derivado | `REJECTED` por falta de transformación documentada. |
| `P-STK-001` | consumidor directo `R-STK-001…004` | `REJECTED` como relación directa en la autoridad vigente; mantiene función metodológica M02. |
| `P-STK-002` | consumidor directo `R-STK-001…004` | `REJECTED` como relación directa; mantiene función metodológica M03. |
| `P-STK-003` | consumidor directo `R-STK-001…004` | `REJECTED` como relación directa; mantiene función metodológica M04. |
| `P-STK-006` | consumidor directo `R-STK-001…004` | `REJECTED` como relación directa; gobierna ventana histórica cuando exista valor vigente. |
| `P-PYE-001…006` | consumidor directo `R-STK-001…004` | `REJECTED` como relación directa en esta versión; sus funciones metodológicas no se convierten en condiciones de regla. |
| `P-PYE-005` | ventas históricas → demanda STK | `REJECTED` como transformación implícita; requiere política específica posterior si llegara a autorizarse. |
| `P-PYE-004` | consumidor directo `R-ENT-001` | `REJECTED` como relación directa; no autoriza derivación lead time → fecha de entrega. |
| `lead_time` | `lead_time → expected_delivery_date` dentro de ENT | `REJECTED` como transformación implícita; requiere autoridad externa específica. |
| `scenario_id` | `scenario_id → baseline` | `REJECTED` como semántica suficiente; baseline exige relation/provenance demostrada. |
| `Supplier` | dependencia COMPONENT obligatoria de `R-ENT-001` | `REJECTED` por falta de exclusividad: delivery evidence puede proceder de otra fuente autorizada. |

Estas determinaciones se apoyan en la documentación especializada correspondiente y no deben reabrirse por similitud semántica.

---

# 18. Cobertura inicial y pendientes

La cobertura se limita a relaciones cuya existencia está demostrada documentalmente.

Quedan pendientes de cruce, entre otros:

- dependencias `DATA` no identificadas individualmente;
- dependencias `EVIDENCE` específicas por reglas distintas de `R-ENT-001` cuando aún carezcan de fuente demostrable;
- dependencias `COMPONENT` cuando no exista evidencia documental directa;
- determinación documental de `Criticality` por dependencia;
- determinación documental de `Evaluability_Impact` por dependencia;
- tratamientos de contingencia específicos cuando una autoridad competente los defina;
- relaciones adicionales de parámetros fuera del cruce STK/PYE ya cerrado que sigan marcadas como pendientes en la matriz de parámetros.

El cruce individual `P-STK/P-PYE ↔ R-STK` deja de formar parte de los pendientes generales: queda resuelto por `04_Reglas/Especificacion_Reglas_STK_Parametros_MVP.md` y reconciliado en esta versión.

El cruce `R-ENT-001 ↔ evidencia temporal` deja de formar parte de los pendientes generales: queda demostrado por `04_Reglas/Especificacion_Reglas_Entrega_MVP.md` y se materializa mediante dos dependencias `EVIDENCE / CONFIRMED`. Permanecen `PENDING` la criticidad y el impacto de evaluabilidad por no existir autoridad suficiente para asignarlos.

Estos pendientes no autorizan inferencias. Representan **gaps de evidencia/dependencia aún no resueltos**.

---

# 19. Regla de evaluabilidad

Una regla solo puede considerarse evaluable cuando se cumplen las dependencias que su documentación declare críticas para esa evaluación.

La ausencia de una dependencia no autoriza a:

- asumir un valor;
- reutilizar otro parámetro sin evidencia;
- convertir ausencia de evidencia en resultado positivo;
- omitir silenciosamente la regla.

La RDM registra el impacto documentalmente determinado de la ausencia. El resultado de evaluación pertenece al contrato de `Assessment` y a la autoridad de la regla.

---

# 20. Regla de actualización

Cuando se confirme una nueva dependencia:

1. debe identificarse la fuente que la demuestra;
2. debe determinarse su tipo;
3. debe registrarse su estado;
4. debe determinarse su `Criticality` solo si existe autoridad documental suficiente;
5. debe determinarse su `Evaluability_Impact` solo si existe autoridad documental suficiente;
6. debe incorporarse a esta matriz;
7. deben actualizarse las vistas especializadas que correspondan.

La incorporación a esta matriz no permite modificar silenciosamente la fuente que tiene autoridad sobre el concepto dependiente.

---

# 21. No regresión

No se debe:

- eliminar una dependencia `CONFIRMED` sin documentar su sustitución;
- cambiar el tipo de una dependencia sin evidencia;
- convertir una relación `PENDING` en `CONFIRMED` sin fuente demostrable;
- asignar `Criticality` por extrapolación de la severidad de la regla;
- asignar `Evaluability_Impact` por extrapolación del resultado esperado;
- crear una segunda autoridad transversal de dependencias;
- utilizar una dependencia `REJECTED` como si estuviera vigente;
- modificar las condiciones de una regla desde esta matriz.

---

# 22. Estado

**Versión:** 1.5  
**Estado:** CERRADO  
**Ámbito:** Dependencias transversales de reglas EIOS  
**Autoridad:** `00_Gobierno/Matriz_Autoridad_Documental.md`

Esta versión conserva íntegramente la cobertura previa y amplía exclusivamente dos relaciones `EVIDENCE` demostradas para `R-ENT-001`, manteniendo `Criticality` y `Evaluability_Impact` en `PENDING` donde no existe autoridad suficiente. No amplía por inferencia la cobertura `DATA` ni `COMPONENT`.

La reconciliación STK mantiene:

- `P-STK-004 → R-STK-002` como relación directa;
- `P-STK-004 → R-STK-003` como relación derivada;
- `P-STK-005 → R-STK-003` como relación derivada;
- ausencia de consumidor directo demostrado para el resto de `P-STK/P-PYE` en las reglas STK vigentes;
- prohibición de utilizar `P-PYE-005` como transformación implícita ventas → demanda.

La reconciliación ENT confirma:

- `R-ENT-001 → BaselineStockoutQualification` como `EVIDENCE / CONFIRMED`;
- `R-ENT-001 → PurchaseSpecificDeliveryTimingEvidence` como `EVIDENCE / CONFIRMED`;
- ausencia de parámetro ENT demostrado;
- rechazo de `P-PYE-004` como consumidor directo de `R-ENT-001`;
- rechazo de la transformación implícita lead time → expected delivery date;
- ausencia de dependencia COMPONENT obligatoria a Supplier o STK por mera procedencia de datos.

### Dictamen de cierre

La auditoría documental confirma:

- conformidad con `00_Gobierno/Matriz_Autoridad_Documental.md`;
- coherencia con la Matriz de Parámetros y la Matriz de Reglas;
- compatibilidad con `04_Reglas/Evidence_Contract.md`;
- conformidad con `03_Arquitectura/Architecture_Blueprint.md`;
- compatibilidad con `01_Modelo/STK_Contract_Entry_Authority.md` y M01…M10;
- compatibilidad con `01_Modelo/Delivery_Stockout_Methodological_Closure_v0.3.md`;
- ausencia de redefinición de C0;
- mantenimiento de gaps no demostrados como `PENDING` o `REJECTED`, sin inferencias.

El cierre es **contractual y documental**. No implica completar dependencias `DATA`, `EVIDENCE` o `COMPONENT` de otras reglas que carezcan de evidencia demostrable, ni asignar `Criticality` o `Evaluability_Impact` por inferencia.

Los pendientes declarados constituyen deuda controlada de cobertura y no invalidan el contrato cerrado de la matriz.

**Estado de cierre: CERRADO.**

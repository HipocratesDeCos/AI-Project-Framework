# PLAN DE PRUEBAS MVP

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Fecha:** 20/08/2026

---

# 1. Propósito

Este documento define el marco inicial de pruebas del EIOS Vertical MVP.

Su finalidad es demostrar, mediante casos verificables, que el comportamiento del sistema es coherente con las capas funcionales ya definidas en `01_Modelo`, `02_Parametros`, `03_Arquitectura`, `04_Reglas` y `05_Motor`.

Este documento no define nuevas reglas de negocio ni modifica la autoridad de los documentos aprobados.

---

# 2. Principios de prueba

Las pruebas deberán:

1. derivarse de requisitos, reglas, parámetros o comportamientos documentados;
2. disponer de un resultado esperado verificable;
3. diferenciar decisión, bloqueo, advertencia e información insuficiente;
4. comprobar la trazabilidad de la decisión cuando corresponda;
5. comprobar la explicación de la decisión cuando corresponda;
6. evitar que una prueba introduzca una regla no documentada.

---

# 3. Estados de una prueba

| Estado | Significado |
|---|---|
| PENDIENTE | Caso definido pero todavía no ejecutado |
| APROBADA | Resultado obtenido conforme al esperado |
| FALLIDA | Resultado obtenido distinto al esperado |
| BLOQUEADA | No puede ejecutarse por una dependencia pendiente |
| NO APLICA | El caso no corresponde al alcance actual |

Una prueba en estado **FALLIDA** deberá generar una incidencia antes de modificar cualquier documento o componente. La incidencia deberá determinar si el origen está en la implementación, los datos, el propio caso de prueba o la documentación de referencia. Una prueba fallida no constituye por sí misma autorización para cambiar el diseño.

---

# 4. Identificación de pruebas

Cada caso utilizará un identificador único con el formato:

`T-[ÁREA]-[NÚMERO]`

Ejemplos:

- `T-DAT-001`
- `T-PAR-001`
- `T-RGL-001`
- `T-MOT-001`
- `T-TRZ-001`
- `T-REG-001`

---

# 5. Pruebas de datos y suficiencia de información

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-DAT-001 | Datos suficientes para evaluar una decisión | EIOS puede continuar con la evaluación | PENDIENTE |
| T-DAT-002 | Falta información crítica para evaluar | EIOS identifica la insuficiencia y no fuerza una recomendación favorable | PENDIENTE |
| T-DAT-003 | Información histórica insuficiente | EIOS refleja la limitación de evidencia según las reglas aplicables | PENDIENTE |
| T-DAT-004 | Datos cuya antigüedad supera el umbral aplicable | EIOS aplica el criterio de calidad correspondiente | PENDIENTE |
| T-DAT-005 | Datos con nivel de fiabilidad insuficiente | EIOS no debe presentar una recomendación como suficientemente sustentada cuando la evidencia requerida no lo permite | PENDIENTE |

**Nota:** `DAT-004` del catálogo de parámetros no constituye una capacidad configurable. La prueba verifica que los datos insuficientes no puedan convertirse por parametrización en una recomendación favorable.

---

# 6. Pruebas de parámetros

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-PAR-001 | Modificar un parámetro ordinario permitido | El nuevo valor queda aplicado según su alcance y vigencia | PENDIENTE |
| T-PAR-002 | Modificar un parámetro crítico sin autorización | El cambio es rechazado | PENDIENTE |
| T-PAR-003 | Modificar un parámetro crítico con autorización válida | El cambio se realiza y queda trazado | PENDIENTE |
| T-PAR-004 | Parámetro sin consumidor funcional | No se considera parámetro MVP confirmado | PENDIENTE |
| T-PAR-005 | Cambio de parámetro entre empresas | La configuración permanece aislada entre empresas | PENDIENTE |
| T-PAR-006 | Cambio de parámetro con vigencia definida | EIOS aplica el valor correspondiente al periodo de vigencia | PENDIENTE |

---

# 7. Pruebas de reglas

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-RGL-001 | Regla de precio aplicable | La regla se evalúa con los parámetros que documentalmente correspondan | PENDIENTE |
| T-RGL-002 | Regla de stock aplicable | La regla se evalúa con los parámetros que documentalmente correspondan | PENDIENTE |
| T-RGL-003 | Regla de margen aplicable | La regla se evalúa diferenciando margen porcentual y margen en euros cuando corresponda | PENDIENTE |
| T-RGL-004 | Regla financiera crítica activada | El resultado se ajusta a la resolución documentalmente establecida para la regla | PENDIENTE |
| T-RGL-005 | Regla crítica que se intenta desactivar mediante parámetro ordinario | La desactivación no está permitida | PENDIENTE |
| T-RGL-006 | Excepción no autorizada | EIOS no permite habilitarla mediante parametrización ordinaria | PENDIENTE |
| T-RGL-007 | Regla no crítica configurable | Solo puede configurarse cuando su autoridad documental lo permita | PENDIENTE |

---

# 8. Pruebas de resolución de conflictos

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-CRC-001 | Dos reglas generan señales diferentes | Se aplica la resolución de conflictos definida por la CRC | PENDIENTE |
| T-CRC-002 | Dos reglas entran en conflicto | Se aplica el mecanismo de resolución definido por la CRC, sin asumir que prioridad o criticidad sustituyan a la autoridad de resolución | PENDIENTE |
| T-CRC-003 | Prioridad modificada sin autoridad para alterar resolución | La prioridad no sustituye la autoridad de resolución | PENDIENTE |
| T-CRC-004 | Conflicto entre reglas con igual nivel | Se aplica el mecanismo de resolución documentado | PENDIENTE |

---

# 9. Pruebas del motor de decisión

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-MOT-001 | Evaluación normal con evidencia suficiente | El motor produce la salida correspondiente a las reglas aplicables | PENDIENTE |
| T-MOT-002 | Evaluación con condición de bloqueo | El motor refleja el bloqueo correspondiente | PENDIENTE |
| T-MOT-003 | Evaluación con información insuficiente | El motor evita una recomendación favorable no sustentada | PENDIENTE |
| T-MOT-004 | Variación de un parámetro permitido | El resultado cambia conforme a la regla que consume dicho parámetro | PENDIENTE |
| T-MOT-005 | Parámetro sin consumidor | El cambio no debe producir un efecto de decisión no documentado | PENDIENTE |

---

# 10. Pruebas de trazabilidad

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-TRZ-001 | Cambio de parámetro | Se registra valor anterior, nuevo valor, fecha, usuario, motivo, empresa, vigencia y estado cuando corresponda | PENDIENTE |
| T-TRZ-002 | Decisión generada por el motor | Puede identificarse la evidencia y las reglas relevantes según el alcance definido | PENDIENTE |
| T-TRZ-003 | Modificación de parámetro crítico | Existe trazabilidad reforzada y control de autorización | PENDIENTE |

---

# 11. Pruebas de explicabilidad

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-EXP-001 | Decisión con evidencia suficiente | La salida permite identificar el motivo principal de la decisión | PENDIENTE |
| T-EXP-002 | Decisión bloqueada | La salida identifica la condición que provoca el bloqueo | PENDIENTE |
| T-EXP-003 | Información insuficiente | La salida identifica la insuficiencia de información | PENDIENTE |
| T-EXP-004 | Cambio de parámetro con impacto en decisión | Puede explicarse qué parámetro intervino cuando corresponda | PENDIENTE |

---

# 12. Matriz de trazabilidad Regla → Prueba

Esta matriz se utiliza como estructura de trazabilidad y **no implica que las relaciones estén todavía confirmadas**. Solo podrán completarse relaciones concretas cuando estén documentalmente demostradas en `04_Reglas` y `02_Parametros`.

| Regla / familia | Parámetro relacionado | Caso de prueba | Resultado esperado | Estado |
|---|---|---|---|---|
| Precio | Pendiente de cruce documental | T-RGL-001 | Evaluación conforme a regla aprobada | PENDIENTE |
| Stock | Pendiente de cruce documental | T-RGL-002 | Evaluación conforme a regla aprobada | PENDIENTE |
| Margen | Pendiente de cruce documental | T-RGL-003 | Evaluación conforme a regla aprobada | PENDIENTE |
| Finanzas | Pendiente de cruce documental | T-RGL-004 | Aplicación conforme a regla y resolución aprobadas | PENDIENTE |
| Conflictos | CRC | T-CRC-* | Resolución conforme a CRC | PENDIENTE |

---

# 13. Pruebas de no regresión

Las pruebas de no regresión verifican que una modificación controlada no altere comportamientos que no forman parte del cambio.

| ID | Caso | Resultado esperado | Estado |
|---|---|---|---|
| T-REG-001 | Modificación de un parámetro | Las reglas no afectadas por dicho parámetro mantienen su comportamiento | PENDIENTE |
| T-REG-002 | Modificación de una regla | Las reglas no relacionadas mantienen su comportamiento | PENDIENTE |
| T-REG-003 | Modificación del motor | Las salvaguardas y restricciones aprobadas permanecen intactas | PENDIENTE |
| T-REG-004 | Modificación de configuración de empresa A | La configuración y comportamiento de empresa B permanecen aislados | PENDIENTE |
| T-REG-005 | Cambio de parámetro crítico autorizado | Los controles y trazabilidad exigidos permanecen activos | PENDIENTE |

---

# 14. Criterios de aceptación MVP

Una prueba funcional podrá considerarse aprobada cuando:

- el escenario ejecutado coincide con el caso definido;
- el resultado obtenido coincide con el resultado esperado;
- no se haya introducido una regla no documentada para obtener el resultado;
- los bloqueos se comporten conforme a la autoridad aplicable;
- los casos de información insuficiente no produzcan recomendaciones favorables no sustentadas;
- los cambios de parámetros críticos respeten los controles definidos;
- la trazabilidad requerida esté disponible.

---

# 15. Dependencias

La ejecución completa de este Plan requiere que las capas de implementación necesarias estén disponibles.

En particular, `06_SQL` está actualmente reservada para la futura implementación y no contiene todavía artefactos SQL del MVP. Por ello, los casos de ejecución física permanecen pendientes.

Este documento define **qué debe comprobarse**, no cómo construir la infraestructura técnica para hacerlo.

---

# 16. Reglas de gobierno del Plan de Pruebas

1. Una prueba no puede modificar una regla aprobada para conseguir un resultado esperado.
2. Un resultado esperado debe poder justificarse mediante documentación EIOS aprobada o mediante una decisión posterior formalmente aprobada.
3. Los casos que requieran una regla, parámetro o capacidad todavía no aprobada deberán permanecer `PENDIENTE`.
4. Las pruebas no sustituyen a la autoridad documental de las capas anteriores.
5. Cualquier contradicción detectada durante las pruebas deberá registrarse como incidencia antes de modificar el diseño.
6. Una prueba `FALLIDA` deberá generar una incidencia y su resolución deberá identificar el origen antes de plantear cualquier modificación.

---

# 17. Estado documental

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP

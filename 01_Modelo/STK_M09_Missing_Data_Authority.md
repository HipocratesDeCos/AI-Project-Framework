# EIOS — STK-M09 · Autoridad metodológica de ausencia de datos

**Versión:** 1.0
**Estado:** APROBADO — STK-M09 CERRADO
**Fecha de decisión:** 11/09/2026
**Autoridad:** decisión humana expresa incorporada al gobierno metodológico STK

## 1. Decisión autorizada

STK-M09 representa la imposibilidad de determinar de forma suficientemente evidenciada uno o varios datos necesarios para evaluar correctamente la situación de stock de un artículo.

La ausencia de datos no equivale a cero, inexistencia, normalidad ni ausencia de riesgo. Cuando un dato obligatorio no esté disponible, no sea verificable, esté desactualizado o carezca de evidencia suficiente, EIOS conserva explícitamente dicha incertidumbre.

## 2. Estados mínimos

- `UNKNOWN`: el valor no puede determinarse.
- `NOT_EVIDENCED`: existe un valor declarado, pero carece de evidencia suficiente.
- `NOT_APPLICABLE`: el dato no resulta aplicable al caso evaluado.
- `CONFLICTING_DATA`: existen fuentes válidas materialmente contradictorias que impiden determinar un valor único.

`NOT_APPLICABLE` exige evidencia de que el dato no aplica. No sustituye a un valor ausente, no verificable o contradictorio.

## 3. Prohibición de sustitución implícita

EIOS no sustituye automáticamente datos ausentes por cero, medias históricas, valores anteriores, estimaciones ni valores por defecto.

Una imputación solo es admisible cuando una política empresarial específica la autoriza expresamente y dicha política está documentada, versionada y es trazable. El valor imputado debe identificarse como tal y conservar la referencia de la política aplicada; nunca se presenta como observación original.

## 4. Propagación a STK-M01…M08

Cuando la ausencia afecte a una variable necesaria para STK-M01…M08, el módulo afectado propaga el estado de incertidumbre y evita emitir como cierta una conclusión que dependa del dato ausente.

Esta autoridad no declara por inferencia nuevas criticidades ni tratamientos parciales. La necesidad de una variable y el impacto concreto de su ausencia proceden de la autoridad cerrada del módulo o regla afectada. Cuando dicho impacto no esté documentalmente determinado, permanece `PENDING` conforme a la matriz de dependencias.

Una salida conocida e independiente puede conservarse, pero no convierte en evaluable ni completa una conclusión que dependa del dato ausente.

## 5. Registro y trazabilidad

Siempre que sea posible, STK-M09 identifica y conserva:

- el dato ausente o insuficientemente evidenciado;
- la fuente esperada;
- la fecha de referencia;
- la causa conocida de la ausencia;
- los módulos afectados;
- el estado aplicable;
- la evidencia disponible;
- la evaluación afectada y su versión.

La ausencia puede generar una alerta de calidad o insuficiencia de evidencia. La alerta describe la limitación; no completa el dato ni resuelve la evaluación.

## 6. Reevaluación y vigencia

Una evaluación afectada puede actualizarse cuando el dato requerido sea incorporado y validado. EIOS conserva la trazabilidad entre la evaluación anterior y la nueva versión, incluyendo la evidencia incorporada, la fecha de reevaluación y el cambio de estado.

La nueva evaluación no reescribe retroactivamente la anterior. Cada versión mantiene su fecha de referencia, entradas, evidencia y resultado.

## 7. Autoridad decisional

STK-M09 no constituye por sí mismo una decisión de compra, reposición, exceso, rotura de stock ni otra acción empresarial automática.

La ausencia o insuficiencia de evidencia impide presentar como cierta la conclusión dependiente. La autoridad decisional final permanece en la persona autorizada.

## 8. Continuidad

`STK-M01…M09` quedan cerrados. `STK-M10` permanece pendiente y continúa bloqueando el contrato técnico y la implementación cuantitativa STK.

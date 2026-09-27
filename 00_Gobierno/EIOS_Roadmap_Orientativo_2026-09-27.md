# EIOS — Roadmap orientativo · 27/09/2026

**Base de lectura:** `main @ d5accda522ca804ebf0892d395387bb013d3d616` (PR #433). **Naturaleza:** mapa de trabajo y comunicación; no modifica contratos, reglas, parámetros, autoridad documental ni criterios de admisión. Los hitos posteriores se revisan cuando exista evidencia nueva.

## 1. Meta del proyecto

EIOS es un sistema de apoyo a decisiones de compra y negociación adaptable a empresas distintas. Debe ayudar a explicar si una compra es viable, qué información falta, qué alternativas existen y qué podría negociarse. La decisión empresarial final corresponde a una persona autorizada. El vertical de ventas queda en espera; el foco actual es compras.

## 2. Dónde estamos

| Frente | Estado comprobado | Qué significa para el usuario |
|---|---|---|
| Gobierno y arquitectura | Marco Core + Vertical, límites, contratos y baselines documentados. | Existe una referencia para mantener coherencia y trazabilidad; no equivale a un producto listo para una empresa. |
| Motor y capacidades | Hay código y pruebas para la cadena central de evidencia, QTG, reglas/C0, escenarios, Decision Twin, negociación, O1 y otras capacidades especializadas. | Las capacidades pueden ensayarse bajo sus contratos; su mera existencia no prueba utilidad empresarial con datos reales. |
| Demostración sintética | Casos ficticios 001 y 002, observaciones JSON y paquete comparativo HTML reproducible. | Se puede recorrer una demostración de solo lectura y verificarla repitiendo los casos. Ningún caso autoriza comprar. |
| Presentación para lectura | Resúmenes visibles, conclusiones diferenciadas, límites y trazas desplegables. | El recorrido existe; la comprensión y comodidad visual en usuarios reales todavía necesitan observación. |
| Preparación operacional | Intake documental y vínculo QTG↔O1 implementados; guía y hoja vacía de referencias disponibles. | Se puede preparar la recogida del primer expediente; todavía no hay un E2E operacional positivo. |

**Frontera vigente:** las dos empresas de demostración permanecen `SYNTHETIC`, con `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, efecto `NO_OPERATIONAL_EFFECT` y `decision_authority=false`. No se promocionan cambiando etiquetas.

## 3. Camino propuesto

| Hito | Trabajo concreto | Criterio de salida | Dependencia |
|---|---|---|---|
| **A · Cerrar la lectura de la demostración** | Observar cómo un CEO o responsable de compras entiende comparación, aptitud de entrada, ejecución parcial, fiabilidad y límites. Registrar página y frase cuando haya confusión; corregir solo hallazgos verificables. | El lector localiza la conclusión antes de la traza y explica por qué `APTO` no autoriza comprar ni acredita fiabilidad. | Lectura humana del paquete actual. No requiere expediente real. |
| **B · Preparar la primera colaboración empresarial** | Elegir una operación y fecha de corte, inventariar las 24 claves canónicas y reunir versiones, soportes y responsables mediante el intake vigente. Separar referencias de contenido y de autoridad. | Material recibido y revisable, con faltantes y contradicciones visibles. `REQUIRED_SET_COMPLETE` por sí solo no cierra el hito. | Una empresa participante y documentos auténticos aportados por ella. No se fabrican desde las fixtures. |
| **C · Piloto supervisado** | Aplicar admisión al expediente presentado; solo si procede, ejecutar QTG operacional, consumo operacional, binding QTG↔O1 y O1. Registrar revisiones humanas y resultados sin conceder autoridad automática. | Resultado del piloto documentado: E2E positivo sustentado y trazable sobre material `PRESENTED_OPERATIONAL` admitido, o bloqueo explicado y nueva iteración si faltan condiciones. | Hito B, admisión y actos de mandato/revisión efectivos. |
| **D · Convertir la prueba en experiencia de producto** | Priorizar con los hallazgos del piloto la interfaz de trabajo, la configuración por empresa, el manejo de documentos y los controles de operación. Reconciliar los casos funcionales del Plan de Pruebas MVP con evidencia ejecutada. | Flujo usable y verificable para el alcance acordado con la primera empresa, con límites, roles y mantenimiento definidos. | Aprendizaje del hito C y decisiones de alcance; no se presupone que el HTML de demostración sea la interfaz final. |
| **E · Extensión controlada** | Repetir con otras operaciones y empresas, validar portabilidad, adaptar conectores de datos y ampliar dominios o verticales solo cuando el MVP de compras lo justifique. | Resultados comparables entre empresas sin mezclar datos, autoridad ni configuración. | Hito D y validaciones empresariales adicionales. |

El orden indica dependencias, **no fechas prometidas**. Los hitos A y la preparación técnica de B pueden avanzar en paralelo. El inicio de C depende de material y actos empresariales externos; por ello no existe hoy una fecha fiable para el primer piloto real ni para un lanzamiento comercial.

## 4. Próxima decisión práctica

La siguiente acción inmediata es una lectura guiada del paquete comparativo por una persona objetivo, anotando qué conclusión no se comprende y dónde. Mientras tanto, se pueden pulir guías y comprobaciones sintéticas sin abrir la ruta operacional. Cuando una empresa desee participar, la guía `08_Implementacion/First_Company_Intake_Guide_v0.1.md` ofrece la entrada al hito B.

## 5. Fuentes y límites de esta lectura

- `00_Gobierno/Project_Charter.md` y `00_Gobierno/Project_Context.md`: propósito, alcance y autoridad del decisor.
- `03_Arquitectura/Framework_Map.md`: mapa de fuentes especializadas, no inventario de implementación completa.
- `07_Pruebas/Real_Pilot_Readiness_Consolidated_Audit_v0.1.md` (23/09): corte histórico; su antiguo pendiente de software QTG↔O1 fue resuelto posteriormente.
- `07_Pruebas/Projection_Quality_O1_Binding_Materialization_Audit_v0.1.md` y `07_Pruebas/Real_Pilot_Readiness_Reconciliation_2026_09_27.md`: estado posterior del binding y bloqueo del E2E real.
- `07_Pruebas/Reference_Comparison_Usability_Review_2026_09_27.md`: auditoría estructural favorable, sin prueba de lectura humana.
- `07_Pruebas/Plan_Pruebas_MVP.md`: plan de casos oficiales; las pruebas automáticas existentes no convierten automáticamente todos sus casos `PENDIENTE` en aprobados.

Este roadmap describe **avance técnico, evidencia disponible y dependencias**. No es una declaración de porcentaje global de finalización ni de preparación comercial.

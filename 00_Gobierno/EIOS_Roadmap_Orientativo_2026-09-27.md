# EIOS — Roadmap de desarrollo y validación · 27/09/2026

**Base de lectura:** `main @ aff7ccfd691cef03a2aa146adb89b80d16dd00d0` (PR #434). **Naturaleza:** mapa de trabajo y comunicación; no modifica contratos, reglas, parámetros, autoridad documental ni criterios de admisión. Los hitos posteriores se revisan cuando exista evidencia nueva.

> **Diagnóstico:** EIOS puede demostrar un recorrido completo con dos empresas ficticias y verificar exactamente sus resultados. Aún no ha demostrado una decisión supervisada sobre material de una empresa real ni una aplicación empresarial lista para uso cotidiano.

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

### Inventario más preciso de avances

| Área | Evidencia disponible | Límite pendiente |
|---|---|---|
| Datos y confianza | Decision Input Package, cadena documental financiera, productor/recibo/consumidor QTG sintético y operacional, intake y preflight de admisión. | Una referencia no acredita contenido, origen o revisión; falta el primer expediente empresarial admitido. |
| Análisis y decisión | Código Python y pruebas para PRICE, TCO, finanzas, stock, proveedor, reglas/C0/CRC, viabilidad, escenarios, Decision Twin, negociación, Ladder y O1 según el alcance de cada contrato. | La presencia de módulos no demuestra que todos se hayan ejercitado juntos con datos reales ni cierra automáticamente el Plan de Pruebas MVP. |
| Procedencia y control | Taxonomía de casos, límites de ejecución, binding causal QTG↔O1 implementado y Shadow Mode posterior a O1. | Falta un E2E operacional positivo y una decisión humana observada. El informe del 23/09 que aún llamaba pendiente al binding es un corte histórico superado. |
| Presentación | Contratos UI, componentes de presentación locales y HTML de solo lectura para las dos empresas ficticias. | El HTML no es una aplicación desplegada con usuarios, permisos, entrada documental y soporte. No hay prueba observacional de comprensión íntegra con lectores objetivo. |

**Cinco niveles de evidencia que no se deben confundir:** (1) contrato diseñado; (2) código y pruebas de su alcance; (3) demostración con datos ficticios; (4) piloto con material y actos humanos reales; (5) producto utilizable de forma repetida. Una CI satisfactoria confirma únicamente los controles ejecutados en ella.

## 3. Camino propuesto

| Hito | Trabajo concreto | Criterio de salida | Dependencia |
|---|---|---|---|
| **H0 · Base técnica gobernada — alcanzado dentro de sus contratos** | Mantener arquitectura Core + Vertical, autoridad documental, motor, salvaguardas y trazas. | Cada cambio nuevo se deriva de una fuente especializada; los cierres conservan su alcance. | Ya disponible; se reaudita al ampliar alcance. |
| **H1 · Demostración sintética — alcanzado** | Ejecutar casos ficticios 001/002 y producir terminales, observaciones, revisión para comprador y comparación. | Paquete completo verificable por repetición exacta, inventario y CI; ruta operacional prohibida. | H0. No implica piloto real. |
| **H2 · Comprensión de la demostración — en curso** | Observar cómo un CEO o responsable de compras entiende comparación, aptitud de entrada, ejecución parcial, fiabilidad y límites. Registrar página y frase cuando haya confusión; corregir hallazgos concretos. | El lector localiza la conclusión antes de la traza y explica por qué `APTO` no autoriza comprar ni acredita fiabilidad. Una auditoría estructural no sustituye esta observación. | Lectores objetivo; no requiere expediente real. |
| **H3 · Preparación de incorporación — técnica disponible, uso real pendiente** | Preparar operación y fecha de corte, guía de entrega, custodia de versiones y hoja de 24 claves canónicas. Separar inventario, contenido, admisión y mandato. | Empresa participante y material realmente recibido, con faltantes visibles. `REQUIRED_SET_COMPLETE` no acredita suficiencia. | Empresa que decida colaborar; puede prepararse en paralelo a H2. |
| **H4 · Primer expediente y admisión — bloqueado por material** | Examinar compra/contexto, pedidos, cuotas, tesorería, flujos, criterios, soportes y actos de revisión conforme a `PROJECTION_ONLY`. | Expediente `PRESENTED_OPERATIONAL` admisible según su contrato, o rechazo documentado con faltantes y contradicciones. | H3 y personas competentes para los actos requeridos. |
| **H5 · E2E operacional supervisado — pendiente de H4** | Ejecutar productor/consumidor QTG operacional, binding QTG↔O1 y O1 sobre el expediente admitido. | Resultado terminal reproducible, trazable y auditado; sin autoridad automática de compra. Si falla un gate, no se fuerza un positivo. | H4. |
| **H6 · Decisión humana observada — pendiente de H5** | Registrar la decisión posterior del responsable y contrastarla con el resultado en Shadow Mode. | Coincidencias, divergencias y límites explicados sin convertir el resultado técnico en orden empresarial. | H5 y acto humano efectivo. |
| **H7 · MVP utilizable en una empresa — alcance por decidir** | Definir con lo aprendido la interfaz de trabajo, entrada documental, configuración autorizada, roles, errores, trazas, operación y soporte; reconciliar pruebas oficiales con evidencia ejecutada. | Usuarios aceptan un flujo repetible en el alcance acordado, con controles de empresa/rol y mantenimiento comprobados. | H2 y aprendizaje de H4–H6; el HTML actual no adquiere este estado automáticamente. |
| **H8 · Portabilidad y extensión — posterior** | Probar otra operación/empresa, fuentes y conectores, aislamiento de datos/autoridad/configuración y eventuales nuevos dominios. | El flujo se repite sin contaminación entre empresas y con cambios gobernados. | H7 y decisión de alcance específica; ventas continúa en espera. |

**Objetivo de calendario adoptado:** realizar el primer piloto real y un **lanzamiento comercial inicial de alcance controlado antes del 31/10/2026**. Es un objetivo exigente, no una certificación anticipada: H4–H6 requieren una empresa, un expediente admisible y actos humanos efectivos. El lanzamiento inicial significa presentar y ofrecer un servicio/piloto asistido con alcance, límites y soporte explícitos; no equivale a declarar terminado H7 para uso autónomo general ni a abrir H8. H2 y la preparación técnica de H3 avanzan en paralelo.

## 4. Trabajo próximo, ordenado por valor y dependencia

| Prioridad | Unidad concreta | Evidencia esperada | Participación necesaria |
|---|---|---|---|
| **P0 · Empresa piloto y operación** | Identificar una empresa dispuesta a colaborar, una compra concreta, fecha de corte, persona responsable y canal autorizado de entrega. No incorporar documentos sensibles al repositorio público. | Participante y operación acordados; se puede iniciar la recogida real. | Promotor del proyecto y empresa; es la dependencia decisiva del objetivo de octubre. |
| **P1 · Lectura guiada** | Abrir primero `comparison.html`, luego las revisiones 001/002. Registrar dónde se confunden «apta», «completada», «favorable» y «no determinable». Comprobar pantalla normal y estrecha. | Observaciones con página, sección, frase y lectura errónea; corrección focalizada y nueva verificación del paquete. | Uno o varios lectores con perfil CEO/Compras; el equipo ejecuta la corrección. |
| **P1 · Coherencia de resultados visibles** | Contrastar conclusiones y límites de los HTML con los JSON validados: QTG, precio, TCO, proveedor, C0, escenarios y negociación. | Matriz de afirmación visible → campo/observación → límite. No alterar resultados para acomodar la presentación. | Equipo técnico; no precisa una empresa real. |
| **P1 · Entrada de primera empresa** | Ensayar la hoja vacía y concretar qué referencias, versiones y responsables se solicitarían para esa compra. | Guía de recogida revisable y separación explícita entre referencia, contenido, admisión y autoridad. | Equipo técnico ahora; empresa y revisores al iniciar H3/H4. |
| **P2 · Plan de Pruebas MVP** | Comparar los casos oficiales marcados `PENDIENTE` con pruebas ejecutables reales, sin equiparar cobertura parcial a aprobación. | Matriz caso → evidencia → estado justificado; pendientes preservados donde no exista demostración. | Equipo técnico y fuente documental competente. |

No se propone fabricar una fixture `PRESENTED_OPERATIONAL`, abrir una nueva capa funcional por numeración o convertir la demo HTML en producto por cambio de etiqueta.

## 5. Plan de octubre de 2026 y decisiones de paso

**Supuesto de ejecución:** una persona técnica disponible unas 20–30 horas semanales, decisiones rápidas, una empresa colaboradora accesible al comienzo de octubre y capacidad de revisar documentos de forma segura fuera del repositorio público. El trabajo técnico y la captación empresarial ocurren en paralelo. Estas fechas son **objetivos con gates**, revisables cada semana; no convierten material ausente en admisible.

| Semana objetivo | Entrega y responsable principal | Decisión al cierre |
|---|---|---|
| **28/09–04/10** | Promotor: identificar empresa, operación, responsable y canal autorizado. Equipo: lectura guiada H2, preparar hoja de intake, instrucciones de entrega y alcance de oferta asistida. | **04/10:** confirmar participante y compra. Si no existen, el piloto real de octubre entra en riesgo alto; mantener la demostración y buscar otra empresa, sin cambiar etiquetas. |
| **05/10–11/10** | Empresa: entregar versiones y soportes disponibles; revisor competente: identificar actos de revisión requeridos. Equipo: inventariar referencias, faltantes, discrepancias y corte documental. | **11/10:** determinar si hay expediente que pueda pasar a preflight o lista concreta de material faltante con responsables. |
| **12/10–18/10** | Equipo y revisores: ejecutar preflight de admisión sin operación, resolver discrepancias con fuentes auténticas, preparar ejecución supervisada y comprobar trazas. | **18/10:** admisión según contrato o bloqueo motivado. No ejecutar QTG operacional con material sintético o insuficiente. |
| **19/10–25/10** | Si H4 pasó: QTG operacional → binding QTG↔O1 → O1; auditoría del terminal; decisión humana posterior y Shadow Mode cuando proceda. | **25/10:** piloto real documentado y límites conocidos, o incidente/bloqueo registrado. Un resultado negativo también informa el producto, pero no cuenta como E2E positivo. |
| **26/10–31/10** | Preparar la oferta comercial inicial controlada: público objetivo, alcance exacto, forma de prestación asistida, demostración separada del piloto, condiciones de uso, soporte y hechos que sí pueden mostrarse. | **31/10:** lanzamiento solo si la descripción comercial es fiel a la evidencia y el servicio ofrecido puede prestarse con seguridad. H7 autónomo queda pendiente si aún no se validó. |

**Camino crítico:** empresa y operación → material auténtico → admisión → ejecución supervisada → revisión humana → oferta verificable. Si el expediente no supera la admisión, se puede presentar la demostración sintética y captar interés comercial, pero **no anunciar un piloto operacional realizado**. Si H5 no se completa, la oferta debe describir su alcance real sin atribuirle ese resultado.

**Esfuerzo orientativo interno:** H2 y preparación H3 pueden consumir unas 1–3 y 2–5 semanas de trabajo, parcialmente solapadas. La disponibilidad documental y humana de H4–H6 domina el calendario; el seguimiento semanal determina si el objetivo de octubre sigue siendo alcanzable. El producto autónomo H7 y la expansión H8 se planifican después de los hallazgos del piloto.

## 6. Riesgos que pueden alterar la ruta

| Riesgo | Señal de alerta | Respuesta |
|---|---|---|
| No hay empresa o expediente admisible. | H3 sin colaborador o H4 con faltantes. | Mantener H4–H6 bloqueados y avanzar solo trabajo no operacional. |
| El lector interpreta `APTO` o «favorable» como compra aprobada. | Respuesta equivocada en lectura guiada. | Ajustar la explicación, volver a observarla y conservar estados técnicos. |
| Un inventario de referencias se presenta como prueba de autenticidad. | Hoja completa sin contraste del material y mandato. | Separar manifest, preflight y actos humanos; rechazar atajos. |
| Se confunde amplitud de módulos con cobertura oficial. | Plan MVP aún `PENDIENTE` frente a CI verde. | Vincular prueba con caso y alcance antes de cambiar estado. |
| La primera empresa no encaja en las fixtures. | Datos, flujo o controles diferentes de 001/002. | Registrar diferencia, resolver autoridad y priorizar producto según evidencia. |

## 7. Fuentes y límites de esta lectura

- `00_Gobierno/Project_Charter.md` y `00_Gobierno/Project_Context.md`: propósito, alcance y autoridad del decisor.
- `03_Arquitectura/Framework_Map.md`: mapa de fuentes especializadas, no inventario de implementación completa.
- `07_Pruebas/Real_Pilot_Readiness_Consolidated_Audit_v0.1.md` (23/09): corte histórico; su antiguo pendiente de software QTG↔O1 fue resuelto posteriormente.
- `07_Pruebas/Projection_Quality_O1_Binding_Materialization_Audit_v0.1.md` y `07_Pruebas/Real_Pilot_Readiness_Reconciliation_2026_09_27.md`: estado posterior del binding y bloqueo del E2E real.
- `07_Pruebas/Reference_Comparison_Usability_Review_2026_09_27.md`: auditoría estructural favorable, sin prueba de lectura humana.
- `07_Pruebas/Plan_Pruebas_MVP.md`: plan de casos oficiales; las pruebas automáticas existentes no convierten automáticamente todos sus casos `PENDIENTE` en aprobados.
- `03_App/UI_Implementation_Contract_Closure_v0.1.md`: contrato de UI cerrado dentro de su alcance; no equivale a un despliegue empresarial.

**Regla de actualización:** cambiar el estado de un hito solo con un entregable, su auditoría y el gate realmente satisfecho. Este roadmap describe **avance técnico, evidencia disponible y dependencias**. No es una declaración de porcentaje global de finalización ni de preparación comercial.

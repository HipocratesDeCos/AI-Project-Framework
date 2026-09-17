# EIOS — QTG-DIP-CONTROL-01 — Coverage Design and Audit
Fecha: 17/09/2026
Baseline operativo: main @ b41b89dd81f5d2d61500a0d4d70e054b2efe841c.
Estado: análisis de cobertura auditado; diseño del productor de resultado global NO CERRADO.
Autoridad: Quality_Trust_Implementation_Contract.md v0.4; contrato DIP-AGG-01 v0.1.
Este registro no añade reglas, estados de ejecución ni un sistema de evidencia.

## 1. DISEÑAR
Objetivo: determinar los controles que pueden producirse desde el DIP seleccionado, y la autoridad todavía necesaria para transformar hallazgos en QualityCheck aplicables y en un resultado QTG.
El paquete físico existe: PR #158, CI #826/#827 SUCCESS. Se conserva el cierre de su composición/coherencia/reproducibilidad.
El productor futuro debe consumir material verificable del paquete y conservar su fingerprint, compra completa y los cinco campos DecisionContext. Una coincidencia de IDs o un fingerprint aislado no acredita origen.

## 2. Cobertura contrastada
| Control QTG v0.4 §5 | Material físico observable | Límite de la comprobación | Determinación pendiente |
|---|---|---|---|
| Existencia | purchase/context; snapshot opcional; IDs disponibles/ausentes; evidencia presentada | Presencia o ausencia respecto de selección explícita | Qué piezas necesita el uso previsto |
| Integridad | Modelos revalidados; claves canónicas; captura profunda | Integridad del subconjunto capturado | Completitud empresarial y captura coordinada entre fuentes |
| Validez | Validadores de tipos/modelos y vigencia de configuración | Validez estructural; no admisibilidad universal | Criterios adicionales específicos del consumidor |
| Consistencia interna | Compra/contexto; snapshot/empresa/snapshot ID; partición de parámetros | Vínculos técnicos declarados en DIP | Consistencia económica/comercial cuando corresponda |
| Consistencia entre fuentes | Referencias conservadas y metadatos disponibles | Referencias no son prueba de acuerdo entre fuentes | Productor y criterio autorizado de comparación/resolución |
| Temporalidad | operation_date, captured_at, as_of_date, effective_at y vigencias | Fechas y vigencia técnica observables; no frescura universal | Ventanas y fronteras aplicables al uso concreto |
| Semántica | Tipos y unidades declarados en contratos existentes | No convierte unidades/monedas ni determina comparabilidad | Semántica especializada necesaria para cada uso |
| Trazabilidad | Fingerprint, identidad contextual, referencias y configuración completa | Identidad/conservación del contenido | Cadena verificable de origen y vínculos de referencias al requisito |
| Contradicciones críticas | Estados GAP y referencias conservados; IDs ambiguos rechazados | No hay productor genérico de contradicciones entre fuentes | Hallazgo concreto, aplicabilidad y criticidad documentadas |
| Modificaciones humanas | El paquete captura un estado; el Centro dispone de gobierno/historial separados | Dos capturas diferentes no identifican actor, autorización o causa | Productor de eventos/historial vinculados cuando el uso lo requiera |

No todas las determinaciones pendientes son requisitos universales. Deben justificarse por el uso previsto. No se exige completar todos los dominios EIOS para un productor acotado.

## 3. Frontera entre comprobación técnica y calidad
Una incoherencia de tipo, identidad o configuración que DIP-AGG-01 rechaza sigue siendo error técnico; esta unidad no la convierte en NO_APTO.
La ausencia explícita de snapshot, parámetro seleccionado o evidencia no demuestra por sí sola que esa información sea crítica para el consumidor.
Evidence GAP no es FALSE; Evidence DEMONSTRATED no demuestra suficiencia para cualquier regla.
No se usa validación C0 como sustituto de un control QTG global. La validación física y la suficiencia especializada son niveles distintos.
No se repite una comprobación ya realizada por el builder para presentar esa repetición como autenticación del paquete.

## 4. Hallazgo de diseño: riesgo de APTO por cobertura incompleta
evaluate_quality(...) evalúa exclusivamente QualityCheck ya suministrados y aplicables. No construye el inventario de controles requerido por un uso.
Con checks vacíos o solo controles satisfechos/inaplicables devuelve APTO/ALTA conforme a su algoritmo cerrado.
Por ello un productor que genere solo controles estructurales satisfechos y omita controles no determinables podría certificar una fiabilidad que no ha observado.
Este hallazgo no demuestra un defecto del gate dentro de su contrato: demuestra una obligación del productor de cubrir los controles requeridos por su alcance antes de invocarlo.
No se modifica evaluate_quality ni se añade un estado QTG, score, default o QualityCheck de criticidad inventada para cubrir esa carencia.

## 5. Gaps concretos del productor
QTG-DIP-G01 — Uso y cobertura: declarar consumidor/operación concretos, entradas necesarias y límites del resultado. Los IDs solicitados de DIP son una selección; no son un inventario autorizado de requisitos.
QTG-DIP-G02 — Applicabilidad y criticidad: para cada control requerido, fuente especializada, observación, criterio y tratamiento de ausencia/contradicción deben estar determinados. La definición general de criticidad de QTG §9.1 no aporta por sí sola esa determinación.
QTG-DIP-G03 — Observación suficiente: disponer de material/productor verificable para los controles requeridos. Conservar una referencia o fecha no permite inferir admisibilidad, comparación entre fuentes, antigüedad aceptable o autorización humana.
QTG-DIP-G04 — Frontera de reutilización: diseñar evaluación/reevaluación desde inputs capturados y binding completo a compra/contexto; no aceptar QualityTrustResult desprendido ni un callback opaco.
Estos IDs son hallazgos documentales de esta unidad, no estados funcionales nuevos.
La RDM mantiene Criticality/Evaluability_Impact PENDING donde no están determinados. Sus categorías pertenecen a evaluabilidad de reglas; no se trasladan automáticamente al booleano critical de QualityCheck, ni PENDING se convierte en False.

## 6. AUDITAR
Fuentes contrastadas: arquitectura funcional §7–8, Architecture_Blueprint §5, contrato QTG v0.4 §§4–12, Evidence_Contract §§6–10 y §15, RDM §§7–8 y cobertura vigente, contrato DIP-AGG-01 §§3–10, cuarentena QTG y código quality/gate.py, core/validation.py y core/decision_input_package.py.
Hallazgos:
A1 distinguir observabilidad de suficiencia;
A2 separar criticidad QTG de Criticality RDM;
A3 identificar riesgo de APTO por un conjunto de controles incompleto;
A4 no exigir universalmente autenticación/atomicidad/historial si el uso acotado no lo requiere;
A5 no declarar que sigue faltando un paquete físico: existe DIP-AGG-01, pero su existencia no cierra el productor.

## 7. DEPURAR
A1–A5 incorporados en la tabla y §§3–5.
Se conserva separado el cierre DIP y el bloqueo del productor. La selección de entradas no se transforma en política de admisibilidad.
Los gaps permiten diseñar un productor acotado, sin exigir una arquitectura empresarial completa.
No se fabrican QualityCheck con satisfied/critical/material arbitrarios ni se registra QTG ejecutado en el Vertical.

## 8. AUDITAR 2
Segunda revisión del análisis depurado:
- estados y precedencia QTG cerrados intactos;
- no se reabre DIP ni se declara un defecto objetivo del builder;
- no se convierte captura/fingerprint en prueba de procedencia;
- faltas de cobertura se mantienen como bloqueo del diseño, no resultado QTG;
- no se reutiliza severidad/regla/RDM para inventar criticidad;
- ningún gap se convierte en requisito universal sin contexto;
- las cuarentenas QTG, Stage 2/VF y wrapper Decision Twin dependiente permanecen intactas.
Resultado: análisis de cobertura SUPERADO; productor de resultado global sigue sin diseño completo autorizado.

## 9. CERRAR
Se cierra únicamente el análisis QTG-DIP-CONTROL-01.
No se cierra el contrato del productor QTG ni se autoriza implementar integración positiva.
Siguiente unidad legítima: QTG-DIP-G01 — especificar el uso/consumidor acotado y sus obligaciones de entrada con fuentes existentes; después determinar G02/G03 para ese alcance y diseñar G04.
No se exige aprobación de política económica no propuesta; cuando una determinación sí requiera nueva política, deberá presentarse explícitamente.

## 10. MATERIALIZAR / CI
Un único registro en 07_Pruebas. Ningún cambio ejecutable, API, regla, parámetro, dominio QTG o fuente canónica.
CI #827 certifica el baseline, no este delta documental. La CI de la nueva PR debe verificarse sobre su HEAD exacto y, tras integración, sobre el merge.
La CI prueba ausencia de regresión; no demuestra suficiencia de cobertura ni aprueba política.

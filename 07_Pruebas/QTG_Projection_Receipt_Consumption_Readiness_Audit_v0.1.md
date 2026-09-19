# EIOS — QTG PROJECTION_ONLY Receipt Consumption Readiness Audit v0.1

**Estado:** CERRADO — NO LISTO PARA INTEGRACIÓN VERTICAL  
**Baseline auditado:** `main @ db159b90f0736422025b0596d28460d2a87a5497`  
**Ámbito:** preparación de la frontera de consumo/invocación del primer productor QTG `PROJECTION_ONLY`.

## 1. DISEÑAR

### 1.1 Pregunta de decisión

Determinar si el productor aislado `QTG-PROJECTION-PRODUCER-01` ya puede incorporarse de forma verificable al Vertical MVP o a su `CapabilityInvoker` genérico, sin reabrir las fronteras cerradas ni degradar la procedencia materializada por `ProjectionMaterialEnvelope` y `ProjectionQualityReceipt`.

### 1.2 Criterio de readiness

Una ruta de consumo se considera preparada únicamente si:

1. recibe o conserva el `ProjectionMaterialEnvelope` exacto;
2. valida el `ProjectionQualityReceipt` por recomputación contra ese material y el modo declarado;
3. distingue `SYNTHETIC_TEST` de `OPERATIONAL` y nunca publica material sintético como resultado operacional;
4. conserva perfil, productor, catálogo, huellas, inventario de controles, resultado QTG y alcance de aseguramiento;
5. no acepta un `QualityTrustResult`, `CapabilityExecution` o callable desprendido como prueba de procedencia;
6. no confunde ejecución técnica `COMPLETED` con los estados funcionales QTG;
7. vincula de forma verificable el material consumido con la ejecución que lo presenta;
8. mantiene QTG sin autoridad decisional y no habilita por sí sola la ruta Vertical.

## 2. AUDITAR

### 2.1 Inventario físico

| Frontera | Entrada real | Evidencia preservada | Resultado |
|---|---|---|---|
| `produce_projection_quality(...)` | `ProjectionMaterialEnvelope` + modo | envelope completo, huellas, catálogo, controles, resultado y alcance | `ProjectionQualityReceipt` |
| `validate_projection_quality_receipt(...)` | receipt + envelope + modo | recomputación exacta de payload y huella | validación o rechazo |
| `CapabilityInvoker` | `PurchaseOperation` + `DecisionContext` | solo lo que devuelva el callable | `CapabilityExecution` |
| `adapt_qtg(...)` | `QualityTrustResult` desprendido | no conserva receipt, envelope, modo, perfil, catálogo ni huellas | `QTG / COMPLETED` |
| `run_mvp_execution(...)` | invocadores genéricos autorizados | envelope O1 reducido | no acepta QTG |
| `run_vertical_mvp_support(...)` | compra, contexto, reglas e invocadores autorizados | soporte Vertical reducido | no acepta QTG |

### 2.2 Hallazgos

**A1 — incompatibilidad de entrada.** El productor exige el envelope exacto; la firma `CapabilityInvoker` solo entrega compra y contexto. No puede reconstruir el material sin introducir una fuente o agregación no autorizada.

**A2 — pérdida de prueba en el adaptador existente.** `adapt_qtg(...)` traduce cualquier `QualityTrustResult` a ejecución técnica completada. El tipo recibido no acredita productor, perfil, catálogo, modo, pertenencia ni reproducibilidad.

**A3 — semántica insuficiente de `CapabilityExecution`.** El envelope O1 solo conserva estado técnico, disponibilidad, referencias y pendientes. No puede transportar ni demostrar por sí mismo el receipt completo.

**A4 — riesgo de bypass.** Reintroducir `quality_invoker`, capturar un receipt en un closure o adaptar únicamente `receipt.quality_result` volvería opaca la procedencia que el productor acaba de materializar.

**A5 — modos no representables.** La frontera genérica no distingue `SYNTHETIC_TEST` de `OPERATIONAL`. Por tanto no puede demostrar que un `QTG / COMPLETED` procede de material operacional.

**A6 — estado funcional no equivale a ejecución técnica.** `NO_APTO`, `APTO_CON_ADVERTENCIAS` y `APTO` son resultados QTG; `COMPLETED` solo indica que una ejecución técnica terminó. El adaptador actual conserva esta distinción parcialmente, pero pierde el resultado funcional en el registro O1.

**A7 — orden no es autorización.** La presencia de `QTG` en `MVP_CAPABILITY_ORDER` mantiene el orden arquitectónico y no habilita una ruta de ejecución.

**A8 — ausencia de consumidor autorizado.** No existe todavía una función que valide receipt, envelope y modo exactos antes de producir una representación consumible, ni un contrato que defina dónde se conserva el receipt íntegro.

## 3. DEPURAR

Se descartan las siguientes vías:

1. **Restaurar `quality_invoker: CapabilityInvoker`**: no transporta material verificable.
2. **Usar `adapt_qtg(receipt.quality_result)`**: elimina receipt, modo y huellas.
3. **Capturar envelope/receipt en un closure**: la firma pública seguiría sin acreditar qué material ejecutó.
4. **Añadir campos QTG ad hoc a `CapabilityExecution`**: reabre el contrato O1 común y mezcla prueba especializada con estado técnico.
5. **Publicar receipts sintéticos en el Vertical**: contradice `operational_effect` y el alcance declarado.
6. **Inferir pertenencia desde identificadores parciales**: el productor valida cadenas materiales completas, no una coincidencia nominal.

La alternativa mínima que sobrevive a la depuración es una **frontera dedicada de consumo QTG de proyección**, exterior al `CapabilityInvoker` genérico. Debe recibir explícitamente receipt, envelope y modo; ejecutar `validate_projection_quality_receipt(...)`; rechazar `SYNTHETIC_TEST` en cualquier exposición operacional; y devolver un artefacto especializado que conserve la prueba íntegra antes de que una unidad posterior evalúe su integración Vertical.

Esta auditoría no nombra un almacén, endpoint, orquestador ni autorización inexistentes, y no materializa todavía ese consumidor.

## 4. AUDITAR 2

La revisión adversarial confirma:

- el nuevo productor satisface la condición histórica de existencia de material agregado y productor verificable, pero no satisface por sí solo la condición de consumo Vertical seguro;
- el adaptador `adapt_qtg(...)` es un legado de traducción de dominio, no una ruta de procedencia válida para el nuevo receipt;
- eliminarlo en esta unidad sería ampliar alcance y podría afectar consumidores ajenos; debe permanecer fuera de la futura ruta o revisarse en una unidad explícita;
- no hay contradicción objetiva que permita reabrir la firma genérica retirada;
- ninguna prueba actual demuestra una integración operacional QTG legítima en el Vertical;
- `SYNTHETIC_TEST` sigue limitado a pruebas y `OPERATIONAL` sigue exigiendo material no sintético;
- QTG continúa sin autoridad para aprobar compra, pago, escenario o decisión.

## 5. CERRAR

### 5.1 Decisión

**No aprobar todavía la integración QTG en `run_mvp_execution(...)` ni en `run_vertical_mvp_support(...)`.**

Se aprueba como siguiente unidad legítima el diseño de una frontera dedicada de consumo del receipt `PROJECTION_ONLY`, aislada del invocador genérico y sin exposición Vertical inicial.

### 5.2 Condiciones de la siguiente unidad

La futura frontera deberá, como mínimo:

1. aceptar tipos concretos `ProjectionQualityReceipt` y `ProjectionMaterialEnvelope`;
2. exigir un modo explícito y validar por recomputación antes de exponer cualquier salida;
3. prohibir consumo operacional de `SYNTHETIC_TEST`;
4. conservar el receipt íntegro y sus huellas, sin reducirlo a `QualityTrustResult`;
5. declarar separadamente resultado funcional QTG y estado técnico de consumo;
6. rechazar recibos o envelopes forjados, cruzados, alterados o de perfil distinto;
7. no crear decisiones, recomendaciones, aprobaciones ni autorizaciones financieras;
8. no modificar aún las firmas públicas del Vertical MVP.

La incorporación posterior al Vertical requerirá otra decisión y otra auditoría sobre la pertenencia entre el receipt especializado y la ejecución O1 concreta.

## 6. MATERIALIZAR

Esta unidad materializa únicamente la presente evidencia de readiness. No modifica código, APIs, adaptadores, modelos, evaluadores, criterios, receipts ni rutas de ejecución.

La modificación local ajena de `08_Implementacion/Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda expresamente excluida de esta unidad.

## 7. CI

El cierre exige:

1. suite completa verde sobre el baseline auditado;
2. PR limitado a este documento;
3. CI pre-merge sobre el SHA exacto del PR;
4. merge protegido por ese SHA;
5. CI post-merge verde sobre el nuevo `main`.

Hasta completar esos gates, esta auditoría no se considera integrada.

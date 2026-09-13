# EIOS — Vertical MVP NI + Ladder Opaque Result Provenance Quarantine Contract v0.1

**Estado:** CERRADO PARA MATERIALIZACIÓN  
**Baseline:** `main @ 7aa995f840bc37a6a5637580ade1c2f6e8d56b88`  
**Ámbito:** fronteras públicas de composición Vertical MVP para `NEGOTIATION_INTELLIGENCE` y `NEGOTIATION_LADDER`.

## 1. Propósito

Eliminar de las fronteras públicas del Vertical MVP la posibilidad de incorporar `NegotiationIntelligenceResult` y `NegotiationLadderResult` preproducidos y convertirlos internamente en capacidades de la ejecución actual mediante un snapshot que ignora el `PurchaseOperation` y el `DecisionContext` recibidos durante la invocación.

Esta unidad corrige exclusivamente una frontera de composición. No modifica la semántica, autoridad ni modelos de Negotiation Intelligence o Negotiation Ladder.

## 2. Hallazgo objetivo

En el baseline indicado:

- `run_mvp_execution(...)` acepta `negotiation_intelligence_result` y `negotiation_ladder_result` ya producidos;
- valida referencias contextuales parciales de esos resultados;
- después los convierte mediante `_snapshot_invoker(...)` en capacidades ejecutables;
- `_snapshot_invoker(...)` ignora el `PurchaseOperation` y el `DecisionContext` que recibe al ejecutarse;
- `NegotiationIntelligenceResult` no conserva la `PurchaseOperation` completa ni existe un productor ejecutable autorizado que permita recalcular NI desde ella;
- `NegotiationLadderResult` tampoco conserva la `PurchaseOperation` completa y su módulo materializa únicamente el contrato estructural de Ladder;
- la comprobación Ladder ↔ NI disponible actualmente depende de inspeccionar dos resultados crudos preproducidos, no de una cadena de procedencia resoluble por el boundary.

Por tanto, la composición puede demostrar determinadas coincidencias de identidad contextual, pero no puede certificar que esos resultados pertenezcan materialmente a la compra completa de la ejecución actual. Convertirlos internamente en invocadores crea procedencia aparente que el boundary no puede probar.

## 3. Autoridades y precedentes preservados

La unidad deriva de contratos ya cerrados:

- `Negotiation_Intelligence_Implementation_Contract.md`: NI determina contenido negociador a partir de autoridades upstream y no recalcula Scenario Engine, Viability Frontier ni Decision Twin.
- `Negotiation_Ladder_Implementation_Contract.md`: Ladder representa y ordena contenido previamente determinado; no crea contenido sustantivo.
- `Vertical_MVP_Opaque_Result_Provenance_Quarantine_Contract_v0.1.md`: un invocador explícito no constituye por sí mismo certificación de procedencia; la cuarentena impide que la capa Vertical fabrique esa certificación mediante re-etiquetado de resultados opacos.
- `E2E_Execution_Boundary_Implementation_Contract.md`: la ejecución conserva su `PurchaseOperation` y `DecisionContext` canónicos y no adquiere autoridad empresarial nueva.

## 4. Diseño autorizado

### 4.1 Servicio core

`run_mvp_execution(...)` elimina de su firma pública:

- `negotiation_intelligence_result`
- `negotiation_ladder_result`

Y acepta en su lugar:

- `negotiation_intelligence_invoker: CapabilityInvoker | None`
- `negotiation_ladder_invoker: CapabilityInvoker | None`

Si están presentes, se incorporan directamente al catálogo:

- `NEGOTIATION_INTELLIGENCE` → `negotiation_intelligence_invoker`
- `NEGOTIATION_LADDER` → `negotiation_ladder_invoker`

El servicio no snapshoteará, adaptará ni re-etiquetará internamente resultados NI/Ladder preproducidos.

### 4.2 Fachada pública

`run_vertical_mvp_support(...)` aplica exactamente la misma frontera:

- elimina `negotiation_intelligence_result` y `negotiation_ladder_result`;
- acepta `negotiation_intelligence_invoker` y `negotiation_ladder_invoker`;
- los reenvía sin transformación a `run_mvp_execution(...)`.

### 4.3 Alcance de la garantía

Un invocador NI o Ladder explícito **no constituye por sí solo una certificación provenance-safe**.

La garantía de esta unidad es más estrecha:

> El Vertical MVP deja de fabricar procedencia aparente a partir de resultados NI/Ladder desprendidos que él mismo no puede vincular materialmente a la `PurchaseOperation` completa.

La construcción de productores NI/Ladder realmente provenance-safe, si llega a existir material suficiente para ello, requerirá contratos específicos posteriores.

### 4.4 Relación NI ↔ Ladder

La antigua comparación entre `NegotiationLadderResult.context_references.negotiation_result_id` y un `NegotiationIntelligenceResult` crudo deja de pertenecer a esta capa porque los resultados crudos dejan de cruzar su frontera.

El Vertical no inventará un nuevo bundle, identificador paralelo ni protocolo lateral para conservar esa comprobación. La coherencia NI ↔ Ladder deberá ser garantizada por el productor/autorizador de los invocadores cuando ambas capacidades formen parte de una misma cadena materializada.

Esto no autoriza a ignorar dicha relación; impide únicamente que esta capa afirme haberla demostrado cuando ya no dispone de los artefactos necesarios para hacerlo.

## 5. Compatibilidad y migración

El cambio es intencionadamente fail-closed.

No se mantienen aliases legacy para:

- `negotiation_intelligence_result`
- `negotiation_ladder_result`

Conservarlos mantendría la misma contradicción que esta unidad elimina.

Los consumidores físicos de las fronteras públicas se migran conjuntamente. Los modelos NI/Ladder y los adaptadores de capacidad no se modifican.

## 6. Invariantes preservadas

1. `MVP_CAPABILITY_ORDER` permanece sin cambios.
2. NI sigue sin decidir, aprobar, ejecutar, recalcular Scenario/Viability/Decision Twin ni gobernar Strategy.
3. Ladder sigue siendo exclusivamente estructural y no determina contenido negociador.
4. No se introduce `decision_version` ni identidad paralela.
5. No se modifica `NegotiationIntelligenceResult`.
6. No se modifica `NegotiationLadderResult`.
7. No se modifica `adapt_ni` ni `adapt_nl`.
8. No se crea productor NI/Ladder nuevo.
9. No se modifica la semántica de `COMPLETED`, `PARTIALLY_COMPLETED`, `FAILED` o `NOT_EVALUABLE` del boundary.
10. No se añade decisión empresarial, recomendación vinculante ni ejecución automática.

## 7. Criterios de aceptación

1. Los invocadores NI y Ladder reciben exactamente el `PurchaseOperation` y `DecisionContext` de la ejecución actual.
2. NI y Ladder conservan sus posiciones canónicas en `MVP_CAPABILITY_ORDER`.
3. La fachada reenvía ambos invocadores sin snapshot, adaptación ni transformación.
4. Las firmas públicas no contienen `negotiation_intelligence_result` ni `negotiation_ladder_result`.
5. Las firmas públicas sí contienen `negotiation_intelligence_invoker` y `negotiation_ladder_invoker`.
6. La ausencia de NI y/o Ladder sigue siendo válida si existe al menos otra capacidad.
7. Una ejecución sin ninguna capacidad sigue fallando cerrada.
8. No existen aliases de compatibilidad para los resultados crudos eliminados.
9. Los modelos y adaptadores NI/Ladder permanecen sin cambios.
10. La suite Python + SQL completa constituye el gate obligatorio de CI.

## 8. Auditoría 1 y depuración

### Auditoría 1

Se confirmó que las validaciones de contexto NI/Ladder existentes comprueban únicamente identidades parciales y que, tras esas comprobaciones, `_snapshot_invoker(...)` ignora la compra/contexto de ejecución. También se confirmó que los módulos NI y Ladder no contienen productores autorizados con los que reconstruir esos resultados desde una entrada completa verificable.

### Depuración

Se descartaron explícitamente:

- recalcular NI desde `PurchaseOperation`;
- generar Ladder dentro del Vertical;
- crear un bundle NI+Ladder nuevo;
- añadir metadata paralela para conservar artificialmente la comparación `negotiation_result_id`;
- mantener parámetros crudos como aliases;
- presentar los invocadores explícitos como certificados de procedencia.

El diseño final aplica el precedente de cuarentena opaca ya cerrado para QTG/Decision Twin y no amplía autoridad funcional.

## 9. Materialización autorizada

La unidad puede modificar únicamente lo necesario para la migración de frontera y pruebas asociadas, principalmente:

```text
08_Implementacion/Vertical_MVP_NI_Ladder_Opaque_Result_Quarantine_Contract_v0.1.md
eios/core/mvp_execution.py
eios/mvp.py
tests/test_mvp_execution_service.py
tests/test_mvp_ni_context_integrity.py
tests/test_mvp_ladder_context_integrity.py
tests/test_vertical_mvp_support.py
```

Cualquier archivo adicional requerirá una necesidad objetiva observada durante la materialización o CI.

## 10. Método y cierre

Método obligatorio:

**DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**

Esta versión autoriza la materialización, pero **no autoriza declarar la unidad integrada o cerrada en `main`**.

El cierre definitivo requiere:

- Auditoría 2 de la materialización sin bloqueadores;
- CI pre-merge sobre el head exacto del PR en verde;
- reconciliación de `main` inmediatamente antes del merge;
- merge protegido por el SHA exacto validado;
- reconciliación postintegración;
- CI post-merge sobre el SHA exacto de `main` en verde.

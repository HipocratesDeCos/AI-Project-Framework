# EIOS — History Sufficiency PRICE Provenance · Depuración v0.1

## Estado

**DEPURACIÓN COMPLETADA**

Unidad: `HIS-PRICE-PROV-01`

Base: diseño v0.1 + Audit 1 SUPERADA.

## 1. Objetivo

Eliminar ambigüedades de implementación antes de Audit 2. Esta depuración no añade autoridad empresarial ni modifica la condición de `R-HIS-002`.

## 2. API depurada

`evaluate_r_his_002(...)` dejará de aceptar `PriceIntelligenceResult` como entrada.

En su lugar recibirá explícitamente:

- `PriceIntelligenceInput`;
- `PriceIntelligenceAssessmentContext`.

`HistorySufficiencyRuleInputs` aplicará el mismo cambio.

No habrá:

- argumento opcional `pricing_result`;
- alias legado;
- fallback a resultado precomputado;
- sobrecarga alternativa.

## 3. Orden de ejecución depurado

El bridge seguirá este orden:

1. validar identidad `PurchaseOperation ↔ DecisionContext ↔ Rule`;
2. validar igualdad completa de `pricing_input.decision_context` con `DecisionContext`;
3. validar igualdad completa de `pricing_input.purchase_operation` con `PurchaseOperation`;
4. crear snapshots profundos de `pricing_input` y `pricing_assessment_context`;
5. ejecutar `run_price_intelligence(snapshot_input, snapshot_context)`;
6. validar la identidad/ligadura de la evidencia PRICE contra el resultado reconstruido;
7. aplicar `validate_evidence(...)` a la evidencia PRICE;
8. validar/recuperar el umbral provenance-safe `P-PRE-006` conforme al contrato vigente;
9. si ambas evidencias son válidas, evaluar exclusivamente `n_comparable < threshold`;
10. devolver el `Assessment` vigente.

## 4. Errores del motor C1

Una excepción contractual producida por `run_price_intelligence(...)`:

- no se convierte en `TRUE`;
- no se convierte en `FALSE`;
- no se sustituye por un resultado manual;
- no activa fallback.

La excepción se propaga al llamador. Esto mantiene fail-closed y hace visible un input/contexto C1 inválido.

`NOT_EVALUABLE` se reserva al comportamiento ya existente de la regla cuando su evidencia requerida/configuración no alcanza el estado válido después de superar las comprobaciones estructurales; no se utiliza para ocultar errores de identidad, ligadura o ejecución PRICE.

## 5. Snapshot

Se copiarán en profundidad antes de ejecutar C1:

- `pricing_input.model_copy(deep=True)`;
- `pricing_assessment_context.model_copy(deep=True)`.

Aunque `PriceIntelligenceAssessmentContext` sea `frozen`, el snapshot explícito conserva simetría con la frontera provenance-safe PRICE ya cerrada y evita depender de estructuras mutables anidadas.

## 6. Evidencia PRICE

La evidencia sigue usando `price_intelligence_result_ref(...)`, pero la referencia esperada se calculará únicamente sobre el resultado reconstruido localmente.

Se preserva la distinción vigente entre **violación estructural** y **evidencia no válida**:

- `source_type` incompatible → `ValueError`;
- `captured_at` incompatible → `ValueError`;
- evidencia `DEMONSTRATED` cuyo `demonstration_ref` no coincide con el resultado reconstruido → `ValueError`;
- evidencia que supera las comprobaciones estructurales pero no alcanza `VALID` según `validate_evidence(...)` → `Assessment(status=NOT_EVALUABLE, outcome=None)`.

Consecuencia: un llamador no puede fabricar un resultado alternativo y una evidencia `DEMONSTRATED` asociada sin que la ligadura se contraste contra el resultado reconstruido por el bridge.

## 7. P-PRE-006

Se conserva sin cambios el contrato de configuración existente.

La ausencia de configuración o evidencia de parámetro sigue dando `NOT_EVALUABLE` cuando corresponda.

Los errores estructurales de identidad, empresa, versión, vigencia, unidad o ligadura de evidencia conservan sus rechazos vigentes; los valores/unidades no utilizables que actualmente producen umbral `None` mantienen `NOT_EVALUABLE`. No se suaviza ninguna protección para facilitar la migración.

## 8. Migración de tests

`tests/test_r_his_002_vertical.py` dejará de fabricar `PriceIntelligenceResult` como entrada autorizada al bridge.

Los casos deberán construir el `n_comparable` mediante referencias C1 reales:

- cada referencia comparable debe corresponder al mismo artículo;
- debe contener evidencia validada;
- el contexto temporal/representatividad/suficiencia debe ser coherente con el conjunto seleccionado cuando proceda.

Casos mínimos:

1. una referencia comparable y umbral 2 → TRUE;
2. dos referencias comparables y umbral 2 → FALSE;
3. ausencia de `P-PRE-006` → NOT_EVALUABLE;
4. configuración de otra empresa → rechazo;
5. evidencia PRICE `DEMONSTRATED` ligada a un resultado distinto del reconstruido → `ValueError`;
6. evidencia PRICE estructuralmente correcta pero no válida → NOT_EVALUABLE;
7. `pricing_input` de otra compra/contexto → rechazo;
8. comprobación de API: `evaluate_r_his_002` y `HistorySufficiencyRuleInputs` no exponen `pricing_result`.

El test CRC que verifica que R3 no domina a R2 debe seguir verde usando el nuevo productor PRICE.

## 9. No cambios

No se modificarán:

- `run_price_intelligence`;
- `PriceIntelligenceResult`;
- `Price_Provenance_Invoker_Contract_v0.1`;
- `eios/core/price_integration.py`;
- Matriz de Reglas;
- RDM;
- Catálogo de Parámetros;
- condición o efecto de `R-HIS-002`;
- semántica de `P-PRE-006`.

## 10. Resultado

La implementación queda especificada sin rutas ambiguas ni compatibilidad insegura, preservando además la semántica fail-closed del bridge vigente.

**DEPURACIÓN COMPLETADA.**

La unidad puede pasar a **AUDITAR 2**.

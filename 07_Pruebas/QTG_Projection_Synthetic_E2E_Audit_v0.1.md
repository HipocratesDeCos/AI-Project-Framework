# EIOS — QTG-PROJECTION-SYNTHETIC-E2E-01 — Auditoría de ensayo v0.1

**Estado:** AUDIT 2 PASS TÉCNICO — CI PENDIENTE

**Baseline:** `main @ e259ddf04aa5114923cff418441da08805d4031e`

## DISEÑAR

Validar la cadena sintética completa utilizando exclusivamente fronteras públicas ya cerradas:

`ProjectionMockDataset → ProjectionOnlySyntheticMaterialBundle → ProjectionMaterialEnvelope → ProjectionQualityReceipt → ProjectionQualityConsumption`.

No se introduce código de producción.

## AUDITAR

1. **Bundle completo no equivale a APTO.** La fixture física actual tiene membresía estructural completa, pero conserva una limitación declarada y findings de flujo no vinculados individualmente en las tres familias que el productor exige por `flow_id`. El productor debe poder responder negativamente sin invalidar el bundle.
2. **Resultado negativo no equivale a fallo técnico.** Un receipt `NO_APTO/BAJA` sintético debe seguir siendo reproducible y consumible como `TEST_ONLY`.
3. **Resultado positivo sintético no equivale a operación.** Una variante Mock Data que elimina la limitación y añade bindings por flujo puede producir `APTO/ALTA`, pero conserva `operational_effect=false` y `decision_authority=false`.
4. **No promoción por modo.** El mismo envelope sintético debe ser rechazado por el productor en `OPERATIONAL`.
5. **Procedencia completa.** Dataset fingerprint → bundle/envelope fingerprint → receipt fingerprint → consumption fingerprint permanecen encadenados.
6. **Finance aislado.** El ensayo intercepta Finance Basic y provenance; el gate QTG sí se ejecuta porque constituye el objeto de esta prueba.
7. **Sin wrapper adicional.** Añadir un invoker o facade para esta secuencia duplicaría fronteras existentes y podría erosionar la separación producer/consumer.

## DEPURAR

Se descartan:

- cambios de etiqueta `SYNTHETIC` a `PRESENTED_OPERATIONAL`;
- modificación del productor para favorecer la fixture;
- modificación de la fixture física para ocultar su limitación;
- consumo de un resultado desprendido;
- integración O1/Vertical;
- nueva API de orquestación;
- efectos persistentes o decisionales.

La variante positiva existe solo dentro del test y completa material explícitamente autorizado por los schemas ya cerrados.

## AUDITAR 2

El delta contra el baseline contiene exclusivamente:

- `08_Implementacion/Projection_Only_Synthetic_QTG_E2E_Contract_v0.1.md`;
- `tests/test_projection_synthetic_qtg_e2e.py`;
- este registro.

La prueba cubre:

- fixture física → `NO_APTO/BAJA` reproducible;
- consumo `TEST_ONLY` técnicamente `VALIDATED`;
- conservación de la razón de conflicto/limitación;
- variante sintética suficientemente completada → `APTO/ALTA`;
- efecto operacional falso en ambos casos;
- autoridad decisional falsa;
- diferencia entre membresía completa y calidad favorable;
- rechazo del modo `OPERATIONAL`;
- cadena exacta de fingerprints;
- ausencia de ejecución Finance.

No se modifica código ejecutable de producción.

## CERRAR → MATERIALIZAR → CI

Cierre técnico aprobado sujeto a CI exact-head. Si la suite pasa, quedará validado el recorrido sintético completo hasta el consumidor QTG especializado.

La ruta `OPERATIONAL` seguirá bloqueada: el repositorio ya dispone del diseño de binding causal QTG↔O1, pero su implementación positiva exige material operacional autorizado y no puede legitimarse con Mock Data.

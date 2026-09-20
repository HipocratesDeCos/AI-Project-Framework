# EIOS — QTG-PROJECTION-CONSUMER-01 — Contrato v0.1

**Baseline:** `main @ 8814ffd1045305f5a424848159274a937e657bc3`
**Estado:** DISEÑADO — AUDITADO — MATERIALIZACIÓN CONDICIONADA A CI

## DISEÑAR

La frontera especializada consume exclusivamente:

```text
ProjectionQualityReceipt + ProjectionMaterialEnvelope
+ execution_mode + consumption_scope
→ ProjectionQualityConsumption
```

Emparejamientos permitidos:

| `execution_mode` | `consumption_scope` | Efecto |
|---|---|---|
| `SYNTHETIC_TEST` | `TEST_ONLY` | no operacional |
| `OPERATIONAL` | `OPERATIONAL` | calidad operacional de la entrada de proyección |

Cualquier otro emparejamiento falla. El consumidor revalida primero el receipt por recomputación completa contra el envelope y el modo exactos.

El artefacto conserva el receipt íntegro, sus huellas, el resultado funcional QTG y un estado técnico independiente `VALIDATED`. No produce `CapabilityExecution`, no usa `adapt_qtg`, no implementa un `CapabilityInvoker` y no modifica el Vertical.

## AUDITAR

1. Un resultado QTG desprendido pierde procedencia: no se acepta.
2. Una huella aislada no prueba el contenido: se recompone el receipt completo.
3. `COMPLETED` podría confundirse con `APTO`: se usa `VALIDATED` como estado técnico especializado.
4. Un receipt sintético podría promoverse cambiando el alcance: modo y alcance deben coincidir exactamente.
5. Reducir el receipt al resultado funcional eliminaría catálogo, controles y evidencia: se conserva completo.
6. Añadir campos al envelope O1 reabriría una frontera común cerrada: se crea un tipo especializado aislado.
7. Una salida válida podría adquirir autoridad por inferencia: declara `decision_authority=false` y limita su assurance scope.

## DEPURAR

Se excluyen: closures opacos, `quality_invoker`, `adapt_qtg(receipt.quality_result)`, estados O1 fabricados, promoción test→operación, inferencias por identificadores parciales y ejecución de Finance Basic.

La recomputación es la única aceptación válida. El consumidor no altera, completa ni interpreta controles; solo valida y conserva.

## AUDITAR 2

La revisión confirma que:

- receipt, envelope, modo y alcance son entradas concretas y visibles;
- la validación ocurre antes de exponer salida;
- prueba y operación son dominios no intercambiables;
- resultado funcional y validación técnica permanecen separados;
- el receipt completo no se reduce a `QualityTrustResult`;
- QTG sigue fuera de `run_mvp_execution(...)` y `run_vertical_mvp_support(...)`;
- no se reabre C0, Rules, PRICE, Finance Basic, Decision Twin ni Scenario Stage 2.

## CERRAR

Se cierra únicamente el consumidor especializado aislado. Su existencia no autoriza integración Vertical.

La siguiente decisión, tras CI, será auditar la pertenencia entre un consumo `OPERATIONAL` especializado y una ejecución O1 concreta. Esa unidad deberá decidir si existe una representación segura sin degradar el receipt ni reintroducir un callable genérico.

## MATERIALIZAR → CI

Material autorizado:

- `eios/core/projection_quality_consumer.py`;
- `tests/test_projection_quality_consumer.py`;
- este contrato.

Se exige suite focal, suite completa, CI exact-head y CI post-merge. La modificación local ajena de `Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda excluida.

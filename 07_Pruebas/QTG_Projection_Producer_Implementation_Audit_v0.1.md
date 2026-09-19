# EIOS — QTG-PROJECTION-PRODUCER-01 — Auditoría de implementación v0.1

Fecha: 19/09/2026. Baseline remoto: `07e3ef71a5ed4c4ce8c7b8b958073b4129396cdf`; PR #201 y CI #913/#914 SUCCESS.
Estado: productor aislado y recibo implementados; integración condicionada a CI; cuarentena Vertical intacta.

## DISEÑAR

Materializar el contrato cerrado mediante:

- `produce_projection_quality(envelope, execution_mode)`;
- `ProjectionQualityReceipt` inmutable;
- `validate_projection_quality_receipt(...)` por recomputación;
- catálogo canónico versionado y fingerprint;
- modos `SYNTHETIC_TEST` y `OPERATIONAL`.

El productor consume exclusivamente `ProjectionMaterialEnvelope`, genera internamente todo el inventario, llama al gate una vez y nunca ejecuta Finance Basic.

## AUDITAR

A1: confiar en fingerprints internos suministrados permitiría sustituir payloads. Se recalcula cada fingerprint de preparación, manifiesto y siete piezas de cadena.

A2: confiar en `recomputed_membership` permitiría ocultar material sintético o pendientes. Se recalculan naturalezas, pendientes, flujos no evaluados, candidatos y cuotas desde los payloads internos.

A3: aceptar manifiesto anterior permitiría omitir tesorería o unicidad. Solo se admite schema v0.2 con las seis funciones exactas y hashes coincidentes.

A4: un envelope forjado podría mezclar cadenas con fingerprints individuales válidos. Se contrastan nuevamente todas las relaciones anidadas.

A5: producir solo checks favorables permitiría APTO parcial. El catálogo deriva dos agregados, seis controles por flujo capturado, uno por cuota y un control final de conflictos.

A6: el gate elimina no aplicables. El receipt conserva el inventario completo y, separadamente, los checks/resultados del gate.

A7: promover una ausencia a incumplimiento borraría no evaluabilidad. El productor mantiene `None`; reserva `False` para negativos, contradicciones o limitaciones explícitas.

A8: excluir por fecha desconocida sería optimista. Solo `AFTER_HORIZON` establecido y revisado hace no aplicables atributos/unicidad; el control de clasificación permanece aplicable.

A9: un modo `OPERATIONAL` suministrado junto a material sintético podría aparentar operación. Se rechaza antes de construir controles, usando naturalezas recalculadas.

A10: un resultado o receipt alterado podría reutilizarse por fingerprint aislado. El validador reconstruye inventario, checks, gate y receipt completos.

A11: la cadena humana positiva podría bastar por sí sola. Los controles exigen conjuntamente mandato, cobertura, estados estructurados, condiciones, soporte y ausencia de conflicto.

A12: el productor podría invocar Finance o integrarse indirectamente. Las pruebas interceptan el motor; no se modifica Vertical, invoker ni cuarentena.

## DEPURAR

A1–A12 incorporados. La auditoría inicial detectó y corrigió una confianza indebida en `contains_synthetic_material`; ahora el resumen completo del envelope se recompone antes del modo.

El productor conserva:

- diferencia entre `False` y `None`;
- controles no aplicables y razón;
- identidad exacta del criterio por control;
- catálogo/productor versionados;
- envelope completo y fingerprint;
- resultado del gate sin aceptar estados suministrados.

No incorpora advertencias no críticas, umbrales, FX, heurísticas, prioridad documental, FinanceResult o autoridad decisional.

## AUDITAR 2

Pruebas focales del productor: **7 satisfactorias**. Cubren:

- caso sintético incompleto → `NO_APTO/BAJA` recomputable;
- caso sintético completo → `APTO/ALTA` sin efecto operativo;
- conservación de checks fuera de horizonte no aplicables;
- rechazo de modo operativo con material sintético;
- alteración de fingerprints y resumen de pertenencia;
- receipt/resultado desprendido o alterado;
- identidad, inmutabilidad, modo y cambio de envelope;
- una única llamada al gate y ninguna llamada a Finance.

Pruebas focales acumuladas de manifiesto, envelope y productor: **37 satisfactorias**.

Suite completa: **1.286 pruebas satisfactorias**, seis avisos preexistentes/no bloqueantes.

PASS técnico: productor y recibo aislados cumplen el contrato dentro de los modos definidos.

PASS de frontera: no se modifica `evaluate_quality`, Finance Basic, Rules, C0, PRICE, Scenario, Decision Twin, invocadores o cuarentena Vertical.

## CERRAR → MATERIALIZAR → CI

Material:

- `eios/core/projection_quality_producer.py`;
- `tests/test_projection_quality_producer.py`;
- este documento.

El cierre integrado exige CI exact-head y post-merge. QTG continúa sin habilitarse en el Vertical.

Siguiente unidad legítima: auditoría de readiness de consumo/invocación para determinar si el receipt puede exponerse de forma acotada sin reabrir el invoker genérico ni conceder autoridad decisional.

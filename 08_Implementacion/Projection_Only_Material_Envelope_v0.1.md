# EIOS — QTG-PROJECTION-MATERIAL-01 — Envelope agregado v0.1

Fecha: 19/09/2026. Baseline remoto: `4e547d11c2a0d33cf2177cadf39f1b2e55faadef`; PR #197 y CI #905/#906 SUCCESS.
Estado: diseño, auditorías e implementación completados; integración condicionada a CI.

## DISEÑAR

Crear `ProjectionMaterialEnvelope`, un material canónico e inmutable para `PROJECTION_ONLY` que vincule:

- `FinanceQualityPreparation` exacta;
- `ProjectionCriteriaManifest` coincidente;
- cadena de tesorería: soporte, valoración contextual, mandato y revisión personal;
- cadena de flujos: registro de completitud, mandato y revisión personal.

Cada elemento se conserva mediante payload completo y fingerprint. Antes de construir el envelope se ejecutan todos los validadores de pertenencia ya cerrados y la coincidencia exacta de criterios autorizados.

El builder recalcula desde el material, sin confiar en resúmenes aportados:

- condiciones pendientes de revisión de tesorería;
- condiciones pendientes de revisión de flujos;
- flujos capturados no evaluados;
- candidatos sin correspondencia;
- cuotas requeridas sin revisión individual;
- naturalezas declaradas y presencia de material sintético.

Schema: `QTG-PROJECTION-MATERIAL-01/v0.1`. Assurance scope: `EXACT_BOUND_PROJECTION_MATERIAL_ONLY`.

## AUDITAR

A1: cadenas pertenecientes a preparaciones diferentes podrían compartir empresa o fecha. Se exige igualdad completa y fingerprint mediante sus validadores, no coincidencia contextual aproximada.

A2: un manifiesto válido pero ajeno podría autorizar otro contenido. Se exige igualdad exacta referencia/versión/hash con la preparación.

A3: soporte, valoración, mandato y revisión de tesorería podrían cruzarse parcialmente. Se valida cada arista de la cadena.

A4: registro, mandato y revisión de flujos presentan el mismo riesgo. Se valida cada arista y el purpose scope de `PROJECTION_ONLY`.

A5: los campos `pending_*` preservados podrían ocultar material modificado o una cobertura parcial. El envelope vuelve a derivar pendientes desde los hallazgos presentes.

A6: una colección de `CashFlow` puede contener elementos no evaluados. Se calcula la diferencia exacta entre flujos capturados y `flow_assessments`.

A7: la condición global de pagos no demuestra revisión individual. Se comparan las cuotas del calendario requerido con los subhallazgos de `PURCHASE_PAYMENT_COHERENCE`.

A8: mezclar material sintético y presentado podría aparentar operatividad. Las naturalezas se conservan por origen y se expone `contains_synthetic_material`.

A9: un envelope estructuralmente completo podría confundirse con resultado QTG. No contiene checks, estado, autorización, confianza ni resultado; tampoco ejecuta Finance o el gate.

A10: exigir positividad al construirlo eliminaría conflictos y bloquearía auditoría de casos negativos. Se admite material incompleto, negativo o conflictivo y se conserva como tal.

## DEPURAR

A1–A10 incorporados. El contrato separa tres niveles:

```text
pertenencia exacta → visibilidad estructural → futura evaluación QTG
```

Esta unidad cierra los dos primeros. La tercera continúa prohibida hasta autorizar y diseñar el productor.

La cadena de tesorería conserva su purpose scope cerrado de revisión para el piloto documental; la cadena de flujos exige `FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY`. No se crea una autoridad paralela.

## AUDITAR 2

Pruebas focales: **12 satisfactorias**. Cubren envelope íntegro, recálculo de pendientes, flujos y cuotas; rechazo individual de manifiesto y siete componentes ajenos; inmutabilidad; cambio de identidad; objetos no construidos; y aislamiento de Finance/QTG.

Suite completa: **1.278 pruebas satisfactorias**, seis avisos preexistentes/no bloqueantes.

PASS técnico: `QTG-PROJECTION-MATERIAL-01` queda resuelto dentro del alcance de vinculación y visibilidad estructural.

No se modifican criterios cerrados, Finance Basic, Rules, C0, PRICE, Scenario, Decision Twin ni las cadenas especializadas existentes.

## CERRAR → MATERIALIZAR → CI

Material:

- `eios/core/projection_material_envelope.py`;
- `tests/test_projection_material_envelope.py`;
- este documento.

El cierre integrado exige CI exact-head y post-merge. QTG continúa inhabilitado.

Siguiente unidad legítima: `QTG-PROJECTION-PRODUCER-01`, que deberá diseñar el inventario completo y la traducción determinista a checks, recibo y recomputación de consumo. No debe implementarse en positivo sin auditar antes la correspondencia exacta entre cada condición material, función autorizada, aplicabilidad y criticidad.

# EIOS — QTG-PROJECTION-CONSUMER-01 — Auditoría de implementación v0.1

**Baseline:** `main @ 8814ffd1045305f5a424848159274a937e657bc3`
**Estado:** AUDIT 2 PASS LOCAL — INTEGRACIÓN CONDICIONADA A CI

## DISEÑAR → AUDITAR → DEPURAR

Se materializa una frontera especializada e inmutable que conserva el receipt completo después de validarlo por recomputación contra el envelope y modo exactos. Se exige además un alcance explícito no intercambiable:

- `SYNTHETIC_TEST` ↔ `TEST_ONLY`;
- `OPERATIONAL` ↔ `OPERATIONAL`.

La salida separa `technical_status=VALIDATED` de `functional_quality_result` y declara ausencia de autoridad decisional.

La auditoría adversarial eliminó cuatro atajos: resultado desprendido, huella sin payload, promoción sintética y conversión a `CapabilityExecution`. El consumidor no invoca Finance ni modifica el productor o el gate.

La primera ejecución focal detectó siete errores de setup porque el nuevo módulo de pruebas no había importado las fixtures transitivas de preparación financiera. Se corrigió el arnés mediante importaciones explícitas y se repitió toda la selección focal desde cero; no se modificó la lógica de producción o consumo para resolverlos.

## AUDITAR 2

Las pruebas focales cubren:

1. conservación exacta de receipt y huellas;
2. recomputación satisfactoria del consumo sintético de prueba;
3. rechazo de exposición operacional de receipt sintético;
4. rechazo de modo cruzado, envelope alterado y entrada desprendida;
5. inmutabilidad y rechazo de artefacto de consumo alterado;
6. rechazo de alcances no canónicos;
7. permanencia de la cuarentena en ambas firmas Vertical.

Resultado focal final: **15 pruebas satisfactorias** —ocho del consumidor y siete del productor—.

Suite completa local: **1.294 pruebas satisfactorias**, con seis avisos preexistentes/no bloqueantes.

No se afirma la existencia de un caso operacional real ni se inventa material operacional. La rama operacional queda definida y fail-closed; solo será alcanzable con un receipt `OPERATIONAL` que el productor pueda recomputar desde material no sintético válido.

## CERRAR → MATERIALIZAR → CI

PASS local sujeto a los resultados anotados en el PR. QTG continúa aislado y sin habilitación Vertical. CI exact-head y post-merge son obligatorias.

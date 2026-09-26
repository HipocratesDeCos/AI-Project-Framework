# EIOS — Reconciliación de revisión completa de referencia v0.1

**Base:** `main @ 77ab8c3b1401404c8a34dcb5c454a8f676d38f82`  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## DISEÑAR

La demo completa genera dos terminales, HTML y ocho parejas de sidecars:
PRICE, TCO, Supplier Risk/Value, C0, Decision Twin, Scenario Coordination,
Negotiation Intelligence y Negotiation Ladder. Añadir coherencia entre
capturas cuando están presentes conjuntamente, sin ampliar el alcance de
autoridad ni cambiar productores.

## AUDITAR

Cada sidecar tiene validación individual y `--verify-dir` repite los fixtures.
La vista individual `render_review` podía aceptar capturas válidas por
separado con fuentes distintas, aun cuando aparentasen una historia única.
Los terminales no contienen prueba causal suficiente para deducir la igualdad
de las fuentes a partir de sus capacidades.

## DEPURAR

Tras validar cada captura, la vista comprueba únicamente igualdades de fuente
demostrables en este fixture:

- C0 y NI/Ladder comparten el mismo conjunto ordenado de bindings raíz.
- NI y Ladder comparten la fuente completa y el ID de resultado NI que Ladder
  reconstruye.
- Twin y Scenario Coordination comparten preparación y entradas Stage 2.

Estas igualdades no prueban que un invocador separado haya causado el
resultado de otro ni que exista admisión operacional.

## AUDITAR 2

El paquete completo de 19 archivos se exporta y verifica por CLI para ambas
variantes. Las huellas terminales permanecen intactas. Una prueba crea una
captura NI alternativa, verificable individualmente con sus huellas
recalculadas; la vista conjunta la rechaza frente a Ladder. Las parejas
ausentes siguen siendo admisibles como revisiones parciales.

## CERRAR

Material `SYNTHETIC`, política `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`,
efecto `NO_OPERATIONAL_EFFECT` y `decision_authority=false`. La coherencia
de fuentes es una propiedad de esta simulación, no una decisión de compra.

## MATERIALIZAR

Desde la raíz del repositorio actualizado, con un directorio nuevo:

```powershell
python -m examples.reference_business_case_demo --output-dir reference-demo-full --with-price --with-tco --with-supplier-risk --with-c0 --with-decision-twin --with-scenario-coordination --with-negotiation-intelligence --with-negotiation-ladder
Invoke-Item .\reference-demo-full\reference-review.html
python -m examples.reference_business_case_demo --verify-dir reference-demo-full
```

## CI

Suite completa y CI de la PR requeridas antes de integrar.

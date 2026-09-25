# EIOS — Reference Negotiation Intelligence Observation Capture v0.1

**Base:** `main @ 9a06d7496c19d702f324c829d2761a4e1ec1cb27`  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## DISEÑAR

Capturar el resultado NI producido durante la invocación de la capacidad del
caso ficticio, su material de entrada C0 y su `CapabilityExecution` terminal.
Mantener Negotiation Ladder como productor separado, sin inferir contenido de
negociación a partir de otros módulos.

## AUDITAR

`build_c0_bound_ni_ladder_invokers` valida el `AssessmentTraceBinding` contra
la compra y el contexto en cada invocación. La autoridad negociadora y el
contenido proceden de evidencia **sintética declarada**, no de una empresa
real. `decision_twin_reference` y `viability_reference` están ausentes; no
existe prueba causal NI↔Twin/VF ni de que NI derive su texto del Assessment C0.
La validación de la traza tampoco acredita la ejecución de otro invocador C0
en ese mismo plan.

## DEPURAR

Un productor C0-bound común alimenta al invocador existente y a la variante
observada. Esta fija compra y fuentes, valida trazas durante la llamada y
adapta exactamente el resultado capturado a la capacidad. Uso único y captura
solo después de éxito. El cierre conserva resultado, fuentes, huellas,
capacidad y terminal, con los límites causales explícitos en `false`.

## AUDITAR 2

El validador verifica el scope sintético, compra raíz, huellas, capacidad
terminal y repetición del productor desde las fuentes y bindings. Rechaza
contenido NI desprendido incluso con huellas recalculadas. Pruebas cubren
ambas variantes, mutación, compra extranjera, binding C0 alterado y uso único.
Las huellas terminales y el orden de capacidades no cambian.

## CERRAR

`material_nature=SYNTHETIC`, `qtg_mode_policy=SYNTHETIC_TEST_ONLY`,
`operational_path=FORBIDDEN`, `effect_scope=NO_OPERATIONAL_EFFECT` y
`decision_authority=false`. `AUTHORIZED` dentro del carrier es una
declaración de prueba; no constituye mandato de negociación externo.

## MATERIALIZAR

Código en `eios/rules/negotiation_provenance.py`,
`eios/core/reference_ni_observation.py` y el caso ejecutable. La exportación
JSON/HTML se realizará como unidad siguiente.

## CI

La suite completa y CI de la PR deben pasar antes de integrar.

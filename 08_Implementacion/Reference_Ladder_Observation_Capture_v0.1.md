# EIOS — Reference Negotiation Ladder Observation Capture v0.1

**Base:** `main @ 12515ae58e036ce5b621b23926e8a274a7f29749`  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## DISEÑAR

Capturar la estructura Ladder resultante de su invocación en el caso de
referencia, desde la reproducción NI vinculada a los mismos bindings C0.
Representar los pasos y las transiciones como estructura de contenido
preexistente; no constituyen instrucciones para un proveedor.

## AUDITAR

El invocador C0-bound existente valida las asociaciones de Assessment y Trace
en cada llamada, produce NI de nuevo y estructura Ladder. El contenido y la
autoridad son declaraciones ficticias. La reproducción NI interna de Ladder no
demuestra que el invocador NI separado haya ejecutado el mismo resultado en
el plan; el binding C0 tampoco demuestra derivación causal del contenido.

## DEPURAR

Se extrae la ruta interna compartida `_produce_c0_bound_ladder` y la usan
el invocador cerrado y el observado. Este último fija compra y fuentes,
produce Ladder una sola vez, adapta ese resultado a O1 y habilita la captura
únicamente tras una invocación exitosa. No admite un resultado NI o Ladder
desprendido como entrada.

## AUDITAR 2

El validador exige scope sintético, compra raíz, huellas, capacidad terminal
y reproducción desde las fuentes C0-bound. Rechaza cambios de estructura
incluso con huellas recalculadas. El fixture tiene tres pasos estructurales:
`OBJECTIVE`, `OPENING_REQUEST` y `FALLBACK`, una ruta lineal y dos transiciones.
Ambas variantes conservan las huellas terminales precedentes.

## CERRAR

`material_nature=SYNTHETIC`, `qtg_mode_policy=SYNTHETIC_TEST_ONLY`,
`operational_path=FORBIDDEN`, `effect_scope=NO_OPERATIONAL_EFFECT` y
`decision_authority=false`. El carrier `AUTHORIZED` solo describe evidencia
ficticia de prueba; Ladder no concede mandato ni realiza una negociación.

## MATERIALIZAR

Código en `eios/rules/negotiation_provenance.py`,
`eios/core/reference_ladder_observation.py` y el caso ejecutable.
La exportación JSON/HTML es una unidad posterior.

## CI

Suite completa y CI de la PR requeridas para integrar.

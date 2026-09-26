# EIOS — Material NI y Ladder de la empresa ficticia 002 v0.1

**Resultado de prueba:** Negotiation Intelligence plantea solicitar
información de fiabilidad que falta; Ladder ordena objetivo, petición
inicial y alternativa de esperar revisión humana. Es contenido sintético
de ensayo, sin mandato para contactar a nadie ni cerrar una compra.

## DISEÑAR → AUDITAR

Se reutiliza el Assessment/Trace C0 raíz propio del caso 002, que marca
indeterminado un requisito de suficiencia. La fuente de negociación declara
una autoridad **exclusivamente sintética**, evidencia identificada y
`trace_refs` iguales a la traza C0. `authority_state=AUTHORIZED` habilita el
contenido dentro del contrato de prueba; no representa autorización
empresarial u operacional. No se declaran hechos de proveedor ni ventajas
de precio como justificación negociadora.

## DEPURAR → AUDITAR 2

Los constructores observados existentes capturan NI y Ladder en llamadas
separadas. La prueba verifica la procedencia del bundle, la identidad del
contenido, la traza C0 exacta y las tres etapas de Ladder. Una modificación
del Assessment que rompe su fingerprint se rechaza antes de producir NI.
El binding confirma la procedencia de C0; no demuestra que el texto haya
sido generado automáticamente por C0 ni que Ladder consuma la ejecución
NI de la otra llamada.

## CERRAR → MATERIALIZAR → CI

Se añade `tests/test_second_synthetic_company_negotiation.py`. No se
modifican contratos, motores ni el runner 001. Son capturas aisladas de
prueba: aún falta una ejecución E2E 002 y su terminal. Se conservan
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.

La siguiente unidad debe auditar la composición de las ocho capacidades
antes de construir el runner 002, prestando atención al estado parcial de
Supplier Risk/Value y al resultado C0 de información insuficiente.
Verificación local focalizada: trece pruebas satisfactorias (NI/Ladder 002,
C0 002 y observaciones NI/Ladder 001). Integración sujeta a CI de PR.

# EIOS — Auditoría de material para invocadores de la empresa ficticia 002 v0.1

**Resultado:** la segunda empresa ya dispone de dataset, bundle y procedencia
sintética independientes. El runner de ocho capacidades aún necesita fuentes
propias de esa empresa. Las fábricas existentes se pueden reutilizar sin
alterar sus contratos; copiar las afirmaciones del expediente 001 produciría
una demostración engañosa.

## DISEÑAR → AUDITAR

Se revisaron `examples/reference_business_case_001.py`, sus preparadores y
`run_reference_operational_simulation`. La fachada valida la unión exacta de
bundle, procedencia, QTG y compra/contexto. El ejemplo 001 fija sus dos
fixtures, identificadores, versiones y fuentes de evidencia; por eso no es
un runner genérico de carpetas.

| Capacidad | Componente existente reutilizable | Material propio requerido para 002 |
|---|---|---|
| QTG | Productor y consumidor en `SYNTHETIC_TEST` / `TEST_ONLY`. | Bundle 002 y recibo ligado a ese bundle. La exploración local dio `APTO/ALTA`; falta observación cerrada en un runner 002. |
| PRICE | Constructor con procedencia y captura observada. | Transacciones de referencia, precios, cantidades, proveedores, validaciones, representatividad, suficiencia y metodología coherentes con 002. Los `REF-PRICE-TX-001/002` son afirmaciones del ejemplo 001. |
| TCO | `TCOInput(purchase_operation=...)` y captura observada. | Compra 002 extraída del bundle; este preparador no añade una hipótesis económica externa. |
| SUPPLIER_RISK_VALUE | Evaluador y constructor con procedencia/captura. | Ámbito `COMPANY-MOCK-002` y cualquier evaluación de riesgo/valor con evidencias y autoridad sintética propias. El `RELIABILITY=FAVORABLE` de 001 se declara con fuentes vacías y no es un hecho transferible. |
| C0 | Productor de suficiencia, regla autorizada `R-DAT-003`, assessment/trace y constructor observado. | Requirement set, clasificación y evidencia vinculados a decisión, escenario, snapshot y empresa 002; `base_result` justificado como entrada de prueba. `COMPRAR` en 001 no es una recomendación deducida por QTG. |
| DECISION_TWIN | Preparación y constructor de alternativas/captura existentes. | Escenarios hijos válidos 002, compras y trazas C0 propias, identificadores de representación 002. |
| SCENARIO_COORDINATION | Preparación O4/O2/O3 y constructor/captura existentes. | Política de generación 002 y dos escenarios hijos coherentes, cada uno con compra/contexto y assessment/trace C0 correspondientes. |
| NEGOTIATION_INTELLIGENCE + LADDER | Constructores ligados a C0 y capturas observadas. | Contenido de negociación 002, evidencia, autoridad **sintética** y referencias a la traza C0 exacta; Ladder consume esa fuente. El binding verifica la traza, pero no afirma que el texto se haya derivado automáticamente de C0. |

## DEPURAR → AUDITAR 2

**Dependencias concretas:** TCO puede prepararse directamente desde la compra
002. PRICE y Supplier Risk/Value necesitan declaraciones independientes de
material de prueba. C0 necesita su propio expediente de suficiencia; Scenario
Coordination y Decision Twin dependen de trazas C0 para los hijos. NI y Ladder
requieren una fuente de contenido y autoridad sintética ligada a C0. La
política terminal y los identificadores de observación también deben referirse
al caso 002.

La revisión distingue tres cosas que pueden confundirse en pantalla:

1. **Dato del fixture:** compra, identidad y finanzas serializadas en 002.
2. **Hipótesis declarada de prueba:** referencias de precio, assessment de
   proveedor, suficiencia y contenido de negociación que aún deben redactarse.
3. **Resultado calculado:** salida de cada capacidad al ejecutar esas fuentes.

No se presenta una hipótesis como si hubiera sido descubierta en el dataset.
Tampoco se usa el `APTO/ALTA` exploratorio de QTG como admisión operacional o
como autorización de compra.

## CERRAR → MATERIALIZAR → CI

Esta unidad cierra **solo el inventario de material**. Próxima unidad concreta:
preparar una fuente 002 mínima para TCO y capturar su resultado con el
constructor observado existente; validar identidad, fingerprint y ausencia de
efecto operacional. Después incorporar por separado las fuentes declarativas
de PRICE, proveedor, C0 y los hijos, hasta que el segundo E2E sea demostrable.
El paquete visual llegará tras verificar esas fuentes y la ejecución.

En todo tramo conservar
`SYNTHETIC · SYNTHETIC_TEST_ONLY · FORBIDDEN · NO_OPERATIONAL_EFFECT · decision_authority=false`.
Esta auditoría no modifica ejecutores, contratos ni fixtures.

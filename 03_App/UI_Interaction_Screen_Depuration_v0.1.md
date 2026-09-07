# EIOS — Depuración de Especificación de Pantalla de Interacción v0.1

**Estado:** DEPURACIÓN COMPLETADA
**Baseline:** `e3f096413fb5f9217b96c907f3e78e6a8f244d74`
**Fecha:** 2026-09-07

## Objetivo

Eliminar ambigüedades de implementación manteniendo intactos el Registro Maestro, el mapping campo→componente, la lógica de negocio y las salvaguardas.

## Controles

| ID | Control | Resultado |
|---|---|---|
| UI-SCR-D01 | Cada zona tiene una finalidad única y no solapada | PASS |
| UI-SCR-D02 | El orden de interacción no introduce dependencia funcional nueva | PASS |
| UI-SCR-D03 | INPUT, READONLY, CALCULATED, DECISION, TRACE y CONFIG conservan su comportamiento | PASS |
| UI-SCR-D04 | Los estados de pantalla no se confunden con Field_ID | PASS |
| UI-SCR-D05 | No se crean campos visuales auxiliares con semántica canónica | PASS |
| UI-SCR-D06 | Los estados compuestos conservan el comportamiento del mapping | PASS |
| UI-SCR-D07 | STK permanece informativo y sin autoridad matemática adicional | PASS |
| UI-SCR-D08 | ERROR e INSUFFICIENT_DATA no generan resultados ni campos ficticios | PASS |

## Reglas depuradas

1. Las zonas son contenedores de presentación; no son nuevas entidades de dominio.
2. El orden visual no implica que una zona pueda modificar los datos de otra salvo por las reglas ya autorizadas.
3. Los componentes se resuelven mediante el `Field_ID` del mapping.
4. Los estados `INITIAL`, `INPUT_REQUIRED`, `READY`, `EVALUATING`, `RESULT`, `INSUFFICIENT_DATA` y `ERROR` son estados de presentación.
5. Un estado de pantalla nunca puede utilizarse como sustituto de un `Field_ID`.
6. La zona de configuración queda separada de los datos de propuesta.
7. Resultado, recomendaciones y trazabilidad permanecen de salida/lectura según el mapping.
8. STK no obtiene autoridad cuantitativa por aparecer en la pantalla.

## Resultado

**DEPURACIÓN: PASS.** La especificación queda lista para AUDITAR 2.

No se modifica `main`.

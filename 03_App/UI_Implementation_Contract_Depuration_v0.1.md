# EIOS — Depuración del Contrato Implementable de UI v0.1

**Estado:** DEPURACIÓN COMPLETADA — 8/8 PASS
**Baseline:** `17607e65b7f07e01f5d5d9ef9a48a4783b26e02e`
**Fecha:** 2026-09-07

## Matriz de depuración

| ID | Control | Resultado |
|---|---|---|
| UII-D01 | Cada componente tiene una fuente documental identificable | PASS |
| UII-D02 | Props limitadas a datos y estado autorizado | PASS |
| UII-D03 | Eventos no ejecutan lógica de negocio en presentación | PASS |
| UII-D04 | Validaciones no amplían reglas del dominio | PASS |
| UII-D05 | Estados UI no se convierten en datos canónicos | PASS |
| UII-D06 | STK permanece fuera de la autoridad M01–M10 | PASS |
| UII-D07 | Trazabilidad no permite alterar evidencia histórica | PASS |
| UII-D08 | No se introducen Field_ID/Test_ID ni cambios de pruebas | PASS |

## Ajustes de implementación

1. Todo componente debe declarar su fuente de autoridad antes de ser implementado.
2. Ningún componente puede recibir una prop que contenga una regla de negocio implícita.
3. Los handlers solo coordinan interacción; la evaluación pertenece al mecanismo autorizado.
4. Los mensajes de validación deben derivar de restricciones existentes.
5. Los estados `INITIAL`, `INPUT_REQUIRED`, `READY`, `EVALUATING`, `RESULT`, `INSUFFICIENT_DATA` y `ERROR` son exclusivamente estados de presentación/interacción.
6. La representación STK queda desacoplada de cualquier cálculo M01–M10 no autorizado.
7. La trazabilidad es de lectura y no puede modificarse desde la UI.
8. La implementación no amplía el Plan de Pruebas.

## Resultado

**DEPURACIÓN: PASS — 8/8.**

El contrato queda preparado para AUDITAR 2.

No se modifica `main`.
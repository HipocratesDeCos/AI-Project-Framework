# EIOS — Depuración de Reconciliación del Inventario de Campos UI v0.1

**Estado:** DEPURACIÓN COMPLETADA
**Fecha:** 2026-09-06

## Objetivo

Convertir las reglas preliminares de reconciliación en criterios deterministas, sin modificar el Registro Maestro ni ampliar el alcance funcional.

## Controles

| ID | Control | Resultado |
|---|---|---|
| UI-FIR-D01 | Cada diferencia se resuelve por identidad semántica, no por similitud textual | PASS |
| UI-FIR-D02 | Un alias no genera un nuevo campo canónico | PASS |
| UI-FIR-D03 | Una diferencia de granularidad bloquea la materialización automática | PASS |
| UI-FIR-D04 | Los campos extra del inventario no adquieren autoridad | PASS |
| UI-FIR-D05 | Los campos ausentes se documentan sin modificar el registro | PASS |
| UI-FIR-D06 | Los campos calculados no se confunden con entradas | PASS |
| UI-FIR-D07 | Los campos STK siguen sujetos a su autoridad cuantitativa | PASS |
| UI-FIR-D08 | Ninguna reconciliación genera Test_ID ni altera el Plan de Pruebas | PASS |

## Reglas depuradas

1. La comparación se realiza contra el identificador y semántica del Registro Maestro.
2. Los nombres descriptivos del Excel pueden conservarse como alias de trabajo, nunca como autoridad.
3. Si un campo Excel agrupa o divide varios campos canónicos, queda `AMBIGUO` hasta resolución formal.
4. Ningún `EXTRA_EN_EXCEL` se incorpora automáticamente.
5. Ningún `FALTA_EN_EXCEL` provoca modificación automática del Registro Maestro.
6. Los campos derivados mantienen su estado canónico y no se convierten en inputs por conveniencia de UI.
7. STK permanece fuera de cualquier autorización cuantitativa implícita.

## Resultado

**DEPURACIÓN: PASS.** No se requiere modificación del Registro Maestro para cerrar esta fase. La reconciliación queda preparada para AUDITAR 2.

`main` no se modifica durante esta fase.

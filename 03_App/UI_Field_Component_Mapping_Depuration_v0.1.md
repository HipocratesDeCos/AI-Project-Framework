# EIOS — Depuración del UI Field ↔ Component Mapping v0.2

**Estado:** DEPURACIÓN COMPLETADA
**Baseline:** `423f729935ab4db6e27f5035d4b42ad8f77590fa`
**Fecha:** 2026-09-06

## Objetivo

Eliminar ambigüedades de implementación sin alterar la autoridad del Registro Maestro ni introducir lógica funcional nueva.

## Controles

| ID | Control | Resultado |
|---|---|---|
| UI-FCM-D01 | Cada Field_ID conserva exactamente su identidad canónica | PASS |
| UI-FCM-D02 | Cada campo tiene un componente primario determinista | PASS |
| UI-FCM-D03 | Los estados compuestos tienen comportamiento explícito | PASS |
| UI-FCM-D04 | La editabilidad no puede contradecir el estado canónico | PASS |
| UI-FCM-D05 | Los componentes calculados no crean fórmulas nuevas | PASS |
| UI-FCM-D06 | Los componentes de decisión no crean resultados adicionales | PASS |
| UI-FCM-D07 | TRACE permanece informativo y no editable | PASS |
| UI-FCM-D08 | STK permanece sin autoridad cuantitativa adicional | PASS |

## Reglas depuradas

1. La implementación utilizará `Field_ID` como clave estable de enlace.
2. El nombre mostrado puede variar por UX, pero el nombre canónico permanece inalterado en el contrato.
3. `INPUT/READONLY` requiere determinar el modo desde el origen autorizado; no se permite edición implícita.
4. `INPUT/CONFIG` se trata como control restringido y no como input libre.
5. `READONLY/CALCULATED` no autoriza recalcular desde la capa visual.
6. `DECISION_BADGE` solo representa resultados autorizados por el contrato.
7. `TRACE_PANEL` no permite edición de datos de trazabilidad.
8. `UI-STK-007` y `UI-STK-008` pueden tener representación visual, pero su cálculo permanece bloqueado hasta disponer de autoridad metodológica.

## Resultado

**DEPURACIÓN: PASS.** El mapping queda preparado para AUDITAR 2. No se modifica `main`, el Registro Maestro ni el Plan de Pruebas.

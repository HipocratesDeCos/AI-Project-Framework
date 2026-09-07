# EIOS — Depuración del UI Field ↔ Component Mapping v0.2

**Estado:** DEPURACIÓN COMPLETADA
**Baseline:** `423f729935ab4db6e27f5035d4b42ad8f77590fa`

## Controles

| ID | Control | Resultado |
|---|---|---|
| UI-FCM-D01 | Cada Field_ID conserva identidad canónica | PASS |
| UI-FCM-D02 | Cada campo tiene componente primario determinista | PASS |
| UI-FCM-D03 | Estados compuestos tienen comportamiento explícito | PASS |
| UI-FCM-D04 | Editabilidad compatible con estado canónico | PASS |
| UI-FCM-D05 | Componentes calculados no crean fórmulas nuevas | PASS |
| UI-FCM-D06 | Componentes de decisión no crean resultados adicionales | PASS |
| UI-FCM-D07 | TRACE es informativo y no editable | PASS |
| UI-FCM-D08 | STK no adquiere autoridad cuantitativa adicional | PASS |

## Reglas

1. `Field_ID` es la clave estable de enlace.
2. El nombre canónico permanece inalterado en el contrato.
3. `INPUT/READONLY` depende del origen autorizado; no existe edición implícita.
4. `INPUT/CONFIG` es control restringido.
5. `READONLY/CALCULATED` no autoriza recálculo desde la UI.
6. `DECISION_BADGE` solo representa resultados autorizados.
7. `TRACE_PANEL` no permite edición.
8. `UI-STK-007` y `UI-STK-008` permanecen sin autoridad metodológica de cálculo.

**Resultado: DEPURACIÓN PASS.**

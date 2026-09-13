# EIOS — Configuration Center UI Slice 1 — Depuración

**Fecha:** 2026-09-13  
**Resultado:** COMPLETADA

Incorporados los tres reajustes de Audit 1:

1. el contexto queda definido como carrier inmutable y no como autenticador;
2. actor, empresa y parámetro quedan ligados al contexto y no pueden sustituirse durante propuesta/confirmación;
3. solo un retorno real de `ParameterConfigurationCenter.apply_change(...)` puede producir `APPLIED`; toda excepción conserva código y falla cerrado.

No se amplió alcance ni autoridad.

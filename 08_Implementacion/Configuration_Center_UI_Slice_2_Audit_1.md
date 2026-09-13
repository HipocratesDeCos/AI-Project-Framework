# EIOS — Configuration Center UI Slice 2 — Audit 1

**Fecha:** 2026-09-13  
**Baseline auditado:** `b162dc9b5262abc469d6052eeef3308e58edf96e`  
**Dictamen:** APTO PARA DEPURACIÓN — 2 reajustes, 0 bloqueos

## A1 — Confirmación no debe aceptar identificadores paralelos

Si `ConfigurationConfirmationPanel` aceptara `company_id`, `parameter_id` o `actor` como strings separados, Presentation podría representar una identidad distinta de la contenida en `ConfigurationDetailViewModel`.

**Reajuste:** la confirmación debe contener la referencia al `ConfigurationDetailViewModel` y al `ChangeProposal`; no recibe identificadores duplicados.

## A2 — Propuesta no pendiente no debe producir panel de confirmación

Una propuesta puede existir mientras el usuario edita, pero no debe aparecer visualmente como una confirmación validada hasta que Slice 1 indique `AWAITING_CONFIRMATION`.

**Reajuste:** el builder crea `ConfigurationConfirmationPanel` exclusivamente cuando `state == "AWAITING_CONFIRMATION"` y existe propuesta. Si el estado exige confirmación y falta propuesta, falla cerrado mediante `ValueError`. En los demás estados no crea el panel de confirmación.

## Verificación transversal

- Slice 2 permanece presentacional.
- No crea autenticación, autorización, empresa, actor ni catálogo.
- No llama a `ParameterConfigurationCenter`.
- No modifica Slice 1.
- No toca Rules, CRC, SQL ni componentes decisionales cerrados.
- `None` y secuencia vacía permanecen distintos.

**Resultado:** incorporar A1–A2 y ejecutar Audit 2.

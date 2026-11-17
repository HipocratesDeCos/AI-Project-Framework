# EIOS — F6.8 · REANUDACIÓN SEGURA DESPUÉS DE PARADA

**Fecha:** 17/11/2026. **Base:** F6.7 cerrada en `main @ c2c3294effa4d301b70e532a5f191099b0e34b13`.

## 1. NECESIDAD

F6.7 demuestra que un fallo sobrevenido invalida el resultado F6.6 previo y devuelve `SAFE_STOPPED`.

Quedaba sin contrato la pregunta siguiente: **¿qué significa reanudar con seguridad después de una parada?**

F6.8 establece que reanudar NO significa continuar desde el recibo anterior. El recibo F6.6 invalidado y el `SAFE_STOPPED` son historia de auditoría. La recuperación requiere una comprobación externa completa nueva.

## 2. DISEÑO

Se amplía únicamente el mismo paquete externo `eios-onboarding-example==0.1.0` con:

- `recovery.py`: frontera explícita de recuperación;
- `recovery_demo.py`: revocación sintética, parada y recuperación tras nueva revisión;
- pruebas adversarias.

No se modifica el núcleo `eios/`, QTG, O1, admisión operacional ni motores canónicos.

## 3. REGLAS DE RECUPERACIÓN

`recover_after_safe_stop(...)` exige:

1. un recibo F6.7 exacto con estado `SAFE_STOPPED`;
2. el resultado F6.6 exacto que fue invalidado por ese recibo;
3. misma empresa, proyecto y snapshot de la cadena que se intenta recuperar;
4. un pin F6.5 vigente para el estado actual;
5. un manifiesto F6.6 coherente con ese pin;
6. una ejecución fresca de F6.5, que vuelve a revisar F6.3 y F6.4;
7. una evaluación F6.6 fresca y completa.

El resultado antiguo conserva siempre:

`stale_result_reusable=false`

Una recuperación satisfactoria produce exclusivamente:

`SYNTHETIC_RECOVERY_REVALIDATED`

con `fresh_chain_revalidated=true` y una referencia separada al fingerprint fresco.

## 4. CASOS QUE NO SE RECUPERAN

Si F6.7 paró por `CONTEXT_REBIND` —cambio de empresa, proyecto o snapshot— F6.8 no debe tratarlo como una recuperación de la misma cadena. Debe iniciarse una cadena nueva.

Si el proveedor, documento, permiso o registro siguen fallando, el resultado es:

`RECOVERY_BLOCKED`

El `SAFE_STOPPED` anterior no queda superado.

## 5. AUTORIDAD

Incluso una recuperación completa mantiene:

- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`

F6.8 no autentica empresas reales, no admite un expediente operacional y no reactiva QTG/O1.

## 6. CRITERIO DE CIERRE

F6.8 se cerrará únicamente con:

- regresión Python/SQL completa;
- pruebas adversarias de historial incorrecto, estado no resuelto, pin/manifiesto obsoleto y contexto distinto;
- ejecución de `recovery_demo` desde wheel auditado e instalación offline;
- validación Linux y Windows 3.12;
- diff sin cambios en `eios/`;
- PR verde en SHA exacto;
- merge;
- CI postmerge verde sobre el nuevo `main`.

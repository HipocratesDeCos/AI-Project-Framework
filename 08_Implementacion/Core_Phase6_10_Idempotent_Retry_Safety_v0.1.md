# EIOS — F6.10 · IDEMPOTENCIA Y RETRY SAFETY

**Fecha:** 17/11/2026  
**Base:** `main @ 970a4d970ad2b1f6491a06def8191e2b3039fc2b`

## 1. HUECO DETECTADO

F6.4 protege la custodia con escritura única: una segunda escritura sobre la misma identidad se rechaza siempre. F6.9 enlaza F6.6 → F6.7 → F6.8 en una historia verificable.

Faltaba distinguir dos situaciones operacionalmente distintas:

1. **retry idéntico** después de pérdida de respuesta, timeout o reinicio;
2. **segundo intento conflictivo** que pretende sustituir el estado ya custodiado.

Sin esa distinción, un consumidor que pierde el ACK después de una escritura correcta no puede recuperar de forma segura el recibo esperado.

## 2. CONTRATO F6.10

F6.10 añade una capa externa sobre F6.4/F6.9. No modifica la semántica write-once.

`record_lifecycle_event_retry_safe(...)` solo puede devolver:

- `CREATED`: el evento no existía y se custodió una vez;
- `REUSED_IDENTICAL`: la escritura ya existía y F6.4 verificó exactamente el mismo binding, digest y bytes.

Cualquier otro caso falla cerrado.

## 3. REGLAS

Un retry solo es reutilizable si:

- empresa, proyecto, snapshot y etapa son los mismos;
- el evento esperado produce el mismo SHA-256;
- F6.4 puede cargar el registro existente con ese digest esperado;
- los bytes almacenados coinciden exactamente con los bytes canónicos esperados;
- la autoridad continúa desactivada.

Nunca se sobrescribe, repara ni elimina un registro preexistente.

## 4. CASOS BLOQUEADOS

- mismo stage con contenido/fingerprint diferente;
- manifiesto F6.6 cambiado;
- registro corrupto;
- archivo parcial o JSON inválido;
- recibo previo de otra empresa;
- scope distinto;
- replay con autoridad elevada;
- cualquier digest diferente bajo la misma identidad.

## 5. REINICIO / PÉRDIDA DE ACK

Si una escritura terminó correctamente pero el proceso perdió el recibo antes de responder, un proceso nuevo puede repetir el mismo input. F6.10 reconstruye el mismo `LifecycleEventReceipt` únicamente después de que F6.4 confirme el registro exacto.

Esto hace segura la recuperación frente a **ack-loss / retry**, pero no convierte la demo local en un sistema transaccional distribuido.

## 6. LÍMITES

F6.10 sigue siendo sintético y local.

No implementa:

- consenso distribuido;
- locks multi-host;
- reloj confiable;
- exactly-once entre servicios;
- autenticación empresarial;
- autoridad de decisión;
- admisión operacional.

Se mantienen:

- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`

## 7. CRITERIO DE CIERRE

- pruebas positivas, negativas y adversarias;
- retry idéntico sin crear nuevos archivos;
- reinicio tras pérdida de ACK;
- rechazo de conflicto/tamper/parcial;
- historial F6.9 verificable después de retries;
- wheel externo offline;
- Linux/SQL y Windows 3.12 verdes;
- diff sin cambios en `eios/`;
- PR, merge y CI postmerge verdes.

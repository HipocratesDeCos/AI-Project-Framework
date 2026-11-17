# EIOS — F6.9 · LIFECYCLE INTEGRITY JOURNAL

**Fecha:** 17/11/2026. **Base:** F6.8 cerrada en `main @ c772ba1cad472e547b4d2e56f3f62e11eaa502eb`.

## 1. HUECO DETECTADO

F6.6 produce una preparación sintética; F6.7 puede invalidarla con `SAFE_STOPPED`; F6.8 puede producir una recuperación fresca.

Los resultados son deterministas, pero todavía no existía un contrato que custodiara **la secuencia completa como una historia única**. Un consumidor podía conservar resultados individuales sin demostrar su orden, su enlace o si faltaba un estado intermedio.

F6.9 cierra exclusivamente ese hueco.

## 2. PRINCIPIO

F6.9 no crea otro sistema de almacenamiento.

Reutiliza `SyntheticCustodyVault` de F6.4 para obtener las propiedades ya cerradas de escritura única, rechazo de duplicados, comprobación de digest y aislamiento por empresa/proyecto/snapshot.

Sobre esa primitive añade una semántica de tres eventos:

1. `F6_6_BASELINE`
2. `F6_7_SAFE_STOP`
3. `F6_8_RECOVERY`

Cada evento contiene el SHA-256 del evento anterior.

## 3. REGLAS

La historia completa solo se verifica si:

- el baseline es un `SYNTHETIC_REHEARSAL_COMPLETE` válido;
- el `SAFE_STOPPED` invalida exactamente ese baseline;
- la recuperación referencia exactamente el stop y el baseline anteriores;
- los tres eventos pertenecen a la misma empresa, proyecto y snapshot;
- los tres archivos siguen disponibles y coinciden con sus digests esperados;
- el orden es exactamente F6.6 → F6.7 → F6.8;
- ningún evento declara autoridad operacional.

Una historia correcta devuelve:

`SYNTHETIC_LIFECYCLE_HISTORY_VERIFIED`

## 4. ATAQUES QUE DEBE DETECTAR

- borrado de un evento;
- sustitución de bytes;
- reordenación;
- mezcla de empresas o snapshots;
- enlace a otro baseline;
- enlace a otro `SAFE_STOPPED`;
- intento de escribir dos estados diferentes en la misma etapa;
- promoción de `production_authorized`, `decision_authority` o ruta operacional.

## 5. LÍMITES

El journal es una demostración sintética local. El SHA-256 sirve como control de consistencia frente a un digest esperado por el host. No autentica por sí mismo al emisor, no proporciona tiempo de confianza y no convierte el directorio local en un archivo empresarial seguro.

F6.9 no modifica `eios/`, no activa QTG/O1 y no abre admisión operacional.

## 6. CRITERIO DE CIERRE

- pruebas positivas, negativas y adversarias;
- wheel externo auditado;
- ejecución offline independiente;
- Linux/SQL y Windows 3.12 verdes;
- diff sin cambios en el núcleo canónico;
- PR sobre SHA exacto;
- merge;
- CI postmerge verde en `main`.

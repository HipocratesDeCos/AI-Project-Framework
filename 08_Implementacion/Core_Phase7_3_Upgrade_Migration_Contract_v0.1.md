# EIOS — F7.3 · UPGRADE & MIGRATION CONTRACT

**Fecha:** 18/11/2026  
**Base:** `main @ de7d8c046fb58f2727bf0c40a405c22a3a6621d7`

## 1. OBJETIVO

F7.1 fijó la API pública y F7.2 fijó qué combinaciones de releases están certificadas. F7.3 define **cómo pasar de una combinación certificada a otra sin dejar un proyecto en estado híbrido**.

No se crea todavía una release 0.2.0. Se fija el procedimiento que deberá cumplir cualquier migración futura.

## 2. PRINCIPIO CENTRAL

**Queda prohibido actualizar encima de la instalación activa.**

Una migración válida debe mantener dos entornos separados:

- **source environment**: instalación actualmente certificada y sin modificar;
- **candidate environment**: instalación nueva, preparada en paralelo.

La conmutación solo puede producirse después de certificar completamente el candidato.

## 3. ESTADOS

La máquina de estados permitida es:

`SOURCE_ACTIVE → CANDIDATE_PREPARED → CANDIDATE_CERTIFIED → SWITCH_COMMITTED`

Después del switch existe una única ruta explícita de vuelta:

`SWITCH_COMMITTED → ROLLBACK_COMMITTED`

Los fallos previos al switch terminan en:

`MIGRATION_REJECTED`

No se admite:

- source → switch directo;
- candidato preparado → switch sin certificación;
- actualización parcial de paquetes;
- mezcla de versiones no certificada;
- mutación del entorno fuente.

## 4. EVIDENCIA OBLIGATORIA ANTES DEL SWITCH

Antes de conmutar deben existir, como mínimo:

1. fingerprint exacto del stack fuente;
2. recibo de certificación del entorno fuente;
3. fingerprint exacto del candidato;
4. certificación F7.2 del candidato;
5. recibo de instalación limpia del candidato;
6. regresión de consumidores existentes;
7. regresión del tercer dominio;
8. certificación Linux;
9. certificación Windows Python 3.12;
10. rollback anchor.

Si falta cualquiera, el switch se bloquea.

## 5. ROLLBACK

El rollback no significa “reinstalar deprisa lo antiguo”.

Debe existir una referencia verificable al entorno fuente que:

- permanezca sin modificar;
- conserve su fingerprint;
- conserve su recibo de certificación;
- pueda recuperarse sin reconstruir a partir de memoria o dependencias flotantes.

F7.3 no permite considerar rollback seguro si la migración incluye una transformación destructiva de datos o esquema sin evidencia específica adicional.

## 6. RELACIÓN CON F5.10

F5.10 ya exige instalaciones nuevas, aisladas, offline y hash-locked. F7.3 reutiliza esa filosofía y la eleva a contrato de ciclo de vida.

No se modifica F5.10 ni el Motor.

## 7. GATE EJECUTABLE

`tools/verify_f7_3_upgrade_migration.py` verifica:

- prohibición de upgrade in-place;
- prohibición de candidato no certificado por F7.2;
- bloqueo del switch si falta evidencia;
- obligatoriedad del rollback anchor;
- prohibición de mutar el entorno fuente;
- máquina de estados y transiciones exactas;
- ausencia de escalada de autoridad.

## 8. LÍMITES

F7.3 no ejecuta todavía una migración real entre versiones diferentes porque no existe una segunda release neutral certificada.

La prueba de referencia usa dos entornos separados con el mismo stack 0.1.0 para validar el **protocolo**, no para fingir una compatibilidad 0.1.0 → 0.2.0 inexistente.

## 9. AUTORIDAD

Sin cambios:

- `production_authorized=false`
- `decision_authority=false`
- `operational_path=FORBIDDEN`

## 10. CRITERIO DE CIERRE

F7.3 queda cerrada si:

- el contrato y la máquina de estados son verificables;
- los casos adversarios fallan correctamente;
- F7.1/F7.2 y regresiones previas permanecen verdes;
- Linux y Windows 3.12 permanecen verdes;
- no se modifica `eios/`;
- PR y CI post-merge son verdes sobre SHA exactos.

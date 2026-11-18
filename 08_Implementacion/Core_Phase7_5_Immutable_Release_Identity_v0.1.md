# EIOS — F7.5 · IMMUTABLE RELEASE IDENTITY & STABLE RELEASE CANDIDATE

**Fecha:** 18/11/2026  
**Base auditada:** `main @ 7a2de895505de1fe8066aff9f58c7a9529a4f714`

## 1. OBJETIVO

F7.1–F7.4 gobiernan API pública, compatibilidad, migración y deprecación. F7.5 cierra el riesgo restante: que dos conjuntos distintos de código o artefactos puedan ser tratados informalmente como la misma release.

F7.5 no modifica el Motor. Define una identidad de release **content-addressed**.

## 2. DOS IDENTIDADES

Una release tiene dos niveles:

### SOURCE RELEASE ID

Identifica de forma determinista:

- SHA Git exacto del checkout;
- versiones exactas de los cuatro paquetes neutrales;
- hashes de las políticas F7.1–F7.4;
- label del candidato;
- autoridad.

Linux y Windows construidos desde el mismo commit deben compartir este identificador.

### ARTIFACT RELEASE ID

Añade al SOURCE RELEASE ID:

- SHA-256 exacto del ZIP F5.10;
- SHA-256 de su `manifest.json`;
- plataforma;
- arquitectura;
- Python minor.

Por tanto, Linux y Windows comparten identidad fuente pero tienen identidades de artefacto diferentes.

## 3. REGLA DE INMUTABILIDAD

Los identificadores son SHA-256 de JSON canónico.

Por construcción:

**mismo release ID + payload diferente = rechazo.**

Cambiar cualquiera de estos elementos cambia la identidad:

- commit fuente;
- versión neutral;
- política F7;
- bytes del kit;
- manifiesto del kit;
- plataforma.

## 4. RELEASE CANDIDATE

La etiqueta humana inicial es:

`EIOS_MOTOR_RC_0_1_0`

Estado:

`RELEASE_CANDIDATE`

Esto no equivale a producción ni a una release 1.0 estable.

## 5. POR QUÉ NO SE INCRUSTA EL SHA DEL PROPIO COMMIT

Un archivo versionado no puede contener de forma estable el SHA del commit que lo contiene: modificar el archivo cambia el commit y crea una referencia circular.

Por ello el SHA se toma del checkout real de CI y se incorpora al recibo generado. GitHub Actions compara además `GITHUB_SHA` con `git rev-parse HEAD`.

## 6. EVIDENCIA

El recibo generado vincula:

- F7.1 — API pública;
- F7.2 — matriz de compatibilidad;
- F7.3 — migración;
- F7.4 — deprecación;
- stack neutral exacto;
- kit F5.10;
- plataforma y Python.

La CI solo ejecuta F7.5 después de que las puertas precedentes hayan pasado.

## 7. AUTORIDAD

Permanece expresamente:

- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`

## 8. LÍMITES

F7.5 no aporta:

- firma criptográfica del distribuidor;
- PKI o gestión de claves;
- una nueva versión 0.2.0;
- certificación operacional;
- datos empresariales reales.

Tampoco afirma reproducibilidad bit a bit entre plataformas: precisamente por eso cada artefacto tiene identidad propia.

## 9. CRITERIO DE CIERRE

F7.5 queda cerrada si:

- la identidad fuente es determinista;
- Linux y Windows del mismo SHA comparten SOURCE RELEASE ID;
- sus artefactos conservan ARTIFACT RELEASE ID propio;
- cualquier mutación cambia identidad o es rechazada;
- versiones no declaradas son rechazadas;
- no existe escalada de autoridad;
- no se modifica `eios/`;
- CI pre-merge y post-merge son verdes en Linux y Windows 3.12.

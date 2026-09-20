# EIOS — U1.5C · Designated Synthetic Preview Artifact — Audit v0.1

**Baseline:** `main @ 8767c173087d65f547360040f7ad5568177cb269`

**Estado:** AUDIT 1 → DEPURADO → AUDIT 2 DE MATERIALIZACIÓN SUPERADA ESTÁTICAMENTE — CI PENDIENTE

## 1. Objeto

Auditar la materialización U1.5C contra el cierre de viabilidad G03, U1.5A, U1.3/U1.4 y las fronteras de pureza EIOS.

## 2. Hallazgos de Audit 1

### M1 — segundo renderer

No se importa ni invoca el renderer U1.2 ni el builder de view-model.

**Resultado:** PASS. La fuente visual única es U1.3 revalidado.

### M2 — identidad confundida

El artifact U1.5C posee filename, schema y digest propios y exige que su digest difiera del source digest U1.3.

**Resultado:** PASS.

### M3 — notice solo en metadata

El NOTICE exacto y `SYNTHETIC · TEST_ONLY · NO OPERATIONAL EFFECT` se insertan físicamente en el body final.

**Resultado:** PASS.

### M4 — persistencia visual

La designación usa `position:sticky; top:0` dentro del mismo documento.

**Resultado:** PASS estructural. No depende de URL, tab, header, consola, landing o ventana paralela.

### M5 — superficies activas heredadas

La composición rechaza estructura inesperada y tokens de script, framing, forms, recursos externos y navegación activa antes de emitir U1.5C.

**Resultado:** PASS.

### M6 — CSP relajada

Se conserva una CSP deny-by-default con `script-src 'none'`, `connect-src 'none'`, `object-src 'none'` y `frame-ancestors 'none'`.

**Resultado:** PASS.

### M7 — revalidación insuficiente del delivery

Hallazgo: la primera materialización verificaba bytes y digest U1.5C pero el carrier no retenía suficiente evidencia para reconstruir toda la derivación hasta U1.5A durante el delivery.

Aunque el constructor estaba cerrado, una manipulación deliberada de lineage podía no quedar ligada a la admission original durante la revalidación final.

**Depuración aplicada:** el artifact retiene internamente una `LocalSyntheticPreviewAdmission` reconstruida y válida. El delivery:

- revalida esa admission;
- reconstruye U1.3/U1.4;
- recompone U1.5C;
- compara contenido exacto;
- revalida case id, case fingerprint y source digest.

**Resultado tras depuración:** PASS.

### M8 — I/O encubierto

El módulo solo importa dataclass, hashlib, hmac y U1.5A. No importa filesystem, socket, HTTP, subprocess, frameworks web ni motores.

**Resultado:** PASS.

### M9 — autoridad U1.5B

No existen servidor, route, URL, socket, path, save, send ni surface de autenticación.

**Resultado:** PASS. U1.5B continúa bloqueada.

## 3. Audit 2

### B1 — correspondencia con #229

#229 demostró que G03 era incompatible si se exigía mantener simultáneamente identidad de bytes U1.3 y delivery U1.4.

U1.5C no contradice ese cierre: crea deliberadamente un artefacto distinto.

**Resultado:** PASS.

### B2 — correspondencia U1.5A

La única entrada pública es `LocalSyntheticPreviewAdmission`. La factoría reconstruye la admission desde su case y compara sus U1.3/U1.4.

**Resultado:** PASS.

### B3 — derivación provenance-safe

La cadena del artifact no se acredita con hashes sueltos: la revalidación final vuelve a construir la derivación física.

**Resultado:** PASS después de M7.

### B4 — no contaminación U1.3/U1.4

No se modifican módulos ni contratos U1.3/U1.4. U1.5C solo consume sus objetos ya construidos.

**Resultado:** PASS.

### B5 — fail-closed

Una desviación de apertura/cierre HTML, número de anclajes, surface activa, admission, digest o lineage lanza error antes de obtener delivery.

**Resultado:** PASS.

### B6 — gate G03

Existe evidencia física en los bytes finales del notice y de los marcadores sintéticos dentro del mismo documento, con sticky positioning y sin framing.

**Resultado:** APTO PARA CIERRE FÍSICO condicionado a CI exact-head.

### B7 — U1.5B

Resolver G03 no constituye autorización de I/O.

**Resultado:** BLOQUEO PRESERVADO.

## 4. Matriz de pruebas materializada

| Grupo | Evidencia |
|---|---|
| determinismo | dos admissions registradas producen bytes y metadata idénticos |
| identidad | digest U1.5C distinto de source digest U1.3 |
| notice | notice y tres marcadores en body |
| persistencia | clase sticky y top:0 |
| contenido | se conservan secciones visuales U1.3 |
| CSP | política exacta deny-by-default |
| constructor | carriers factory-built y frozen |
| entrada | rechazo de tipos desprendidos |
| admission | manipulación case fingerprint/digest/artifact/delivery rechazada |
| lineage | case id, source digest y admission retenida revalidados |
| artifact | contenido y digest manipulados rechazados |
| HTML | surfaces activas y drift estructural rechazados |
| pureza | sin imports I/O/web/motores |
| API | sin routing/auth/decision actions |
| regresión | U1.5A no mutada por U1.5C |

## 5. Dictamen

**AUDIT 2 DE MATERIALIZACIÓN: SUPERADA ESTÁTICAMENTE — 0 bloqueadores pendientes de código.**

La condición restante es CI sobre el HEAD exacto de la PR.

Si la CI exact-head es satisfactoria:

- U1.5C podrá declararse técnicamente cerrada en la rama;
- U15-G03 podrá declararse físicamente resuelto en esa rama;
- U1.5B seguirá bloqueada hasta una autorización y ciclo propios;
- cualquier merge requerirá reconciliación de `main` y protección por SHA.

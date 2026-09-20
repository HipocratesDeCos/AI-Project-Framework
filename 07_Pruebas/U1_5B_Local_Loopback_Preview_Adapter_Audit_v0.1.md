# EIOS — U1.5B · Local Loopback Preview Adapter — Audit v0.1

**Baseline:** `main @ b400846d7ea9be07a774d19408cff8391dc0c385`

**Estado:** AUDIT 1

## 1. Objeto

Auditar el diseño U1.5B antes de cualquier implementación de socket o HTTP.

## 2. Hallazgos

### A1 — servir U1.4 tras resolver G03 con U1.5C

El contrato U1.5 original reservaba un endpoint para U1.4. Tras U1.5C, servir U1.4 volvería a perder la designación persistente.

**Depuración:** U1.5B consume y sirve exclusivamente `DesignatedSyntheticPreviewDelivery`.

### A2 — landing page + artifact

Dos rutas separarían advertencia y contenido, reintroduciendo el defecto G03.

**Depuración:** una única ruta entrega el documento U1.5C ya designado.

### A3 — bind por hostname

Usar `localhost` delegaría en resolución de nombres y podría variar entre IPv4/IPv6 o configuración local.

**Depuración:** bind literal a `127.0.0.1`.

### A4 — seleccionar puerto libre antes del bind

Buscar un puerto libre y cerrarlo antes de iniciar el servidor introduce TOCTOU.

**Depuración:** bind directo a puerto `0` y lectura del puerto real después del bind.

### A5 — Host permisivo

Un navegador local puede emitir requests con Host arbitrario, y DNS rebinding puede alcanzar servicios loopback.

**Depuración:** Host exacto `127.0.0.1:<port>`; no se acepta localhost ni dominios resolventes a loopback.

### A6 — query/path normalization

Normalizar rutas o aceptar query puede convertir múltiples request targets en equivalentes al endpoint autorizado.

**Depuración:** comparación exacta del request target; query, percent-encoding alternativo, absolute-form y traversal se rechazan.

### A7 — métodos con body

Aceptar POST o incluso GET con body amplía superficie innecesaria.

**Depuración:** solo GET/HEAD; body, Transfer-Encoding y Content-Length positivo se rechazan.

### A8 — HEAD tratado como GET truncado

Ejecutar la misma ruta y luego descartar body puede ser correcto, pero debe conservar Content-Length representacional.

**Depuración:** HEAD comparte metadata de GET, cuerpo vacío y mismo Content-Length del artefacto.

### A9 — CORS

Agregar ACAO facilitaría lectura desde páginas web locales o remotas que alcancen loopback.

**Depuración:** ausencia total de CORS permisivo.

### A10 — servidor estándar con headers/logging automáticos

Librerías estándar pueden añadir `Server`, `Date` o access logs.

**Depuración:** el diseño exige auditar y minimizar esos extras; no se permite identificación de producto ni persistencia de logs. Cualquier header inevitable debe documentarse y no alterar los headers semánticos U1.5C.

### A11 — background thread

Un `serve_forever` en thread puede sobrevivir al objeto llamador y convertir la preview en servicio semipersistente.

**Depuración:** lifecycle explícito, foreground por defecto y cierre idempotente. Si tests requieren thread auxiliar, debe quedar confinado al harness.

### A12 — autenticación inventada

Añadir token “por seguridad” ampliaría diseño, persistencia y manejo de secretos sin necesidad para datos exclusivamente sintéticos.

**Depuración:** no auth; loopback se declara contención, no identidad.

### A13 — datos reales futuros

Una API genérica podría reutilizarse con otro delivery.

**Depuración:** tipo exacto U1.5C y perfil fijo; no hay overload de bytes ni delivery U1.4.

## 3. Audit 2 — coherencia transversal

### B1 — U1.5A

U1.5B no consume fixture ni admission directamente.

**Resultado:** PASS.

### B2 — U1.5C

La única representación servida conserva notice físico, sticky designation, digest propio y CSP deny-by-default.

**Resultado:** PASS.

### B3 — G03

No se depende de ruta, tab, landing, iframe o wrapper para la advertencia.

**Resultado:** PASS.

### B4 — no operación

El diseño no ejecuta motores ni acepta payload empresarial.

**Resultado:** PASS.

### B5 — pureza previa a I/O

La construcción del adapter puede mantenerse pura; el socket se reserva para runtime explícito.

**Resultado:** PASS.

### B6 — red

La única red permitida es listen/accept en `127.0.0.1`; no hay connect saliente.

**Resultado:** PASS.

### B7 — persistencia

No se requiere filesystem, DB, logs persistentes, cache o sesión.

**Resultado:** PASS.

### B8 — protocolos

HTTP/1.x mínimo con GET/HEAD es suficiente; no se requiere TLS, HTTP/2, async, websocket o chunking.

**Resultado:** PASS.

## 4. Matriz obligatoria para materialización

| Grupo | Evidencia mínima |
|---|---|
| construcción | solo acepta `DesignatedSyntheticPreviewDelivery` exacto |
| revalidación | delivery manipulado falla antes del bind |
| bind | socket queda en `127.0.0.1` |
| puerto | puerto real no fijo y asignado con `0` |
| GET | status/headers/body corresponden a U1.5C |
| HEAD | mismo status/headers, body vacío |
| ruta | única ruta exacta |
| métodos | POST/PUT/PATCH/DELETE/OPTIONS etc. → 405 |
| query | query y variantes → 404 |
| Host | solo `127.0.0.1:<port>` |
| body | GET/HEAD con body → rechazo |
| CORS | sin ACAO |
| cookies | sin Set-Cookie |
| cache | no-store preservado |
| CSP | exacta U1.5C |
| logging | sin access log persistente |
| lifecycle | start/stop y close idempotente |
| cierre | conexión posterior al close falla |
| pureza | sin filesystem/browser/motores/outbound connect |
| regresión | suite completa permanece verde |

## 5. Dictamen

**AUDIT 1 + AUDIT 2 DEL DISEÑO: SUPERADAS — 0 bloqueadores documentales.**

U1.5B es materializable sin reabrir U1.2–U1.5C.

La siguiente fase legítima es materialización del adapter loopback con pruebas reales de socket sobre `127.0.0.1`, manteniendo estrictamente la superficie definida en este contrato.

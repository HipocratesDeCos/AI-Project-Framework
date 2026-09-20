# EIOS — U1.5B · Local Loopback Preview Adapter — Contract v0.1

**Baseline:** `main @ b400846d7ea9be07a774d19408cff8391dc0c385`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → MATERIALIZADO → AUDITORÍA FÍSICA SUPERADA — CI PR REGISTRADA

## 1. Propósito

U1.5B define el adaptador local mínimo que podrá exponer una única vista sintética U1.5C mediante HTTP loopback efímero.

Esta unidad no ejecuta EIOS, no produce nuevos resultados, no transforma contenido visual y no admite material operacional.

## 2. Fuente única autorizada

La única entrada admisible será un objeto exacto:

`DesignatedSyntheticPreviewDelivery`

producido por U1.5C.

U1.5B no acepta:

- `LocalSyntheticPreviewAdmission` directamente;
- `VerticalMVPReadOnlyArtifact`;
- `VerticalMVPReadOnlyDelivery`;
- bytes HTML libres;
- mappings;
- paths;
- URLs;
- hashes o metadata desprendida.

Antes de servir cualquier respuesta, el adaptador deberá reconstruir o revalidar U1.5C mediante su factoría pública de delivery y exigir igualdad exacta de status, headers, body, size y digest.

## 3. Cambio respecto al contrato U1.5 original

El diseño inicial de U1.5 reservaba una ruta que servía U1.4. Esa opción queda superada por U1.5C.

U1.5B servirá exclusivamente el delivery U1.5C designado. No expondrá U1.3/U1.4 directamente ni creará una landing page separada.

La designación sintética persistente forma parte de los bytes U1.5C, por lo que no se requiere framing, wrapper, tab auxiliar ni modificación de CSP.

## 4. Perfil operativo

Nombre exacto:

`LOCAL_SYNTHETIC_PREVIEW`

Propiedades obligatorias:

- bind IPv4 explícito a `127.0.0.1`;
- puerto `0` en creación para asignación efímera por el sistema;
- lectura del puerto efectivo solo después del bind;
- proceso foreground;
- lifecycle explícito start/stop;
- un solo delivery U1.5C inmutable por instancia;
- sin background daemon persistente;
- sin autostart;
- sin apertura automática de navegador;
- sin filesystem;
- sin uploads;
- sin request body;
- sin cookies;
- sin sesiones;
- sin autenticación;
- sin CORS permisivo;
- sin compresión;
- sin cache intermedia;
- sin transformación del body;
- sin logging persistente;
- sin proxying;
- sin DNS/hostname resolution para el bind;
- sin escucha en `0.0.0.0`, LAN o interfaz pública.

Loopback se considera contención técnica, no autenticación.

## 5. Ruta única

Ruta exacta autorizada:

`/eios/local-synthetic-preview`

No existen rutas auxiliares, health endpoints, index, static, favicon, API, assets o directory listing.

Comportamiento:

- `GET` → status y body U1.5C exactos;
- `HEAD` → mismo status y headers de GET, body vacío;
- cualquier otra ruta → `404`;
- cualquier otro método → `405`;
- query string → `404`;
- absolute-form request target → rechazo;
- path traversal, percent-encoded alternativo o normalización equivalente → rechazo;
- request body presente → rechazo;
- `Transfer-Encoding` presente → rechazo;
- `Content-Length` distinto de ausencia o cero → rechazo.

No se realiza redirect.

## 6. Host y origen

El request debe usar como Host efectivo exactamente el loopback y puerto real de la instancia:

`127.0.0.1:<port>`

Se rechazan:

- `localhost`;
- hostname arbitrario;
- dominio que resuelva a loopback;
- Host sin puerto;
- puerto distinto;
- múltiples cabeceras Host;
- Host inválido.

No se usa DNS rebinding como mecanismo legítimo de acceso.

No se devuelve `Access-Control-Allow-Origin`.

## 7. Response contract

Para `GET`, U1.5B transmite:

- status exacto U1.5C;
- headers semánticos U1.5C exactos;
- body exacto U1.5C;
- digest recomputable idéntico al delivery U1.5C.

El adaptador puede añadir únicamente cabeceras estrictamente de framing HTTP necesarias por la librería subyacente si son inevitables y están documentadas. No puede modificar:

- `Content-Type`;
- `Content-Length`;
- `Content-Disposition`;
- `Cache-Control`;
- `X-Content-Type-Options`;
- `Referrer-Policy`;
- `Content-Security-Policy`.

No añade cookies, ETag, Last-Modified, Server identificable por producto, CORS o cache headers adicionales.

## 8. HEAD

`HEAD` devuelve:

- mismo status que GET;
- mismas cabeceras de representación, incluido `Content-Length` del GET;
- body vacío.

No se recalcula ni transforma el contenido.

## 9. Lifecycle

La futura API deberá separar construcción y ejecución:

```python
build_local_synthetic_preview_adapter(
    delivery: DesignatedSyntheticPreviewDelivery,
) -> LocalSyntheticPreviewAdapter
```

El carrier resultante será inmutable y sin side effects.

La apertura efectiva del socket ocurrirá solo mediante una acción explícita de runtime, por ejemplo:

```python
serve_local_synthetic_preview(adapter) -> LocalSyntheticPreviewRuntime
```

El runtime:

- hace bind una sola vez;
- conserva host fijo `127.0.0.1`;
- obtiene puerto efímero del socket;
- no se reconfigura;
- expone estado mínimo de lifecycle;
- debe poder cerrarse idempotentemente;
- al cerrar, deja de aceptar conexiones;
- no reinicia automáticamente.

La API exacta de runtime se fijará durante materialización; no se autoriza todavía código.

## 10. Concurrencia y límites

La implementación deberá minimizar superficie:

- una conexión o manejo secuencial es suficiente;
- no se requiere thread pool;
- no se requiere async;
- no se requiere WebSocket;
- no se requiere keep-alive;
- no se requiere chunked transfer;
- no se requiere TLS para loopback sintético;
- no se requiere HTTP/2.

Si la librería elegida añade concurrencia implícita o comportamiento extra, deberá auditarse y desactivarse cuando sea posible.

## 11. Errores

El adaptador falla cerrado:

- tipo de delivery incorrecto → `TypeError`;
- delivery manipulado o inconsistente → `ValueError`;
- bind no loopback o configuración inválida → error antes de servir;
- request inválido → respuesta 4xx sin body sensible;
- excepción interna → 500 genérico, sin traceback al cliente;
- ninguna excepción debe volcar el body sintético completo a logs persistentes.

## 12. No persistencia y logging

No se escriben:

- archivos;
- access logs persistentes;
- body;
- headers completos;
- identifiers del caso;
- fingerprints;
- digests.

La implementación puede suprimir completamente el logging del servidor estándar.

## 13. Seguridad de superficie

U1.5B no debe:

- importar motores EIOS;
- ejecutar Rules/CRC/Scenario/Decision Twin/PRICE;
- leer environment secrets;
- cargar configuración empresarial;
- leer filesystem;
- abrir browser;
- resolver DNS;
- llamar red saliente;
- aceptar conexiones no loopback;
- aceptar contenido operacional;
- convertir loopback en claim de autenticación.

## 14. Criterio de cierre de diseño

El diseño puede cerrarse si una auditoría demuestra:

1. fuente única U1.5C;
2. revalidación provenance-safe antes de I/O;
3. bind solo a `127.0.0.1`;
4. puerto efímero real;
5. ruta y método cerrados;
6. Host estricto;
7. body GET byte-identical;
8. HEAD sin body y headers equivalentes;
9. ausencia de filesystem, auth, cookies, CORS, browser, persistencia y salida de red;
10. lifecycle explícito y cierre idempotente;
11. ninguna reapertura U1.2–U1.5C.

La materialización requerirá un ciclo separado y pruebas de socket reales sobre loopback.


## 15. Materialización física

La implementación queda contenida en:

- `eios/frontend/visual/local_synthetic_preview_adapter.py`;
- export explícito en `eios/frontend/visual/__init__.py`;
- `tests/test_local_synthetic_preview_adapter.py`;
- hardening mínimo U1.5C en `designated_synthetic_preview.py` para retener el artifact exacto dentro del delivery;
- prueba de regresión U1.5C que fija `delivery → artifact`.

La cadena física es:

```text
DesignatedSyntheticPreviewDelivery
→ artifact U1.5C retenido
→ reconstrucción U1.5C desde U1.5A
→ LocalSyntheticPreviewAdapter
→ HTTPServer(127.0.0.1, 0)
→ /eios/local-synthetic-preview
```

La construcción del adapter no abre sockets. El socket solo se abre mediante `serve_local_synthetic_preview`.

## 16. Evidencia CI de materialización

La PR #232 ejecutó la suite completa sobre el código materializado:

- **1589 passed**;
- **8 warnings** preexistentes;
- validaciones SQL C0 / Decision Versioning / Parameter Configuration: **SUCCESS**.

La integración queda condicionada a una CI final sobre el HEAD exacto después de fijar esta documentación.

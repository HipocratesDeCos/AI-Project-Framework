# EIOS — U1.4 · Controlled Visual Delivery Boundary — Contract v0.1

**Baseline:** `main @ 0ef51860c9346e3c703a4f90cd9bc0624dd7c2d4`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → CERRADO TÉCNICAMENTE — CI PENDIENTE

## 1. Propósito

Materializar una frontera de entrega controlada y agnóstica de framework para el artefacto HTML read-only cerrado en U1.3.

```text
VerticalMVPReadOnlyArtifact
        ↓
verificación de integridad de transporte
        ↓
VerticalMVPReadOnlyDelivery
        ↓
partes de respuesta HTTP inmutables
```

U1.4 describe una respuesta transportable. No abre sockets, no atiende peticiones, no escribe archivos y no ejecuta el Vertical.

## 2. Entrada única

La única entrada autorizada es una instancia exacta de `VerticalMVPReadOnlyArtifact` producida por U1.3.

U1.4 no acepta:

- view-models;
- HTML `str` o `bytes` arbitrarios;
- modelos de dominio;
- `VerticalMVPSupportResult`;
- invocadores o callbacks;
- rutas, file handles, URLs o claves de almacenamiento;
- cabeceras aportadas por el llamador.

## 3. Objeto público

`VerticalMVPReadOnlyDelivery` será un objeto inmutable y factory-built que conservará:

- `status_code = 200`;
- secuencia ordenada e inmutable de cabeceras HTTP;
- cuerpo exacto del artefacto U1.3;
- `content_sha256` ya verificado, exclusivamente como integridad de contenido.

El constructor directo permanecerá cerrado.

## 4. Builder público

`build_vertical_mvp_readonly_delivery(artifact)` deberá:

1. exigir el tipo exacto U1.3;
2. verificar `size_bytes == len(content)`;
3. recalcular SHA-256 sobre los bytes y exigir igualdad con `content_sha256`;
4. exigir media type y filename canónicos U1.3;
5. conservar los bytes sin transformación;
6. generar exclusivamente cabeceras fijas derivadas de propiedades de transporte verificadas;
7. devolver el descriptor completo o fallar de forma explícita;
8. no realizar I/O.

No existe fallback, respuesta vacía ni conversión de errores a `200`.

## 5. Cabeceras autorizadas

La respuesta declarada contiene exactamente:

- `Content-Type: text/html; charset=utf-8`;
- `Content-Length` derivado de los bytes;
- `Content-Disposition: inline; filename="eios-vertical-mvp-readonly.html"`;
- `Cache-Control: no-store`;
- `X-Content-Type-Options: nosniff`;
- `Content-Security-Policy` restrictiva:
  - `default-src 'none'`;
  - `style-src 'unsafe-inline'` únicamente para el CSS estático embebido por U1.2;
  - `img-src 'none'`;
  - `script-src 'none'`;
  - `connect-src 'none'`;
  - `object-src 'none'`;
  - `base-uri 'none'`;
  - `form-action 'none'`;
  - `frame-ancestors 'none'`.

El llamador no puede añadir, sustituir o eliminar cabeceras dentro de U1.4.

## 6. Semántica de entrega

`as_response_parts()` expone:

```text
(status_code, headers, body)
```

como tupla de valores inmutables y agnósticos de framework.

Esta superficie:

- no es un servidor HTTP;
- no es un endpoint;
- no selecciona host, puerto, ruta o método;
- no autentica usuarios;
- no decide quién puede recibir el artefacto;
- no registra ni persiste la entrega;
- no garantiza que un adaptador externo haya transmitido los bytes.

## 7. Integridad ≠ autoridad

La reverificación de `content_sha256` detecta alteraciones del artefacto antes de describir su entrega.

No constituye:

- firma digital;
- autenticación;
- autorización;
- provenance EIOS;
- identidad decisional;
- aprobación humana;
- evidencia de recepción;
- prueba de transmisión por red.

## 8. Fronteras

No se autoriza:

- `http.server`, WSGI, ASGI, FastAPI, Flask, Django o servidor equivalente;
- sockets o networking;
- filesystem, descarga, exportación o almacenamiento;
- cookies, sesiones, tokens, CORS o autenticación;
- compresión, streaming, rangos o caché;
- JavaScript;
- transformación, minificación o reserialización del HTML;
- acceso a Application Boundary, O1 o motores EIOS;
- ejecución, recomendación o decisión.

## 9. Pruebas mínimas

- cuerpo idéntico byte a byte al artefacto U1.3;
- estado y cabeceras exactos;
- `Content-Length` exacto;
- CSP restrictiva completa;
- inmutabilidad y constructor cerrado;
- determinismo;
- rechazo de tipos no autorizados;
- rechazo fail-closed de tamaño, hash, media type o filename alterados;
- ausencia de mutación del artefacto;
- ausencia de filesystem, red, framework web y motores;
- ausencia de campos de identidad decisional o autenticación.

## 10. Criterio de cierre

U1.4 queda cerrada cuando el artefacto U1.3 puede convertirse en partes de respuesta HTTP verificadas, deterministas e inmutables sin introducir serving, persistencia, autenticación ni autoridad funcional.

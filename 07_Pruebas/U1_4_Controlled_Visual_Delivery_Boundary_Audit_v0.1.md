# EIOS — U1.4 Controlled Visual Delivery Boundary — Audit v0.1

**Baseline:** `main @ 0ef51860c9346e3c703a4f90cd9bc0624dd7c2d4`

**Objeto:** auditar la frontera de entrega U1.4 antes y después de su materialización.

## AUDITAR

### A1 — descriptor HTTP ≠ servidor

Una implementación con sockets, WSGI/ASGI o framework web convertiría Presentation en frontera de ejecución y operación.

**Depuración:** U1.4 solo produce partes inmutables de respuesta. No escucha, enruta ni transmite.

### A2 — entrega ≠ persistencia

Aceptar rutas, directorios, file handles o métodos `save/export/download` reabriría la prohibición de I/O de U1.3.

**Depuración:** entrada única `VerticalMVPReadOnlyArtifact`; salida única en memoria.

### A3 — bytes arbitrarios

Aceptar `str` o `bytes` permitiría saltar U1.2/U1.3 y servir contenido no autorizado.

**Depuración:** se exige el tipo exacto U1.3 y se reverifican tamaño, SHA-256, media type y filename.

### A4 — cabeceras controladas por el llamador

Cabeceras dinámicas permitirían debilitar CSP, habilitar caché o inyectar un filename.

**Depuración:** conjunto cerrado y determinista; U1.4 no recibe headers.

### A5 — HTML activo o exfiltración

Aunque U1.2 no contiene JavaScript, un contexto de navegador debe declarar una política defensiva.

**Depuración:** CSP deny-by-default; solo se admite estilo inline requerido por el documento autosuficiente. Scripts, red, objetos, imágenes, formularios y framing quedan bloqueados.

### A6 — hash como firma o identidad

Reexponer el digest podría elevarlo a firma, autenticación o identidad decisional.

**Depuración:** conserva el nombre `content_sha256`, limitado a integridad de bytes, sin `ETag`, firma, token ni alias de provenance.

### A7 — mutabilidad anidada

Un `dict` de cabeceras dentro de una dataclass frozen seguiría siendo mutable.

**Depuración:** las cabeceras se conservan como tupla de pares y `as_response_parts()` devuelve estructuras inmutables.

### A8 — transformación del cuerpo

Compresión, normalización o re-encoding romperían la identidad con U1.3.

**Depuración:** el cuerpo es exactamente `artifact.content`; no se decodifica ni recodifica.

### A9 — errores convertidos en respuesta válida

Capturar fallos de integridad y emitir un cuerpo vacío con `200` ocultaría corrupción.

**Depuración:** toda inconsistencia lanza error antes de construir el descriptor.

### A10 — autenticación implícita

Cookies, sesiones, CORS o cabeceras de identidad aparentarían resolver una autoridad no diseñada.

**Depuración:** U1.4 no autentica ni autoriza. La selección de destinatario queda fuera de alcance.

## DEPURAR

La forma autorizada queda reducida a:

```text
U1.3 artifact
  ↓ verify transport invariants
exact bytes + fixed headers
  ↓
immutable response descriptor
```

No se incorpora otro paso.

## Dictamen Audit 1

**SUPERADA — 0 bloqueadores.**

U1.4 es implementable sin datos operacionales ni framework web si se mantiene como adaptador puro de transporte en memoria y no reclama serving, autenticación o persistencia.

## AUDITAR 2 — implementación materializada

### Delta físico

La rama añade/modifica únicamente:

- contrato U1.4;
- este registro;
- `eios/frontend/visual/vertical_mvp_delivery.py`;
- export explícito en `eios/frontend/visual/__init__.py`;
- `tests/test_vertical_mvp_readonly_delivery.py`.

No se modifica U1.2, U1.3, U1.1, Application Boundary, O1, Vertical MVP, Rules, CRC, Scenario, Twin, Finance, QTG, NI/Ladder, SQL, reglas o parámetros.

### Verificación estática

La implementación:

1. acepta únicamente el tipo exacto U1.3;
2. reverifica media type, filename, tamaño y SHA-256;
3. reutiliza los bytes sin transformación;
4. construye estado y cabeceras mediante constantes cerradas;
5. conserva cabeceras en una tupla de pares;
6. cierra el constructor directo;
7. no recibe headers, rutas, URLs, métodos o callbacks;
8. no captura errores para fabricar respuestas válidas;
9. no importa filesystem, networking, framework web ni motores EIOS;
10. no abre una frontera de ejecución, persistencia o autenticación.

### Cobertura materializada

Las pruebas verifican:

- identidad byte a byte U1.3 → U1.4;
- status y cabeceras exactos;
- política CSP cerrada;
- determinismo e inmutabilidad;
- constructor directo cerrado;
- rechazo de entradas arbitrarias;
- fail-closed ante alteración de cada invariante U1.3;
- no mutación del artefacto;
- ausencia de aliases decisionales/autenticación;
- ausencia de imports y primitivas de I/O/serving.

**AUDITAR 2: SUPERADA — 0 bloqueadores.**

## CERRAR → MATERIALIZAR → CI

U1.4 queda **CERRADA TÉCNICAMENTE — CI PENDIENTE**.

La unidad materializa una descripción de entrega controlada; no materializa la entrega real.

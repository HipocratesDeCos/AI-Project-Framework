# EIOS — U1.3 · Read-Only Visual Artifact — Contract v0.1

**Baseline:** `main @ 8bb0bb48c361991548b6340150747b9ced7ffe05`

**Estado:** DISEÑADO — AUDITORÍA 1 PENDIENTE

## 1. Propósito

Materializar una frontera de empaquetado reproducible para el HTML read-only producido por U1.2.

```text
authorized Vertical MVP view-model
        ↓
render_vertical_mvp_readonly(...)
        ↓
UTF-8 bytes
        ↓
VerticalMVPReadOnlyArtifact
```

U1.3 no ejecuta el Vertical, no sirve HTTP, no persiste archivos y no modifica el HTML U1.2.

## 2. Objeto público

`VerticalMVPReadOnlyArtifact` será un objeto inmutable y factory-built que conservará:

- media type fijo `text/html; charset=utf-8`;
- nombre de archivo orientativo fijo y no identificador;
- bytes exactos del render U1.2;
- tamaño exacto en bytes;
- SHA-256 de contenido.

El constructor directo permanecerá cerrado.

## 3. Builder público

`build_vertical_mvp_readonly_artifact(view_model)`

deberá:

1. aceptar únicamente el mismo `Mapping` autorizado por U1.2;
2. llamar a `render_vertical_mvp_readonly`;
3. codificar exactamente una vez en UTF-8;
4. calcular SHA-256 de esos bytes;
5. devolver el artefacto completo o lanzar el error original del renderer;
6. no escribir en filesystem ni red.

## 4. Semántica del SHA-256

El hash acredita exclusivamente identidad de los bytes renderizados.

No es:

- `decision_fingerprint`;
- `input_fingerprint`;
- Trace;
- versión de decisión;
- prueba de provenance del Vertical;
- firma digital;
- autenticación;
- aprobación;
- autoridad operacional.

Se denominará `content_sha256` para evitar ambigüedad.

## 5. Inmutabilidad

El artefacto será `frozen=True`.

Los bytes son inmutables y se devolverán sin reconstrucción semántica.

`to_metadata()` podrá exponer únicamente metadatos de transporte:

- media type;
- filename;
- size;
- content SHA-256.

No incluirá resultado CRC, estado de reglas, escenarios ni contenido decisional duplicado.

## 6. Determinismo

Un mismo view-model debe producir exactamente:

- mismos bytes;
- mismo tamaño;
- mismo SHA-256;
- mismos metadatos.

Un cambio material en el view-model que altere el render debe alterar `content_sha256`.

## 7. Fronteras

No se autoriza:

- filesystem;
- HTTP;
- servidor web;
- almacenamiento;
- caché;
- subida/descarga;
- browser automation;
- ejecución JavaScript;
- dominio EIOS adicional;
- validación de provenance;
- firma criptográfica;
- cifrado;
- recomendación o decisión.

## 8. Pruebas mínimas

- bytes = `render_vertical_mvp_readonly(view).encode("utf-8")`;
- SHA-256 reproducible;
- metadatos exactos;
- constructor cerrado;
- inmutabilidad;
- cambio material → hash distinto;
- propagación fail-closed del renderer;
- ausencia de filesystem/red/motores;
- contenido malicioso permanece escapado porque U1.3 no transforma el HTML.

## 9. Criterio de cierre

U1.3 queda cerrada cuando el artefacto permite transportar/verificar exactamente el HTML U1.2 sin introducir persistencia, autoridad ni identidad paralela.

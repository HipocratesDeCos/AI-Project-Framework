# EIOS — U1.3 Read-Only Visual Artifact — Audit v0.1

**Baseline:** `main @ 8bb0bb48c361991548b6340150747b9ced7ffe05`

**Objeto:** auditar la frontera de empaquetado U1.3 antes de implementación.

## AUDITAR

### A1 — hash de contenido ≠ identidad decisional

Un SHA-256 del HTML podría confundirse con `decision_fingerprint`, `input_fingerprint` o Trace.

**Depuración:** el único nombre autorizado es `content_sha256`. Contrato, API y tests deben rechazar cualquier alias de identidad decisional.

### A2 — packaging ≠ persistence

Aceptar rutas, directorios, file handles o métodos `save/write/export` convertiría U1.3 en una frontera de I/O.

**Depuración:** U1.3 solo devuelve bytes y metadatos. No importa `pathlib`, `os`, `tempfile`, `shutil`, networking o frameworks web.

### A3 — no revalidar dominio

El artefacto no debe inspeccionar CRC, Rules, escenarios o capacidades.

**Depuración:** delega totalmente en `render_vertical_mvp_readonly` y solo opera sobre el string resultante.

### A4 — doble serialización

Recrear HTML desde payload o metadata podría divergir del renderer cerrado.

**Depuración:** una única cadena: renderer → `encode("utf-8")` → bytes.

### A5 — metadatos con semántica duplicada

Incluir estado, decisión, regla o escenario en `to_metadata()` duplicaría contenido y abriría divergencia.

**Depuración:** metadata limitada a media_type, filename, size_bytes y content_sha256.

### A6 — filename como identidad

Derivar filename desde decision/scenario puede convertirlo en identificador auxiliar.

**Depuración:** filename fijo `eios-vertical-mvp-readonly.html`.

### A7 — constructor abierto

Permitir construir el artefacto con bytes arbitrarios rompería el vínculo con U1.2.

**Depuración:** `init=False`; construcción exclusiva mediante builder.

### A8 — contenido mutable

Un `bytearray` permitiría mutación post-construcción.

**Depuración:** conservar exclusivamente `bytes`.

### A9 — transformación posterior del HTML

Minificar, normalizar saltos o reordenar atributos en U1.3 cambiaría la salida y duplicaría autoridad visual.

**Depuración:** los bytes corresponden exactamente al string U1.2 codificado en UTF-8.

### A10 — error oculto

Capturar errores del renderer y devolver artefacto vacío podría transformar invalidación en ausencia.

**Depuración:** errores U1.2 se propagan; no existe fallback.

## DEPURAR

La forma autorizada queda reducida a:

```text
Mapping
  ↓
render_vertical_mvp_readonly
  ↓
str
  ↓ exact UTF-8
bytes
  ↓
sha256(bytes)
  ↓
immutable transport artifact
```

No se incorpora ningún otro paso.

## Dictamen Audit 1

**SUPERADA — 0 bloqueadores.**

La implementación puede materializarse siempre que permanezca como wrapper puro de contenido y no introduzca I/O, identidad decisional o semántica duplicada.


## AUDITAR 2 — implementación materializada

### Delta físico

La rama añade/modifica únicamente:

- contrato U1.3;
- este registro;
- `eios/frontend/visual/vertical_mvp_artifact.py`;
- export explícito en `eios/frontend/visual/__init__.py`;
- `tests/test_vertical_mvp_readonly_artifact.py`.

No se modifica U1.2 renderer/view-model, U1.1, Application Boundary, O1, Vertical MVP, Rules, CRC, Scenario, Twin, Finance, QTG, NI/Ladder, SQL, reglas o parámetros.

### Verificación estática

La implementación:

1. consume únicamente `Mapping`;
2. delega la validación/render en U1.2;
3. ejecuta exactamente `.encode("utf-8")`;
4. calcula `sha256(content).hexdigest()`;
5. conserva `bytes` inmutables;
6. usa constructor directo cerrado;
7. expone metadata exclusivamente de transporte;
8. no acepta ruta, file handle, URL, storage key ni callback;
9. no importa filesystem, networking, framework web ni motores EIOS;
10. no transforma, minifica o reserializa HTML;
11. no captura errores del renderer;
12. denomina el hash exclusivamente `content_sha256`.

### Cobertura materializada

Las pruebas verifican:

- bytes exactos U1.2;
- hash reproducible;
- metadata exacta;
- constructor cerrado e inmutabilidad;
- determinismo;
- cambio material → hash distinto;
- no mutación del view-model;
- propagación fail-closed;
- preservación del escape HTML;
- ausencia de aliases decisionales/provenance;
- ausencia de imports filesystem/red/motores.

**AUDITAR 2: SUPERADA — 0 bloqueadores.**

## CERRAR → MATERIALIZAR → CI

U1.3 queda **CERRADA TÉCNICAMENTE — CI PENDIENTE**.

La unidad crea un artefacto de transporte verificable, no una nueva identidad EIOS ni una frontera de persistencia.

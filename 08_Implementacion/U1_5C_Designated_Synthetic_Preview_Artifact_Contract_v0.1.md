# EIOS — U1.5C · Designated Synthetic Preview Artifact — Contract v0.1

**Baseline:** `main @ 8767c173087d65f547360040f7ad5568177cb269`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → MATERIALIZADO — CI REGISTRADA EN PR #230

## 1. Propósito

U1.5C materializa una superficie visual exclusivamente sintética que mantiene visible e inequívoca la clasificación de prueba en el mismo documento que contiene la presentación Vertical MVP.

No modifica ni reetiqueta U1.2, U1.3 o U1.4. No ejecuta EIOS y no introduce servidor, loopback, socket, HTTP activo, filesystem, persistencia, autenticación, navegador, extensión ni host nativo.

## 2. Cadena autorizada

```text
LocalSyntheticPreviewAdmission U1.5A exacta
→ revalidación integral U1.5A
→ U1.3 exacto retenido en la admission
→ composición cerrada y determinista
→ DesignatedSyntheticPreviewArtifact
→ revalidación de derivación completa
→ DesignatedSyntheticPreviewDelivery
```

U1.5C es un artefacto nuevo. `source_artifact_content_sha256` referencia U1.3 únicamente como igualdad de contenido fuente; no constituye firma, provenance, autenticación ni evidencia de ejecución.

## 3. Constantes

| Nombre | Valor |
|---|---|
| `ARTIFACT_SCHEMA_VERSION` | `EIOS-DESIGNATED-SYNTHETIC-PREVIEW-ARTIFACT-01/v0.1` |
| `DELIVERY_SCHEMA_VERSION` | `EIOS-DESIGNATED-SYNTHETIC-PREVIEW-DELIVERY-01/v0.1` |
| `PROFILE` | `LOCAL_SYNTHETIC_PREVIEW` |
| `CLASSIFICATION` | `SYNTHETIC_PRESENTATION_FIXTURE` |
| `SCOPE` | `TEST_ONLY` |
| `NOTICE` | `VISTA SINTÉTICA DE PRUEBA — NO ES UNA EJECUCIÓN OPERACIONAL DE EIOS` |
| `MEDIA_TYPE` | `text/html; charset=utf-8` |
| `FILENAME` | `eios-synthetic-preview.html` |

`operational_effect`, `decision_authority` y `execution_claim` permanecen siempre en `false`.

## 4. Factoría de artefacto

```python
build_designated_synthetic_preview_artifact(
    admission: LocalSyntheticPreviewAdmission,
) -> DesignatedSyntheticPreviewArtifact
```

La factoría acepta exclusivamente el tipo exacto U1.5A. Antes de componer:

1. reconstruye una `LocalSyntheticPreviewAdmission` desde el `case` retenido;
2. revalida case id, case fingerprint, notice, profile y flags sintéticos;
3. reconstruye U1.3 y U1.4 mediante las factorías existentes;
4. verifica bytes, tamaño y digest frente a la admission aportada;
5. rechaza cualquier divergencia antes de producir U1.5C.

No se aceptan view-models, HTML libre, artifacts U1.3 sueltos, deliveries U1.4 sueltos, mappings, hashes o metadata.

## 5. Composición cerrada

U1.5C no importa ni llama a `render_vertical_mvp_readonly` ni a `build_vertical_mvp_view_model`.

La transformación opera solo sobre U1.3 ya revalidado y exige:

- apertura HTML contractual exacta;
- cierre HTML contractual exacto;
- un único anclaje `</style>`;
- un único anclaje `<body>`;
- ausencia de superficies activas prohibidas: `script`, `iframe`, `object`, `embed`, `form`, `img`, `link`, `base`, navegación activa, `src`, `srcset`, `action` y equivalentes.

La composición añade únicamente:

- CSS estático para una banda `position:sticky; top:0`;
- el NOTICE contractual;
- `SYNTHETIC · TEST_ONLY · NO OPERATIONAL EFFECT`.

Cualquier deriva estructural falla cerrada. No existe reparación HTML tolerante.

## 6. Artefacto

`DesignatedSyntheticPreviewArtifact` es `frozen`, `init=False` y factory-built.

Retiene internamente:

- la `LocalSyntheticPreviewAdmission` revalidada de origen;
- `case_id`;
- `case_fingerprint`;
- `source_artifact_content_sha256`;
- bytes U1.5C;
- SHA-256 U1.5C.

Expone además schema, profile, classification, scope, notice, media type, filename, size y flags no operacionales.

El digest U1.5C debe ser distinto del digest U1.3.

## 7. Revalidación provenance-safe del delivery

`build_designated_synthetic_preview_delivery` no confía únicamente en el contenido o digest del artefacto.

Antes de emitir el descriptor:

1. revalida la admission fuente retenida;
2. reconstruye U1.3/U1.4;
3. recompone determinísticamente U1.5C;
4. exige igualdad exacta del contenido recompuesto;
5. revalida case id, case fingerprint y source digest;
6. recomputa el digest final y verifica notice y marcadores.

Esto impide convertir metadata o hashes desprendidos en autoridad de construcción.

## 8. Delivery

```python
build_designated_synthetic_preview_delivery(
    artifact: DesignatedSyntheticPreviewArtifact,
) -> DesignatedSyntheticPreviewDelivery
```

El descriptor usa:

- status 200;
- body exacto del artifact;
- `Content-Type`;
- `Content-Length`;
- `Content-Disposition`;
- `Cache-Control: no-store`;
- `X-Content-Type-Options: nosniff`;
- `Referrer-Policy: no-referrer`;
- CSP exacta deny-by-default.

CSP:

```text
default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; script-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'
```

No realiza HTTP activo.

## 9. Evidencia física

Materialización:

- `eios/frontend/visual/designated_synthetic_preview.py`;
- `tests/test_designated_synthetic_preview.py`;
- export explícito en `eios/frontend/visual/__init__.py`.

La suite específica cubre:

- happy path y determinismo;
- identidad U1.5C distinta de U1.3;
- notice físico y banda sticky;
- CSP exacta;
- constructores cerrados e inmutabilidad;
- revalidación de admission, artifact U1.3 y delivery U1.4;
- manipulación de lineage y digest;
- rechazo de superficies activas;
- deriva estructural fail-closed;
- ausencia de I/O, routing, auth y motores;
- no mutación U1.5A.

## 10. G03

U1.5C aporta evidencia física para U15-G03 porque el notice y los tres marcadores forman parte de los bytes del mismo documento y permanecen en una banda sticky durante la presentación.

El gate no se declara integrado hasta que la CI del HEAD exacto resulte satisfactoria y, si se autoriza merge, se verifique de nuevo sobre `main`.

U1.5B permanece bloqueada y requiere un ciclo independiente incluso si G03 queda cerrado.

## 11. Fronteras preservadas

U1.5C no:

- modifica U1.2–U1.5A;
- re-renderiza el view-model;
- ejecuta Rules, CRC, Scenario, Decision Twin, PRICE, Finance o Quality;
- usa QTG como provenance;
- habilita datos operacionales;
- crea servidor, loopback, socket, ruta o puerto;
- introduce autenticación, sesión o persistencia;
- interpreta hashes como firma o provenance.

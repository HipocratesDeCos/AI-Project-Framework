# EIOS — U1.5 · Local Synthetic Preview Admission & Operating Profile — Contract v0.1

**Baseline:** `main @ 8d90654bc2e9825e7c8739c389aeedb2e88049bd`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → DISEÑO CERRADO — IMPLEMENTACIÓN BLOQUEADA POR GATES U15-G01…G03

## 1. Propósito

Definir la única ampliación de entrega visual admisible sin expediente operacional: un perfil local, efímero y exclusivamente sintético denominado `LOCAL_SYNTHETIC_PREVIEW`.

U1.5 no implementa todavía servidor, red, filesystem, persistencia, autenticación ni apertura automática de navegador. Cierra las condiciones que una futura implementación deberá satisfacer antes de realizar I/O.

## 2. Punto de partida cerrado

La cadena visual vigente termina en:

```text
authorized Vertical MVP view-model
→ U1.2 HTML read-only
→ U1.3 immutable artifact
→ U1.4 controlled delivery descriptor
```

U1.4 acredita integridad de transporte. No acredita naturaleza sintética, provenance de ejecución, destinatario, autenticación ni transmisión.

## 3. Separación de dominios sintéticos

`ProjectionOnlySyntheticMaterialBundle` demuestra exclusivamente que un dataset `PROJECTION_ONLY` fue traducido como material sintético S1–S7.

No demuestra que:

- se haya ejecutado el Vertical MVP;
- un `VerticalMVPSupportResult` derive de ese bundle;
- un view-model visual derive de ese resultado;
- un artefacto U1.3 derive de ese material;
- exista integración QTG sintética con O1/Vertical.

Por tanto, U1.5 no puede aceptar el bundle y el artefacto como parámetros independientes ni inferir su relación por IDs, referencias o fingerprints.

## 4. Fuente admisible futura

La admisión deberá partir de un nuevo carrier factory-built, todavía no materializado:

`VerticalMVPSyntheticPreviewCase`.

Este carrier representará una fixture de presentación, no una ejecución EIOS. Deberá conservar como mínimo:

- `case_id` fijo y no empresarial;
- versión de schema;
- clasificación fija `SYNTHETIC_PRESENTATION_FIXTURE`;
- alcance fijo `TEST_ONLY`;
- `operational_effect = false`;
- `decision_authority = false`;
- `execution_claim = false`;
- view-model U1.2 completo;
- fingerprint canónico calculado internamente sobre el caso completo.

El constructor directo permanecerá cerrado. No se admitirá un `Mapping`, etiqueta o fingerprint aportado por el llamador como prueba suficiente de naturaleza sintética.

## 5. Frontera de admisión futura

Una única factoría atómica deberá ejecutar:

```text
VerticalMVPSyntheticPreviewCase
→ validate exact synthetic case
→ build_vertical_mvp_readonly_artifact(case.view_model)
→ build_vertical_mvp_readonly_delivery(artifact)
→ LocalSyntheticPreviewAdmission
```

La factoría no aceptará artefacto o delivery preconstruidos. Así se evita asociar una declaración sintética a bytes diferentes.

`LocalSyntheticPreviewAdmission` deberá conservar:

- profile fijo `LOCAL_SYNTHETIC_PREVIEW`;
- identidad del caso sintético;
- fingerprint del caso;
- `artifact_content_sha256`;
- `delivery_content_sha256` idéntico;
- `operational_effect = false`;
- `decision_authority = false`;
- `execution_claim = false`;
- objeto U1.4 exacto admitido.

Ningún hash será firma, autenticación, provenance operacional o identidad decisional.

## 6. Designación inequívoca

Todo punto de entrada futuro deberá denominar el perfil literalmente `LOCAL_SYNTHETIC_PREVIEW` y declarar antes de la visualización:

> VISTA SINTÉTICA DE PRUEBA — NO ES UNA EJECUCIÓN OPERACIONAL DE EIOS

La designación no se insertará modificando los bytes U1.3 ni debilitando las cabeceras U1.4.

La forma visual persistente de esta advertencia todavía no está materializada. Un mensaje de consola, un nombre de ruta o una etiqueta externa aislada no se consideran por sí solos suficientes para declarar cerrado este gate.

## 7. Perfil operativo futuro

Cuando los gates de admisión estén cerrados, el adaptador local deberá cumplir simultáneamente:

- bind exclusivo a loopback;
- prohibición de `0.0.0.0`, interfaces LAN, hostname público o proxy externo;
- puerto efímero asignado por el sistema, no puerto fijo;
- proceso foreground iniciado y detenido explícitamente por el usuario;
- un único admission/artifact inmutable por proceso;
- rutas cerradas y sin parámetros empresariales;
- `GET` y `HEAD` como únicos métodos de lectura;
- sin request body, upload, formularios, cookies, sesiones o tokens;
- sin directorio de archivos, filesystem o contenido dinámico;
- sin caché adicional, compresión o transformación de bytes;
- cabeceras U1.4 transmitidas sin modificación;
- sin apertura automática de navegador;
- sin logs persistentes ni registro del contenido;
- terminación del proceso elimina toda disponibilidad;
- ningún efecto operacional o decisional.

Loopback es contención técnica, no autenticación. Este perfil nunca habilitará datos operacionales o empresariales reales.

## 8. Rutas conceptuales

El diseño reserva únicamente:

- `/eios/local-synthetic-preview` para la designación inequívoca y acceso controlado;
- `/eios/local-synthetic-preview/artifact` para los bytes exactos U1.4, solo si la advertencia persistente puede preservarse sin modificar el artefacto.

Cualquier otra ruta responderá `404`; cualquier método distinto de `GET`/`HEAD`, `405`.

Estas rutas son especificación futura y no autorizan todavía un endpoint ejecutable.

## 9. Gates de implementación

### U15-G01 — carrier sintético visual

Debe existir `VerticalMVPSyntheticPreviewCase` con schema, fixture física, validación estricta, fingerprint recomputable y constructor cerrado.

### U15-G02 — binding atómico

Debe existir una factoría pura que construya artefacto U1.3, delivery U1.4 y admission desde el mismo caso, sin aceptar piezas desprendidas.

### U15-G03 — advertencia persistente

Debe demostrarse una designación visual inequívoca `SYNTHETIC / TEST_ONLY / NO OPERATIONAL EFFECT` sin modificar los bytes U1.3, debilitar CSP o reabrir U1.2.

Hasta cerrar G01–G03, no se implementará el adaptador loopback.

## 10. Fronteras

U1.5 no autoriza:

- usar `ProjectionOnlySyntheticMaterialBundle` como prueba de provenance visual;
- integrar QTG sintético con O1/Vertical;
- aceptar `OPERATIONAL` o `PRESENTED_OPERATIONAL`;
- cambiar etiquetas sintéticas;
- exponer material empresarial real;
- servidor HTTP, WSGI/ASGI o framework web en esta unidad;
- filesystem, descarga o exportación;
- autenticación, SSO o IAM;
- persistencia o logging;
- API pública;
- ejecución del Vertical;
- decisión, recomendación o compra.

## 11. Descomposición autorizada

La materialización futura deberá separarse en:

1. **U1.5A — Synthetic Visual Admission:** carrier, fixture, binding atómico y pruebas; componente puro sin I/O.
2. **U1.5B — Local Loopback Preview Adapter:** solo después de cerrar U15-G01…G03 y superar nueva auditoría de I/O.

No se implementarán ambas unidades en un único salto.

## 12. Criterio de cierre

Este contrato cierra el diseño del perfil `LOCAL_SYNTHETIC_PREVIEW`, pero mantiene la implementación bloqueada hasta que la admisión sintética visual sea físicamente demostrable y la advertencia persistente no erosione U1.2–U1.4.

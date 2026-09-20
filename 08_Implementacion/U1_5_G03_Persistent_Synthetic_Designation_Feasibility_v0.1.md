# EIOS — U1.5 · U15-G03 Persistent Synthetic Designation — Feasibility v0.1

**Baseline:** `main @ 0712eb513da0db085cf2110199579ae98b7783c1`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → DECISIÓN CERRADA CON NO-GO — U15-G03 ABIERTO

## 1. Propósito

Determinar si un navegador ordinario puede mantener visible e inequívoca la designación sintética de U1.5 mientras presenta los bytes exactos U1.3 con las cabeceras exactas U1.4, sin reabrir U1.2 ni introducir otro runtime de confianza.

Esta unidad no materializa servidor, loopback, rutas, filesystem, persistencia, autenticación, extensión de navegador, aplicación nativa ni transformación de contenido.

## 2. Premisas inmutables

La evaluación conserva simultáneamente:

1. el body presentado debe ser el artefacto U1.3 exacto, sin prefijo, banner, wrapper, inyección o reserialización;
2. la entrega debe conservar las cabeceras U1.4 exactas, incluida la CSP;
3. U1.2 no se reabre y su HTML no contiene clasificación de entorno;
4. la advertencia debe permanecer visible durante la visualización, no solo antes de navegar;
5. un nombre de ruta, consola, header, metadata o etiqueta externa aislada no cierra el gate;
6. la solución debe funcionar con capacidades web ordinarias, sin exigir extensión, navegador modificado o host nativo nuevo;
7. el texto contractual es:

> VISTA SINTÉTICA DE PRUEBA — NO ES UNA EJECUCIÓN OPERACIONAL DE EIOS

y la designación mínima debe comunicar `SYNTHETIC / TEST_ONLY / NO OPERATIONAL EFFECT`.

La CSP U1.4 exacta es:

```text
default-src 'none'; style-src 'unsafe-inline'; img-src 'none'; script-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'
```

La especificación CSP Level 3 establece que `frame-ancestors` restringe qué orígenes pueden embeber un recurso mediante `frame`, `iframe`, `object` o `embed`, y que `'none'` representa una lista de ancestros vacía. Fuente normativa: <https://www.w3.org/TR/CSP3/#directive-frame-ancestors>.

## 3. Criterio de éxito

U15-G03 solo podría cerrarse si una misma presentación garantiza todo lo siguiente:

- el usuario observa el artefacto y la advertencia persistentemente y de forma conjunta;
- la advertencia no depende de recordar una pantalla anterior ni de inspeccionar herramientas técnicas;
- los bytes del body siguen siendo exactamente U1.3;
- las cabeceras siguen siendo exactamente U1.4;
- no se atribuye al artefacto provenance, ejecución o autoridad que U1.5A no acredita;
- no se introduce una nueva frontera confiable fuera del diseño autorizado.

## 4. Matriz de alternativas

| Alternativa | Persistencia visible | Preserva U1.3/U1.4 | Dentro de autoridad | Dictamen |
|---|---:|---:|---:|---|
| nombre de ruta, URL o título de pestaña externo | no garantiza la advertencia completa | sí | sí | NO-GO |
| consola, metadata o response headers | no es interfaz visual persistente | sí | sí | NO-GO |
| landing page con aviso y enlace | el aviso desaparece al navegar al artefacto | sí | sí | NO-GO |
| ventana o pestaña acompañante | puede cerrarse, ocultarse o separarse del artefacto | sí | sí | NO-GO |
| shell con `frame`/`iframe` | sí en principio | no: U1.4 impide ancestros | no | NO-GO |
| shell con `object`/`embed` | sí en principio | no: `frame-ancestors 'none'` y `object-src 'none'` | no | NO-GO |
| script que obtiene e inserta el artefacto | sí en principio | no: CSP impide script/conexión y el DOM mostrado ya no es U1.3 | no | NO-GO |
| banner inyectado o transformación server-side | sí | no: cambia body, tamaño y SHA-256 | no | NO-GO |
| entrega de los mismos bytes con CSP alterada | potencialmente | no: deja de ser U1.4 | no | NO-GO |
| respuesta multipart o composición del navegador | no ofrece una presentación interoperable equivalente | no: cambia la entrega | no | NO-GO |
| extensión, navegador modificado o aplicación nativa | potencialmente | puede preservar el body interno | no: crea un runtime confiable nuevo | FUERA DE ALCANCE |

## 5. Demostración de incompatibilidad

Sea `A` el artefacto U1.3 exacto y `D(A)` su entrega U1.4 exacta.

1. Si `D(A)` se presenta como documento top-level, la advertencia no forma parte de `A`; el navegador no dispone de una superficie web persistente adicional perteneciente al documento sin modificarlo.
2. Si una página contenedora intenta presentar conjuntamente la advertencia y `D(A)`, debe embeber el recurso. `frame-ancestors 'none'` rechaza `frame`, `iframe`, `object` y `embed` con ancestro; `object-src 'none'` añade una prohibición específica para contenido plugin.
3. Si la página contenedora copia, obtiene o transforma `A`, el documento mostrado deja de ser el body exacto de `D(A)`; además, la CSP vigente prohíbe script y conexiones.
4. Si la advertencia vive en otra página, pestaña, ventana, URL, consola o header, no se puede garantizar su visibilidad conjunta y persistente durante la observación de `A`.
5. Si una extensión o host nativo impone chrome persistente, aparece una nueva frontera de confianza no definida por U1.5 ni autorizada para U1.5B.

Por agotamiento de las clases de composición disponibles, no existe una solución web ordinaria que satisfaga simultáneamente todas las premisas vigentes.

## 6. Decisión

**U15-G03: ABIERTO — NO-GO bajo las restricciones actuales.**

**U1.5B: NO-GO.** No se autoriza adaptador loopback, servidor, socket, ruta ni I/O.

El cierre de esta unidad es un cierre de decisión de viabilidad, no el cierre del gate. Impide seguir buscando una variante sintáctica dentro de una arquitectura contradictoria y evita erosionar U1.2–U1.4 mediante una excepción implícita.

## 7. Autoridad mínima requerida para un diseño posterior

La opción de menor impacto es autorizar explícitamente una nueva unidad arquitectónica, provisionalmente denominada `U1.5C — Designated Synthetic Preview Artifact`, con estas propiedades:

- produce un artefacto de presentación **distinto** de U1.3 y no afirma que sus bytes sean U1.3;
- parte atómicamente del `LocalSyntheticPreviewAdmission` exacto ya registrado;
- incorpora en sus propios bytes la advertencia contractual visible y persistente;
- conserva `case_id`, `case_fingerprint` y `artifact_content_sha256` como referencias de igualdad, no como firma o provenance operacional;
- usa una entrega y una CSP propias, al menos tan restrictivas como permita su función;
- no modifica, sustituye ni reetiqueta U1.3/U1.4;
- permanece sintético, `TEST_ONLY`, sin efecto operacional, autoridad decisional ni claim de ejecución;
- debe atravesar un ciclo independiente de diseño, auditoría, depuración, Audit 2, cierre, materialización y CI antes de reconsiderar U1.5B.

Esta opción requiere autorización expresa porque amplía la arquitectura de presentación. Este documento no la concede ni la materializa.

Alternativas de mayor impacto —reabrir U1.2 para hacerlo consciente del entorno o autorizar un host nativo con chrome persistente— quedan identificadas, pero no recomendadas ni diseñadas.

## 8. Criterio de cierre de este documento

La decisión queda cerrada cuando:

- se conserva la contradicción reproducible entre persistencia, exactitud U1.3/U1.4 y CSP;
- ninguna alternativa rechazada se presenta como cierre parcial de G03;
- U15-G03 y U1.5B permanecen explícitamente bloqueados;
- cualquier siguiente paso exige una decisión de autoridad arquitectónica separada.


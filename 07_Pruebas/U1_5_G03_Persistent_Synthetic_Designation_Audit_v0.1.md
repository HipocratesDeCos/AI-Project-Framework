# EIOS — U1.5 · U15-G03 Persistent Synthetic Designation — Audit v0.1

**Baseline:** `main @ 0712eb513da0db085cf2110199579ae98b7783c1`

**Estado:** AUDIT 1 SUPERADA → DEPURADO → AUDIT 2 SUPERADA — NO-GO CONFIRMADO; GATE ABIERTO

**Objeto:** auditar si U15-G03 puede cerrarse sin modificar U1.2, los bytes U1.3 o las cabeceras U1.4, y sin introducir una frontera de confianza nueva.

## AUDITAR

### A1 — confundir aviso previo con persistencia

Una landing page puede mostrar el notice antes de abrir el artefacto, pero deja de estar visible al navegar.

**Depuración:** el criterio exige co-visibilidad durante toda la presentación; la precedencia temporal no es persistencia.

### A2 — convertir chrome contingente en garantía

Ruta, URL, nombre de pestaña o segunda ventana dependen del navegador, del tamaño de ventana y de acciones del usuario. No garantizan la advertencia exacta ni su visibilidad.

**Depuración:** esas señales pueden complementar una designación interna, pero no cerrar G03 por sí solas.

### A3 — inspección técnica como interfaz

Headers, consola o metadata son observables mediante herramientas, no una advertencia visual persistente para quien consume la vista.

**Depuración:** se rechazan como mecanismo primario.

### A4 — framing incompatible con U1.4

Un shell permitiría disponer aviso y artefacto en una superficie, pero el artefacto se entrega con `frame-ancestors 'none'`.

**Depuración:** no se crea excepción para loopback, mismo origen o ruta local. Alterar o retirar la directiva deja de preservar U1.4.

### A5 — composición equivalente a bytes exactos

Obtener el HTML y copiarlo dentro de otro documento puede parecer visualmente equivalente, pero ya no presenta la respuesta U1.4 ni conserva la identidad del body servido. La CSP prohíbe además script y conexión.

**Depuración:** equivalencia visual no sustituye igualdad de bytes, digest y entrega.

### A6 — banner añadido sin reabrir U1.2

Una transformación posterior evita editar el renderer fuente, pero modifica el artefacto U1.3 resultante.

**Depuración:** toda inyección, prefijo, wrapper o reserialización se clasifica como un artefacto distinto y no puede llamarse U1.3.

### A7 — extensión o host tratado como detalle de implementación

Un componente fuera de la página podría imponer una banda persistente sin tocar el body.

**Depuración:** ese componente sería una nueva frontera confiable, con distribución, identidad y ciclo de seguridad propios; está fuera del adaptador loopback autorizado conceptualmente.

### A8 — cerrar G03 por descarte documental

Demostrar que el diseño actual es imposible no satisface el requisito visual.

**Depuración:** se cierra la decisión de viabilidad con NO-GO; U15-G03 permanece abierto y U1.5B bloqueado.

## DEPURAR

El resultado depurado distingue tres estados que no deben mezclarse:

| Objeto | Estado | Significado |
|---|---|---|
| decisión de viabilidad G03 bajo U1.2–U1.4 vigentes | CERRADA CON NO-GO | no queda una alternativa web admisible dentro de estas premisas |
| gate U15-G03 | ABIERTO | no existe todavía advertencia visual persistente demostrada |
| U1.5B | BLOQUEADO | no se puede diseñar/materializar I/O loopback |

## AUDITAR 2

### B1 — cobertura de alternativas

La matriz cubre señales del navegador, observabilidad técnica, navegación secuencial, superficies paralelas, embedding, composición cliente, transformación servidor y runtimes externos. Cada rechazo identifica la premisa incumplida.

**Resultado:** PASS.

### B2 — correspondencia normativa

La lectura normativa de CSP Level 3 confirma que `frame-ancestors` controla embedding mediante `frame`, `iframe`, `object` y `embed`, y que `'none'` no admite ancestros. No se infiere que `default-src 'none'` sustituya esa directiva; U1.4 declara `frame-ancestors 'none'` explícitamente.

**Resultado:** PASS.

### B3 — preservación de evidencia física

Se contrastó la baseline integrada:

- U1.2 conserva `<title>EIOS · Vertical MVP · Solo lectura</title>` y no contiene clasificación sintética;
- U1.3 conserva bytes y SHA-256 inmutables;
- U1.4 conserva la CSP exacta con `script-src 'none'`, `connect-src 'none'`, `object-src 'none'` y `frame-ancestors 'none'`;
- U1.5A conserva el notice en metadata de admisión, sin afirmar visibilidad.

**Resultado:** PASS.

### B4 — ausencia de autoridad inventada

El documento no autoriza U1.5C, reapertura de U1.2, cambio de U1.3/U1.4, host nativo ni extensión. Solo identifica la decisión futura mínima que podría pedirse.

**Resultado:** PASS.

### B5 — ausencia de materialización encubierta

El delta se limita a:

- `08_Implementacion/U1_5_G03_Persistent_Synthetic_Designation_Feasibility_v0.1.md`;
- este registro de auditoría.

No se modifican `eios/`, `tests/`, fixtures, dependencias, rutas, procesos ni configuración.

**Resultado:** PASS.

## Dictamen

**AUDIT 2 SUPERADA — 0 contradicciones documentales pendientes.**

**NO-GO CONFIRMADO PARA U15-G03 BAJO LAS RESTRICCIONES VIGENTES.**

U15-G03 permanece abierto y U1.5B bloqueado. El siguiente paso legítimo no es implementar loopback, sino obtener —o denegar— autoridad expresa para diseñar un artefacto sintético designado distinto de U1.3, sometido a un ciclo completo independiente.


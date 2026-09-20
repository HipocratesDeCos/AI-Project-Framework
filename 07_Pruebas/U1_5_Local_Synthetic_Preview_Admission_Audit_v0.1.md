# EIOS — U1.5 Local Synthetic Preview Admission — Audit v0.1

**Baseline:** `main @ 8d90654bc2e9825e7c8739c389aeedb2e88049bd`

**Objeto:** auditar y depurar el diseño `LOCAL_SYNTHETIC_PREVIEW` sin materializar servidor o I/O.

## AUDITAR

### A1 — etiqueta sintética autoafirmada

Un booleano, string o fingerprint aportado junto al artefacto permitiría etiquetar bytes arbitrarios como sintéticos.

**Depuración:** nuevo carrier factory-built con fixture exacta, schema cerrado y fingerprint recomputable. La factoría de admisión recibe el carrier, no etiquetas sueltas.

### A2 — bundle PROJECTION_ONLY ≠ provenance visual

El bundle S7 demuestra material sintético de proyección, pero la cadena QTG sintética termina en consumo `TEST_ONLY` y prohíbe integración O1/Vertical.

**Depuración:** U1.5 no crea ningún binding entre bundle y artefacto visual. La fuente futura será una fixture de presentación que declara `execution_claim=false`.

### A3 — asociación de piezas desprendidas

Aceptar por separado caso, artefacto y delivery permitiría combinarlos sin demostrar correspondencia.

**Depuración:** una única factoría construirá U1.3, U1.4 y admission en la misma operación.

### A4 — fixture visual presentada como ejecución

Un HTML realista puede interpretarse como resultado ejecutado.

**Depuración:** el caso y admission conservan `execution_claim=false`; además se exige designación persistente y visible antes de habilitar loopback.

### A5 — aviso que modifica el artefacto

Inyectar un banner en U1.3 rompería `content_sha256` y duplicaría autoridad de render.

**Depuración:** la advertencia debe permanecer fuera de los bytes U1.3. Su forma concreta constituye U15-G03 y no se presume resuelta.

### A6 — wrapper mediante iframe

Un shell que enmarque el artefacto chocaría con `frame-ancestors 'none'` de U1.4 o exigiría debilitar CSP.

**Depuración:** no se autoriza iframe ni cambio de cabeceras. G03 deberá resolverse sin framing.

### A7 — loopback tratado como autenticación

Escuchar solo en `127.0.0.1` reduce exposición, pero cualquier proceso local podría intentar acceder.

**Depuración:** loopback se declara contención, nunca autenticación. Solo es admisible para fixture sintética sin datos empresariales.

### A8 — servidor prematuro

Implementar HTTP antes de cerrar admisión permitiría servir un artefacto arbitrario.

**Depuración:** U1.5A pura precede obligatoriamente a U1.5B; el adaptador debe exigir el tipo exacto de admission.

### A9 — servicio residente

Autostart, background service o puerto estable crearían una superficie disponible fuera de una sesión controlada.

**Depuración:** futuro proceso foreground, puerto efímero y lifecycle explícito. No daemon ni disponibilidad persistente.

### A10 — extensión accidental a operación

Un perfil genérico `LOCAL_PREVIEW` podría reutilizarse con datos reales alegando que no sale del equipo.

**Depuración:** el único nombre autorizado es `LOCAL_SYNTHETIC_PREVIEW`; `OPERATIONAL` y material real quedan estructuralmente fuera.

## DEPURAR

La cadena de diseño se reduce a:

```text
exact synthetic presentation fixture
→ factory-built synthetic visual case
→ atomic U1.3 + U1.4 binding
→ local synthetic admission
→ future loopback adapter
```

Se eliminan del alcance actual servidor, socket, rutas ejecutables, filesystem y navegador.

## Dictamen Audit 1

**SUPERADA PARA DISEÑO — 0 contradicciones pendientes.**

**IMPLEMENTACIÓN: NO-GO hasta U15-G01…G03.**

El perfil puede cerrarse documentalmente porque define una trayectoria que no necesita datos operacionales. No puede materializarse todavía porque no existe carrier visual sintético ni solución demostrada para la advertencia persistente.

## AUDITAR 2 — contrato depurado

### Evidencia física contrastada

- U1.2 consume únicamente el view-model autorizado y no contiene clasificación de entorno.
- U1.3 conserva bytes y `content_sha256`, sin provenance.
- U1.4 conserva respuesta controlada, sin destinatario ni autenticación.
- `ProjectionOnlySyntheticMaterialBundle` conserva naturaleza sintética S1–S7.
- el E2E QTG sintético termina en `TEST_ONLY`, con `operational_effect=false` y `decision_authority=false`.
- no existe productor físico bundle/receipt sintético → `VerticalMVPSupportResult`.
- no existe rama, PR o contrato U1.5 previo.

### No duplicación

U1.5 no crea otro artefacto de transporte ni otro delivery descriptor. Añade únicamente el concepto de admisión futura y un perfil operativo cerrado.

### Autoridad preservada

El contrato no:

- reabre U1.2–U1.4;
- integra QTG con O1;
- afirma ejecución del Vertical;
- añade efecto operacional;
- autoriza material real;
- convierte hashes en autenticación o provenance;
- implementa I/O.

### Delta autorizado de esta unidad

Exclusivamente:

- `08_Implementacion/U1_5_Local_Synthetic_Preview_Admission_Contract_v0.1.md`;
- este registro de auditoría.

No se modifican `eios/`, `tests/`, fixtures, SQL, reglas, parámetros o dependencias.

**AUDITAR 2: SUPERADA PARA EL DISEÑO — 0 bloqueadores documentales.**

## CERRAR

U1.5 queda **CERRADA A NIVEL DE DISEÑO** con implementación bloqueada por U15-G01…G03.

La siguiente unidad legítima es **U1.5A — Synthetic Visual Admission**, comenzando por diseñar el schema exacto de `VerticalMVPSyntheticPreviewCase`. U1.5B no puede iniciarse todavía.

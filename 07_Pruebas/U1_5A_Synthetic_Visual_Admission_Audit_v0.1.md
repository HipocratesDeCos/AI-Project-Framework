# EIOS — U1.5A Synthetic Visual Admission — Audit v0.1

**Baseline:** `main @ 5dabd8ada1013f74c6ed6358ace8475a778d8233`

**Objeto:** auditar y depurar el schema, la allowlist y el binding atómico de U1.5A sin materializar I/O.

## AUDITAR

### A1 — schema U1.2 permisivo

El renderer U1.2 exige claves mínimas, pero no rechaza claves adicionales. Una fixture podría incorporar metadata o superficies no auditadas que U1.2 ignore hoy y consuma una versión futura.

**Depuración:** U1.5A aplica igualdad exacta de conjuntos de claves en la raíz y en cada objeto cerrado antes de llamar a U1.3.

### A2 — declaración sintética autoafirmada

Aceptar `classification`, `scope` o `execution_claim=false` sin más permitiría rotular contenido arbitrario como sintético.

**Depuración:** el caso completo se canonicaliza y su digest debe coincidir con la allowlist literal asociada al `case_id`. Las etiquetas siguen siendo obligatorias, pero no constituyen por sí solas la prueba.

### A3 — fingerprint aportado por el llamador

Un campo `fingerprint` dentro de la fixture podría ser incoherente o circular.

**Depuración:** el schema prohíbe ese campo; el digest se calcula internamente sobre el objeto completo canonicalizado.

### A4 — ambigüedad de serialización

Whitespace, orden de claves, escapes Unicode o representaciones no finitas podrían producir digests distintos o validaciones divergentes.

**Depuración:** parseo UTF-8 estricto, rechazo de duplicados y no finitos, y serialización canónica única con claves ordenadas y separadores compactos.

### A5 — claves JSON duplicadas

Los parsers convencionales conservan una de dos claves duplicadas. Un revisor y el runtime podrían observar valores distintos.

**Depuración:** `object_pairs_hook` equivalente detecta y rechaza duplicados en cualquier profundidad.

### A6 — objeto mutable después de admitir

Retener el `dict` del llamador permitiría cambiar el view-model entre fingerprint, render y delivery.

**Depuración:** el carrier retiene bytes canónicos inmutables; cada acceso al view-model produce una estructura nueva. La admission retiene los objetos inmutables exactos generados en la operación.

### A7 — piezas desprendidas

Aceptar un artefacto o delivery preconstruido permitiría asociarlo a un case sintético distinto.

**Depuración:** `build_local_synthetic_preview_admission` acepta solo el carrier exacto y construye internamente U1.3 y U1.4. No existen overloads de piezas sueltas.

### A8 — carrier falsificado o alterado

Un constructor cerrado reduce mal uso normal, pero Python permite técnicas de mutación deliberada.

**Depuración:** la factoría de admission revalida schema, digest y registro desde los bytes internos; no confía solo en la identidad del objeto.

### A9 — hash interpretado como provenance

La igualdad de digest podría describirse erróneamente como prueba de origen o ejecución.

**Depuración:** el contrato limita el hash a igualdad con contenido revisado y elimina un digest adicional de admission que no aportaría una propiedad independiente.

### A10 — fixture realista confundida con expediente

IDs o cifras plausibles pueden aparentar una ejecución real aunque el objeto declare `TEST_ONLY`.

**Depuración:** IDs inequívocamente sintéticos, ausencia de actores y expedientes reales, estados incompletos/no evaluables y notice contractual en el caso.

### A11 — lectura de archivo incorporada al runtime

Una API que aceptase paths mezclaría admisión pura con filesystem y ampliaría U1.5A.

**Depuración:** la API acepta exclusivamente bytes. Solo el harness de pruebas abre la fixture física.

### A12 — DoS por fixture ilimitada o profundidad extrema

Una estructura JSON muy grande o profundamente anidada puede consumir memoria o recursión aun sin I/O.

**Depuración:** límite de 262144 bytes y profundidad JSON máxima 32, ambos anteriores al render.

### A13 — aviso visible presumido

Conservar `notice` en metadata no demuestra que sea visible de forma persistente cuando se presente U1.3.

**Depuración:** U1.5A no declara cerrado G03 y no autoriza U1.5B. El notice aquí clasifica la fixture; no sustituye una solución visual.

## DEPURAR

El diseño depurado queda reducido a dos factorías puras y dos carriers inmutables:

```text
fixture bytes → validated registered case
registered case → exact U1.3 artifact + exact U1.4 delivery → admission
```

Se excluyen paths, file handles, payloads operacionales, bundles QTG, mappings libres, artefactos aportados, deliveries aportados y hashes aportados.

## Matriz de pruebas obligatoria para materialización

| Grupo | Evidencia mínima |
|---|---|
| Happy path | fixture física registrada produce case, artifact, delivery y admission deterministas |
| Constructor | construcción directa de ambos carriers rechazada |
| Entrada | rechazo de no-bytes, vacío, exceso de tamaño, BOM, UTF-8 inválido y trailing content |
| JSON | rechazo de claves duplicadas, `NaN`, infinitos y profundidad > 32 |
| Schema raíz | rechazo de cada clave ausente, extra, tipo incorrecto o constante alterada |
| Schema U1.2 | rechazo de claves extra/ausentes y tipos incorrectos en cada objeto cerrado |
| Invariantes | rechazo de bloques Rules/CRC y scenario support incoherentes con sus booleanos |
| Registro | rechazo de `case_id` desconocido, digest no registrado y fixture mutada |
| Inmutabilidad | mutar la entrada original o el view-model devuelto no cambia case, digest ni admission |
| Revalidación | carrier interno alterado se rechaza antes de construir U1.3 |
| Atomicidad | la factoría no acepta artifact/delivery; los tres digests de body son idénticos |
| U1.3 | bytes, size, media type, filename y SHA-256 satisfacen el contrato existente |
| U1.4 | status, headers, body y SHA-256 satisfacen el contrato existente sin cambios |
| Semántica | no se afirma ejecución, efecto operacional, decisión, autenticación ni provenance |
| Pureza | módulo sin imports o llamadas de filesystem, socket, HTTP, subprocess o persistencia |
| Regresión | suite U1.2–U1.4 y suite completa permanecen verdes |

Las pruebas negativas deben mutar una propiedad por caso y demostrar fallo previo a la emisión de admission. No basta comparar metadata final.

## Dictamen Audit 1

**SUPERADA PARA DISEÑO — 0 contradicciones pendientes en G01/G02.**

El schema y el binding son materializables sin I/O y sin inventar una relación QTG → Vertical. La evidencia física todavía no existe; por ello G01 y G02 no se declaran cerrados en implementación.

**U1.5B: NO-GO por U15-G03.**

## AUDITAR 2 — contrato depurado

### Correspondencia con evidencia existente

- U1.2 recibe un view-model de presentación y no clasifica el entorno.
- U1.3 construye bytes HTML y conserva su SHA-256, sin provenance.
- U1.4 verifica U1.3 y conserva response parts, sin realizar HTTP.
- la CSP vigente contiene `frame-ancestors 'none'`.
- no existe productor probado de material QTG sintético hacia un resultado O1/Vertical.

U1.5A se apoya solo en esas propiedades y no les atribuye autoridad adicional.

### No duplicación

La unidad no crea otro renderer, artifact ni delivery. Añade:

- un carrier de fixture registrada;
- una frontera de admisión que compone las factorías U1.3/U1.4 existentes.

### Autoridad preservada

El diseño no:

- reabre o transforma el HTML U1.2;
- modifica U1.3/U1.4;
- usa un hash como firma;
- convierte `TEST_ONLY` en ejecución;
- habilita datos operacionales;
- resuelve ficticiamente G03;
- materializa I/O.

### Delta autorizado de la fase de diseño

Exclusivamente:

- `08_Implementacion/U1_5A_Synthetic_Visual_Admission_Contract_v0.1.md`;
- este registro de auditoría.

No se modifican `eios/`, `tests/`, fixtures, dependencias, reglas, parámetros ni superficies de ejecución.

**AUDITAR 2: SUPERADA PARA EL DISEÑO — 0 bloqueadores documentales.**

## CERRAR

U1.5A queda **CERRADA A NIVEL DE DISEÑO**.

La siguiente acción legítima es materializar U15-G01 y U15-G02 exactamente según este contrato, auditar las pruebas y mantener U1.5B bloqueada hasta una solución independiente para U15-G03.

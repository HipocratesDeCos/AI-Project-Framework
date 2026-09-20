# EIOS — U1.5A · Synthetic Visual Admission — Contract v0.1

**Baseline:** `main @ 5dabd8ada1013f74c6ed6358ace8475a778d8233`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA → DISEÑO CERRADO — MATERIALIZACIÓN PENDIENTE

## 1. Propósito y alcance

U1.5A diseña una admisión visual exclusivamente sintética y pura, capaz de demostrar que un artefacto U1.3 y su descriptor U1.4 fueron construidos, en una misma operación, desde una fixture de presentación registrada.

Esta unidad no ejecuta el Vertical MVP y no introduce servidor, socket, HTTP activo, filesystem de producción, persistencia, autenticación, navegador ni datos empresariales. La lectura de la fixture física corresponde solo al harness de pruebas; la API de producción recibe bytes ya residentes en memoria.

## 2. Resultado autorizado

La única cadena admisible es:

```text
registered UTF-8 JSON fixture bytes
→ strict parse + exact schema + canonicalization
→ VerticalMVPSyntheticPreviewCase
→ build_vertical_mvp_readonly_artifact(case.view_model)
→ build_vertical_mvp_readonly_delivery(artifact)
→ LocalSyntheticPreviewAdmission
```

La cadena declara una **fixture de presentación**, no una ejecución EIOS ni provenance de un resultado operacional.

## 3. Constantes contractuales

| Nombre | Valor exacto |
|---|---|
| `SCHEMA_VERSION` | `EIOS-VERTICAL-MVP-SYNTHETIC-PREVIEW-CASE-01/v0.1` |
| `ADMISSION_SCHEMA_VERSION` | `EIOS-LOCAL-SYNTHETIC-PREVIEW-ADMISSION-01/v0.1` |
| `PROFILE` | `LOCAL_SYNTHETIC_PREVIEW` |
| `CLASSIFICATION` | `SYNTHETIC_PRESENTATION_FIXTURE` |
| `SCOPE` | `TEST_ONLY` |
| `NOTICE` | `VISTA SINTÉTICA DE PRUEBA — NO ES UNA EJECUCIÓN OPERACIONAL DE EIOS` |
| `MAX_FIXTURE_BYTES` | `262144` |

`operational_effect`, `decision_authority` y `execution_claim` son siempre el booleano JSON `false`. Strings, enteros o valores truthy equivalentes se rechazan.

## 4. Schema exacto de `VerticalMVPSyntheticPreviewCase`

### 4.1 Raíz de la fixture

La fixture es un único objeto JSON con estas claves exactas, sin extensiones:

| Clave | Tipo | Restricción |
|---|---|---|
| `schema_version` | string | valor `SCHEMA_VERSION` exacto |
| `case_id` | string | `SYNTHETIC-PREVIEW-[A-Z0-9][A-Z0-9-]{0,63}` y entrada existente en el registro autorizado |
| `classification` | string | valor `CLASSIFICATION` exacto |
| `scope` | string | valor `SCOPE` exacto |
| `operational_effect` | boolean | `false` exacto |
| `decision_authority` | boolean | `false` exacto |
| `execution_claim` | boolean | `false` exacto |
| `notice` | string | valor `NOTICE` exacto |
| `view_model` | object | schema exacto de la sección 4.2 |

No existe un campo de fingerprint aportado por la fixture. El fingerprint se calcula después de validar y canonicalizar el objeto completo.

### 4.2 Raíz del view-model U1.2

`view_model` contiene exactamente las catorce claves consumidas por U1.2:

| Clave | Tipo contractual |
|---|---|
| `execution_status` | string no vacío |
| `policy_version` | string no vacío |
| `failure_reason` | string o `null` |
| `unresolved_items` | array de strings |
| `capabilities` | array de `Capability` |
| `rules_available` | boolean |
| `rule_coverage` | `RuleCoverage` o `null` |
| `crc_support_result` | `CRCResult` o `null` |
| `assessments` | array de `Assessment` o `null` |
| `rule_trace_references` | array de strings o `null` |
| `scenario_support_available` | boolean |
| `scenario_execution_context` | `ScenarioContext` o `null` |
| `scenario_records` | array de `ScenarioRecord` o `null` |
| `scenario_comparison` | `ScenarioComparison` o `null` |

Los objetos anidados también son cerrados:

| Objeto | Claves exactas |
|---|---|
| `Capability` | `capability: string`, `status: string`, `result_available: boolean`, `trace_references: string[]`, `unresolved_items: string[]` |
| `RuleCoverage` | `executed_rule_ids: string[]`, `omitted_rule_ids: string[]` |
| `CRCResult` | `consolidated_result: string`, `dominant_reason: string`, `relevant_factors: string[]`, `conflicts: string[]` |
| `Assessment` | `rule_id: string`, `status: string`, `outcome: string|null`, `reason: string`, `evidence_ids: string[]` |
| `ScenarioContext` | `execution_id: string`, `decision_id: string`, `rules_version: string`, `parameters_version: string`, `data_snapshot_id: string` |
| `ScenarioRecord` | `scenario_id: string`, `status: string`, `values: JsonObject`, `trace_references: string[]`, `unresolved_items: string[]`, `failure_reason: string|null` |
| `ScenarioComparison` | `scenario_ids: string[]`, `observations: JsonArray`, `differences: JsonArray`, `missing: JsonArray`, `statuses: string[]`, `unresolved_items: string[]`, `traceability: string[]` |

`JsonObject` y `JsonArray` admiten solo el dominio JSON finito: objetos con claves string, arrays, strings, booleanos, `null` y números finitos. Se rechazan `NaN`, infinitos, tipos Python no JSON y profundidad superior a 32 niveles.

Las invariantes condicionales son:

- si `rules_available=false`, `rule_coverage`, `crc_support_result`, `assessments` y `rule_trace_references` deben ser `null`;
- si `rules_available=true`, esos cuatro campos deben estar presentes con sus tipos no nulos;
- si `scenario_support_available=false`, `scenario_execution_context`, `scenario_records` y `scenario_comparison` deben ser `null`;
- si `scenario_support_available=true`, context y records deben ser no nulos; comparison puede ser objeto o `null`;
- todas las claves adicionales, incluso las que U1.2 actualmente ignoraría, se rechazan en cualquier objeto cerrado;
- el orden de arrays se conserva; no se ordenan capacidades, reglas, assessments ni escenarios.

## 5. Parseo, canonicalización y registro

La factoría pura propuesta es:

```python
build_vertical_mvp_synthetic_preview_case(
    fixture_content: bytes,
) -> VerticalMVPSyntheticPreviewCase
```

Su comportamiento normativo es:

1. exigir `type(fixture_content) is bytes` y `0 < len <= MAX_FIXTURE_BYTES`;
2. decodificar UTF-8 estricto, sin BOM;
3. parsear un solo documento JSON y rechazar claves duplicadas en cualquier nivel;
4. rechazar constantes no JSON (`NaN`, `Infinity`, `-Infinity`) y trailing content;
5. validar claves, tipos, constantes e invariantes de la sección 4;
6. serializar canónicamente con UTF-8, claves ordenadas, separadores `(',', ':')`, `ensure_ascii=False` y `allow_nan=False`;
7. calcular `case_fingerprint = sha256(canonical_case_bytes).hexdigest()`;
8. exigir igualdad constante con el digest literal registrado para `case_id`;
9. crear el carrier mediante factoría cerrada.

El registro privado tiene la forma conceptual:

```python
AUTHORIZED_SYNTHETIC_PREVIEW_CASES: Mapping[str, str]
# case_id -> sha256 hexadecimal de los bytes canónicos del caso completo
```

Cada entrada es una allowlist de contenido exacto. Un nuevo `case_id` o cualquier cambio de valor exige modificar fixture, digest literal, pruebas y revisión de código. Un fingerprint no registrado se rechaza, aunque el schema sea válido.

El hash acredita igualdad con una fixture revisada; no acredita firma, autoría, autenticación, origen operacional ni ejecución.

## 6. Carrier inmutable

`VerticalMVPSyntheticPreviewCase` será `frozen`, `init=False` y con constructor directo que lance `TypeError`. Conservará internamente solo los bytes JSON canónicos y su fingerprint recomputable.

Expondrá como mínimo:

- constantes contractuales y `case_id`;
- `canonical_content: bytes`;
- `case_fingerprint: str`;
- `view_model`, devuelto como una nueva estructura JSON en cada acceso;
- `to_metadata()`, sin incorporar ni reinterpretar datos del view-model.

La factoría de admisión volverá a comprobar tipo exacto, digest, registro y schema. El cierre del constructor no se usa como sustituto de revalidar el contenido.

## 7. Binding atómico y admission

La única factoría de binding propuesta es:

```python
build_local_synthetic_preview_admission(
    case: VerticalMVPSyntheticPreviewCase,
) -> LocalSyntheticPreviewAdmission
```

No admite `Mapping`, view-model, artefacto, delivery, etiquetas ni hashes sueltos. Después de revalidar el caso exacto, la misma llamada:

1. construye `VerticalMVPReadOnlyArtifact` con `case.view_model`;
2. construye `VerticalMVPReadOnlyDelivery` desde ese artefacto;
3. exige igualdad entre el digest recomputado del body, el digest U1.3 y el digest U1.4;
4. crea `LocalSyntheticPreviewAdmission` mediante constructor cerrado.

La admission inmutable conserva referencias a los objetos exactos `case`, `artifact` y `delivery`, y expone este metadata derivado:

| Campo | Valor/invariante |
|---|---|
| `schema_version` | `ADMISSION_SCHEMA_VERSION` |
| `profile` | `PROFILE` |
| `case_id` | derivado del case registrado |
| `case_fingerprint` | recomputado del case |
| `artifact_content_sha256` | digest U1.3 |
| `delivery_content_sha256` | digest U1.4 e idéntico al anterior |
| `content_size_bytes` | longitud exacta del body U1.4 |
| `operational_effect` | `false` |
| `decision_authority` | `false` |
| `execution_claim` | `false` |
| `notice` | `NOTICE` |

No se define `admission_sha256`: añadir otro hash no prueba ninguna propiedad nueva y podría confundirse con una credencial o firma.

## 8. Fixture física de materialización

U1.5A deberá materializar exactamente una fixture inicial:

`tests/fixtures/vertical_mvp_synthetic_preview_case_01.json`

El contenido deberá:

- usar IDs inequívocamente sintéticos, sin nombres de persona, proveedor, cliente, contrato, pedido o expediente real;
- combinar estados `COMPLETED`, `PARTIAL` o `NOT_EVALUABLE` solo para demostrar presentación;
- incluir reglas omitidas, unresolved items y al menos un resultado no evaluable;
- evitar cifras o hechos presentables como cotización empresarial;
- contener el `NOTICE` contractual;
- quedar fijado por el digest literal del registro.

La fixture no se importará en runtime ni se leerá desde el módulo de producción. Las pruebas leerán el archivo y pasarán sus bytes a la factoría pura.

## 9. Errores y cierre seguro

La API falla de forma cerrada:

- `TypeError` para tipo de entrada o carrier incorrecto;
- `ValueError` para UTF-8, JSON, schema, constante, tamaño, digest, registro o invariante incumplidos;
- ningún fallback, coercion, normalización semántica o reparación automática;
- ningún resultado parcial, artifact o delivery retornado si falla cualquier paso;
- mensajes de error sin volcar el contenido completo de la fixture.

## 10. Fronteras preservadas

U1.5A no:

- usa `ProjectionOnlySyntheticMaterialBundle` como provenance visual;
- afirma binding QTG sintético → O1/Vertical;
- llama `build_vertical_mvp_view_model` desde un payload operacional;
- ejecuta capacidades, reglas, CRC o escenarios;
- modifica los bytes HTML de U1.3 o las cabeceras de U1.4;
- inserta el `NOTICE` dentro del HTML U1.3;
- habilita perfil operacional o datos reales;
- implementa U1.5B, servidor, rutas o I/O.

## 11. Gates y criterio de cierre

Este diseño resuelve contractualmente:

- **U15-G01:** schema exacto, fixture física requerida, validación estricta, fingerprint recomputable y constructor cerrado;
- **U15-G02:** factoría atómica sin piezas desprendidas.

G01 y G02 solo quedarán **cerrados físicamente** cuando el módulo, la fixture y las pruebas sean materializados y auditados.

**U15-G03 permanece bloqueado:** U1.5A no resuelve una advertencia visual persistente fuera de los bytes U1.3 y compatible con `frame-ancestors 'none'`. En consecuencia, U1.5B y cualquier adaptador loopback continúan en `NO-GO`.

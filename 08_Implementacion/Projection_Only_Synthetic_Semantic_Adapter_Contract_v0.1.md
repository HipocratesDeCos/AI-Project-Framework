# EIOS — PROJECTION_ONLY Synthetic Semantic Adapter Contract v0.1

**Estado:** CERRADO — IMPLEMENTACIÓN PENDIENTE

**Baseline:** `main @ 1075df27bdcb48628d729c809a11b80baa8019a5`

**Precondición:** paquete admitido por `load_projection_mock_dataset()` bajo `EIOS-PROJECTION-ONLY-MOCK-DATASET-01/v0.1`.

## 1. DISEÑAR

### 1.1 Objetivo y salida

El adaptador traducirá exclusivamente un `ProjectionMockDataset` ya validado a un agregado inmutable `ProjectionOnlySyntheticMaterialBundle`. La salida conservará, sin sustituirlos, los objetos canónicos construidos por las factorías EIOS y culminará en un `ProjectionMaterialEnvelope`.

```text
ProjectionMockDataset
→ decodificación JSON exacta
→ modelos canónicos y cadenas vinculadas
→ ProjectionMaterialEnvelope
→ ProjectionOnlySyntheticMaterialBundle
```

El adaptador **no** ejecutará Finance Basic, reglas, Quality Gate, productor QTG ni consumidor QTG. Tampoco convertirá el envelope en resultado de calidad.

### 1.2 Resultado atómico

Solo existen dos resultados:

1. bundle completo, reproducible y ligado al fingerprint del dataset; o
2. rechazo con error estable, ruta del componente y causa.

No se devolverán objetos parciales. El error no podrá contener bytes documentales ni datos completos del componente.

### 1.3 Orden de construcción

| Etapa | Componentes fuente | Construcción canónica |
|---|---|---|
| S1 Identidad | `operation`, `decision_context` | `PurchaseOperation`, `DecisionContext`, `Evidence[]` |
| S2 Finanzas | `finance_input`, `parameter_resolutions` | `FinancialSnapshot`, `CashFlow[]`, `FinanceBasicInput`, centro sintético de parámetros de solo lectura, `FinanceDecisionInputPackage` |
| S3 Pagos | `payment_documents`, `required_installment_calendar` | `DocumentaryMaterial[]`, `DocumentaryPaymentBinding[]`, `DocumentaryPaymentCapture`, `RequiredInstallmentCalendar`, cobertura recomputada |
| S4 Criterios | `projection_criteria` | `PresentedQualityCriteria[]`, `ProjectionCriteriaManifest`, `FinanceQualityPreparation` |
| S5 Tesorería | `treasury_material`, `treasury_mandate`, `treasury_review` | soporte documental, valoración contextual, verificación de mandato y revisión personal |
| S6 Flujos | `flow_inventory`, `flow_mandate`, `flow_review` | registro de completitud, verificación de mandato y revisión personal |
| S7 Cierre | todas las anteriores | `ProjectionMaterialEnvelope` y bundle final |

Cada etapa usa las factorías públicas existentes. El adaptador no reconstruye sus reglas ni usa `model_construct`.

### 1.4 Contrato físico de componentes

Cada archivo debe ser un objeto JSON UTF-8 con claves exactas. Se rechazan aliases, claves adicionales, `null` no autorizado y coerciones. Fechas y datetimes usan ISO 8601; los datetimes deben incluir zona. Importes se presentan como cadenas decimales finitas para impedir pérdida binaria.

Los componentes contienen:

- `operation`: campos exactos de `PurchaseOperation` y `evidence[]` con campos exactos de `Evidence`;
- `decision_context`: campos exactos de `DecisionContext`;
- `finance_input`: `company_id`, `effective_at`, `snapshot`, `cash_flows`, `horizon_days`, `treasury_minimum` y, si procede, `working_capital_input`;
- `parameter_resolutions`: `requested_parameter_ids`, definiciones y configuraciones efectivas necesarias; no contiene permisos de escritura;
- `payment_documents`: referencias de operación/pedido/confirmación, documentos sintéticos en base64 con SHA-256 y bindings;
- `required_installment_calendar`: declaración, autoridad sintética, referencias, total y cuotas con locators;
- `projection_criteria`: criterios presentados en base64 con SHA-256 y manifiesto autorizado sintético;
- `treasury_material`: argumentos del soporte documental y de la valoración contextual;
- `treasury_mandate`: material y observaciones de verificación del mandato;
- `treasury_review`: hallazgos de revisión personal y sus referencias;
- `flow_inventory`: perímetros, documentos, candidatos y evaluaciones de flujos capturados;
- `flow_mandate`: material y observaciones de verificación del mandato de inventario;
- `flow_review`: hallazgos de revisión personal y sus referencias.

Los bytes base64 se decodifican con validación estricta y se comparan con su SHA-256 declarado antes de construir `DocumentaryMaterial` o criterios. Esta comprobación interna complementa, pero no reemplaza, el hash del archivo del manifiesto.

### 1.5 Centro sintético de parámetros

`parameter_resolutions` alimentará implementaciones privadas y de solo lectura de `ParameterCatalogue` y `ConfigurationRepository`. La autorización rechazará toda modificación. Solo se aceptarán configuraciones explícitas, vigentes en `effective_at`, pertenecientes a `company_id` y vinculadas a `DecisionContext.parameters_version` por las APIs existentes.

No habrá valores por defecto, fallback, consulta externa ni escritura. `P-FIN-001` debe existir y coincidir exactamente con `horizon_days`; `P-FIN-002` será obligatorio cuando exista `treasury_minimum`.

### 1.6 Correspondencias transversales obligatorias

Antes del cierre deben cumplirse, además de las validaciones propias de cada factoría:

1. identidad completa entre operación, contexto y `FinanceBasicInput.context`;
2. `data_snapshot_id` común entre contexto y snapshot;
3. `company_id == snapshot.company_scope`;
4. `effective_at.date() == snapshot.as_of_date`;
5. todos los casos y submateriales declaran `SYNTHETIC`;
6. referencias documentales resueltas por igualdad exacta y únicas en su ámbito;
7. cada cuota y flujo conserva importe, moneda, vencimiento y pertenencia sin derivación;
8. perímetro de flujos coincide con empresa, fecha, horizonte y moneda preparados;
9. criterios presentados coinciden por referencia, versión y hash con su manifiesto;
10. mandatos y revisiones pertenecen a los targets exactos construidos en la misma ejecución;
11. el fingerprint final liga el fingerprint del dataset, el envelope y los fingerprints intermedios;
12. ninguna identidad se interpreta por prefijo, nombre de archivo o valor empresarial.

### 1.7 Estado de la fixture actual

`projection_only_mock_dataset_01` sigue siendo una fixture **estructural**. Sus componentes mínimos no aportan cantidad, precio, fechas, parámetros, documentos, cuotas ni material de revisión suficientes. Por tanto:

- continuará siendo válida para `load_projection_mock_dataset()`;
- deberá ser rechazada por el adaptador semántico por incompletitud;
- no se completará mediante defaults;
- una fixture semántica completa se materializará separadamente y tendrá otro `dataset_id`.

Esta distinción evita convertir una demostración de carpetas y hashes en una supuesta operación financiera.

## 2. AUDITAR

**A1 — bypass del cargador.** El adaptador solo acepta `ProjectionMockDataset`, nunca una ruta o diccionario.

**A2 — JSON válido pero ambiguo.** Claves exactas, tipos estrictos y conversores explícitos impiden coerciones silenciosas.

**A3 — autoridad por dataset.** Las referencias `authority_ref`, `reviewer_ref` o `verifier_ref` son material sintético presentado; no autentican personas ni habilitan efectos.

**A4 — parámetros autocertificados.** El centro local solo reproduce configuraciones sintéticas. No acredita que existan en un repositorio empresarial.

**A5 — bytes sustituidos.** Hash del archivo, base64 estricto y hash del contenido se verifican en capas distintas.

**A6 — objetos parcialmente válidos.** La salida atómica impide reutilizar una cadena incompleta tras un fallo posterior.

**A7 — resultado QTG infiltrado.** Se prohíben campos `expected_result`, `quality_result`, `status`, `score`, `authorized` o equivalentes en cualquier componente.

**A8 — fixture estructural promovida.** El dataset actual debe fallar en la primera ausencia semántica, sin inferir valores.

**A9 — doble implementación.** Las invariantes financieras, documentales y de revisión permanecen en las factorías existentes; el adaptador solo decodifica, ordena y vincula.

**A10 — mezcla entre datasets.** Todos los objetos del bundle se construyen dentro de una sola llamada y quedan ligados al fingerprint del único dataset admitido.

## 3. DEPURAR

Se eliminan del alcance:

- soporte YAML, CSV o aliases empresariales;
- lectura directa de carpetas por el adaptador;
- persistencia o modificación del centro de parámetros;
- interpretación OCR o documental;
- búsqueda de flujos no declarados;
- corrección automática de importes, divisas, fechas o identidades;
- equivalencias flexibles de referencias;
- objetos parciales como salida pública;
- ejecución de Finance Basic, Quality Gate o QTG;
- admisión `PRESENTED_OPERATIONAL`.

La primera implementación solo soportará el JSON canónico sintético de este contrato.

## 4. AUDITAR 2

La revisión física confirma que las factorías actuales ya controlan las relaciones críticas: contexto financiero completo, procedencia del horizonte, captura y cobertura de cuotas, preparación, soporte y revisión de tesorería, completitud y revisión de flujos, manifiesto de criterios y envelope final.

El único elemento técnico nuevo necesario es la frontera de traducción y un centro sintético de parámetros de solo lectura. Ambos quedan fuera del core de dominio y no cambian contratos cerrados.

La fixture estructural existente no satisface el contrato semántico; este rechazo es intencional y comprobable.

## 5. CERRAR

Se aprueba el adaptador como frontera exclusiva `SYNTHETIC_TEST`. Su salida máxima será `ProjectionMaterialEnvelope`; no producirá `ProjectionQualityProducerResult` ni `QualityResult`.

La implementación deberá incluir:

1. schemas internos estrictos para los trece componentes;
2. bundle inmutable con constructor cerrado;
3. errores estables por etapa y componente;
4. test de rechazo de la fixture estructural actual;
5. nueva fixture semántica completa, agnóstica y sintética;
6. pruebas de mutación para cada enlace transversal;
7. pruebas que demuestren ausencia de ejecución Finance/Quality/QTG.

## 6. MATERIALIZAR → CI

Esta unidad materializa únicamente el contrato de implementación. No modifica el validador, la fixture ni el dominio.

La modificación local ajena de `Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` permanece excluida. Se exige suite completa, PR exact-head, merge protegido por SHA y CI post-merge.

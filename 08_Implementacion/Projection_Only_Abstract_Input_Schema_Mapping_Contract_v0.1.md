# EIOS — PROJECTION_ONLY Abstract Input Schema & Mapping Contract v0.1

**Estado:** CERRADO — MOCK DATA AUTORIZADO — IMPLEMENTACIÓN DE FIXTURE PENDIENTE

**Baseline:** `main @ 2454ddb0e319924c44b2e219528b629c994be850`

**Autoridad:** aprobación explícita del titular para adoptar el paquete `OP-2026-001` exclusivamente como dataset sintético estructural y mapearlo al diccionario EIOS.

## 1. DISEÑAR

### 1.1 Frontera

El paquete de archivos es un **formato externo de entrada para Mock Data**. No es el modelo de dominio, no define entidades empresariales fijas y no modifica los contratos canónicos.

```text
Mock Dataset Package
→ validación estructural externa
→ mapeo explícito
→ contratos canónicos EIOS
→ cadena PROJECTION_ONLY en SYNTHETIC_TEST
```

El núcleo solo recibe objetos EIOS validados. Nunca consulta nombres de carpetas, nombres de archivos, etiquetas de empresa o aliases particulares para decidir semántica.

### 1.2 Taxonomía canónica verificada

La inspección física confirma que estos campos propuestos ya son canónicos y se conservan:

| Campo | Autoridad EIOS | Uso |
|---|---|---|
| `decision_id` | `DecisionContext` + `PurchaseOperation` | identidad de decisión |
| `scenario_id` | `DecisionContext` + `PurchaseOperation` | identidad de escenario, no prueba de baseline |
| `article_id` | `PurchaseOperation` | objeto comprado |
| `supplier_id` | `PurchaseOperation` | proveedor de la operación |
| `company_scope` | `FinancialSnapshot` y contratos financieros | perímetro empresarial financiero |
| `data_snapshot_id` | `DecisionContext` + snapshot | identidad del corte de datos |
| `flow_id` | `CashFlow` | identidad de flujo financiero capturado |
| `installment_ref` | calendario/captura documental | identidad especializada de cuota |

Campos especializados que no sustituyen los anteriores:

| Campo | Capa | Regla |
|---|---|---|
| `operation_ref` | captura documental de pagos | referencia de la operación documental; debe vincularse, no reemplazar `decision_id` |
| `order_ref` / `order_version` | pedido | identidad documental versionada |
| `confirmation_ref` | confirmación | referencia documental |
| `company_id` | agregación DIP/centro de parámetros | debe coincidir con `FinancialSnapshot.company_scope` |
| `reviewer_ref` / `verifier_ref` | mandatos y revisiones | referencias presentadas; no autentican identidad por sí solas |
| `document_ref` | material documental | identidad local única dentro de la cadena aplicable |

No se crea un nuevo diccionario paralelo ni se renombran campos canónicos para ajustarlos al ejemplo.

## 2. INPUT SCHEMA ABSTRACTO

### 2.1 Estructura lógica del paquete

```text
projection_only_mock_dataset/
├── dataset_manifest
├── operation
├── decision_context
├── finance_input
├── parameter_resolutions
├── payment_documents
├── required_installment_calendar
├── projection_criteria
├── treasury_material
├── treasury_mandate
├── treasury_review
├── flow_inventory
├── flow_mandate
└── flow_review
```

Los nombres físicos y el formato serializado —JSON, YAML u otro autorizado— son responsabilidad del adaptador. La estructura lógica y los contratos de destino son invariantes.

### 2.2 `dataset_manifest`

Debe declarar como mínimo:

- `schema_id = EIOS-PROJECTION-ONLY-MOCK-DATASET-01`;
- `schema_version`;
- `dataset_id` no semántico y único dentro de las fixtures;
- `case_kind = SYNTHETIC`;
- `profile = PROJECTION_ONLY`;
- mapa explícito de componentes lógicos a archivos;
- SHA-256 de cada archivo preservado;
- declaración visible `NO_OPERATIONAL_EFFECT`;
- limitaciones conocidas del dataset.

No podrá declarar `PRESENTED_OPERATIONAL`, autenticidad, autorización empresarial ni resultado QTG esperado.

### 2.3 Agnosticismo empresarial

Valores como `PROVEEDOR-ANON-01`, `EMPRESA-A` o `ARTICULO-ANON-01` son datos de una fixture, no entidades del framework.

El adaptador:

- los trata como valores opacos no vacíos;
- no contiene listas de empresas, proveedores o artículos;
- no deriva reglas desde prefijos o patrones de esos valores;
- no interpreta nombres para establecer pertenencia, autoridad o confianza;
- solo aplica relaciones y validaciones declaradas por los contratos EIOS.

Cambiar todos los valores de identidad, manteniendo relaciones coherentes, debe producir otra fixture válida sin cambios de código.

## 3. MAPEO AUTORIZADO

| Componente externo | Destino canónico |
|---|---|
| `operation` | `PurchaseOperation` |
| `decision_context` | `DecisionContext` |
| evidencias declaradas | `Evidence[]` |
| `finance_input.snapshot` | `FinancialSnapshot` |
| `finance_input.cash_flows[]` | `CashFlow[]` |
| parámetros | resoluciones del `ParameterConfigurationCenter` usadas por `FinanceDecisionInputPackage` |
| documentos y asociaciones de pago | `DocumentaryMaterial[]` + `DocumentaryPaymentBinding[]` |
| calendario | `RequiredInstallmentCalendar` + `RequiredInstallment[]` |
| criterios | `PresentedQualityCriteria[]` + `ProjectionCriteriaManifest` autorizado para tests |
| tesorería | contratos de soporte, evaluación contextual, mandato y revisión de tesorería |
| flujos | contratos de completitud, mandato y revisión del inventario |

### 3.1 Reglas de correspondencia

1. `operation.decision_id == decision_context.decision_id`.
2. `operation.scenario_id == decision_context.scenario_id`.
3. `finance_input.context == decision_context` completo.
4. `finance_input.snapshot.data_snapshot_id == decision_context.data_snapshot_id`.
5. `company_id == finance_input.snapshot.company_scope`.
6. cada `flow_id` es único dentro del input financiero.
7. cada `installment_ref` es único y se vincula explícitamente a un flujo `PAYMENT` cuando exista asociación.
8. `operation_ref`, pedido, versión y confirmación coinciden entre captura y calendario.
9. documentos y localizadores se resuelven por `document_ref` exacto, nunca por nombre parecido.
10. referencias, versiones y hashes de criterios coinciden exactamente con el manifiesto de pruebas.

### 3.2 Diccionario externo opcional

Un consumidor empresarial futuro podrá aportar un mapa:

```text
campo_fuente → campo canónico EIOS
```

Ese mapa pertenece al adaptador de entrada. Debe ser explícito, versionado y fail-closed. No puede:

- añadir campos al núcleo;
- sustituir contratos EIOS;
- mapear varios significados incompatibles al mismo campo sin regla autorizada;
- derivar valores faltantes;
- corregir silenciosamente incoherencias;
- transformar estados desconocidos o conflictivos en demostrados.

## 4. AUDITAR

**A1 — duplicación taxonómica.** Renombrar `supplier_id` o `article_id` crearía un dialecto paralelo pese a que ya son campos canónicos. Se conservan.

**A2 — confusión de identidades.** `operation_ref` es documental; `decision_id` identifica la decisión y ambos pueden coexistir. No se fusionan.

**A3 — semántica por nombre.** Interpretar prefijos `PROVEEDOR-*`, `EMPRESA-*` o nombres de archivos acoplaría el core a la fixture. Se prohíbe.

**A4 — formato físico como dominio.** La carpeta facilita intercambio y pruebas, pero no se convierte en arquitectura del núcleo.

**A5 — mock promovido.** El manifiesto fija `SYNTHETIC` y `NO_OPERATIONAL_EFFECT`. Ningún adaptador puede promoverlo.

**A6 — aliases silenciosos.** Todo nombre empresarial distinto debe resolverse mediante mapa explícito y versionado antes de construir modelos canónicos.

**A7 — resultado esperado.** El dataset no declara `APTO`, confianza ni checks esperados como entradas. Esos resultados se derivan y se prueban por separado.

**A8 — documentos ficticios.** Los bytes de la fixture pueden ser sintéticos, pero deben declararse como tales y conservarse de forma reproducible; nunca se presentarán como documentos reales.

## 5. DEPURAR

Se excluyen:

- modelos core específicos para `OP-2026-001`;
- proveedores, empresas o artículos preconfigurados;
- heurísticas basadas en nombres;
- segundo `PurchaseOperation` o segundo `DecisionContext` para el schema externo;
- traducciones implícitas;
- promoción a operación real;
- campos de decisión o autorización;
- expectativas QTG suministradas al productor.

La solución depurada es un paquete sintético versionado y una traducción determinista hacia los tipos existentes.

## 6. AUDITAR 2

La segunda revisión confirma:

- la taxonomía de identidad propuesta coincide mayoritariamente con el estándar físico EIOS;
- las referencias documentales especializadas permanecen en sus capas;
- el núcleo continúa agnóstico respecto de empresas concretas;
- el mapa externo es opcional y no invade el dominio;
- el caso se limita a `SYNTHETIC_TEST`;
- no cambia el contrato de admisión operacional cerrado;
- no desbloquea el binding causal operacional;
- no reabre Finance Basic, PRICE, C0, Decision Twin ni Scenario Stage 2.

## 7. CERRAR

Se aprueba `EIOS-PROJECTION-ONLY-MOCK-DATASET-01` como esquema lógico abstracto para materializar posteriormente una fixture completa.

La siguiente unidad podrá definir el manifiesto JSON y el validador estructural del paquete sintético. Ese validador deberá producir únicamente material apto para la ruta `SYNTHETIC_TEST` y fallar ante cualquier intento de efecto operacional.

## 8. MATERIALIZAR → CI

Esta unidad materializa solo el contrato de schema y mapeo. No crea todavía la fixture, el adaptador ni el validador.

La modificación local ajena de `08_Implementacion/Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda excluida.

Se exige suite completa, PR de un archivo, CI exact-head, merge protegido por SHA y CI post-merge.

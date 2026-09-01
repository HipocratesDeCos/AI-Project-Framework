# EIOS — Price Intelligence Implementation Contract

## 1. Identidad

**Documento:** Price Intelligence Implementation Contract  
**Versión:** 1.3  
**Estado:** CERRADO  
**Baseline:** EIOS Vertical MVP  
**Autoridad metodológica:** `01_Modelo/Price_Intelligence_Methodological_Matrix.md`  
**Autoridad arquitectónica:** `03_Arquitectura/Architecture_Blueprint.md`  
**Ubicación:** `08_Implementacion/Price_Intelligence_Implementation_Contract.md`

## 2. Propósito

Define el contrato físico C1 para materializar Price Intelligence / Precio de Referencia (PR) sin redefinir su metodología.

No constituye una nueva autoridad funcional. La metodología de PR permanece en `01_Modelo/Price_Intelligence_Methodological_Matrix.md`.

La implementación debe materializar únicamente semántica previamente autorizada.

## 3. Posición arquitectónica

```text
Decision Input Package
        ↓
Quality & Trust
        ↓
Price Intelligence / PR
        ↓
TCO
```

Price Intelligence es Capa 1. Assurance, trazabilidad y versionado atraviesan el flujo.

## 4. Frontera con C0 y QTG

PR consume el contexto y datos autorizados del flujo existente. No crea un contexto paralelo y no redefine:

- `InputContract`;
- `DecisionContext`;
- `Evidence`;
- `EvidenceValidation`;
- `Assessment`;
- `Trace`.

No modifica C0 para resolver necesidades de PR.

QTG mantiene autoridad sobre calidad/confianza de evidencia. PR mantiene autoridad sobre su metodología económica. QTG confidence no es ponderación de precio ni representatividad.

## 5. Identidad y contexto

C1 debe reutilizar las identidades canónicas de `DecisionContext`:

```text
DecisionContext
├── decision_id
├── scenario_id
├── rules_version
├── parameters_version
└── data_snapshot_id
```

`input_fingerprint`, cuando forme parte del contexto/trazabilidad disponible, debe conservarse por el mecanismo canónico existente. C1 no crea sustitutos semánticos de estas identidades.

## 6. Entrada física

La operación de PR recibe una estructura equivalente a:

```text
PriceIntelligenceInput
├── decision_context: DecisionContext
├── purchase_operation: PurchaseOperation
├── references: list[PriceReference]
├── evidence_validations: list[EvidenceValidation]
├── normalization_basis: NormalizationBasis (nullable)
└── methodology_version: string
```

`evidence_validations` contiene los resultados de validación producidos aguas arriba por el contrato canónico de evidencia. C1 los consume; no vuelve a validar la evidencia ni transforma `VALID` en representatividad o suficiencia.

### 6.1 `PurchaseOperation`

Representa la operación de compra evaluada y debe contener únicamente los datos necesarios para establecer el contexto de comparabilidad. No constituye una nueva entidad de decisión.

C0 no contiene una unidad objetivo de compra. C1 no añade ese atributo a `PurchaseOperation` ni modifica C0 para obtenerlo.

### 6.2 `PriceReference`

Cada referencia histórica puede contener:

```text
PriceReference
├── source_transaction_id
├── article_identity
├── supplier_identity (nullable)
├── quantity
├── unit
├── unit_price
├── currency
├── operation_date
├── commercial_conditions (nullable)
└── evidence_refs
```

`source_transaction_id` conserva la identidad de origen cuando exista. Cualquier clave técnica interna será auxiliar, determinista y sin semántica empresarial.

Ningún campo adquiere significado metodológico adicional por existir en el contrato.

### 6.3 `NormalizationBasis`

`NormalizationBasis` es una interfaz física especializada de C1 para datos objetivo que no forman parte del contrato C0 y son necesarios para ejecutar transformaciones autorizadas.

```text
NormalizationBasis
├── target_unit
├── basis_reference
├── rule_reference
└── trace_reference
```

Reglas:

1. `target_unit` no se infiere de `article_id`, proveedor, historial o contexto implícito.
2. `basis_reference` identifica la fuente o referencia que sustenta la unidad objetivo.
3. `rule_reference` identifica la regla autorizada que permite utilizar esa base.
4. `trace_reference` permite reconstruir la procedencia de la base.
5. La ausencia de `NormalizationBasis` impide ejecutar una transformación que requiera conocer la unidad objetivo.
6. `NormalizationBasis` no crea una nueva identidad empresarial ni modifica C0.
7. La base no autoriza por sí misma una conversión: la transformación concreta debe seguir estando autorizada por la matriz de normalización.

## 7. Estados físicos cerrados

### Comparabilidad

```text
COMPARABLE
NO_COMPARABLE
PENDING
```

### Normalización

```text
NORMALIZED
PENDING
NOT_NORMALIZABLE
```

### Representatividad

```text
REPRESENTATIVE
NON_REPRESENTATIVE
INDETERMINATE
```

### Suficiencia

```text
SUFFICIENT
LIMITED
NOT_JUSTIFIABLE
```

### Estado final PR

```text
PR_AVAILABLE
PR_LIMITED
PR_NOT_JUSTIFIABLE
```

No se permiten estados adicionales en MVP.

Mapeo obligatorio:

```text
SUFFICIENT        → PR_AVAILABLE
LIMITED           → PR_LIMITED
NOT_JUSTIFIABLE   → PR_NOT_JUSTIFIABLE
```

## 8. Pipeline físico

El motor debe ejecutar exactamente:

```text
INPUT
→ IDENTIFICATION
→ DEDUPLICATION
→ COMPARABILITY
→ NORMALIZATION
→ TEMPORAL_RELEVANCE
→ REPRESENTATIVENESS
→ SELECTION
→ SUFFICIENCY
→ AGGREGATION
→ PR_RESULT
```

Una etapa posterior no puede corregir retrospectivamente una deficiencia anterior.

## 9. Deduplificación

Los duplicados documentales de una misma transacción no incrementan el conjunto económico.

El resultado debe conservar, como mínimo, los conteos:

```text
N_RAW
N_UNIQUE
N_COMPARABLE
N_REPRESENTATIVE
N_SELECTED
```

La deduplicación debe ser determinista y trazable.

## 10. Normalización

No existe normalización implícita.

Toda transformación aplicada debe conservar:

```text
NormalizationRecord
├── field
├── original_value
├── normalized_value
├── rule_reference
└── trace_reference
```

La ausencia de información necesaria impide la transformación correspondiente; no se sustituye por cero, media, estimación ni valor por defecto.

### 10.1 Moneda

Una referencia en moneda distinta de la moneda objetivo no puede convertirse mediante una tasa inventada, implícita o tomada de una fuente no trazada.

Para aplicar conversión monetaria debe existir una regla/fuente de conversión autorizada y trazable. La tasa o referencia utilizada debe quedar registrada mediante `NormalizationRecord` y su trazabilidad correspondiente.

Si la conversión necesaria no está autorizada o no puede demostrarse, la referencia no puede considerarse normalizada para el cálculo.

## 11. Representatividad

La evaluación debe conservar el resultado de los criterios observables:

```text
REP-01
REP-02
REP-03
REP-04
REP-05
REP-06
```

La salida debe permitir identificar el motivo de `NON_REPRESENTATIVE` o `INDETERMINATE` mediante trazabilidad y limitaciones.

No se utiliza frecuencia, precio mínimo, último precio, proveedor habitual, score ni proximidad al PR para determinar representatividad.

## 12. Selección

Solo referencias `COMPARABLE` + `REPRESENTATIVE` + `NORMALIZED` pueden integrar `REFERENCE_SET`.

La selección precede a la agregación y no puede depender del PR calculado.

## 13. Suficiencia

Reglas físicas mínimas:

```text
N_SELECTED = 0
→ sufficiency_status = NOT_JUSTIFIABLE
→ PR_STATUS = PR_NOT_JUSTIFIABLE
→ PR_VALUE = null

N_SELECTED = 1
→ sufficiency_status = LIMITED
→ PR_STATUS = PR_LIMITED

N_SELECTED >= 2
→ condición necesaria, pero no suficiente, para SUFFICIENT
```

La suficiencia requiere además el cumplimiento de las condiciones metodológicas de comparabilidad, representatividad, evidencia, trazabilidad, normalización y ausencia de contradicciones materiales no resueltas.

No se reutilizan parámetros existentes como umbrales universales de PR.

## 14. Outliers

Un outlier no se elimina automáticamente por distancia estadística.

La implementación no puede utilizar un filtro estadístico como criterio autónomo de no representatividad.

Toda exclusión debe tener causa metodológica autorizada y trazable.

## 15. Contradicciones

Una diferencia de precio no es por sí sola una contradicción.

Una contradicción material no resuelta no puede resolverse mediante:

```text
average
last value
arbitrary priority
score
fallback
```

Si existe reconciliación autorizada, debe quedar registrada. Si no existe, la referencia afectada no puede sostener el cálculo.

## 16. Ponderación

El MVP utiliza exclusivamente agregación no ponderada.

No existen pesos por:

- recencia;
- frecuencia;
- proveedor;
- volumen;
- QTG confidence;
- conveniencia empresarial.

## 17. Agregación

El método cerrado para MVP es:

```text
MEDIAN_UNWEIGHTED
```

Se calcula exclusivamente sobre `REFERENCE_SET` y precios normalizados válidos.

## 18. Salida física C1

La estructura cerrada es:

```text
PriceIntelligenceResult
├── decision_id
├── scenario_id
├── data_snapshot_id
├── methodology_version
├── pr_value
├── currency
├── pr_status
├── sufficiency_status
├── pr_limitations
├── reference_set
├── counts
├── aggregation_method
└── trace_references
```

### 18.1 `pr_value`

Tipo lógico: decimal monetario nullable.

Debe ser `null` cuando:

```text
pr_status = PR_NOT_JUSTIFIABLE
```

No se permite representar ausencia de PR mediante `0`.

### 18.2 `currency`

Código monetario explícito asociado a `pr_value`. No puede existir `pr_value` sin moneda cuando el resultado sea disponible.

### 18.3 `sufficiency_status`

Representa explícitamente el estado metodológico de suficiencia:

```text
SUFFICIENT | LIMITED | NOT_JUSTIFIABLE
```

Debe ser coherente con `pr_status` según el mapeo cerrado del apartado 7.

### 18.4 `pr_limitations`

Lista explícita de limitaciones metodológicas relevantes para interpretar el resultado. No puede utilizarse para ocultar una condición que obligaría a `PR_NOT_JUSTIFIABLE`.

### 18.5 `reference_set`

Colección de identificadores de las referencias seleccionadas y sus trazas necesarias. No se duplica la evidencia documental.

### 18.6 `counts`

```text
counts
├── n_raw
├── n_unique
├── n_comparable
├── n_representative
└── n_selected
```

### 18.7 `aggregation_method`

Valor cerrado en MVP:

```text
MEDIAN_UNWEIGHTED
```

### 18.8 `trace_references`

Referencias a los mecanismos de trazabilidad existentes. No crea una nueva entidad `Trace` paralela ni reutiliza `Trace` de C0 como si Price Intelligence fuese una regla C0.

## 19. Versionado

C1 debe conservar la versión metodológica utilizada y permitir reconstruir el resultado respecto de:

- decisión;
- escenario, cuando corresponda;
- snapshot de datos;
- referencias seleccionadas;
- normalizaciones;
- exclusiones justificadas;
- agregación.

No crea un sistema de versionado paralelo.

## 20. Invariantes físicas

1. `PR = comparable + normalizado + trazable`.
2. `COMPARABLE ≠ REPRESENTATIVE`.
3. `REPRESENTATIVE ≠ SUFFICIENT`.
4. Duplicado documental no crea observación económica nueva.
5. `N_SELECTED = 0 → PR_NOT_JUSTIFIABLE`.
6. `PR_NOT_JUSTIFIABLE → pr_value = null`.
7. `N_SELECTED = 1 → PR_LIMITED`.
8. `N_SELECTED >= 2` es necesario pero no suficiente para `PR_AVAILABLE`.
9. No existe normalización implícita.
10. No existe ponderación implícita.
11. No existe selección retrospectiva.
12. No existe fallback silencioso.
13. Outlier no equivale a error.
14. Contradicción no equivale a outlier.
15. QTG confidence no se convierte en peso de precio.
16. C1 no modifica C0.
17. C1 no crea una nueva identidad empresarial para la transacción.
18. C1 no produce una decisión empresarial.
19. `sufficiency_status` y `pr_status` deben mantener el mapeo cerrado.
20. Una conversión monetaria requiere fuente/regla autorizada y trazabilidad.
21. Toda `evidence_ref` consumida por C1 debe disponer de `EvidenceValidation` correspondiente.
22. C1 no convierte por sí mismo `EvidenceValidation.VALID` en representatividad o suficiencia.
23. Una transformación que requiera unidad objetivo no puede ejecutarse sin `NormalizationBasis`.
24. `NormalizationBasis` no autoriza transformaciones por sí misma.
25. Una referencia no normalizada no entra en `REFERENCE_SET`.

## 21. No alcance

C1 no define ni implementa:

- PO;
- PMR;
- PPV;
- TCO;
- negociación;
- decisión empresarial;
- nuevos parámetros;
- nuevas reglas;
- modificaciones de C0;
- tests.

## 22. Estado de cierre

**C1 — PRICE INTELLIGENCE PHYSICAL CONTRACT: CERRADO.**

Esta revisión 1.3 incorpora la interfaz explícita de `NormalizationBasis` necesaria para materializar transformaciones que requieren una unidad objetivo ausente de C0. No modifica C0 ni la metodología normativa.

El código debe materializar este contrato sin introducir semántica adicional.

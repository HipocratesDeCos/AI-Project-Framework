# EIOS — Modelo Físico SQL Server · C0 Persistence Slice

## Estado

**Versión:** 0.2  
**Estado:** CERRADO — Diseño técnico  
**Fase:** 8 — Implementación Técnica  
**SGBD objetivo:** Microsoft SQL Server  
**Ámbito:** Persistencia del perímetro C0 ya materializado

---

# 1. Propósito

Este documento define el diseño físico de persistencia SQL Server para el perímetro C0 ya materializado.

No constituye una nueva autoridad funcional. Traduce a persistencia relacional los contratos ya autorizados de:

- InputContract / PurchaseOperation;
- DecisionContext;
- Evidence;
- EvidenceValidation;
- Rule;
- Assessment;
- Trace.

No implementa todavía Decision Versioning completo, Scenario Engine, Viability, CRC, Negotiation, Decision Twin ni otras capacidades posteriores.

---

# 2. Principios de diseño

1. **Persistencia sin redefinición:** SQL almacena conceptos ya autorizados.
2. **Separación contractual:** InputContract, DecisionContext, Evidence, Rule, Assessment y Trace permanecen distinguibles.
3. **No inferencia funcional:** ninguna tabla crea dependencias DATA/EVIDENCE/COMPONENT no demostradas por la RDM.
4. **Reproducibilidad preservada:** `input_fingerprint`, contexto y Trace se almacenan sin recalcular ni sustituir los artefactos producidos por C0.
5. **NOT_EVALUABLE ≠ FALSE:** la restricción física conserva esta semántica.
6. **Versiones funcionales preservadas:** `rules_version`, `parameters_version` y `data_snapshot_id` se almacenan como referencias, no como versiones SQL.
7. **Identificadores técnicos separados:** los identificadores `IDENTITY` son exclusivamente técnicos y no adquieren significado empresarial.
8. **Sin JSON como sustituto del modelo:** el perímetro C0 se persiste relacionalmente; no se utiliza un documento JSON como fuente alternativa de verdad.
9. **Sin triggers en esta fase:** el contrato SQL no los exige y C0 no delega en SQL ninguna semántica de ejecución.
10. **Sin temporalidad automática en esta fase:** la continuidad histórica de Decision Versioning no se sustituye por temporal tables de SQL Server.

---

# 3. Esquema técnico

Se utilizará el esquema SQL Server `eios` para separar físicamente los objetos de EIOS de otros objetos de la base de datos.

El esquema es una decisión técnica de organización y no constituye un concepto funcional.

---

# 4. Tablas del perímetro C0

## 4.1 `eios.c0_input`

Representa persistentemente `InputContract` / `PurchaseOperation`.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `input_row_id` | `bigint IDENTITY` | NO | Identificador técnico |
| `decision_id` | `nvarchar(64)` | NO | `PurchaseOperation` |
| `scenario_id` | `nvarchar(64)` | NO | `PurchaseOperation` |
| `article_id` | `nvarchar(64)` | NO | `PurchaseOperation` |
| `supplier_id` | `nvarchar(64)` | NO | `PurchaseOperation` |
| `quantity` | `decimal(38,4)` | NO | `PurchaseOperation` |
| `unit_price` | `decimal(38,4)` | NO | `PurchaseOperation` |
| `currency` | `char(3)` | NO | `PurchaseOperation` |
| `operation_date` | `date` | NO | `PurchaseOperation` |
| `input_fingerprint` | `char(64)` | NO | Fingerprint C0 |

`input_fingerprint` se conserva como resultado producido por C0. SQL no lo recalcula.

La unicidad del fingerprint se considera una garantía técnica de identidad del InputContract persistido, no una nueva semántica.

---

## 4.2 `eios.c0_context`

Representa persistentemente `DecisionContext`.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `context_row_id` | `bigint IDENTITY` | NO | Identificador técnico |
| `decision_id` | `nvarchar(64)` | NO | `DecisionContext` |
| `scenario_id` | `nvarchar(64)` | NO | `DecisionContext` |
| `rules_version` | `nvarchar(64)` | NO | `DecisionContext` |
| `parameters_version` | `nvarchar(64)` | NO | `DecisionContext` |
| `data_snapshot_id` | `nvarchar(64)` | NO | `DecisionContext` |

La combinación de referencias contextuales se conserva íntegramente. SQL no crea una `Decision State Version` propia.

---

## 4.3 `eios.c0_evidence`

Representa persistentemente `Evidence`.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `evidence_id` | `nvarchar(64)` | NO | `Evidence` |
| `source_type` | `nvarchar(64)` | NO | `Evidence` |
| `source_ref` | `nvarchar(256)` | NO | `Evidence` |
| `captured_at` | `date` | NO | `Evidence` |
| `state` | `varchar(16)` | NO | `Evidence` |
| `demonstration_ref` | `nvarchar(256)` | SÍ | `Evidence` |

`state` queda restringido físicamente a `DEMONSTRATED` / `GAP`.

La tabla no determina si una evidencia es suficiente para una regla; esa responsabilidad permanece fuera de SQL.

---

## 4.4 `eios.c0_evidence_validation`

Representa persistentemente `EvidenceValidation`.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `evidence_id` | `nvarchar(64)` | NO | `EvidenceValidation` |
| `status` | `varchar(8)` | NO | `EvidenceValidation` |
| `reason` | `nvarchar(256)` | NO | `EvidenceValidation` |

Clave primaria: `evidence_id`.

Clave externa: `evidence_id → eios.c0_evidence.evidence_id`.

`status` queda restringido a `VALID` / `INVALID`.

---

## 4.5 `eios.c0_rule_contract`

Representa exclusivamente el contrato mínimo `Rule` utilizado por C0.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `rule_id` | `nvarchar(64)` | NO | `Rule` |
| `version` | `nvarchar(64)` | NO | `Rule` |
| `requires_evidence` | `bit` | NO | `Rule` |

Clave primaria: (`rule_id`, `version`).

Esta tabla **no sustituye** la Matriz de Reglas ni pretende persistir todos sus atributos normativos.

---

## 4.6 `eios.c0_assessment`

Representa exclusivamente `Assessment`.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `assessment_row_id` | `bigint IDENTITY` | NO | Identificador técnico |
| `rule_id` | `nvarchar(64)` | NO | `Assessment` |
| `status` | `varchar(16)` | NO | `Assessment` |
| `outcome` | `bit` | SÍ | `Assessment` |
| `reason` | `nvarchar(256)` | NO | `Assessment` |

Restricción de integridad:

```text
status = EVALUABLE      → outcome IS NOT NULL
status = NOT_EVALUABLE  → outcome IS NULL
```

`NOT_EVALUABLE` nunca se representa como `FALSE`.

No se añaden a esta tabla `severity`, `effect`, `recommendation`, `decision`, `priority`, `confidence`, `score` ni otros atributos excluidos por el contrato de Assessment.

---

## 4.7 `eios.c0_assessment_evidence`

Normaliza la colección `Assessment.evidence_ids` y conserva su orden original sin convertirlo en semántica decisional.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `assessment_row_id` | `bigint` | NO | Referencia técnica a Assessment |
| `evidence_ordinal` | `int` | NO | Posición técnica de la colección |
| `evidence_id` | `nvarchar(64)` | NO | `Assessment.evidence_ids` |

Clave primaria: (`assessment_row_id`, `evidence_ordinal`).

Restricción única adicional: (`assessment_row_id`, `evidence_id`).

Claves externas:

```text
assessment_row_id → eios.c0_assessment.assessment_row_id
evidence_id       → eios.c0_evidence.evidence_id
```

La tabla no introduce una nueva semántica de evidencia; conserva la colección definida por el contrato.

---

## 4.8 `eios.c0_trace`

Representa persistentemente `Trace`.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `trace_id` | `nvarchar(128)` | NO | `Trace` |
| `decision_id` | `nvarchar(64)` | NO | `Trace` |
| `scenario_id` | `nvarchar(64)` | NO | `Trace` |
| `rules_version` | `nvarchar(64)` | NO | `Trace` |
| `parameters_version` | `nvarchar(64)` | NO | `Trace` |
| `data_snapshot_id` | `nvarchar(64)` | NO | `Trace` |
| `input_fingerprint` | `char(64)` | NO | `Trace` |
| `rule_id` | `nvarchar(64)` | NO | `Trace` |
| `assessment_status` | `varchar(16)` | NO | `Trace` |
| `assessment_outcome` | `bit` | SÍ | `Trace` |
| `created_at` | `datetimeoffset(7)` | NO | `Trace` |

`trace_id` es la identidad canónica del Trace. SQL no genera ni sustituye el Trace producido por C0.

La combinación de `decision_id`, `scenario_id`, versiones, `data_snapshot_id`, fingerprint y regla se conserva como parte material del Trace.

---

## 4.9 `eios.c0_trace_evidence`

Normaliza la colección `Trace.evidence_ids` y conserva su orden original.

| Columna | SQL Server | Null | Origen |
|---|---|---:|---|
| `trace_id` | `nvarchar(128)` | NO | `Trace` |
| `evidence_ordinal` | `int` | NO | Posición técnica de la colección |
| `evidence_id` | `nvarchar(64)` | NO | `Trace.evidence_ids` |

Clave primaria: (`trace_id`, `evidence_ordinal`).

Restricción única adicional: (`trace_id`, `evidence_id`).

Claves externas:

```text
trace_id    → eios.c0_trace.trace_id
evidence_id → eios.c0_evidence.evidence_id
```

---

# 5. Relaciones físicas autorizadas

Las relaciones físicas confirmadas en este slice son únicamente:

```text
c0_evidence_validation
        └── evidence_id → c0_evidence

c0_assessment_evidence
        ├── assessment_row_id → c0_assessment
        └── evidence_id       → c0_evidence

c0_trace_evidence
        ├── trace_id    → c0_trace
        └── evidence_id → c0_evidence
```

No se introducen claves externas hacia catálogos funcionales todavía no materializados en SQL.

Tampoco se crean relaciones físicas para dependencias RDM `DATA`, `EVIDENCE` o `COMPONENT` que continúan `PENDING`.

---

# 6. Integridad física

Se aplicarán `PRIMARY KEY`, `UNIQUE`, `FOREIGN KEY` y `CHECK` únicamente para garantizar integridad del modelo ya autorizado.

Restricciones mínimas:

- identificadores obligatorios: `NOT NULL`;
- `quantity > 0`;
- `unit_price >= 0`;
- `currency = 'EUR'`;
- `state IN ('DEMONSTRATED','GAP')`;
- `status` de validación en `VALID/INVALID`;
- `Assessment.status` en `EVALUABLE/NOT_EVALUABLE`;
- coherencia `Assessment.status/outcome`;
- `Trace.assessment_status` en `EVALUABLE/NOT_EVALUABLE`;
- coherencia `Trace.assessment_status/assessment_outcome`;
- `input_fingerprint` exactamente 64 caracteres;
- `Trace.input_fingerprint` exactamente 64 caracteres;
- `evidence_ordinal >= 0`.

Estas restricciones son técnicas y no redefinen reglas empresariales.

---

# 7. Tipos numéricos

`quantity` y `unit_price` se almacenarán como `decimal(38,4)` para preservar los cuatro decimales autorizados por el contrato Python y evitar tipos aproximados. La precisión 38 es el máximo decimal soportado por SQL Server y no introduce una cota funcional adicional respecto al contrato Python, que no establece un máximo superior.

No se utilizará `float` para estos campos.

---

# 8. Fechas y tiempo

- `operation_date` y `captured_at` → `date`, conforme al modelo Python.
- `created_at` → `datetimeoffset(7)`, para conservar el carácter aware del `datetime` producido por C0 y evitar perder el offset.

SQL no reinterpretará `created_at` como fecha de negocio.

---

# 9. Fingerprint

El fingerprint de C0 se almacena como `char(64)` en representación hexadecimal.

SQL no lo recalcula.

El algoritmo y la serialización canónica permanecen bajo la autoridad de C0. SQL solo conserva el resultado.

---

# 10. Índices iniciales

Además de las claves primarias y restricciones `UNIQUE`, el diseño contempla índices no clúster para los patrones de acceso derivados del propio modelo:

- `c0_input(decision_id, scenario_id)`;
- `c0_context(decision_id, scenario_id, rules_version, parameters_version, data_snapshot_id)`;
- `c0_assessment(rule_id, status)`;
- `c0_trace(decision_id, scenario_id, created_at)`;
- claves externas de las tablas de relación.

No se crean índices sobre campos cuya utilidad no esté justificada por el perímetro actual.

---

# 11. Versionado técnico SQL

El esquema físico tendrá su propio versionado de migraciones.

```text
SQL Schema Version
        ≠
Rules_Version
        ≠
Parameters_Version
        ≠
Scenario Version
        ≠
Decision State Version
```

No se implementan todavía migraciones concretas en este documento.

---

# 12. Fuera de alcance

Este diseño no define todavía:

- tablas funcionales de parámetros;
- catálogo completo de reglas;
- persistencia completa de RDM;
- Decision Versioning físico completo;
- Scenario Engine;
- Viability;
- CRC;
- Negotiation;
- Decision Twin;
- API;
- ORM;
- driver Python;
- conexión operacional;
- despliegue SQL Server;
- permisos de producción;
- particionamiento;
- temporal tables;
- triggers;
- procedimientos almacenados.

Cualquier incorporación posterior deberá superar la auditoría correspondiente.

---

# 13. Trazabilidad de diseño

| Elemento físico | Autoridad principal |
|---|---|
| `c0_input` | C0 `PurchaseOperation` / InputContract |
| `c0_context` | C0 `DecisionContext` |
| `c0_evidence` | C0 `Evidence` + Evidence Contract |
| `c0_evidence_validation` | C0 `EvidenceValidation` |
| `c0_rule_contract` | C0 `Rule` + Matriz de Reglas |
| `c0_assessment` | Assessment Contract |
| `c0_assessment_evidence` | Assessment Contract |
| `c0_trace` | C0 `Trace` + Decision Versioning para referencias |
| `c0_trace_evidence` | C0 `Trace` |

---

# 14. Auditoría de cierre

La auditoría de diseño ha confirmado:

- correspondencia de las columnas con los contratos físicos C0;
- preservación de cadenas y referencias Unicode mediante tipos Unicode donde corresponde;
- ausencia de campos funcionales inventados;
- ausencia de relaciones funcionales inferidas;
- preservación de `NOT_EVALUABLE ≠ FALSE`;
- preservación del fingerprint y Trace producidos por C0;
- integridad referencial limitada a relaciones físicamente demostradas;
- independencia entre versionado SQL y versionado funcional/decisional;
- compatibilidad de los tipos y restricciones propuestos con SQL Server;
- ausencia de necesidad de modificar autoridades superiores.

La auditoría detectó y corrigió en esta versión la utilización inicial de `varchar` para campos de texto procedentes de contratos Python `str`; el diseño final utiliza `nvarchar` para conservar Unicode sin depender de la colación del servidor.

El orden de las colecciones `evidence_ids` se conserva mediante un ordinal técnico, sin atribuirle significado decisional.

**Estado de cierre: CERRADO.**

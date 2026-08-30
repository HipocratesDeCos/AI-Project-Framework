# EIOS — Decision Versioning · Modelo Físico SQL Server

## Estado

**Versión:** 1.0  
**Estado:** CERRADO — Diseño físico técnico  
**Fase:** 8 — Implementación Técnica  
**SGBD objetivo:** Microsoft SQL Server  
**Ámbito:** Persistencia mínima de Decision Versioning

---

## 1. Autoridad y propósito

Este documento desarrolla técnicamente el `Decision_Versioning_Implementation_Contract.md` sin redefinir `05_Motor/Decision_Versioning.md`.

`06_SQL` es responsable de transformar el contrato de implementación en persistencia física. SQL no crea significado funcional nuevo.

El diseño se limita a conservar la continuidad histórica y las referencias necesarias del estado decisional EIOS.

No implementa Scenario Engine, Viability, Decision Twin, Negotiation, CRC, Forecast, RFP ni decisión empresarial humana.

---

## 2. Objeto físico

Se materializa un único objeto principal:

```text
eios.decision_state
```

La tabla representa un registro físico de estado decisional EIOS, no una nueva autoridad funcional.

Cada fila debe permanecer distinguible de las demás y no debe sobrescribirse para representar un estado posterior.

---

## 3. Identidad

### 3.1 Identificador técnico

```text
decision_state_record_id bigint IDENTITY(1,1) NOT NULL
```

Es exclusivamente técnico y no representa `Decision_ID`, una versión funcional, una decisión humana ni un acto de aprobación.

### 3.2 Identidad funcional

```text
decision_id nvarchar(64) NOT NULL
```

Reutiliza la semántica de `Decision_ID` ya establecida por C0 y Decision Versioning. No se genera una clave funcional alternativa.

---

## 4. Columnas

| Columna | SQL Server | Null | Semántica |
|---|---|---:|---|
| `decision_state_record_id` | `bigint IDENTITY(1,1)` | NO | Identificador físico técnico |
| `decision_id` | `nvarchar(64)` | NO | Unidad decisional EIOS |
| `scenario_id` | `nvarchar(64)` | NO | Referencia al escenario |
| `data_snapshot_id` | `nvarchar(64)` | NO | Referencia al snapshot utilizado |
| `rules_version` | `nvarchar(64)` | NO | Referencia a versión de reglas |
| `parameters_version` | `nvarchar(64)` | NO | Referencia a versión de parámetros |
| `forecast_version` | `nvarchar(64)` | SÍ | Referencia futura/aplicable |
| `rfp_version` | `nvarchar(64)` | SÍ | Referencia futura/aplicable |
| `eios_version` | `nvarchar(64)` | SÍ | Referencia de versión EIOS cuando exista su contrato físico |
| `timestamp` | `datetimeoffset(7)` | NO | Instante de registro del estado, UTC |
| `user_id` | `nvarchar(128)` | NO | Identificador técnico del actor que origina/registra el estado |
| `input_fingerprint` | `char(64)` | SÍ | Fingerprint producido por C0, cuando exista |
| `trace_id` | `nvarchar(128)` | SÍ | Referencia al Trace C0 pertinente, cuando exista |

En el DDL, `timestamp` se delimita como identificador SQL Server (`[timestamp]`).

---

## 5. Tipos y límites

`decision_id`, `scenario_id`, `data_snapshot_id`, `rules_version` y `parameters_version` utilizan `nvarchar(64)`, conforme al perímetro C0.

`input_fingerprint` utiliza `char(64)` y, cuando no sea `NULL`, debe contener exactamente 64 caracteres hexadecimales. SQL no recalcula el fingerprint.

`trace_id` utiliza `nvarchar(128)`, conforme a `Trace.trace_id` en C0.

`user_id` utiliza `nvarchar(128)` como límite técnico para el identificador del actor. Puede representar un actor humano o un servicio/proceso autorizado. No define política de identidad, autenticación o autorización.

`timestamp` utiliza `datetimeoffset(7)` y representa el instante de registro del estado en UTC.

---

## 6. Nulabilidad

Son obligatorias las referencias mínimas del estado:

```text
decision_id
scenario_id
data_snapshot_id
rules_version
parameters_version
timestamp
user_id
```

Son opcionales, por depender de disponibilidad y aplicabilidad:

```text
forecast_version
rfp_version
eios_version
input_fingerprint
trace_id
```

La ausencia de una referencia opcional no se convierte en cadena vacía, versión cero ni valor ficticio.

---

## 7. Integridad física

Los campos obligatorios no pueden ser `NULL` ni cadena vacía. La persistencia no normaliza ni modifica el valor recibido.

Si `input_fingerprint IS NOT NULL`, debe cumplirse longitud 64 y contenido hexadecimal `0-9A-Fa-f`.

`decision_state_record_id` es la única identidad técnica de la fila. No se establece `UNIQUE(decision_id)`, porque una unidad decisional puede tener múltiples estados históricos.

No se establece unicidad sobre la combinación contextual: dos registros físicamente distintos pueden representar estados históricos distinguibles aun cuando algunas referencias coincidan.

---

## 8. Continuidad histórica

La tabla es conceptualmente append-only. Un nuevo estado se representa mediante una nueva fila.

No se utiliza trigger de versionado, temporal table como sustituto de Decision Versioning, `current_flag` como identidad histórica, ni una `Decision State Version` generada por SQL.

La protección física se realiza mediante el perfil de permisos de persistencia: el rol de escritura recibe `SELECT` e `INSERT` y tiene `UPDATE` y `DELETE` expresamente denegados sobre `eios.decision_state`.

---

## 9. Relación con C0

Cuando exista una evaluación C0 asociada, la fila puede conservar `input_fingerprint` y `trace_id` procedentes de C0.

La tabla no sustituye a `eios.c0_context` ni `eios.c0_trace`, y no genera un segundo fingerprint, Trace, snapshot o DecisionContext.

No se crea FK hacia `c0_trace` en esta primera materialización porque el contrato de implementación exige conservar la referencia sin imponer todavía una política de ciclo de vida compartido entre ambas persistencias.

---

## 10. Referencias opcionales

No se crean FKs ni catálogos ficticios para `forecast_version`, `rfp_version` o `eios_version` mientras no existan sus contratos físicos correspondientes.

---

## 11. Índices

En esta etapa solo queda justificado el índice implícito de la clave primaria:

```text
PK_decision_state
    → decision_state_record_id
```

No se materializan índices adicionales.

La razón es metodológica: el contrato de implementación exige que los índices respondan a patrones de acceso demostrados por implementación y pruebas. En ausencia de implementación específica de Decision Versioning y de tests de acceso, añadir índices adicionales sería una inferencia documental y no una necesidad demostrada.

Los índices adicionales podrán diseñarse posteriormente, pero deberán justificar su existencia mediante evidencia de acceso real y pasar la auditoría correspondiente.

---

## 12. Reconstrucción

Una fila permite recuperar las referencias del estado decisional registrado. La reconstrucción completa depende de la disponibilidad de los artefactos referenciados.

```text
eios.decision_state
        │
        ├── Decision_ID
        ├── Scenario_ID
        ├── Data_Snapshot_ID
        ├── Rules_Version
        ├── Parameters_Version
        ├── Forecast_Version
        ├── RFP_Version
        ├── EIOS_Version
        ├── Timestamp
        ├── User
        ├── input_fingerprint
        └── trace_id
```

SQL proporciona recuperación física; no realiza por sí mismo reconstrucción semántica.

---

## 13. Límites

Este modelo no define escenarios, reglas, parámetros, Forecast, RFP, versión funcional de EIOS, autorización de usuarios ni decisión empresarial.

---

## 14. Auditoría 2 — dictamen

El diseño ha sido contrastado contra:

- `05_Motor/Decision_Versioning.md`;
- `08_Implementacion/Decision_Versioning_Implementation_Contract.md`;
- `06_SQL/06_LEEME_SQL.md`;
- modelos y tipos físicos de C0;
- límites y nulabilidad de C0;
- reglas de no duplicación de fingerprint/Trace/snapshot;
- frontera de referencias futuras;
- patrón SQL Server ya materializado en C0;
- criterio de índices basado en acceso demostrado.

Resultado:

- no se modifica ninguna autoridad funcional;
- no se modifica C0;
- no se introducen FKs sobre artefactos futuros;
- `Timestamp` queda resuelto como `datetimeoffset(7)` UTC;
- `User` queda representado técnicamente mediante `user_id nvarchar(128)` como identificador de actor;
- la inmutabilidad se expresa como frontera de permisos, sin trigger ni temporal table;
- no se introducen índices no demostrados;
- el uso de `[timestamp]` queda explícitamente delimitado para SQL Server;
- el DDL resultante coincide con esta frontera técnica.

**DICTAMEN: AUDITORÍA 2 SUPERADA. DISEÑO FÍSICO CERRADO.**

---

## 15. Estado

**CERRADO — DISEÑO FÍSICO TÉCNICO**

El DDL puede someterse ahora a validación real en SQL Server y CI. La validación no autoriza cambios funcionales ni modifica las autoridades superiores.

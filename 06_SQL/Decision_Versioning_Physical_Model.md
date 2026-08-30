# EIOS — Decision Versioning · Modelo Físico SQL Server

## Estado

**Versión:** 0.1  
**Estado:** BORRADOR DE DISEÑO TÉCNICO  
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

Se propone un único objeto principal:

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

---

## 8. Continuidad histórica

La tabla es conceptualmente append-only. Un nuevo estado se representa mediante una nueva fila.

No se utiliza trigger de versionado, temporal table como sustituto de Decision Versioning, `current_flag` como identidad histórica, ni una `Decision State Version` generada por SQL.

La protección física contra modificación o borrado destructivo se resolverá mediante el mecanismo de permisos/operación de persistencia definido por `06_SQL`, sin alterar la semántica del contrato.

---

## 9. Relación con C0

Cuando exista una evaluación C0 asociada, la fila puede conservar `input_fingerprint` y `trace_id` procedentes de C0.

La tabla no sustituye a `eios.c0_context` ni `eios.c0_trace`, y no genera un segundo fingerprint, Trace, snapshot o DecisionContext.

La relación física inicial se mantiene deliberadamente sin FK hacia esos objetos hasta que su ciclo de vida de persistencia defina una relación de largo plazo.

---

## 10. Referencias opcionales

No se crean FKs ni catálogos ficticios para `forecast_version`, `rfp_version` o `eios_version` mientras no existan sus contratos físicos correspondientes.

---

## 11. Índices

Índices iniciales propuestos:

```text
PK_decision_state
    → decision_state_record_id

IX_decision_state_decision_timestamp
    → (decision_id, timestamp)

IX_decision_state_scenario_timestamp
    → (scenario_id, timestamp)
```

Se justifican por reconstrucción histórica de una unidad decisional y recuperación histórica por escenario y tiempo.

No se indexan inicialmente `user_id`, `input_fingerprint`, `forecast_version`, `rfp_version` ni `eios_version` por ausencia de un patrón de acceso demostrado.

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

## 14. Auditoría previa al DDL

Antes de materializar el DDL deberán comprobarse:

1. correspondencia exacta con `Decision_Versioning_Implementation_Contract.md`;
2. ausencia de contradicciones con C0;
3. ausencia de FKs sobre artefactos futuros;
4. validez de `datetimeoffset(7)` / UTC;
5. adecuación del límite de `user_id`;
6. validación hexadecimal del fingerprint;
7. mecanismo append-only definido por `06_SQL`;
8. justificación de índices por patrones reales de acceso;
9. rollback/limpieza segura en CI;
10. ausencia de modificación de autoridades superiores.

---

## 15. Estado

**BORRADOR DE DISEÑO TÉCNICO — PENDIENTE DE AUDITORÍA**

Este documento no autoriza todavía la creación del DDL.

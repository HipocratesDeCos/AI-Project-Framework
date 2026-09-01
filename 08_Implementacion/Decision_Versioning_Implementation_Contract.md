# EIOS — Decision Versioning Implementation Contract

## 1. Identidad

**Documento:** Decision Versioning Implementation Contract  
**Versión:** 1.3  
**Estado:** CERRADO — Contrato técnico de implementación  
**Baseline:** EIOS Vertical MVP  
**Ubicación:** `08_Implementacion/Decision_Versioning_Implementation_Contract.md`

---

## 2. Propósito

Este documento define la frontera técnica mínima para materializar `Decision Versioning` sin redefinir su contrato funcional ni crear autoridades paralelas.

No constituye una nueva autoridad funcional.

La autoridad conceptual permanece en `05_Motor/Decision_Versioning.md`.

La autoridad de persistencia técnica corresponde a `06_SQL/06_LEEME_SQL.md`.

---

## 3. Principio de materialización mínima

La implementación debe persistir únicamente las referencias que ya tienen significado autorizado y que sean necesarias para conservar la continuidad histórica del estado decisional.

No se materializarán como obligatorias referencias cuya autoridad o contrato físico todavía no exista.

En particular, `Forecast_Version`, `RFP_Version` y `EIOS_Version` quedan como referencias opcionales hasta disponer de sus contratos físicos correspondientes.

---

## 4. Identidad física

La persistencia utiliza un identificador técnico interno denominado `decision_state_record_id`.

Este identificador:

- identifica exclusivamente el registro físico;
- no redefine `Decision_ID`;
- no representa una decisión humana;
- no constituye por sí mismo una nueva `Decision State Version`;
- no sustituye a `Decision_ID`;
- no adquiere significado empresarial.

La identidad funcional continúa siendo la definida por `Decision Versioning`.

---

## 5. Referencias mínimas de materialización

El registro físico conserva:

```text
Decision_ID
Scenario_ID
Data_Snapshot_ID
Rules_Version
Parameters_Version
Timestamp
User
```

Estas referencias se almacenan sin modificar su semántica.

La presencia física de una referencia refleja su aplicabilidad y disponibilidad reales. No se inventan valores para satisfacer restricciones físicas.

---

## 6. Referencias opcionales

Pueden existir, cuando estén disponibles y autorizadas:

```text
Forecast_Version
RFP_Version
EIOS_Version
```

No se crean FK ni catálogos físicos para estos conceptos mientras no exista autoridad física suficiente para los artefactos referenciados.

La ausencia de estas referencias no debe interpretarse como versión vacía, versión cero ni valor por defecto.

---

## 7. C0

La materialización reutiliza las referencias producidas o conservadas por C0:

```text
Decision_ID
Scenario_ID
Data_Snapshot_ID
input_fingerprint
Trace
```

`Rules_Version` y `Parameters_Version` continúan siendo referencias del `DecisionContext` de C0; no se duplican como nuevas autoridades.

`input_fingerprint` y `Trace` se conservan como referencias o valores derivados del flujo C0 según corresponda.

No se genera:

- segundo fingerprint;
- segundo Trace;
- segundo snapshot;
- sustituto de `DecisionContext`.

No se modifica C0 para implementar Decision Versioning.

---

## 8. Timestamp

`Timestamp` representa el momento temporal del registro del estado.

**Decisión técnica cerrada:**

```text
Tipo SQL          → datetimeoffset(7)
Zona horaria      → UTC
Origen conceptual → instante de registro del estado
```

La implementación mantiene una fuente de reloj coherente y no introduce una segunda semántica temporal para Decision Versioning.

El precedente técnico es `Trace.created_at` de C0, que ya utiliza `datetimeoffset(7)` y se genera con un `datetime` consciente de zona horaria en UTC.

Esta decisión no convierte `Trace.created_at` en `Decision Versioning.Timestamp`; son atributos distintos que comparten una convención temporal común.

---

## 9. User

`User` identifica técnicamente al **actor que origina o registra el estado en EIOS**.

El actor puede ser:

- un usuario humano;
- un servicio o proceso técnico autorizado.

No implica que sea:

- decisor;
- aprobador;
- CEO;
- propietario de la decisión;
- responsable jurídico.

La implementación no creará semántica adicional de roles dentro de Decision Versioning.

La semántica de `User` no autoriza por sí sola una política de identidad, autenticación o autorización; esas materias permanecen fuera de este contrato.

---

## 10. Inmutabilidad histórica

Un registro histórico materializado no se sobrescribe para representar un estado posterior.

La evolución se representa mediante registros distinguibles.

La implementación no introduce un mecanismo paralelo de versionado funcional.

La inmutabilidad funcional queda cerrada como invariante y se materializa físicamente mediante controles de persistencia definidos en `06_SQL`.

---

## 11. Reconstrucción

La persistencia permite recuperar las referencias necesarias para reconstruir un estado decisional, pero no promete la recuperación de artefactos históricos que ya no estén disponibles bajo sus respectivas autoridades.

SQL proporciona recuperación técnica.

Decision Versioning conserva la continuidad histórica.

Assurance utiliza esa continuidad para verificar reconstruibilidad.

---

## 12. Integridad

El esquema físico impide, cuando es técnicamente determinable:

- referencias imposibles dentro del mismo registro;
- pérdida silenciosa de identificadores necesarios cuando estén disponibles;
- modificación destructiva de registros históricos;
- duplicación semántica de mecanismos C0.

Las restricciones no introducen reglas empresariales nuevas.

---

## 13. Índices

Los índices físicos se mantienen exclusivamente a partir de patrones de acceso demostrados por la implementación y las pruebas.

No se considera obligatorio ningún índice por mera conveniencia documental.

---

## 14. Límites

Este contrato no define:

- reglas de negocio;
- parámetros;
- escenarios;
- Forecast;
- RFP;
- Decision Twin;
- CRC;
- recomendaciones;
- decisiones humanas;
- política de selección;
- API;
- autenticación;
- retención legal;
- archivado empresarial.

---

## 15. Materialización física

La materialización física autorizada se encuentra en:

```text
06_SQL/002_Decision_Versioning_Schema.sql
06_SQL/Decision_Versioning_Physical_Model.md
```

El DDL crea `eios.decision_state` con el identificador técnico `decision_state_record_id` y las referencias mínimas y opcionales definidas por este contrato.

La persistencia utiliza `datetimeoffset(7)` para `timestamp`, con control de UTC, y aplica controles físicos de inmutabilidad mediante permisos de escritura.

El modelo físico declara expresamente la frontera técnica cerrada y su correspondencia con el DDL.

---

## 16. Relación con SQL

`06_SQL` transforma este contrato técnico en persistencia física conforme a sus propias convenciones.

SQL no resuelve mediante DDL una ambigüedad funcional no autorizada.

La relación materializada es:

```text
Decision Versioning
        ↓
contrato funcional
        ↓
Implementation Contract
        ↓
06_SQL
        ↓
DDL materializado
```

---

## 17. Criterio de cierre

El presente contrato queda cerrado cuando:

- sus campos y referencias son trazables a autoridades existentes;
- no introduce semántica funcional nueva;
- C0 permanece inalterado;
- las referencias opcionales permanecen explícitamente condicionadas;
- Timestamp y User mantienen una frontera técnica sin inventar semántica funcional;
- la inmutabilidad es implementable sin crear una nueva versión funcional;
- los índices pueden justificarse por acceso real;
- la materialización física puede auditarse contra este contrato.

Estas condiciones se encuentran satisfechas para la materialización física actualmente presente en `06_SQL` y validada por CI.

---

## 18. Estado

**DICTAMEN:** CERRADO Y MATERIALIZADO  
**Tipo de cambio:** DOCUMENTACIÓN DE IMPLEMENTACIÓN  
**Cambios técnicos derivados:** NINGUNO  
**C0:** NO ALTERADO  
**DDL:** CREADO Y MATERIALIZADO  
**CI:** VERIFICADA SATISFACTORIAMENTE  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

---

## Historial

### v1.3

Corrección documental post-materialización. Se actualiza el estado del DDL y se sustituyen los criterios previos a la creación física por la referencia a la materialización existente. No se modifica el contrato funcional ni el DDL.

# EIOS — Decision Versioning Implementation Contract

## 1. Identidad

**Documento:** Decision Versioning Implementation Contract  
**Versión:** 1.2  
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

La persistencia puede utilizar un identificador técnico interno denominado `decision_state_record_id`.

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

El registro físico debe poder conservar, cuando formen parte del contexto disponible:

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

La presencia física de una referencia debe reflejar su aplicabilidad y disponibilidad reales. No se inventarán valores para satisfacer restricciones físicas.

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

La implementación deberá mantener una fuente de reloj coherente y no introducir una segunda semántica temporal para Decision Versioning.

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

Un registro histórico materializado no debe sobrescribirse para representar un estado posterior.

La evolución se representa mediante registros distinguibles.

La implementación no introducirá un mecanismo paralelo de versionado funcional.

La inmutabilidad funcional queda cerrada como invariante; el mecanismo físico concreto se definirá en `06_SQL` sin alterar esta semántica.

---

## 11. Reconstrucción

La persistencia debe permitir recuperar las referencias necesarias para reconstruir un estado decisional, pero no debe prometer la recuperación de artefactos históricos que ya no estén disponibles bajo sus respectivas autoridades.

SQL proporciona recuperación técnica.

Decision Versioning conserva la continuidad histórica.

Assurance utiliza esa continuidad para verificar reconstruibilidad.

---

## 12. Integridad

El esquema físico deberá impedir, cuando sea técnicamente determinable:

- referencias imposibles dentro del mismo registro;
- pérdida silenciosa de identificadores necesarios cuando estén disponibles;
- modificación destructiva de registros históricos;
- duplicación semántica de mecanismos C0.

Las restricciones no podrán introducir reglas empresariales nuevas.

---

## 13. Índices

Los índices físicos se definirán exclusivamente a partir de patrones de acceso demostrados por la implementación y las pruebas.

No se considerará obligatorio ningún índice por mera conveniencia documental.

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

## 15. Dependencias de cierre físico

Antes de crear el DDL deberán estar cerrados:

1. tipo y precisión de `Timestamp`;
2. longitud/tipo técnico de identificadores y referencias;
3. semántica física de `User`;
4. política física de inmutabilidad;
5. patrones de acceso que justifiquen índices;
6. estrategia de referencia de `input_fingerprint` y `Trace`;
7. alcance exacto de las referencias opcionales.

Con la decisión de `Timestamp` y `User` adoptada para EIOS, quedan resueltos los puntos 1 y 3. Los puntos restantes continúan siendo criterios técnicos previos al DDL y serán resueltos por la autoridad de persistencia sin redefinir este contrato.

La ausencia de estos cierres restantes impide pasar legítimamente a DDL.

---

## 16. Relación con SQL

`06_SQL` será responsable de transformar este contrato técnico en persistencia física conforme a sus propias convenciones.

SQL no podrá resolver mediante DDL una ambigüedad funcional no resuelta.

La relación es:

```text
Decision Versioning
        ↓
contrato funcional
        ↓
Implementation Contract
        ↓
06_SQL
        ↓
DDL
```

---

## 17. Criterio de cierre

El presente contrato queda cerrado cuando:

- sus campos y referencias sean trazables a autoridades existentes;
- no introduzca semántica funcional nueva;
- C0 permanezca inalterado;
- las referencias opcionales permanezcan explícitamente condicionadas;
- Timestamp y User mantengan una frontera técnica sin inventar semántica funcional;
- la inmutabilidad sea implementable sin crear una nueva versión funcional;
- los índices puedan justificarse por acceso real;
- la materialización física pueda auditarse contra este contrato.

La auditoría de cierre confirma estas condiciones para el nivel de contrato técnico definido aquí. Los detalles físicos enumerados en la sección 15 permanecen como criterios previos al DDL y no constituyen un bloqueo del contrato de implementación.

---

## 18. Estado

**DICTAMEN:** CERRADO

**Tipo de cambio:** DOCUMENTACIÓN DE IMPLEMENTACIÓN  
**Cambios técnicos derivados:** NINGUNO  
**C0:** NO ALTERADO  
**DDL:** NO CREADO  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR

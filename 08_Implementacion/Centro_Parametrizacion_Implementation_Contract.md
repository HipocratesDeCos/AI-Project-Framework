# EIOS — Centro de Parametrización — Implementation Contract

## 1. Identidad

**Documento:** Centro de Parametrización — Implementation Contract  
**Versión:** 1.2  
**Estado:** CERRADO — Contrato técnico de implementación  
**Baseline de referencia:** EIOS-BL-001  
**Autoridad funcional:** `02_Parametros/Centro_Parametrizacion.md`  
**Autoridad de parámetros:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`  
**Autoridad de reglas:** `04_Reglas/Matriz_Reglas_MVP.md`  
**Autoridad de persistencia:** `06_SQL/06_LEEME_SQL.md`

## 2. Propósito

Define la frontera técnica mínima para materializar el Centro de Parametrización sin redefinir su contrato funcional, el Catálogo de Parámetros, las Reglas ni crear una autoridad paralela.

El Centro administra configuración. No interpreta reglas, no decide viabilidad y no produce decisiones empresariales.

## 3. Perímetro MVP

La implementación soporta:

- identificación de parámetros autorizados;
- consulta de configuración;
- valor y tipo/unidad cuando estén definidos por el catálogo;
- ámbito por empresa;
- vigencia;
- modificación autorizada;
- histórico de cambios;
- trazabilidad de cambios;
- control de parámetros con restricciones reforzadas;
- recuperación de la configuración aplicable a un contexto decisional.

Quedan fuera del contrato MVP:

- simulación de cambios;
- creación arbitraria de parámetros;
- creación o modificación de lógica de reglas;
- resolución CRC;
- modificación de salvaguardas;
- creación de excepciones no autorizadas;
- decisión o recomendación empresarial;
- autenticación como política autónoma;
- UI concreta;
- fórmulas de cálculo no definidas por la autoridad funcional.

## 4. Principios de autoridad

1. El Catálogo determina qué parámetros existen y su semántica autorizada.
2. El Centro administra valores/configuraciones de esos parámetros.
3. Rules interpreta las reglas; el Centro no las evalúa.
4. CRC conserva su autoridad sobre resolución/consolidación.
5. SQL define la representación física de persistencia.
6. Ninguna operación del Centro puede utilizarse para eludir una salvaguarda superior.
7. La configuración no constituye una decisión humana.

## 5. Identidad física

La implementación utiliza una identidad técnica interna para el registro de configuración.

Esta identidad:

- no sustituye `parameter_id`;
- no redefine la identidad empresarial del parámetro;
- no representa una regla;
- no representa una decisión;
- no constituye por sí misma una autoridad.

`parameter_id` corresponde a un parámetro reconocido por el Catálogo.

## 6. Modelo lógico mínimo

Una configuración representa, cuando corresponde:

```text
parameter_id
company_id
value
value_type / unit
valid_from
valid_to
created_at
updated_at
```

Un cambio conserva:

```text
previous_value
new_value
changed_by
changed_at
change_reason
company_id
parameter_id
```

El contrato no define una taxonomía propia de estados de configuración. Cualquier estado funcional proviene de la autoridad documental correspondiente.

El contrato no fija una unidad propia de versionado decisional. El histórico de configuración se materializa bajo las estructuras físicas de `06_SQL` sin crear una segunda semántica de versionado de decisiones.

## 7. Operaciones semánticas mínimas

```text
get_parameter(parameter_id)
get_current_configuration(company_id, parameter_id)
get_configuration_at(company_id, parameter_id, effective_at)
get_parameter_history(company_id, parameter_id)
validate_change(company_id, parameter_id, value, validity)
apply_change(company_id, parameter_id, value, validity, actor, reason)
```

Estas operaciones son contractuales y no implican una API pública concreta.

`get_configuration_at` expresa recuperación histórica por momento efectivo.

No se define una operación genérica que permita modificar sin validación cualquier parámetro o regla.

## 8. Invariantes

**CP-I01 — Identidad:** todo parámetro configurado debe existir en el Catálogo autorizado.

**CP-I02 — Ámbito:** una configuración pertenece a un ámbito empresarial explícito.

**CP-I03 — Vigencia:** no deben coexistir configuraciones activas incompatibles para el mismo parámetro y ámbito.

**CP-I04 — Histórico:** un cambio no sobrescribe destructivamente el estado histórico.

**CP-I05 — Trazabilidad:** toda modificación conserva actor, instante, motivo y valores anterior/nuevo.

**CP-I06 — Autorización:** una modificación requiere autorización conforme a la política funcional aplicable.

**CP-I07 — Tipado:** el valor debe ser compatible con el tipo/unidad autorizado.

**CP-I08 — No autoridad de reglas:** modificar un valor no modifica la definición estructural de una regla.

**CP-I09 — No bypass:** ningún valor configurable puede anular por sí mismo una salvaguarda de autoridad superior.

**CP-I10 — No inferencia:** un parámetro sin consumidor autorizado no adquiere consumidor por estar almacenado.

**CP-I11 — Reconstruibilidad:** la evolución de configuración puede reconstruirse históricamente sin imponer una unidad de versionado decisional no autorizada.

**CP-I12 — No decisión:** el Centro no produce `BUY`, `BLOCK`, `NEGOTIATE`, viabilidad ni decisión final.

## 9. Parámetros restringidos

Los parámetros sujetos a controles reforzados, especialmente los financieros críticos, no deben seguir necesariamente el mismo flujo que un parámetro ordinario.

La implementación permite aplicar una política de autorización diferenciada sin redefinir esa política.

Los elementos de reglas, prioridades y excepciones que estén sometidos a autoridad específica no se convierten automáticamente en parámetros editables por el Centro.

## 10. Versionado y Decision Versioning

El Centro administra la evolución histórica de **configuración**.

Decision Versioning versiona **estado decisional**.

No se crea una segunda semántica de versionado de decisiones.

La relación conceptual es:

```text
Configuración aplicable
        ↓
DecisionContext
        ↓
Decision Version
```

La implementación del Centro no modifica C0 ni Decision Versioning.

## 11. Persistencia materializada

La persistencia física autorizada se encuentra en:

```text
06_SQL/003_Centro_Parametrizacion_Schema.sql
```

El esquema materializa `eios.parameter_configuration` y `eios.parameter_configuration_history`, junto con los controles físicos de integridad, índices y permisos de escritura definidos por SQL.

La persistencia preserva:

- identidad;
- aislamiento empresarial;
- vigencia;
- histórico;
- reconstruibilidad;
- trazabilidad;
- integridad de los valores.

No se introducen reglas empresariales mediante restricciones físicas que carezcan de autoridad funcional.

## 12. Errores mínimos

Las operaciones distinguen, como mínimo:

```text
PARAMETER_NOT_FOUND
INVALID_VALUE
INVALID_TYPE
INVALID_VALIDITY
UNAUTHORIZED_CHANGE
CONFLICTING_ACTIVE_CONFIGURATION
RESTRICTED_PARAMETER
INVALID_COMPANY_SCOPE
```

Los códigos definitivos son parte de la implementación, siempre que conserven estas semánticas.

## 13. Tests derivados

La implementación proporciona evidencia para, como mínimo:

```text
CP-I01 Identity
CP-I02 Company isolation
CP-I03 Validity
CP-I04 History
CP-I05 Traceability
CP-I06 Authorization
CP-I07 Type/unit integrity
CP-I08 No rule authority
CP-I09 No bypass
CP-I10 No inferred consumer
CP-I11 Historical reconstructibility
CP-I12 No decision output
```

Los tests no redefinen el contrato; cualquier contradicción se resuelve primero por autoridad documental.

## 14. Límites explícitos

Este contrato no define:

- reglas de negocio;
- fórmulas de precio;
- forecasting;
- viabilidad;
- escenarios;
- negociación;
- CRC;
- Decision Twin;
- política de selección de proveedores;
- autenticación o identidad corporativa;
- retención legal;
- UI;
- API pública;
- taxonomía propia de estados de configuración;
- semántica adicional de versionado decisional.

## 15. Criterio de cierre técnico

El Centro queda materializado cuando:

1. existe implementación ejecutable compatible con este contrato;
2. la persistencia física es compatible con `06_SQL`;
3. las invariantes críticas están cubiertas por tests;
4. no se han introducido autoridades nuevas;
5. la suite correspondiente termina satisfactoriamente en CI;
6. la evidencia permite reconstruir los cambios de configuración realizados.

Estas condiciones están satisfechas por la implementación y persistencia actualmente materializadas y validadas por CI.

## 16. Estado

**DICTAMEN:** CERRADO Y MATERIALIZADO  
**Tipo de cambio:** DOCUMENTACIÓN DE IMPLEMENTACIÓN  
**Cambios técnicos derivados:** NINGUNO  
**C0:** NO ALTERADO  
**Implementación Python:** MATERIALIZADA  
**DDL:** CREADO Y MATERIALIZADO  
**Tests:** MATERIALIZADOS  
**CI:** VERIFICADA SATISFACTORIAMENTE  
**Método:** DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI

## Historial

### v1.2

Corrección documental post-materialización. Se elimina el lenguaje condicional que describía el componente como potencialmente no implementado y se refleja la implementación Python, el DDL, los tests y la validación CI existentes. No se modifica la autoridad funcional ni la implementación técnica.

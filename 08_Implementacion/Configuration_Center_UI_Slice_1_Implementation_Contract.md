# EIOS — Configuration Center UI Slice 1 — Implementation Contract v0.1

**Estado:** DEPURADO — PENDIENTE DE AUDITORÍA 2  
**Fecha:** 2026-09-13  
**Baseline:** `main @ 6206df223f2f952977802300b2579f1e51e491d5`  
**Autoridad UI:** `03_App/Configuration_Center_UI_Contract_v0.1.md`  
**Backend:** `eios/parameters/center.py`

## 1. Objeto

Implementar el primer slice ejecutable provenance-safe del Configuration Center UI sin inventar capacidades que el backend físico no expone.

## 2. Alcance ejecutable

El slice recibe un contexto inmutable suministrado por una frontera aguas arriba con `company_id`, `parameter_id` y `actor`. El contexto es un carrier técnico: su existencia no constituye autenticación ni prueba de identidad.

Sobre ese contexto puede cargar definición, configuración vigente e histórico mediante `ParameterConfigurationCenter`; construir ViewModels inmutables; preparar una propuesta de cambio con nuevo valor, vigencia y motivo; validar; solicitar confirmación humana; revalidar inmediatamente antes de escribir; aplicar únicamente mediante `ParameterConfigurationCenter.apply_change(...)`; y devolver estado y configuración efectivamente aplicada.

## 3. Capacidades no implementables todavía

Quedan fuera porque no existe productor físico autorizado demostrado:

- enumeración global de parámetros;
- búsqueda/filtro por catálogo;
- enumeración de empresas autorizadas;
- autenticación o resolución de identidad del actor;
- cambio interactivo de actor o `company_id`;
- simulación de impacto.

No se fabrican adaptadores leyendo Markdown/YAML para suplir estas ausencias.

## 4. Frontera de confianza

`AuthorizedConfigurationUIContext` es un carrier inmutable, no un autenticador ni una credencial. El slice:

- no lo crea desde texto libre de Presentation;
- rechaza `company_id`, `parameter_id` o `actor` vacíos;
- no permite sustituir esos campos al preparar o confirmar cambios;
- no afirma que la identidad esté autenticada: esa garantía pertenece al integrador aguas arriba.

El backend conserva la última palabra sobre autorización mediante `validate_change` y `apply_change`.

## 5. Arquitectura

```text
Trusted upstream integration boundary
        ↓
AuthorizedConfigurationUIContext
        ↓
ConfigurationCenterUIController
        ↓
ParameterConfigurationCenter
        ↓
Catalogue / Authorization / Repository
```

El controlador no accede directamente a catálogo, autorización ni repositorio.

## 6. Estado ejecutable

Estados del slice: `READY`, `VIEWING`, `EDITING`, `VALIDATING`, `VALIDATION_FAILED`, `AWAITING_CONFIRMATION`, `REVALIDATING`, `APPLYING`, `APPLIED`, `FORBIDDEN`, `CONFLICT`, `ERROR`.

Son estados de interacción, no de dominio.

## 7. Propuesta pendiente y confirmación

Una propuesta pendiente contiene exclusivamente `value`, `valid_from`, `valid_to` y `reason`; `company_id`, `parameter_id` y `actor` se reconstruyen siempre desde el contexto inmutable del controlador.

La validación inicial no autoriza por sí misma la escritura.

`confirm_and_apply()` no recibe identificadores de actor, empresa o parámetro. Debe:

1. exigir una propuesta validada pendiente;
2. reconstruir `ChangeRequest` con contexto + propuesta;
3. ejecutar de nuevo `validate_change(...)`;
4. invocar `apply_change(...)`, que conserva su propia revalidación y atomicidad;
5. producir `APPLIED` únicamente si `apply_change(...)` retorna una `Configuration`;
6. ante cualquier excepción de contrato, producir fallo cerrado con código original y descartar la propuesta pendiente para exigir una nueva validación.

## 8. Datos presentacionales

El ViewModel expone solo datos procedentes de `ParameterDefinition`, `Configuration`, `HistoryEntry` y contexto. No inventa nombre descriptivo, categoría, valor estándar, impacto ni etiquetas de negocio ausentes.

## 9. Mapeo de errores

Los códigos de `ParameterConfigurationError` se conservan íntegros:

- `UNAUTHORIZED_CHANGE`, `RESTRICTED_PARAMETER` → `FORBIDDEN`;
- `CONFLICTING_ACTIVE_CONFIGURATION` → `CONFLICT`;
- `INVALID_VALUE`, `INVALID_TYPE`, `INVALID_VALIDITY`, `INVALID_COMPANY_SCOPE`, `PARAMETER_NOT_FOUND` → `VALIDATION_FAILED` cuando ocurren durante propuesta/revalidación;
- fallos no clasificados → `ERROR`.

Ninguna excepción produce `APPLIED`.

## 10. Tests obligatorios

- detalle vigente conserva identidad/valor/tipo/unidad;
- histórico conserva actor, motivo, empresa y valores;
- contexto incompleto se rechaza;
- propuesta no acepta actor/empresa/parámetro alternativos;
- validación fallida no crea confirmación pendiente;
- aplicar sin propuesta pendiente falla cerrado;
- confirmación revalida antes de aplicar;
- autorización revocada entre validación y confirmación impide escritura;
- conflicto aparecido entre validación y confirmación impide escritura;
- aplicación satisfactoria retorna `APPLIED` y configuración real;
- fallo de `apply_change` nunca produce éxito;
- no existe acceso directo del controlador a repository/catalogue/authorization.

## 11. Invariantes

**CCUIS1-I01:** contexto ≠ autenticación; no se fabrica identidad.  
**CCUIS1-I02:** no se enumeran parámetros/empresas sin productor.  
**CCUIS1-I03:** semántica funcional delegada a `ParameterConfigurationCenter`.  
**CCUIS1-I04:** identidad/empresa/parámetro ligados al contexto inmutable.  
**CCUIS1-I05:** confirmación explícita + revalidación obligatoria.  
**CCUIS1-I06:** solo retorno real de backend puede producir `APPLIED`.  
**CCUIS1-I07:** fail-closed ante autorización, conflicto o error.  
**CCUIS1-I08:** ViewModel sin inferencias de negocio.  
**CCUIS1-I09:** no direct persistence.  
**CCUIS1-I10:** no decisión de compra.

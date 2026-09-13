# EIOS — Configuration Center UI Slice 1 — Implementation Contract v0.1

**Estado:** DISEÑO  
**Fecha:** 2026-09-13  
**Baseline:** `main @ 6206df223f2f952977802300b2579f1e51e491d5`  
**Autoridad UI:** `03_App/Configuration_Center_UI_Contract_v0.1.md`  
**Backend:** `eios/parameters/center.py`

## 1. Objeto

Implementar el primer slice ejecutable provenance-safe del Configuration Center UI sin inventar capacidades que el backend físico no expone.

## 2. Alcance ejecutable

El slice recibe un contexto de selección ya autorizado aguas arriba con:

- `company_id`;
- `parameter_id`;
- `actor`.

Sobre ese contexto puede:

- cargar `ParameterDefinition` y configuración vigente mediante `ParameterConfigurationCenter`;
- cargar histórico;
- construir ViewModels inmutables de detalle e histórico;
- preparar una propuesta de cambio con nuevo valor, vigencia y motivo;
- ejecutar `validate_change(...)`;
- producir un estado `AWAITING_CONFIRMATION` únicamente tras validación satisfactoria;
- exigir confirmación explícita;
- reconstruir y revalidar el `ChangeRequest` inmediatamente antes de `apply_change(...)`;
- aplicar únicamente mediante `ParameterConfigurationCenter.apply_change(...)`;
- devolver el estado final y la configuración aplicada.

## 3. Capacidades no implementables todavía

Quedan fuera de este slice porque no existe productor físico autorizado demostrado:

- enumeración global de parámetros;
- búsqueda/filtro por catálogo;
- enumeración de empresas autorizadas;
- autenticación o resolución de identidad del actor;
- cambio interactivo de actor o `company_id`;
- simulación de impacto.

No se fabrican adaptadores leyendo Markdown/YAML para suplir estas ausencias.

## 4. Frontera de confianza

`AuthorizedConfigurationUIContext` es un **carrier**, no un autenticador. El slice nunca lo crea a partir de texto libre de Presentation.

La procedencia/autorización del contexto corresponde a una frontera aguas arriba. Si no existe contexto completo, el slice no opera.

El backend conserva la última palabra sobre autorización de modificación mediante `validate_change`/`apply_change`.

## 5. Arquitectura

```text
Trusted upstream context
        ↓
ConfigurationCenterUIController
        ↓
ParameterConfigurationCenter
        ↓
Catalogue / Authorization / Repository
```

El controlador no accede directamente a catálogo, autorización ni repositorio.

## 6. Modelo de estado

Estados ejecutables del slice:

- `READY`
- `VIEWING`
- `EDITING`
- `VALIDATING`
- `VALIDATION_FAILED`
- `AWAITING_CONFIRMATION`
- `REVALIDATING`
- `APPLYING`
- `APPLIED`
- `FORBIDDEN`
- `CONFLICT`
- `ERROR`

Los estados son de interacción, no de dominio.

## 7. Confirmación y anti-stale

La validación inicial no autoriza por sí misma la escritura.

`confirm_and_apply(...)` debe:

1. exigir una propuesta validada pendiente;
2. reconstruir `ChangeRequest` desde la propuesta almacenada y el contexto inmutable;
3. ejecutar de nuevo `validate_change(...)`;
4. solo después invocar `apply_change(...)`;
5. propagar cualquier conflicto/restricción como fallo cerrado.

## 8. Datos presentacionales

El ViewModel puede exponer únicamente datos procedentes de `ParameterDefinition`, `Configuration`, `HistoryEntry` y del contexto confiable.

No inventa nombre descriptivo, categoría, valor estándar, explicación de impacto ni etiquetas de negocio si no existen físicamente en esas fuentes.

## 9. Manejo de errores

Los códigos de `ConfigurationCenterError` se mapean a estados UI sin convertir un error en éxito.

Como mínimo:

- autorización/restricción → `FORBIDDEN`;
- conflicto de configuración → `CONFLICT`;
- errores de validación → `VALIDATION_FAILED`;
- resto → `ERROR`.

El código original permanece disponible para trazabilidad/presentación.

## 10. Tests obligatorios

- detalle vigente conserva identidad/valor/tipo/unidad;
- histórico conserva actor, motivo, empresa y valores;
- contexto incompleto se rechaza;
- actor/empresa/parámetro del contexto no pueden ser sustituidos en la propuesta;
- validación fallida no crea confirmación pendiente;
- aplicar sin confirmación pendiente falla cerrado;
- `confirm_and_apply` revalida antes de aplicar;
- autorización revocada entre validación y confirmación impide escritura;
- conflicto aparecido entre validación y confirmación impide escritura;
- aplicación satisfactoria retorna `APPLIED` y configuración real del backend;
- no existe acceso directo del controlador a repository/catalogue/authorization.

## 11. Invariantes

**CCUIS1-I01:** contexto ≠ autenticación; no se fabrica identidad.  
**CCUIS1-I02:** no se enumeran parámetros/empresas sin productor.  
**CCUIS1-I03:** toda semántica funcional se delega a `ParameterConfigurationCenter`.  
**CCUIS1-I04:** confirmación explícita + revalidación obligatoria.  
**CCUIS1-I05:** fail-closed ante autorización, conflicto o error.  
**CCUIS1-I06:** ViewModel sin inferencias de negocio.  
**CCUIS1-I07:** no direct persistence.  
**CCUIS1-I08:** no decisión de compra.

# EIOS — Configuration Center UI Slice 4 — Application Presentation Boundary Contract v0.1

**Estado:** DEPURADO — PENDIENTE DE AUDITORÍA 2  
**Fecha:** 2026-09-14  
**Baseline:** `main @ 480ff8cbe92b1604eddd4cfdcdc9da902f292b3e`  
**Dependencias cerradas:** Configuration Center UI Slices 1–3  
**Frontera existente:** `eios/frontend/application_boundary.py`

## 1. Objeto

Exponer un `ConfigurationWorkflowSnapshot` como `Mapping[str, Any]` JSON-safe para una futura capa de transporte o interfaz, sin ejecutar lógica de configuración, crear contexto autorizado, certificar procedencia ni elegir tecnología web.

Slice 4 es un **serializador/presentador tipado**. No es una frontera de autenticación, autorización, provenance ni validación de coherencia interna.

## 2. Única operación autorizada

```python
present_configuration_center_snapshot(snapshot) -> Mapping[str, Any]
```

La operación es estrictamente presentacional.

No crea ni modifica:

- `AuthorizedConfigurationUIContext`;
- `ConfigurationCenterUIController`;
- `ConfigurationCenterSelectedWorkflow`;
- parámetros;
- empresas;
- identidad/actor;
- autorización;
- configuración;
- histórico;
- estados.

## 3. Entrada y límite del type-check

La entrada debe ser una instancia de:

`ConfigurationWorkflowSnapshot`

Cualquier otro tipo debe producir `FrontendBoundaryError`.

La frontera no acepta diccionarios libres que imiten un snapshot.

**Importante:** `isinstance(snapshot, ConfigurationWorkflowSnapshot)` verifica únicamente el tipo. No demuestra que el objeto haya sido producido por `ConfigurationCenterSelectedWorkflow`, no certifica procedencia y no sustituye las garantías de Slices 1–3.

Slice 4 no revalida invariantes internos del snapshot y no intenta corregir composiciones manuales incoherentes. Proyecta literalmente los datos tipados recibidos.

## 4. Salida

La salida contiene únicamente proyección explícita de datos ya presentes en el snapshot:

```text
{
  "data_ready": bool,
  "history_stale": bool,
  "status": {
    "state": str,
    "error_code": str | None
  },
  "detail": Mapping | None,
  "history": list[Mapping] | None,
  "form": Mapping | None,
  "confirmation": Mapping | None
}
```

La frontera preserva las diferencias semánticas existentes:

- `history is None` → `history: null`;
- `history == ()` → `history: []`;
- `detail is None` → `detail: null`;
- ausencia de formulario/confirmación → `null`.

## 5. Proyección de detalle

Cuando existe detalle:

- `company_id`;
- `parameter_id`;
- `actor`;
- `value_type`;
- `unit`;
- `restricted`;
- `configuration` completa o `null`.

La `Configuration` se proyecta explícitamente, campo a campo:

- `configuration_id`;
- `parameter_id`;
- `company_id`;
- `value`;
- `value_type`;
- `unit`;
- `valid_from`;
- `valid_to`;
- `created_at`;
- `updated_at`.

No se utilizará `dataclasses.asdict()` como mecanismo de serialización JSON.

## 6. Proyección de histórico

Cada entrada conserva explícitamente:

- `configuration_id`;
- `parameter_id`;
- `company_id`;
- `previous_value`;
- `new_value`;
- `changed_by`;
- `changed_at`;
- `change_reason`.

El orden recibido se conserva.

## 7. Formulario y confirmación

### Formulario

Conserva:

- `value`;
- `valid_from`;
- `valid_to`;
- `reason`.

No normaliza texto ni valida funcionalmente.

### Confirmación

Proyecta exclusivamente:

- el detalle contenido por `ConfigurationConfirmationPanel`;
- la propuesta (`value`, `valid_from`, `valid_to`, `reason`).

Slice 4 no compara ese detalle contra el detalle principal del screen, no reconstruye coherencia de Slice 2/3, no infiere autorización adicional y no llama a `confirm()`.

## 8. Fechas y JSON safety

Todo `datetime` se serializa explícitamente mediante `.isoformat()`.

No se convierte timezone, no se redondea y no se inventa offset.

Los valores `None`, `bool`, `str`, `int`, listas y mappings resultantes deben ser serializables mediante `json.dumps(...)` estándar.

## 9. No inferencia

Slice 4 no:

- certifica procedencia del snapshot;
- revalida coherencia de Slices 1–3;
- calcula etiquetas de negocio;
- traduce estados a decisiones;
- calcula impacto;
- añade permisos;
- selecciona empresa/parámetro;
- autentica actor;
- deduce si un valor está autorizado;
- convierte `history_stale=True` en datos refrescados;
- inventa histórico;
- ejecuta backend.

## 10. Frontera arquitectónica

```text
Slice 1 — controller
      ↓
Slice 3 — selected workflow
      ↓
Slice 2 — screen/components
      ↓
Slice 4 — application presentation boundary
      ↓
future transport / UI technology (not selected here)
```

Las garantías de autoridad/coherencia pertenecen a las capas productoras. Slice 4 solo serializa la representación recibida.

Slice 4 no importa ni usa `ParameterConfigurationCenter` directamente.

## 11. Tests obligatorios

- rechaza objeto que no sea `ConfigurationWorkflowSnapshot`;
- el type-check no se presenta como prueba de procedencia;
- snapshot vacío/READY se proyecta con `None` apropiados;
- detalle/configuración se proyectan sin pérdida;
- datetimes conservan `isoformat()` exacto;
- `history=None` permanece `None`;
- histórico vacío se convierte en `[]`;
- histórico conserva orden y campos;
- formulario conserva texto exacto;
- confirmación conserva literalmente su propio detalle + propuesta;
- `history_stale` se preserva literalmente;
- estado/error se preservan literalmente;
- payload completo pasa por `json.dumps(...)`;
- no se accede a backend ni se crean contextos.

## 12. Invariantes

**CCUIS4-I01:** presentación/serialización solamente.  
**CCUIS4-I02:** input tipado, pero tipo ≠ procedencia.  
**CCUIS4-I03:** `None` ≠ vacío.  
**CCUIS4-I04:** orden histórico preservado.  
**CCUIS4-I05:** datetimes solo `isoformat`, sin transformación temporal.  
**CCUIS4-I06:** estado/error/frescura se preservan literalmente.  
**CCUIS4-I07:** confirmación visual ≠ autorización.  
**CCUIS4-I08:** no backend directo ni revalidación de dominio.  
**CCUIS4-I09:** no tecnología web elegida.  
**CCUIS4-I10:** no decisión de compra.

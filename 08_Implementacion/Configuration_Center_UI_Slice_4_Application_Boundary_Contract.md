# EIOS — Configuration Center UI Slice 4 — Application Presentation Boundary Contract v0.1

**Estado:** DISEÑO  
**Fecha:** 2026-09-14  
**Baseline:** `main @ 480ff8cbe92b1604eddd4cfdcdc9da902f292b3e`  
**Dependencias cerradas:** Configuration Center UI Slices 1–3  
**Frontera existente:** `eios/frontend/application_boundary.py`

## 1. Objeto

Exponer un `ConfigurationWorkflowSnapshot` ya construido como `Mapping[str, Any]` JSON-safe para una futura capa de transporte o interfaz, sin ejecutar lógica de configuración, crear contexto autorizado ni elegir tecnología web.

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

## 3. Entrada

La entrada debe ser una instancia real de:

`ConfigurationWorkflowSnapshot`

Cualquier otro tipo debe producir `FrontendBoundaryError`.

La frontera no acepta diccionarios libres que imiten un snapshot.

## 4. Salida

La salida contiene únicamente proyección de datos ya presentes en el snapshot:

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

La `Configuration` se proyecta sin renombrar semántica:

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

## 6. Proyección de histórico

Cada entrada conserva exactamente:

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

- el mismo detalle contenido por `ConfigurationConfirmationPanel`;
- la propuesta (`value`, `valid_from`, `valid_to`, `reason`).

No infiere autorización adicional ni llama a `confirm()`.

## 8. Fechas y JSON safety

Todo `datetime` se serializa mediante `.isoformat()`.

No se convierte timezone, no se redondea y no se inventa offset.

Los valores `None`, `bool`, `str`, `int`, listas y mappings resultantes deben ser serializables por JSON estándar.

## 9. No inferencia

Slice 4 no:

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

Slice 4 no importa ni usa `ParameterConfigurationCenter` directamente.

## 11. Tests obligatorios

- rechaza objeto que no sea `ConfigurationWorkflowSnapshot`;
- snapshot vacío/READY se proyecta con `None` apropiados;
- detalle/configuración se proyectan sin pérdida;
- datetimes conservan `isoformat()` exacto;
- `history=None` permanece `None`;
- histórico vacío se convierte en `[]`;
- histórico conserva orden y campos;
- formulario conserva texto exacto;
- confirmación conserva detalle + propuesta;
- `history_stale` se preserva literalmente;
- estado/error se preservan literalmente;
- payload completo puede pasar por `json.dumps(...)`;
- no se accede a backend ni se crean contextos.

## 12. Invariantes

**CCUIS4-I01:** presentación solamente.  
**CCUIS4-I02:** input tipado real; no snapshot libre falsificable.  
**CCUIS4-I03:** `None` ≠ vacío.  
**CCUIS4-I04:** orden histórico preservado.  
**CCUIS4-I05:** datetimes solo `isoformat`, sin transformación temporal.  
**CCUIS4-I06:** estado/error/frescura se preservan literalmente.  
**CCUIS4-I07:** confirmación visual ≠ autorización.  
**CCUIS4-I08:** no backend directo.  
**CCUIS4-I09:** no tecnología web elegida.  
**CCUIS4-I10:** no decisión de compra.

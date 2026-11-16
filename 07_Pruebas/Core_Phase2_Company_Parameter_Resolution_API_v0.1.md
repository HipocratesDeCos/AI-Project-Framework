# EIOS — FASE 2.3 · API CANÓNICA DE CONSULTA DE PARÁMETROS POR EMPRESA

**Fecha:** 2026-11-16  
**Rama:** `phase2/core-company-parameter-resolution-api-20261116`  
**Base:** PR #582 → PR #581 → cierre fase 1 en `main @ 2c2807c`  
**Alcance:** lectura/resolución de configuraciones y vinculación documental por empresa, sin autoridad de cálculo autónoma ni cambios de persistencia.

## 1. Diseño y reutilización

Se reutilizan obligatoriamente:
- `eios.parameters.center.ParameterConfigurationCenter` para `get_parameter()` y `get_configuration_at(company_id, parameter_id, effective_at)`;
- `eios.parameters.resolution.resolve_configuration_for_context` y `ResolvedConfiguration` para vigencia y vinculación con `DecisionContext.parameters_version`;
- `eios.core.models.Evidence` y `eios.core.validation.validate_evidence` para distinguir evidencia demostrada de lagunas;
- los productores de reglas ya cerrados, que continúan siendo **los únicos responsables de su propia evaluación y de revalidar** configuraciones y evidencias.

La nueva API `eios.parameters.read_company_parameters_for_context(...)` no crea un segundo centro, ni inventa valores, ni ejecuta reglas. Utiliza la infraestructura de consulta sin escribir en la base.

### Entrada

`center`, `company_id`, `expected_company_id`, `DecisionContext`, `effective_at` con zona horaria, `parameter_ids: tuple[str, ...]` y `evidence_by_parameter: Mapping[str, Evidence]`.

**`expected_company_id` debe provenir del contexto confiable del adaptador**, no del propio formulario; compararlo no constituye autenticación independiente. La API rechaza identidad de empresa distinta **antes de consultar al repositorio**.

### Salida

`CompanyParameterLookup` es un informe inmutable con:
- identidad de empresa, decisión, escenario, `data_snapshot_id`, `parameters_version` y fecha;
- `ParameterLookupEntry` por parámetro, con estado `DOCUMENTARY_CHECK_PASSED`, `CONFIGURATION_ABSENT`, `EVIDENCE_MISSING` o `EVIDENCE_INVALID`;
- `resolution: ResolvedConfiguration` y `evidence: Evidence` **solo si su vinculación documental pasa las verificaciones**. La ausencia o invalidez no expone un valor como listo;
- `complete_documentary_coverage` solamente cuando todos los parámetros solicitados tienen evidencia documental concordante;
- `decision_authority=False`, `operational_path=FORBIDDEN`, `version_attestation=CALLER_CONTEXT_ONLY`, `origin_attestation=NOT_EXTERNALLY_AUTHENTICATED`.

**Precisión:** «DOCUMENTARY_CHECK_PASSED» significa listo para **ser revalidado por su propio consumidor**, no que el valor sea una política autorizada por una autoridad externa.

## 2. Seguridad de identidad, temporalidad y evidencia

El servicio rechaza:
- empresa esperada distinta, identidades vacías, IDs duplicados y selecciones incompletas;
- fechas sin zona horaria y configuraciones que no estén vigentes;
- registros de empresa/parámetro distintos de los solicitados, `configuration_id` incoherentes o reutilizados entre códigos distintos;
- metadatos de unidad y tipo contradictorios con definiciones **cuando las definiciones los especifican**, y valores que no superen el validador explícito del catálogo;
- evidencias adicionales no solicitadas o `evidence_id` reutilizado por parámetros diferentes;
- evidencias de otro corte, tipo distinto, sin demostración o sin coincidencia exacta con la configuración seleccionada.

Se define un **formato de referencia local**, mediante `configuration_evidence_source_ref`:
`company_parameter:{sha256(JSON_array(company_id, parameter_id, configuration_id))}`.

Se utiliza una matriz JSON canónica de tres campos antes de la huella, de modo que dos combinaciones distintas no se confundan aunque sus identificadores contengan separadores como dos puntos. La referencia vincula la evidencia suministrada al ámbito empresarial y al código de parámetro, incluso si dos empresas utilizan el mismo identificador numérico de configuración. Complementa `demonstration_ref=ResolvedConfiguration.configuration_ref`, cuyo formato heredado **no incorpora la empresa**.

**Advertencia de confianza:** un atacante capaz de crear objetos `Evidence` puede producir esa cadena correctamente. La API no firma, autentica ni demuestra la procedencia del documento. El adaptador debe conservar su verificación independiente de fuentes y permisos.

Las entradas `DecisionContext` y `Evidence` se copian al inicio de la consulta para impedir que una modificación posterior del llamante cambie la versión o la vinculación durante la lectura.

## 3. La versión no se autentica por repetir su identificador

`Configuration` del centro contiene identificador, empresa, valor y vigencia, **pero no almacena** `parameters_version` como una propiedad de su histórico de configuración. `resolve_configuration_for_context` adjunta la versión suministrada por `DecisionContext`.

Por tanto el resultado conserva literalmente:
- `parameters_version`: identidad de ejecución declarada;
- `version_attestation=CALLER_CONTEXT_ONLY`.

**No debe presentarse esa versión como certificada** hasta que un productor de instantáneas autorizado y verificable vincule la selección completa al `parameters_version` del contexto. Ese vínculo se mantendrá como pendiente de fase 2, sin cambiar contratos C0 cerrados ni inventar una segunda historia de versiones.

## 4. Prueba de separación real entre empresas

`tests/test_company_parameter_resolution_api.py` configura dos empresas sintéticas con el mismo escenario y dos valores válidos de `P-PAG-004`:
- Empresa A: `Sí` → `resolve_payment_term_control` devuelve `ENABLED`.
- Empresa B: `No` → `resolve_payment_term_control` devuelve `DISABLED`.

El control corresponde al **productor existente** de PAG, no a una decisión comercial emitida por la API.

También se ensayan dos configuraciones de empresas distintas con el mismo ID numérico; la referencia documental de una empresa no vale para la otra. La ausencia de evidencia o configuración no crea valores por defecto. Se prueba la coherencia temporal, metadatos, versiones, identidades, selección múltiple, duplicados, cambios del contexto durante lectura y aislamiento de copia de evidencias.

## 5. Limitaciones y continuidad

- El catálogo y sus validadores siguen siendo fuentes explícitas. La nueva API no determina por sí misma qué configuración está autorizada para cada usuario.
- La procedencia de fuente y el vínculo histórico entre `parameters_version` y configuraciones reales **aún no están atestados por el centro**.
- No se ha conectado esta consulta con la pantalla de compras/ventas ni con un ERP; es una API reutilizable para futuros adaptadores.
- No se ha declarado operacional ninguna compra ni venta; el acceso a datos reales sigue sujeto a admisión externa.
- No altera PRICE, FIN, STK, MGE, PAG, QTG, las fórmulas ni las pruebas históricas.

**Criterios de cierre F2.3:** ejecución satisfactoria de CI completa y SQL Server, ausencia de regresiones, revisión de diff y PR en borrador apilada sobre #582. La fase 2 completa continúa abierta para atestar la versión canónica y conectar los adaptadores cuando exista una procedencia fiable.

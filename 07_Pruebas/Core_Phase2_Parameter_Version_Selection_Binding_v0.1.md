# EIOS — FASE 2.4 · VINCULACIÓN DE LA VERSIÓN A LA SELECCIÓN COMPLETA DE PARÁMETROS

**Fecha:** 2026-11-16  
**Base de revisión:** PR #583 ← #582 ← #581. Rama independiente, sin modificar `main`.  
**Clase de contrato:** frontera de comparación documental de selección, sin nueva autoridad de versionado ni efectos operacionales.

## 1. Hallazgo de origen

El contrato de `Decision Versioning` (`05_Motor/Decision_Versioning.md`) **conserva referencias** a `Parameters_Version`: no crea una nueva autoridad de parámetros, no sustituye al propietario del catálogo, ni garantiza por sí solo recuperar un artefacto histórico que ya no existe.

El `ParameterConfigurationCenter` existente permite consultas por `company_id`, `parameter_id` y `effective_at`, pero `Configuration` **no contiene `parameters_version`** ni una instantánea transaccional de *toda* la política. `resolve_configuration_for_context` anota la versión que trae `DecisionContext`; no comprueba que esa versión esté vinculada a los valores seleccionados.

Por tanto, la API F2.3 distingue correctamente `version_attestation=CALLER_CONTEXT_ONLY`. La misma empresa podría presentar, sin comprobación adicional, valores cambiados bajo la misma versión textual.

## 2. Solución acotada, sin segundo sistema de versiones

Se añade `eios/parameters/version_binding.py`, sobre las **mismas** clases `DecisionContext`, `ParameterConfigurationCenter`, `ResolvedConfiguration`, `CompanyParameterLookup` y `Evidence`:

- `ParameterVersionSource` (Protocol de solo lectura): puerto para recuperar desde la **autoridad de versionado ya correspondiente al integrador** un `ParameterVersionManifest` por empresa, versión existente y fecha.
- `ParameterVersionManifest`: contiene empresa, **la misma** `parameters_version` de C0, instante, conjunto exhaustivo de IDs de parámetro para esa versión, huella de contenido y `source_ref` del manifiesto.
- `fingerprint_parameter_selection(lookup)`: huella de **comparación** sobre empresa, versión, instante, IDs ordenados y contenido exacto de cada `Configuration` (valor, tipo, unidad, ID, vigencia y metadatos de registro).
- `read_version_bound_parameter_selection`: compara selección de F2.3, evidencia documental y huella con el manifiesto del puerto; reconsulta la referencia al terminar para detectar cambios evidentes de la fuente mientras se lee.
- `VersionBoundParameterSelection`: conserva lookup y manifiesto congruentes, con estado `SOURCE_MANIFEST_MATCHED`, `version_attestation=MATCHED_SUPPLIED_VERSION_SOURCE`, `source_authentication=ADAPTER_RESPONSIBILITY`, `atomicity=MANIFEST_CONSISTENCY_NOT_DB_TRANSACTION`, `decision_authority=False` y `operational_path=FORBIDDEN`.

**La huella NO es una segunda `Parameters_Version`, ni sustituye al fingerprint del DIP o C0.** Únicamente comprueba correspondencia de valores y metadatos con el contenido que una fuente ha declarado como perteneciente a la versión histórica.

## 3. Requisitos de integridad y rechazo

Se rechaza sin fallback:
1. Falta del puerto de versión, del manifiesto o de su `source_ref`.
2. Empresa, versión o fecha de referencia diferentes de la ejecución consultada.
3. Duplicidad o diferencia en el **conjunto completo** de parámetros del manifiesto frente a la selección solicitada; no puede usarse un subconjunto para aparentar completitud.
4. Ausencia de configuración o evidencia, o inconsistencia de una prueba F2.3; no se obtiene huella de una selección incompleta.
5. Contenido cambiado respecto al manifiesto (valor, ID de configuración, unidad, vigencia, sello temporal de actualización, etc.).
6. Manifiesto modificado durante la consulta del Centre (relectura de la referencia).

Se congela `DecisionContext` y el conjunto de evidencias **antes** de llamar al puerto de versiones, para impedir que una mutación del llamante o del puerto reetiquete los resultados.

La huella JSON se calcula con IDs ordenados y fechas normalizadas a UTC: el orden del formulario no altera la identidad. La secuencia compuesta de valores se evalúa con `sha256` para comparación, no como firma.

## 4. Límites explícitos de confianza

**No existe actualmente en la rama de F2.3 una fuente operacional del versionado de la selección completa.** Se añade un puerto, **no** se inventa una base de datos nueva, un registro paralelo de versiones o un origen ficticio.

Si un adaptador suministra un `ParameterVersionSource` falsificado con manifiesto y hash recalculados, la API puede concluir `SOURCE_MANIFEST_MATCHED` aunque la procedencia no sea auténtica. Por eso:
- el estado indica **coincidencia con la fuente suministrada**, no «firma verificada»;
- solo se admitirá como confianza empresarial cuando exista un adaptador autenticado que seleccione la autoridad correcta, con permisos y material inmutable;
- una lectura del centro por varios parámetros no es una transacción atómica de BD; la relectura del manifiesto detecta divergencias evidentes, no toda posible condición de carrera;
- una `Evidence` DEMONSTRATED correctamente formada tampoco verifica por sí misma el documento de origen;
- los consumidores especializados conservan íntegra su autoridad, revalidan resoluciones y evidencias y pueden responder `NOT_EVALUABLE`.

**Por tanto, la F2.4 cierra un contrato de comparación verificable mediante fuente autorizada, no un despliegue multiempresa real de la fuente.**

## 5. Pruebas y compatibilidad

`tests/test_parameter_version_selection_binding.py` cubre:
- dos empresas sintéticas con el mismo escenario, misma versión textual, políticas `P-PAG-004` distintas y resultados `ENABLED` / `DISABLED` del productor existente;
- selección de dos parámetros independientemente del orden, y rechazo de manifiesto parcial o duplicado;
- cambios posteriores de valor, configuración, fecha de vigencia o versión;
- empresa, fecha, versión y material de otro contexto;
- ausencia de manifiesto, fuente mal tipada o evidencia insuficiente;
- alteraciones del origen entre lecturas; mutaciones del contexto/evidencias durante la consulta;
- salida sin autoridad comercial ni firma/atestado criptográfico externo.

No se modifica código de PRICE, FIN, STOCK, MGE, PAG, QTG, ni `company_app.py`, tablas SQL, DIP, reglas ni decisiones.

## 6. Próximo requisito para cierre empresarial

Para conectar este contrato a una empresa real falta **identificar e implementar el adaptador confiable** para la fuente de versiones existente, con persistencia inmutable y lectura consistente. No se autoriza un atajo que genere el manifiesto a partir de los valores recién leídos y lo trate como certificado empresarial: eso sería una prueba circular.

**Criterio de cierre de la unidad:** CI completa Python + SQL verde en HEAD, revisión de compatibilidad y PR borrador apilada sobre #583. El cierre de Fase 2 completa requiere integración de la cadena y evidencia de un adaptador confiable antes de afirmar reutilización empresarial operacional.

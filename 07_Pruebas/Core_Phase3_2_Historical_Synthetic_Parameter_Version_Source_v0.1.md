# EIOS — FASE 3.2 · HISTÓRICO SINTÉTICO DE VERSIONES DE PARÁMETROS

**Fecha:** 16/11/2026  
**Base:** `main @ 49e24e9e8d9b9f93eeee19a730e1112c42a9b3d7`  
**Estado inicial:** unidad de implementación aislada, sin autoridad operacional.

## 1. Auditoría de orígenes (DISEÑAR → AUDITAR)

**No existe en el repositorio una fuente empresarial autenticada de versiones de parámetros.**

- `06_SQL/002_Decision_Versioning_Schema.sql` guarda `parameters_version` como referencia del estado decisional; **no** guarda la selección íntegra ni certifica su origen.
- `06_SQL/003_Centro_Parametrizacion_Schema.sql` guarda configuraciones vigentes e historial de cambios; **no** existe un manifiesto histórico firmado que enlace selección multi-parámetro y versión.
- `eios/company_finance_parameters.py` guarda desde antes de F3.2 una activación **sintética y local**, con empresa, dataset, fecha, revisión, valores, ambas `Configuration` canónicas y una huella local. Este es un histórico físicamente existente y separado de las lecturas actuales del Centro.
- F3.1 ya compara la activación con lo que el consumidor financiero utiliza, pero no implementaba el puerto `ParameterVersionSource` de F2.4.
- F2.4 exige evidencias documentales, rechaza versión sin manifiesto y compara la selección completa, pero la fuente hasta ahora solo existía en fixtures en memoria.

**Conclusión:** el único adaptador materializable hoy sin inventar otra autoridad es el de **histórico financiero sintético local**. No debe confundirse con una fuente empresarial real. Está prohibido generar el manifiesto desde los valores vivos del Centro o asignar confianza externa al hash.

## 2. Implementación

### Lectura del histórico existente

`eios/parameters/local_finance_version_source.py` incorpora `LocalSyntheticFinanceVersionSource`, una implementación de solo lectura de `ParameterVersionSource`.

- Requiere `sqlite3.Connection` ya transaccionada, `dataset_id` y `expected_company_id` proporcionados por el llamante. No autentica quién es el llamante.
- Rechaza fuentes no sintéticas, empresa ajena, fecha distinta o instante que no sea inicio del corte UTC.
- Lee la fila `company_finance_parameter_activation` ya creada por la activación del usuario; valida la huella y alcance mediante `describe_company_parameter_bindings` de F2.1.
- Utiliza como `parameters_version` **la huella ya registrada en esa activación**, no inventa un ID ni sobreescribe el `DecisionContext`.
- Decodifica exactamente los campos canónicos de las dos `Configuration` guardadas históricamente, sin leer las configuraciones actuales para fabricar el manifiesto.
- Calcula la huella de selección esperada desde ese histórico y devuelve el `ParameterVersionManifest` tipado de F2.4, con `source_ref=local_synthetic_finance_activation:<huella>`.
- No crea ni actualiza tablas, versiones, políticas, evidencias o datos de empresa.

### Una única huella de comparación

`eios/parameters/version_binding.py` extrae el serializador de selección ya existente a una función interna compartida. La nueva función pública `fingerprint_historical_parameter_configurations` aplica **la misma** serialización canónica a las configuraciones históricas. Conserva la semántica de `fingerprint_parameter_selection`; no reemplaza C0 `input_fingerprint`, `finance_package_fingerprint` ni `DecisionContext.parameters_version`.

### Interacción con F2.4

`read_version_bound_parameter_selection` recibe el adaptador histórico y el Centro, lee el manifiesto **antes y después** de la consulta actual, exige evidencias de cada parámetro y rechaza discrepancias de contenido, empresa, vigencia o selección. Las evidencias del test son fixtures **sintéticos**, no documentos certificados.

**No se modifica `execute_documentary_finance`**: la aplicación todavía no dispone de la evidencia C0 documental acreditada que F2.4 requiere para cada parámetro. Conectar automáticamente F2.4 a esa ejecución supondría fabricar evidencias o debilitar el contrato. El guardia F3.1 sigue activo y protege el cálculo local.

## 3. Límites de confianza

- `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`: la activación y su huella proceden de SQLite modificable. Si un actor altera coherentemente tanto historial como configuración viva, la comparación local no descubre esa falsificación.
- El manifiesto **no** firma ni autentica empresas, responsables, documentos o permisos de activación.
- La transacción SQLite solo proporciona lectura coherente; no equivale a una operación atómica empresarial multi-sistema.
- El recibo F2.4 mantiene `decision_authority=False` y `operational_path=FORBIDDEN`. `MATCHED_SUPPLIED_VERSION_SOURCE` solo significa coincidencia con la fuente local declarada.
- El flujo de Finanzas sigue utilizando su `parameters_version` histórico de hash local; **no** se renombra, reescribe ni publica como versión empresarial autenticada en esta unidad.
- Los datos reales, el acceso operacional y la integración de parámetros a otros dominios siguen **bloqueados**.

## 4. Pruebas negativas y de regresión

`tests/test_local_synthetic_finance_version_source.py` usa la persistencia real de activación sintética que ya prueban los tests de la app:

- cotejo integral del manifiesto con la selección consultada a través del Centro y F2.4;
- dos empresas y sus versiones distintas; intento de replay entre empresa/dataset;
- activación ausente, versión inexistente, material no sintético y transacción ausente;
- modificación de valor o metadatos de configuración viva;
- activación histórica corrupta o rehasheada sin concordancia con el Centro;
- selección parcial, ausencia de evidencia y evidencia incorrecta;
- solicitud guardada posterior que no reemplaza el historial activo;
- comprobación de que la huella histórica y la huella viva comparten contrato;
- preservación de `FORBIDDEN`, sin autoridad de decisiones.

## 5. Cierre y continuidad

**Cierre de F3.2 limitado:** fuente sintética histórica real conectada al puerto de versión de F2.4, con CI Python+SQL y reconciliación `main`.

**Pendiente para admitir empresas reales:** productor de manifestación histórica completa y **autenticada externamente**, integridad/auditoría de cambios, procedencia documental de evidencias y políticas de confianza/autorización de la empresa. El DDL de Decision Versioning no sustituye estas capacidades. Esta limitación debe informarse sin atribuir verificación empresarial donde solo existe consistencia local.

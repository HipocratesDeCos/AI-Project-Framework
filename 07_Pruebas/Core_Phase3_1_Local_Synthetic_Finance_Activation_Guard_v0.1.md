# EIOS — FASE 3.1 · FRONTERA DE FIABILIDAD DEL ORIGEN FINANCIERO LOCAL

**Fecha:** 2026-11-16  
**Base validada:** `main @ b665535a51abccbb2685c3fe013441db3b117957` (fase 2 integrada y CI satisfactoria).  
**Unidad:** comprobación obligatoria de la activación histórica de parámetros financieros sintéticos antes de utilizarlos en la aplicación empresarial.

## 1. Hallazgo reproducible

`execute_documentary_finance` consultaba directamente los `Configuration` vigentes de `ParameterConfigurationCenter` en SQLite y, si encontraba los dos parámetros, podía ejecutar el cálculo aunque el registro `company_finance_parameter_activation` hubiera sido borrado o dejado de concordar con los valores actuales.

Además construía `DecisionContext.parameters_version` a partir del hash de las configuraciones presentes en el momento de consulta. **Ese hash es identidad de contenido, no prueba de versión histórica autorizada**. La aplicación conserva un registro previo de activación sintética, pero antes de esta unidad la ejecución no cotejaba ambas fuentes.

La fase 3.1 soluciona la correspondencia **sin** atribuir autenticidad externa a una base de datos SQLite modificable.

## 2. Implementación

Módulo `eios/company_finance_activation_guard.py`:

`verify_local_finance_activation(connection, company_id, dataset_id, as_of_date, effective_at, configurations)`

- Reutiliza el inventario/verificador de activación empresarial de F2.1 mediante `describe_company_parameter_bindings`; no replica el catálogo ni autoriza nuevas políticas.
- Opera dentro de la **misma transacción SQLite de lectura** abierta por el consumidor. No crea tablas, no escribe registros ni toma valores por defecto.
- Verifica identidad de dataset, empresa, fecha y `material_nature=SYNTHETIC`.
- Exige activación ya registrada, revisión válida y huella local consistente; rechaza JSON malformado o con claves duplicadas.
- Contrasta **todo** el registro de cada una de las configuraciones canónicas `P-FIN-001` / `P-FIN-002` con la copia histórica guardada: `configuration_id`, valor, unidad, tipo, empresa, vigencia, creación y actualización.
- Rechaza ausencia, duplicidad, replay entre empresas o discrepancias entre activación y la selección que consumiría el Motor.
- El consumidor `execute_documentary_finance` bloquea la ejecución cuando el control falla, no publica un resultado parcial y declara un código estable `parameter_source_issue`.
- El recibo `LocalFinanceActivationReceipt` es inmutable, contiene huella de la activación e identifica `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`, `version_attestation=NOT_ATTESTED`, `decision_authority=False` y `operational_path=FORBIDDEN`.

## 3. Qué se demuestra y qué NO

**Sí se demuestra:** en la aplicación local sintética, la misma empresa, el mismo dataset y fecha, el registro de activación y el contenido financiero consumido coinciden dentro de una transacción de lectura.

**No se demuestra:** autenticación del responsable que creó la base; que una empresa real haya autorizado el registro; que una huella SHA-256 sea firma; ni que la historia SQL local sea inmutable o a prueba de un actor que pueda editar simultáneamente la activación y las configuraciones.

El hash de `parameters_version` emitido por el flujo financiero **todavía no está conectado al puerto `ParameterVersionSource` de F2.4**; esa integración requiere elegir/atestiguar una fuente canónica. No se cambia su semántica aquí.

## 4. Regresiones y auditoría

`tests/test_company_finance_activation_source_guard.py` comprueba:

- activación sintética válida y consumo sin autoridad;
- activación pendiente o borrada con configuración aún presente;
- modificación de valor o metadatos de la configuración;
- manipulación de huella, incluso si el atacante recompone la huella local sin actualizar configuración vigente;
- registro procedente de otra empresa y JSON con claves duplicadas;
- nueva solicitud guardada que no sustituye activación anterior;
- rechazo de datos no sintéticos y de cruces de dataset;
- exigencia de transacción compartida, recibo inmutable y no certificación externa.

No se alteran algoritmos FIN/PRICE/STK/MGE/PAG/QTG, contratos C0 ni esquema SQL. El flujo financiero conserva `operational_path=FORBIDDEN` y `decision_authority=False`.

## 5. Condiciones de cierre

`DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI`.

La unidad se entrega en una PR independiente en **borrador** hasta:
1. CI integral Python y SQL en verde en el HEAD exacto;
2. revisión de diff y ausencia de degradación de cálculos existentes;
3. aceptación posterior de integración, sin atribuir a esta unidad el cierre de toda la fase 3.

**Continuidad F3.2:** admitir un productor real de `ParameterVersionSource` con procedencia comprobable y no circular; antes de que exista, la vía empresarial operacional seguirá bloqueada.

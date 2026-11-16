# EIOS — F4.2.2 · DESACOPLAMIENTO DEL ADAPTADOR HISTÓRICO DE PARÁMETROS

**Fecha:** 2026-11-16  
**Base:** `main @ f88b484ca88bc27a5be08c380fbb54fbf3e6ad7e` (F4.2.1 integrada y CI postmerge satisfactoria).  
**Alcance:** trasladar el proveedor de versiones financieras sintéticas a la **aplicación** y conservar compatibilidad de importación sin crear nuevas reglas o fuentes.

## 1. DISEÑAR — HALLAZGO F4.1

`eios/parameters/local_finance_version_source.py` implementaba `LocalSyntheticFinanceVersionSource` y dependía directamente de:

- `eios.company_finance_activation_guard._read_json`: lector JSON del sistema documental de la aplicación.
- `eios.company_finance_parameters.IDS`: catálogo local `P-FIN-001` / `P-FIN-002`.
- `eios.company_parameter_bindings.describe_company_parameter_bindings`: revisión de la activación **local sintética** y sus consumidores.

Este adaptador no era una propiedad universal del Centro de Parámetros. Gestiona un almacenamiento SQLite y una activación de Finanzas de la aplicación local. **No debe formar parte del futuro runtime/paquete compartido** por el mero hecho de estar situado en `eios/parameters`.

Ya existe el contrato abstracto `ParameterVersionSource` en `eios/parameters/version_binding.py`, que puede recibir implementaciones de otros proyectos sin importar las tablas de Compras.

## 2. AUDITAR — CAMBIO LIMITADO, SIN DUPLICAR LÓGICA

1. La implementación canónica completa pasa a `eios/company_local_finance_version_source.py`. Se conservan contrato de clase, constructor, códigos de error, lectura histórica, transacción SQLite, alcance de empresa, validación de activación, huellas y salida `ParameterVersionManifest`. Las importaciones relativas del centro se hacen absolutas hacia `eios.parameters.center` y `eios.parameters.version_binding`.
2. `eios/parameters/local_finance_version_source.py` pasa a ser exclusivamente un **puente explícito y obsoleto de compatibilidad**, con una importación que reexporta la **misma clase**, no una segunda implementación. Se mantiene temporalmente para no romper scripts que utilicen la ruta pública de F3.2.
3. `tests/test_local_synthetic_finance_version_source.py` pasa a invocar la ruta canónica en aplicación y ejecuta sus pruebas históricas de adversarios.
4. `tests/test_f4_2_parameter_app_adapter_extraction.py` comprueba identidad de clase entre ruta nueva y antigua, los estados `FORBIDDEN`/sin autoridad, ausencia de dependencias directas a `company_*` en los otros módulos del Centro, importación estándar del paquete de parámetros sin carga del adaptador ni de la aplicación, y la inexistencia de dos implementaciones.

**La inversión de propiedad es real**: el código de negocio vive ahora en la aplicación y depende de los contratos de parámetros, nunca a la inversa para el uso normal del paquete. **Limitación transitoria explícita:** el módulo heredado `eios.parameters.local_finance_version_source` **todavía importa** la clase desde `eios.company_local_finance_version_source`. El analizador estático F4.1 debe seguir mostrándolo. No se oculta esa deuda con imports dinámicos. La distribución independiente F4.3 **no debe empaquetar ese puente**, ni la implementación de la aplicación.

## 3. DEPURAR — CONTRATOS QUE NO CAMBIAN

- Sin modificación de `ParameterVersionSource`, `ParameterVersionManifest`, `Configuration`, `read_version_bound_parameter_selection`, F2.4, QTG, reglas o funciones financieras.
- Sin nueva tabla, hash, timestamp, fabricante de manifest, credencial o autoridad de empresa.
- La fuente sigue limitada a `material_nature=SYNTHETIC`, a la transacción local y a la empresa/corte indicados.
- Los errores como `NON_SYNTHETIC_SOURCE`, `INVALID_ACTIVATION`, `COMPANY_SCOPE_MISMATCH`, `READ_TRANSACTION_REQUIRED`, `VERSION_CONTENT_MISMATCH` siguen cubiertos por el test histórico.
- `source_authentication=NOT_EXTERNALLY_AUTHENTICATED`, `decision_authority=False`, `operational_path=FORBIDDEN`.

## 4. AUDITAR 2 — NO DECLARAR LISTA LA DISTRIBUCIÓN

Aunque la ruta canónica ya está en aplicación, el árbol `eios-mvp` todavía incluye **todos** los módulos `eios.*` y por tanto también incluye el puente heredado y las dependencias específicas.

**Estado después de F4.2.2:** `application_adapter_ownership=CORRECTED`, `normal_parameter_package_import=APP_INDEPENDENT`, `legacy_compatibility_bridge=PRESENT`, `standalone_kernel_distribution=NOT_BUILT`, `cross_project_portability=NOT_PROVEN`.

La retirada física del puente de la distribución aislada y el diseño de dependencias mínimas corresponden a **F4.3**. No romper el API heredado en este paso; no confundir traslado de código con prueba de instalación aislada.

## 5. CERRAR → MATERIALIZAR → CI

La unidad solo se cierra con la suite Python completa y los tres controles SQL SUCCESS en el HEAD exacto de la PR; el diff debe limitarse a traslado, puente, tests y este documento. Después, merge controlado y nueva CI postintegración sobre el SHA exacto de `main`.

No se habilita ningún canal operacional. **F4.2 finaliza como separación de contratos e identificación de los acoplamientos restantes; la meta de Motor reutilizable aún requiere F4.3 y F4.4.**

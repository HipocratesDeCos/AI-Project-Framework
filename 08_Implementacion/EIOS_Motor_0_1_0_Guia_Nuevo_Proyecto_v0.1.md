# EIOS — GUÍA DE REUTILIZACIÓN DEL MOTOR NEUTRAL 0.1.0

**Destinatarios:** responsables de nuevos proyectos consumidores y mantenimiento técnico.  
**Estado:** guía de la RC técnica 0.1.0, sin autoridad operativa.

## 1. Qué reutilizar y qué no copiar

Reutilizar **solo las cuatro distribuciones neutrales** en versiones exactas `0.1.0`. No copiar el repositorio EIOS al proyecto nuevo, no usar imports privados (por ejemplo, `eios.core`, `eios.pricing`, `eios.tco`, `eios.company_app`) ni modificar `eios/`.

Los ejemplos independientes de mantenimiento y gestión energética ilustran un patrón, **no reglas válidas para otra empresa**.

## 2. Procedimiento para un nuevo consumidor

1. **Crear un paquete Python independiente**, con su `pyproject.toml`, modelo Pydantic propio, tests y directorio separado del Motor.
2. **Fijar la identidad**: `project_id`, `decision_id`, `scenario_id`, `rules_version`, `parameters_version` y `data_snapshot_id` en `KernelContext`.
3. **Declarar contrato tipado**, identificador y versión de esquema; construir `CapabilityInputSpec`, `CapabilityInputEnvelope` y `CapabilityInputBinding` sin saltarse comprobaciones.
4. **Definir capacidades externas** que devuelvan únicamente `KernelCapabilityResult` y no ejecuten decisiones reales. Registrar versiones y esquemas aceptados en `CapabilityCatalog`.
5. **Gobernar las selecciones** con `CatalogChange`, `AuthorizationGrant` y `commit_catalog_change`; la autorización sintética de las fixtures es exclusivamente un doble de prueba. Para producción, diseñar autenticación real fuera del Motor.
6. **Vincular y ejecutar** con `bind_governed_plan` y `execute_kernel`. Inspeccionar estados, no convertir `COMPLETED` en aprobación empresarial.
7. **Empaquetar y verificar** fuera del checkout: wheel independiente, dependencias exactas, hashes, instalación offline en entorno virtual limpio, `pip check`, ejecución repetida, evidencias negativas y compatibilidad de plataforma. El kit F5.10 se instala sin red solo en la plataforma, arquitectura y Python minor para los que fue construido.
8. **Conservar los bloqueos**: `production_authorized=false`, `decision_authority=false`, `real_pilot_admitted=false`, `operational_path=FORBIDDEN` hasta disponer de otra admisión válida y explícita.

## 3. Ejemplo realmente comprobado

La PR [#629](https://github.com/HipocratesDeCos/AI-Project-Framework/pull/629) añade una fixture `eios-energy-example` y el verificador `tools/verify_f8_1_fourth_domain.py`. La CI premerge `#44273502407` ejecutó pruebas positivas y negativas en Linux y Windows con éxito.

El harness F8.1 **no es un certificador universal**: utiliza un conjunto de reglas esperado para el propio experimento, un nuevo lock externo para el wheel energético y no modifica el ZIP de F5.10. Para otro negocio, escribir pruebas específicas de sus contratos y fuentes.

## 4. Qué queda fuera de EIOS neutral

La interfaz de usuario, importación de Excel, informes, modelos de Compra/Venta/Tesorería, planificación de caja, la autenticación de personas, el origen y verificación de documentos empresariales, el despliegue servidor y la aprobación de acciones se implementan en consumidores externos.

**Criterio de éxito para el siguiente proyecto:** una operación con sus datos y procedencia identificados se transforma en un análisis verificable y entendible para la persona usuaria, manteniendo la decisión en manos del responsable.

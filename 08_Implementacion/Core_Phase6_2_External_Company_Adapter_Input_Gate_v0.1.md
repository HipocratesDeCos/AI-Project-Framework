# EIOS — F6.2 · INCORPORACIÓN CONTROLADA DE ADAPTADORES EMPRESARIALES EXTERNOS

**Fecha:** 17/11/2026. **Baseline:** `main @ 6d5e1b2ef22d0781a2f01fda8d11fe648e998116` (F6.1: Linux y Windows 3.12; CI postmerge #44059065783 SUCCESS).
**Estado de esta unidad:** CANDIDATA, hasta comprobar CI PR en SHA exacto, revisar diff, integrar y repetir CI sobre `main`.

## 1. DISEÑAR — QUÉ SE CONECTA Y QUÉ NO

F5.6 ya admite modelos de entrada tipados; F5.7 exige capacidad, esquema y versión explícitos; F5.8 conserva autorización de catálogo y cadena de revisiones. F5.10/F6.1 permiten instalar el núcleo neutral fuera del repositorio. **No se añade otra API dentro del Motor.**

F6.2 proporciona un **proyecto consumidor separado** `eios-company-adapter-example==0.1.0` que demuestra cómo mapear datos externos de **dos empresas ficticias** a esos contratos sin duplicarlos. Su ejemplo de dominio es mantenimiento de equipos; no supone que el núcleo sepa interpretar balances, pedidos, facturas o referencias documentales de una nueva empresa.

Archivos: `tests/fixtures/f6_2_external_company_adapter/` (paquete independiente) y `tools/verify_f6_2_external_company_adapter.py` (verificador del wheel y de su ejecución aislada), junto con pruebas `tests/test_f6_2_external_company_adapter.py`.

## 2. AUDITAR — CONTRATO DE ENTRADA (RESPONSABILIDAD DEL ADAPTADOR)

Dos elementos estrictamente separados:

- **`ExternalSourceScope` — configuración del integrador, no copiada del registro recibido:** `project_id`, `company_id`, `source_id`, `expected_sha256`, `data_snapshot_id`, `rules_version`, `parameters_version`, `schema_version=v1`, `purpose=SYNTHETIC_TEST_ONLY`.
- **`SyntheticEquipmentRecord` — registro de entrada no confiable:** los mismos identificadores de proyecto, empresa, fuente, snapshot y esquema; `decision_id`, `scenario_id`, instalación, equipo, horas, intervalo de revisión y posible referencia declarada de inspección. Exige `evidence_class=SYNTHETIC_TEST`, `documentary_status=UNVERIFIED`.

Se admite únicamente un JSON UTF-8 de hasta 32 KiB, con claves únicas y tipos exactos. Se rechazan números no finitos, bytes inválidos, campos nuevos o de autoridad, identificadores cruzados, errores de rango y versiones no declaradas. Se compara SHA-256 **antes de interpretar el registro**, pero no se interpreta un hash coincidente como prueba de origen auténtico.

`prepare_external_case()` no ejecuta productores ni autoriza un catálogo: produce `KernelContext`, `KernelOperation`, `KernelPlan`, `CapabilityCatalog` y `CapabilityInputBinding` usando exclusivamente las APIs ya cerradas. Conserva `UNVERIFIED_ADAPTER_RESPONSIBILITY`, `production_authorized=False` y `operational_path=FORBIDDEN`.

## 3. DEPURAR — AISLAMIENTO Y GOBIERNO REALMENTE EJERCITADOS

El ejemplo ejecutable realiza esta secuencia para cada empresa:

`JSON externo` → `preflight de ámbito/versión/hash/esquema` → `bindings F5.6` → `catálogo F5.7` → `commit_catalog_change` con **TEST DOUBLE** → `load_governed_state` → `bind_governed_plan` F5.8 → `execute_kernel` F4.

Comprobaciones obligatorias:
- Un grant ausente no puede crear el ledger.
- La empresa B no puede utilizar el ledger de A (ni viceversa).
- La fuente B no puede hacerse pasar por A, incluso cuando quien envía el registro recalcula su propio SHA-256.
- Una capacidad informativa sobre horas puede completar; **una referencia de inspección no autentica un documento**, de modo que su capacidad queda `NOT_EVALUABLE` y el terminal es `PARTIALLY_COMPLETED`.
- Un error en cualquier entrada o productor no puede presentarse como decisión empresarial autorizada.
- Cada empresa tiene registro, contexto, catálogo y ledger independientes; la ruta operacional siempre permanece prohibida.

## 4. AUDITAR 2 — PORTABILIDAD FÍSICA Y PRUEBAS ADVERSARIAS

El verificador:
1. Reutiliza el ZIP F5.10 existente, lo extrae con los controles de seguridad ya certificados y comprueba su manifiesto en la plataforma actual.
2. Construye un **quinto wheel independiente** desde su propio `pyproject.toml`; audita que solo contenga `eios_company_adapter_example`, sin código de `eios/`, y compara cada archivo Python de su wheel con su fuente exacta mediante SHA-256.
3. Restringe imports de EIOS a kernel, contratos de entrada, catálogo y gobierno; exige versiones `==0.1.0` de estos cuatro paquetes.
4. Crea un entorno virtual aislado fuera del checkout, instala todos los wheels necesarios con `--no-index --require-hashes`, comprueba `pip check` y ejecuta `python -I -m eios_company_adapter_example.demo`.
5. Exige dos empresas distintas y dos ledgers, ambas con `PARTIALLY_COMPLETED` y sin admisión o autorización operacional.

La suite `pytest` comprueba las variantes negativas: intercambio de empresas/proyectos/fuentes/snapshots, cambios de esquema, reescritura con hash antiguo, falsa evidencia operacional, importes/horas con tipo incorrecto, campos extra, JSON duplicado, `NaN`, tamaño excesivo y productores ausentes.

La CI ejecuta F6.2 en **Ubuntu y Windows** usando los kits específicos de F5.10 y F6.1. No se elimina ninguna verificación anterior.

## 5. LÍMITES IMPRESCINDIBLES

- **Sin empresas reales ni datos reales**: dos empresas ficticias, entradas sintéticas y aprobadores sintéticos. No se simulan certificados verdaderos.
- **Identidad declarada ≠ identidad autenticada**: `project_id`/`company_id` comprueban consistencia, no la identidad legal de la empresa.
- **Hash ≠ autenticidad documental**: solo protege contra discordancia con la huella suministrada; no acredita quién firmó o entregó los datos.
- **Referencia documental ≠ documento verificado**: no existe validación de facturas, balances, pedidos ni soportes empresariales.
- **CI verde ≠ sistema listo para producción**: no se acreditan custodias, permisos reales, seguridad de red, escrituras multiusuario, disponibilidad, backups ni acción humana observada.
- F6.2 **no modifica** ningún módulo `eios/`, motor financiero, PRICE/TCO, reglas C0, interfaz o frontera QTG/O1.

## 6. CERRAR → MATERIALIZAR → CI

La unidad solo podrá declararse cerrada cuando:

1. Pasen los tests previos y los nuevos, sin excluir ninguna regresión.
2. Pase el verificador físico externo F6.2 en los trabajos Linux y Windows de la PR.
3. El diff no contenga cambios a módulos canónicos de EIOS ni contradiga la frontera sintética.
4. PR integrada con SHA explícito y CI de `main` satisfactoria en dicho SHA.

**Próxima unidad sugerida — F6.3:** contrato de admisión documental/identidad empresarial en un servicio externo distinto al kernel, con fuentes y actores auténticos solo cuando exista empresa colaboradora y canal seguro. No promocionar fuentes sintéticas mediante cambio de etiquetas.

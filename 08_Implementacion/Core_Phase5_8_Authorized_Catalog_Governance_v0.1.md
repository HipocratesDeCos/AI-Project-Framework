# EIOS — F5.8 · GOBERNANZA VERSIONADA Y AUTORIZADA DE CAPACIDADES

**Fecha:** 2026-11-17.  
**Baseline verificado:** `main @ be1185e5cbff59998426128d940e7f4b3dcf5ceb` (F5.7, CI postmerge #44041478953 SUCCESS).  
**Estado:** candidato hasta CI PR **y CI postmerge** SUCCESS sobre sus respectivos SHA exactos.

## 1. DISEÑAR — PROPÓSITO Y FRONTERA

F5.7 incorporó un catálogo inmutable de versiones **compatibles** por proyecto, pero no estableció un mecanismo persistente que respondiera a estas preguntas: **¿qué versiones están efectivamente habilitadas hoy?, ¿quién autorizó el cambio?, ¿qué estado existía antes?, ¿qué ocurre ante dos actualizaciones simultáneas?**

F5.8 añade un paquete opcional `eios-catalog-governance==0.1.0` que no altera ningún módulo original de `eios/kernel`, `eios/input_contracts`, `eios/capability_catalog`, PRICE ni TCO. Contiene **exactamente dos módulos canónicos** bajo `eios/catalog_governance` y depende únicamente de:

- `pydantic>=2,<3`
- `eios-kernel==0.1.0`
- `eios-input-contracts==0.1.0`
- `eios-capability-catalog==0.1.0`

**No existe catálogo universal ni descubrimiento automático:** cada proyecto aporta su `CapabilityCatalog` técnico de F5.7 desde un registro de código de confianza. F5.8 solo mantiene el estado autorizado de selección de releases dentro de ese catálogo.

### Contratos de F5.8

| API | Responsabilidad |
|---|---|
| `CatalogChange` | Propuesta inmutable: proyecto, catálogo, conjunto completo de releases deseados, revisión y hash anterior, motivo y aceptación explícita de retroceso |
| `AuthorizationGrant` | Declaración inmutable de un **adaptador externo de confianza**: proyecto, actor, referencia de autorización, política y acciones permitidas |
| `commit_catalog_change` | Valida, obtiene permiso externo, compara versión/hash anterior y confirma **una** revisión del historial mediante escritura atómica |
| `load_governed_state` | Reconstruye la última selección, validando registros y cadena de hashes SHA-256 |
| `fingerprint_catalog` | Huella estable de identidad de proyecto, versión y especificaciones de releases; **no es firma digital** |
| `bind_governed_plan` | Carga la selección autorizada; usa el validador F5.7/F5.6 antes del Motor y revalida la revisión activa antes de cada invocador |

## 2. AUDITAR — AUTORIZACIÓN REAL FRENTE A AFIRMACIONES

La autorización es **obligatoria**: no se permite crear ni actualizar una selección sin un callback externo que devuelva un `AuthorizationGrant` correcto para ese proyecto y las acciones requeridas.

**Sin embargo:** la librería NO autentica al usuario del callback ni verifica un documento, token o firma. El integrador debe implementar y custodiar ese callback, las identidades y los permisos. **Pasar un callback permisivo construido por el propio solicitante no constituye seguridad ni aprobación empresarial**. El paquete solo garantiza que las escrituras pasen por la interfaz autorizadora suministrada por el integrador. Las pruebas emplean un aprobador sintético.

Acciones derivadas de la diferencia entre estados:

- `BOOTSTRAP`: primer catálogo, requiere al menos una capacidad;
- `ENABLE`: habilitar una capacidad adicional;
- `DISABLE`: retirar una capacidad previamente habilitada;
- `REPLACE`: reemplazar una versión explícita;
- `UPGRADE_CATALOG`: cambiar la versión del catálogo técnico;
- `ROLLBACK`: retroceder a una versión anterior, exige `allow_rollback=True` y permiso externo adicional.

No hay selección `latest`, compatibilidad semántica inferida ni cambios sin efectos. Un registro de releases puede ser compatible (F5.7) y permanecer **no habilitado** (F5.8). La selección actual nunca se deriva de valores por defecto ni se acepta desde el cliente de ejecución.

## 3. DEPURAR — PERSISTENCIA Y TRAZABILIDAD

El estado de **un proyecto por archivo** se persiste en JSON canónico con revisión monotónica, identificador de proyecto, versión y huella del catálogo, lista ordenada de releases habilitados, acciones, motivo, actor, referencia y política de autorización, fecha UTC, hash del registro anterior y hash del registro actual.

Se aplican:

- Bloqueo local exclusivo `<ledger>.lock` con creación atómica: si existe, **rechaza el cambio**, no lo borra ni lo recicla automáticamente.
- Control optimista por `expected_revision` **y** `expected_head_hash`: no sobrescribe una actualización concurrente ni un estado posterior.
- Escritura mediante archivo temporal en el mismo directorio, `fsync` y `os.replace` atómico, sin archivo parcialmente escrito.
- Lectura estricta con rechazo de formato inválido, revisiones no consecutivas, proyecto ajeno, campos extra, claves JSON duplicadas, cadena de hashes rota y acciones no coherentes con la transición.
- **Aislamiento por proyecto:** un archivo con revisiones de una empresa/proyecto no puede utilizarse como catálogo autorizado de otro proyecto.

**Alcance de seguridad:** un hash SHA-256 no impide que alguien con permiso de escribir TODO el archivo lo reescriba y recalcule toda la cadena. Tampoco detecta por sí solo una truncación maliciosa del historial. Para integridad frente a un adversario hace falta anclaje externo de hashes, firmas digitales/registro inmutable y control del almacenamiento. **F5.8 no afirma aportar firma, anclaje ni autorización empresarial autenticada.** El mecanismo de bloqueo es para filesystem local respetado por los colaboradores, no para sistemas distribuidos de múltiples nodos o almacenamiento en red.

## 4. AUDITAR 2 — EJECUCIÓN BAJO ESTADO AUTORIZADO

Antes de ejecutar el Motor, `bind_governed_plan` requiere la revisión y hash correctos del estado persistido, el mismo proyecto y la huella/versiones del catálogo de F5.7. Resuelve el release de cada capacidad **exclusivamente** desde el ledger.

Si un plan solicita una capacidad deshabilitada, se rechaza **antes de cualquier productor**. Además, cada invocador vuelve a leer la revisión/historial: si se retira una autorización entre preparación y ejecución, la ejecución se detiene con `GOVERNED_CONFIGURATION_CHANGED_DURING_EXECUTION`.

Esta comprobación reduce ejecuciones obsoletas, **pero no es una transacción distribuida**: el estado aún puede cambiar durante el cálculo propio de una capacidad. En un despliegue empresarial real deben añadirse reservas transaccionales y autorización de operación en el vertical; no son responsabilidad del núcleo.

El Motor conserva:

- `decision_authority=False`
- `operational_path=FORBIDDEN`
- `provenance_status=UNVERIFIED_ADAPTER_RESPONSIBILITY`

Ni QTG ni O1 se registran como una capacidad de negocio por esta vía.

## 5. PRUEBAS REALES DE PORTABILIDAD

`tests/test_f5_8_catalog_governance.py` y `tests/test_f5_8_catalog_governance_wheel.py` verifican alta, baja, sustitución, retroceso, actualización de catálogo, autorización faltante/ajena/insuficiente, revisiones desfasadas, huella incorrecta, archivo alterado, bloqueo existente, coherencia de hashes, dos proyectos independientes, selección inmutable, límites de dependencias, ruta de imports y wheel canónico.

`tools/verify_f5_8_governance_two_domains.py` usa **dos entornos virtuales aislados fuera del repositorio**, ejecuta `pip check`, compara SHA-256 de cada módulo instalado y utiliza `python -I` sin `PYTHONPATH`:

1. **VENTAS:** solo Motor + contrato de entrada + catálogo + gobernanza; modelos propios, sin PRICE ni TCO.
2. **COMPRAS:** Motor + contratos + catálogo + gobernanza + C0 + PRICE + TCO, con las fórmulas originales. TCO sintético **57,50 €**; PRICE analítico **11,00 €** y cobertura documental empresarial **insuficiente**.
3. Ambos crean una selección de dos capacidades mediante una autorización sintética, ejecutan y después registran la baja autorizada de una capacidad. Los invocadores preparados con la revisión anterior **se rechazan**. También se comprueba un segundo intento de cambio con revisión obsoleta y la cadena de historial.
4. Todos los resultados conservan ruta operacional `FORBIDDEN` y ninguna autorización de negocio.

## 6. MATERIALIZAR → CI → CERRAR

La CI mantiene Python completo, SQL Server C0/versiones/parámetros, instalaciones F4/F5.3–F5.7 y añade construcción/admisión del wheel F5.8 y los dos entornos anteriores.

```powershell
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_input_contracts_distribution.py --output dist/inputs
python tools/build_eios_capability_catalog_distribution.py --output dist/catalog
python tools/build_eios_contracts_distribution.py --output dist/contracts
python tools/build_eios_price_distribution.py --output dist/price
python tools/build_eios_tco_distribution.py --output dist/tco
python tools/build_eios_catalog_governance_distribution.py --output dist/governance
python tools/verify_f5_8_governance_two_domains.py --kernel-dir dist/kernel --inputs-dir dist/inputs --catalog-dir dist/catalog --governance-dir dist/governance --contracts-dir dist/contracts --price-dir dist/price --tco-dir dist/tco
```

**Cierre únicamente con** PR CI SUCCESS sobre el HEAD exacto; diff auditado, merge controlado y CI postmerge SUCCESS sobre SHA exacto de `main`.

**Objetivo materializado:** `versioned_release_selection=PERSISTED`, `external_policy_callback=REQUIRED`, `concurrent_update=FAIL_CLOSED`, `historical_hash_chain=VERIFIED`, `stale_invocation=BLOCKED`, `sales_procurement_isolation=VERIFIED`, `operational_authority=FORBIDDEN`.

**Fuera de F5.8:** firma digital, autenticación de usuarios, control de acceso de aplicación, almacenamiento distribuido, autorizaciones regulatorias, auditoría inmutable con anclaje externo y primera admisión de datos operacionales reales.

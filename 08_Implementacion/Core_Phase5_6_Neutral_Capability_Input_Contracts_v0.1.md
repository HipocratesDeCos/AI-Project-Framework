# EIOS — F5.6 · CONTRATOS NEUTROS DE ENTRADA PARA NUEVOS PROYECTOS

**Fecha:** 2026-11-17  
**Baseline:** `main @ a27ae6fe86df0a9c0cd842187716ae7accd290ea`, F5.5 cerrada; CI postmerge #44025747883 SUCCESS.  
**Estado:** candidato; el cierre requiere CI de PR y CI postintegración SUCCESS sobre sus SHA exactos.  
**Objetivo:** incorporar un contrato técnico de entrada que sirva a verticales independientes (Compras, Ventas, futuros proyectos) sin copiar modelos de Compras ni alterar el Motor.

## 1. DISEÑAR — FRONTERA Y CONTRATO

La ejecución `eios.kernel.execution.execute_kernel` ya acepta `KernelOperation.payload: BaseModel` y `KernelContext` neutral. No se modifica ese bucle de ejecución. Faltaba una manera física, comprobable y versionada de declarar **qué tipo de entrada está permitido por cada proyecto y capacidad**.

Se añade la distribución opcional **`eios-input-contracts==0.1.0`** con dos únicos archivos Python canónicos:

- `eios/input_contracts/contracts.py` — validación explícita y *fail-closed* de las declaraciones y preparación de invocadores.
- `eios/input_contracts/__init__.py` — API pública de la misma fuente.

Dependencias obligatorias de la distribución: `pydantic>=2,<3` y **`eios-kernel==0.1.0`**. Ninguna dependencia de `eios.core`, PRICE, TCO, Sql Server, Excel o frontend.

La API pública contiene:

| Contrato | Función |
|---|---|
| `CapabilityInputSpec` | Registro explícito del `project_id`, `capability`, `schema_id`, `schema_version` y clase exacta Pydantic del vertical |
| `CapabilityInputEnvelope` | Entrada declarada con 6 identificadores/versiones de contexto, esquema y objeto de dominio tipado |
| `CapabilityInputBinding` | Relación explícita entre contrato, entrada y productor de una capacidad |
| `bind_capability_inputs` | Preflight de **todas** las capacidades del plan antes de entregar un mapa de invocadores al Motor |
| `InputContractError` | Error fail-closed del contrato técnico |

**Los seis campos del contexto verificados:** `project_id`, `decision_id`, `scenario_id`, `rules_version`, `parameters_version`, `data_snapshot_id`.

## 2. AUDITAR — LÍMITES Y SEMÁNTICA

El preflight de F5.6 verifica: plan completo sin invocadores implícitos; capacidad registrada; nombre/versión de esquema; identidad completa; tipo **exacto** de la clase de entrada Pydantic; igualdad entre el payload del Motor y el payload declarado; y `decision_id`/`scenario_id` internos **si el modelo de dominio define esos campos**.

Una identidad/esquema incorrecto de la segunda capacidad bloquea el plan **antes de invocar la primera**, evitando éxitos parciales provenientes de entradas incompatibles. El mapa devuelto es inmutable y el adaptador vuelve a comprobar versiones, tipo y payload en cada invocación, con copias profundas de los datos.

**No se importa ni se asume un `PurchaseOperation`** desde el contrato neutral. El modelo Pydantic lo define el consumidor: puede ser `PurchaseOperation` de EIOS Compras, `SalesQuote` propio del comercial o un modelo futuro de otro sector.

No se concede ninguna de estas autoridades:

- El `provenance_status` de la entrada es **`UNVERIFIED_ADAPTER_RESPONSIBILITY`** y no acepta valores de documentación autenticada.
- La comprobación de un `project_id` declarado **no autentica empresas**. La comprobación de `company_id`, permisos de usuarios, pruebas documentales, moneda, vigencia y demás reglas sectoriales sigue siendo obligación del adaptador de cada vertical.
- El contrato neutral **no evalúa PRICE/TCO ni modifica sus modelos**; solo comprueba que son invocados con la entrada y versión expresamente registradas.
- No se incorporan QTG ni O1 como plugins, ni ejecución de facturas, autorización de operaciones, decisiones o persistencia. `decision_authority=False` y `operational_path=FORBIDDEN` continúan siendo los flags del Motor.

## 3. DEPURAR — DOS PROYECTOS AISLADOS

`tools/verify_f5_6_two_domains.py` audita las rutas y hashes de cada wheel y crea **dos venvs totalmente distintos fuera del checkout**, ejecutando `pip check` y `python -I`, sin `PYTHONPATH`:

**Proyecto VENTAS (sintético):**
- Instala **solo** `eios-kernel` + `eios-input-contracts` (y Pydantic como requisito).
- Define su propio `SalesQuote(company_id, customer_id, product_id, offered_price, payment_days)`.
- Registra capacidades `SALES_FIELDS` y `SALES_DOCUMENTARY` sin importar módulos `eios.core`, `eios.pricing` o `eios.tco`.
- Comprueba copia inmutable de la entrada, rechazo por snapshot inconsistente antes de productores y `PARTIALLY_COMPLETED` por evidencia comercial no aportada.

**Proyecto COMPRAS (sintético):**
- Instala los **cinco** wheels: Motor, nuevo contrato neutral, contrato C0 específico, PRICE v0.2.0 y TCO v0.2.0.
- Declara un solo tipo Pydantic canónico `PurchaseOperation` para ambas capacidades y dos entradas de esquema explícitas.
- Ejecuta TCO real en 10 × 5 euros + transporte 7,50 euros: **57,50 euros**.
- Ejecuta PRICE real con referencias sintéticas de 10 y 12 euros: mediana analítica **11,00 euros**. Pero **bloquea la puerta documental estricta** porque faltan pruebas de comparabilidad económica de empresa; resultado PRICE `NOT_EVALUABLE`, TCO `COMPLETED`, Motor `PARTIALLY_COMPLETED`.
- Cambiar una versión del esquema de TCO impide vincular ambas capacidades; ninguna es ejecutada.
- Verifica que el resultado técnico no concede autoridad: `decision_authority=False`, `operational_path=FORBIDDEN`.

**Los dos clientes instalan los mismos bytes del kernel y de `eios.input_contracts.contracts`**, con SHA-256 comprobados contra los originales de la rama. No existe segunda implementación de PRICE, TCO ni del bucle del Motor.

## 4. AUDITAR 2 — EMBALAJE Y REGRESIONES

El generador `tools/build_eios_input_contracts_distribution.py` crea un staging efímero de solo dos archivos, verifica por AST las dependencias internas y audita el wheel real. Rechaza archivos adicionales, dependencias distintas de Pydantic/kernel, ausencia del pin exacto `eios-kernel==0.1.0` o imports internos de Compras/Ventas.

Pruebas:

- `tests/test_f5_6_neutral_input_contracts.py`: seis derivas de contexto, versiones/nombre de esquema, proyecto cruzado, tipo Pydantic, payload interno, operación distinta, capacidades faltantes, campos de autoridad falsificados, bloqueo QTG/O1, mutaciones en invocadores y proyecto Ventas independiente.
- `tests/test_f5_6_input_contract_wheel.py`: source allowlist, staging byte a byte, dependencias explícitas, paquete sin negocios, import malicioso, nuevas rutas de wheel no autorizadas y prueba de CLI.
- La CI incluye nueva construcción del wheel y las dos instalaciones F5.6 **después** de Python/SQL, pruebas F4, F5.3, F5.4 y F5.5.

No se modifican archivos de producción anteriores: `eios/kernel`, `eios/core`, `eios/pricing`, `eios/tco`, `eios/parameters`, las bases de datos, aplicaciones ni la arquitectura cerrada. El paquete monolítico existente mantiene su ruta pública y sus cálculos.

## 5. CERRAR → MATERIALIZAR → CI

Comandos locales en una copia actualizada de la rama, desde la raíz:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_contracts_distribution.py --output dist/contracts
python tools/build_eios_price_distribution.py --output dist/price
python tools/build_eios_tco_distribution.py --output dist/tco
python tools/build_eios_input_contracts_distribution.py --output dist/inputs
python tools/verify_f5_6_two_domains.py --kernel-dir dist/kernel --inputs-dir dist/inputs --contracts-dir dist/contracts --price-dir dist/price --tco-dir dist/tco
```

**Cierre autorizado únicamente si** la CI PR en HEAD exacto es SUCCESS, el diff mantiene los límites, la PR se fusiona, y la CI postintegración en `main` vuelve a ser SUCCESS en SHA exacto.

**Resultado alcanzable:** `neutral_input_schema_boundary=VERIFIED`; `independent_sales_client=VERIFIED`; `procurement_real_capabilities=VERIFIED`; `provenance_authentication=NOT_PROVEN`; `PRICE_TCO_CROSS_DOMAIN=NOT_PROVEN`; `operational_path=FORBIDDEN`.

F5.6 es una base de entrada tipada y reusable; **no** equivale a la extracción universal de todos los algoritmos sectoriales. Las próximas extensiones deberán realizarse con adaptadores propios y contratos reales de cada proyecto, no cambiando las etiquetas de expedientes sintéticos.

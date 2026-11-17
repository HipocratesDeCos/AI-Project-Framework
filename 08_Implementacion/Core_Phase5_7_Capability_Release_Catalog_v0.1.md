# EIOS — F5.7 · CATÁLOGO EXPLÍCITO DE CAPACIDADES Y VERSIONES

**Fecha:** 2026-11-17.  
**Baseline de partida:** `main @ 4e426cd4e09e1f8dfe0ed8ce258a8d185fc7edeb` — F5.6 cerrada y CI postmerge #44028461371 SUCCESS.  
**Estado:** candidato; **no cerrar antes de CI PR y CI postmerge SUCCESS en SHA exacto**.

## 1. DISEÑAR — QUÉ PROBLEMA RESUELVE

F5.6 validó identidad, procedencia técnica no verificada, contexto y clase Pydantic de la entrada de cada capacidad. Faltaba un mecanismo para expresar **qué release de una capacidad está habilitada para un proyecto y qué versiones de esquema de entrada admite**.

F5.7 introduce una distribución opcional independiente `eios-capability-catalog==0.1.0` con API:

- **`CapabilityRelease`**: proyecto, nombre de capacidad, `release_version` semántica exacta (`major.minor.patch`), `schema_id`, conjunto **explícito** de `compatible_schema_versions`, clase Pydantic exacta, `policy_version`, versiones requeridas del núcleo y de F5.6, y bandera `enabled`.
- **`CapabilityCatalog`**: fotografía **inmutable** de releases de un proyecto, con versión de catálogo y rechazo de claves `(capability,release_version)` duplicadas o ajenas.
- **`bind_catalog_plan`**: exige elección **explícita** del release de **todas** las capacidades del plan; valida catálogo, proyecto, política, versiones técnicas, esquema y modelo. Solo tras aprobar **el plan completo** delega en `bind_capability_inputs` de F5.6 y devuelve su mapa de invocadores inmutable.
- **`CapabilityCatalogError`**: errores específicos, legibles por máquina, sin valores por defecto que oculten incompatibilidades.

**Un `1.1.0` no es compatible por ser mayor o menor que `1.0.0`**: el catálogo no aplica rangos automáticos de SemVer. Deben existir entradas de release independientes y listas explícitas de versiones de esquema. Los identificadores comerciales `v1`, `v1.1` y otros no se convierten ni migran automáticamente: permanecen cadenas de contrato declaradas.

## 2. AUDITAR — FRONTERAS MANTENIDAS

La distribución contiene exactamente **dos módulos** canónicos:

- `eios/capability_catalog/catalog.py`
- `eios/capability_catalog/__init__.py`

Dependencias fijadas del wheel: `pydantic>=2,<3`, `eios-kernel==0.1.0` y `eios-input-contracts==0.1.0`. No importa `eios.core`, PRICE, TCO, finance, reglas de compras, empresa, SQL, Excel ni UI.

Una selección puede fallar por estos motivos: no hay release seleccionado, se pide uno no registrado, el release está deshabilitado, proyecto distinto, esquema distinto, versión de esquema fuera de la lista explícita, tipo Pydantic no coincidente, política distinta o API neutral requerida incompatible. Ninguna de estas situaciones provoca búsqueda automática de un release alternativo.

El plan y la entrada siguen sujetos a **F5.6**: seis dimensiones completas de `KernelContext`, identidad de operación, procedencia técnica `UNVERIFIED_ADAPTER_RESPONSIBILITY`, inmutabilidad de las copias de entrada y rechazo de capacidades reservadas `QTG` y `O1`. El resultado final lo crea **el mismo** `execute_kernel` neutro de F4; este catálogo no lo modifica.

**El catálogo no autentica la identidad de una empresa, un documento ni un paquete instalado por un tercero**: la autenticación de evidencias pertenece al vertical/adaptador. Las versiones físicas de wheels se comprueban por metadatos, `pip check` y hashes SHA-256 en el verificador de distribución, no por confiar en etiquetas suministradas por el usuario.

## 3. DEPURAR — MATRIZ DE COMPATIBILIDAD REPRODUCIBLE

Ejemplo **sintético**, no licencia operativa:

| Proyecto | Capacidad | Release solicitado | Esquema declarado | Versión admitida | Resultado |
|---|---|---|---|---|---|
| Ventas | SALES_FIELDS | 1.0.0 | synthetic.sales.quote | v1 | Compatible |
| Ventas | SALES_DOCUMENTARY | 1.0.0 | synthetic.sales.quote | v1 | Compatible, documentación insuficiente |
| Ventas | SALES_FIELDS | 1.0.1 | synthetic.sales.quote | v1 | **Bloqueado**: release no registrado |
| Compras | PRICE | 1.0.0 | eios.procurement.purchase | v1 | Compatible técnicamente, documentación empresarial insuficiente |
| Compras | TCO | 1.0.0 | eios.procurement.purchase | v1 | Compatible técnicamente |
| Compras | TCO | 1.0.0 | eios.procurement.purchase | v2 | **Bloqueado**: versión de esquema no permitida |
| Compras | TCO | 1.0.0 | eios.procurement.purchase | v1 | **Bloqueado** si `enabled=False` |

El programa `tools/verify_f5_7_capability_catalog.py` reutiliza las **dos pruebas de consumidor reales de F5.6** (sin duplicar ni modificar fórmulas) y sustituye únicamente su fase de enlace por el catálogo:

- **Ventas**: venv limpio con **solo tres** ruedas `eios-kernel`, `eios-input-contracts`, `eios-capability-catalog`. El modelo de oferta es propio, no existe `eios.core`, ni PRICE ni TCO.
- **Compras**: venv limpio con **seis** ruedas, añadiendo contratos C0, PRICE y TCO. Se ejecutan los motores canónicos; TCO sintético **57,50 €** y referencia PRICE analítica **11,00 €**, pero **PRICE de empresa NOT_EVALUABLE por falta documental**.
- En ambos entornos: instalación con `pip`, `pip check`, ejecución `python -I` fuera del repositorio sin `PYTHONPATH`, comprobación de ausencia de solapamientos entre rutas `eios/`, contenido físico idéntico a fuente canónica, huellas SHA-256 y resultado `operational_path=FORBIDDEN`.
- Pruebas de selección adversaria: releases no registrados `1.0.1` y `2.0.0`; esquema `v2` no declarado; release deshabilitado. Deben fallar **antes de invocar ninguna capacidad**.

Los tests del módulo verifican además catálogo inmutable, registros repetidos, proyecto cruzado, plan incompleto, política incompatible, versiones físicas del API neutral exigidas, prohibiciones QTG/O1 y compatibilidad explícita de esquemas.

## 4. AUDITAR 2 — RIESGOS QUE NO SE OCULTAN

- **No es un plugin marketplace** ni descarga módulos ni autodetecta capacidades del sistema. Todo registro y todo release son responsabilidad de una configuración suministrada por el proyecto y autorizada en sus propios procesos.
- Una versión compatible **solo acredita coherencia técnica**; no calidad de datos, procedencia, exactitud económica ni permiso para ejecutar una compra/venta.
- No se permite publicar este wheel con el paquete monolítico `eios-mvp` en el mismo entorno: pueden compartir rutas físicas, aunque aquí se prueben sus distribuciones modulares independientes.
- La política de compatibilidad exige un nuevo registro auditado para releases nuevas. No activa migraciones ni convierte PRICE/TCO de Compras en capacidades universales para Ventas.
- La coexistencia con futuros cambios de API neutral requerirá nueva evidencia; F5.7 exige exactamente `eios-kernel==0.1.0` y `eios-input-contracts==0.1.0`.

## 5. MATERIALIZAR → CI → CERRAR

Desde la raíz de la rama actual:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_input_contracts_distribution.py --output dist/inputs
python tools/build_eios_contracts_distribution.py --output dist/contracts
python tools/build_eios_price_distribution.py --output dist/price
python tools/build_eios_tco_distribution.py --output dist/tco
python tools/build_eios_capability_catalog_distribution.py --output dist/catalog
python tools/verify_f5_7_capability_catalog.py --kernel-dir dist/kernel --inputs-dir dist/inputs --catalog-dir dist/catalog --contracts-dir dist/contracts --price-dir dist/price --tco-dir dist/tco
```

La CI conserva todas las regresiones Python/SQL, F4 y F5.3–F5.6; añade construcción del wheel del catálogo y doble consumidor aislado F5.7. Exige **SUCCESS sobre el HEAD exacto de PR**, comprobación de diff limitado, merge controlado y **SUCCESS postmerge sobre el SHA exacto de `main`**.

**Criterio de cierre esperado:** `catalog_explicit_releases=VERIFIED`; `project_separation=VERIFIED`; `schema_compatibility_fail_closed=VERIFIED`; `new_release_never_auto_selected=VERIFIED`; `real_price_tco_unchanged=VERIFIED`; `operational_path=FORBIDDEN`.

**Siguiente decisión técnica tras F5.7:** evaluar si es prioritario hacer persistente una configuración de catálogo versionada y autorizada o realizar la primera conexión de un proyecto externo real con adaptación por contrato. Ninguna debe inferirse como completada por esta entrega.

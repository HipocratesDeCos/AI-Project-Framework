# EIOS — F5.3 · TCO COMO CAPACIDAD OPCIONAL DE ADQUISICIÓN

**Fecha:** 2026-11-16  
**Baseline:** `main @ 4658f9c353b908046072efa5d4dbaccda801718d`, F5.2 cerrada; CI postmerge #43945404301 SUCCESS.  
**Unidad:** F5.3. Distribución física independiente de TCO **para adquisición/compras** sin refactorizar cálculos.  
**Estado:** candidata hasta que se verifiquen la CI de PR y la CI postmerge sobre sus SHA exactos.

## 1. DISEÑAR — DECISIÓN ARQUITECTÓNICA

La lógica existente de TCO es una capacidad de **coste total de adquisición**, no un algoritmo comercial universal. Su `TCOInput` depende de `eios.core.models.PurchaseOperation` y su resultado `TCOResult` expresa moneda, total, componentes contribuyentes, componentes pendientes y limitaciones.

La política de extracción es estricta:

- **Un solo código fuente:** no copiar `calculate_tco` a otro módulo persistente ni introducir un cálculo alternativo.
- **Una distribución independiente específica**, llamada `eios-tco-procurement 0.1.0`.
- **Dependencia ejecutable mínima:** solo `pydantic>=2,<3`. La capacidad no instala forzosamente `eios-kernel`, Excel, SQL Server ni el frontend.
- **Contrato declarado, no oculto:** este wheel **incluye** `eios.core.models` porque el `TCOInput` original importa directamente `PurchaseOperation`. Por ello incorpora más modelos de C0 de los estrictamente necesarios: una deuda arquitectónica documentada, NO prueba de un TCO neutral para Ventas.
- **No alterar las importaciones públicas** de `eios.tco`, `eios.tco.models`, `eios.tco.engine` ni de `eios.core.models`.

Fuentes exactas de la distribución:

| Archivo canónico | Función |
|---|---|
| `eios/core/models.py` | `PurchaseOperation`, `DecisionContext` y modelos C0 heredados de los que depende |
| `eios/tco/models.py` | `CostComponent`, `TCOInput`, `TCOResult` |
| `eios/tco/engine.py` | **Única implementación** `calculate_tco` |
| `eios/tco/__init__.py` | Reexportación pública existente |

`packaging/eios-tco-procurement/pyproject.toml` define la distribución. `tools/build_eios_tco_distribution.py` verifica dependencias transversales mediante AST, crea temporalmente el proyecto PEP 517 a partir de estas fuentes y audita la lista real de archivos y dependencias del wheel.

**Instalación:** un proyecto nuevo que necesite cálculo de adquisiciones puede instalar este wheel por sí solo. También puede instalar simultáneamente el wheel `eios-kernel` de F4 porque sus rutas físicas no colisionan. La instalación simultánea con el paquete completo `eios-mvp` NO se recomienda; comparten módulos instalados bajo `eios/` y pueden producir sobrescrituras/orden de importación ambiguo.

## 2. AUDITAR — COMPROBACIÓN EN ENTORNOS LIMPIOS

`tools/verify_f5_3_optional_tco.py` crea **dos entornos virtuales diferentes**, siempre fuera del checkout, con `PYTHONPATH` suprimido y ejecución `python -I`:

1. **TCO solo.** Comprueba que `eios-kernel`, `openpyxl`, `eios-mvp` y la aplicación no están instalados. Ejecuta el cálculo canónico y verifica modelo, unidades, exactitud, causas de incompletitud y datos contradictorios.
2. **TCO + Motor.** Instala los mismos wheels ya construidos y auditados para demostrar coexistencia real. Usa `execute_kernel` con un invocador de demostración aportado por el consumidor; el núcleo devuelve **solo estado técnico** y no recibe resultados económicos como autorización.

Antes de instalar, el verificador exige intersección **vacía** de las rutas de ambos wheels. Después compara SHA-256 de **cada archivo TCO instalado** con los bytes correspondientes del wheel original. El contenido del Motor permanece inalterado.

Expediente de prueba **sintético**: compra de 10 unidades a 5 euros y transporte atribuible de 7,50 euros → coste de adquisición total **57,50 euros**. Un transporte en moneda incompatible o un seguro aplicable sin importe devuelve `value=None`, componentes pendientes y limitaciones explícitas: no hay conversión de moneda, inferencia de precios, ni importes fabricados.

## 3. DEPURAR — PRUEBAS Y RESTRICCIONES

`tests/test_f5_3_optional_tco_distribution.py` valida:

- coincidencia byte a byte de los cuatro archivos canónicos, sin ramas de cálculo duplicadas;
- lista cerrada de importaciones internas, incluida la resolución de importaciones relativas;
- bloqueo si alguien añade integración de Compras, UI, Motor genérico u otro módulo no distribuido;
- rechazo de archivos adicionales o dependencias obligatorias como Excel;
- permanencia de la distribución `eios-mvp` y del código TCO existentes.

`tests.yml` añade las comprobaciones **después** de regresión Python, validadores SQL, build/instalación kernel F4 y los dos consumidores F4.4.

Para construir y verificar en una copia local del repositorio, desde Python 3.11+:

```powershell
cd C:\proyectos\AI-Project-Framework
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_tco_distribution.py --output dist/tco
python tools/verify_f5_3_optional_tco.py --tco-dir dist/tco --kernel-dir dist/kernel
```

## 4. AUDITAR 2 — LO QUE NO SE HA DEMOSTRADO

La extracción acredita una capacidad opcional autónoma **de Compras/Adquisiciones** y su coexistencia física con el Motor; **no** demuestra reutilización de TCO para Ventas, servicios u otros dominios ajenos a adquisiciones.

- El modelo físico sigue expresando proveedor, artículo, cantidad, precio unitario y `EUR`.
- La fábrica `build_context_checked_tco_invoker` de F5.2 **no** se empaqueta aquí: es un adaptador sectorial que depende de las interfaces del vertical EIOS Compras. Un consumidor debe implementar sus propias garantías de identidad, versiones y procedencia para ejecutar cálculos en el kernel; el smoke de coexistencia no equivale a una certificación de confianza.
- `TCOResult.complete` significa **cálculo cerrado con los componentes aportados**, NO que los datos externos sean reales, completos o firmados.
- No se incorporan deudas financieras, almacenamiento, obsolescencia, transporte estimado, conversión FX ni otros conceptos no autorizados por el contrato histórico.
- `decision_authority=False`, `operational_path=FORBIDDEN` y `provenance_status=UNVERIFIED_ADAPTER_RESPONSIBILITY` siguen definidos en la frontera neutral.
- La distribución es un wheel local validado; NO se ha publicado en un registro público, ni representa una integración comercial.

**Siguiente refactor potencial (separado de F5.3):** aislar el contrato `PurchaseOperation` de los modelos C0 del vertical, manteniendo compatibilidad; solo entonces evaluar si hay una capacidad económica verdaderamente neutra entre dominios. Nunca forzar estos cambios para anunciar portabilidad antes de tiempo.

## 5. CERRAR → MATERIALIZAR → CI

F5.3 se considera cerrada únicamente si: diff limitado a metadatos de subpaquete, scripts, tests, documentación y CI; suite Python completa, los tres esquemas SQL, pruebas F4 y nueva instalación F5.3 SUCCESS sobre HEAD exacto; merge controlado; CI postmerge en `main` SUCCESS sobre su SHA exacto.

Al cerrar:
- `tco_optional_procurement_distribution=VERIFIED`;
- `tco_kernel_coinstallation=VERIFIED`;
- `legacy_purchase_tco_calculation=UNCHANGED`;
- `tco_cross_domain_neutrality=NOT_PROVEN`.

La fase 5 global sigue abierta hasta que sus restantes capacidades y fronteras pasen validaciones equivalentes.

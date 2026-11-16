# EIOS — F5.4 · PRICE COMO CAPACIDAD OPCIONAL DE ADQUISICIÓN

**Fecha:** 2026-11-16  
**Baseline:** `main @ c3e796f397259bff88ae61a7632ac0b773335943`, F5.3 cerrada; CI postmerge #43955506734 SUCCESS.  
**Estado:** candidato; no cerrar sin CI de PR y CI postmerge sobre commit exacto.  
**Alcance:** distribuir **PRICE C1 de Compras** desde fuentes canónicas sin copiar fórmulas, atajos de suficiencia o autorizaciones.

## 1. DISEÑAR — FRONTERA REAL Y DECISIÓN DE PAQUETE

La inspección de `eios/pricing` demuestra que PRICE no es solo `engine.py`:

- **Cálculo C1:** `engine.py`, `aggregation.py` y los contratos `models.py`.
- **Elegibilidad y límites:** `representativeness.py`, `sufficiency.py`.
- **Cobertura documental estricta:** `company_coverage.py`.
- **Contratos complementarios ya expuestos por `eios.pricing`:** `comparable_reference.py`, `critical_baseline.py`, `recommended_ceiling.py`, `historical_reference.py`, `historical_comparability.py`.
- **Dependencias C0:** `eios.core.models` y `eios.core.validation` (esta última requerida por HIS003).

La **API pública existente `eios.pricing`** importa estos módulos al cargarse; excluirlos rompería importaciones incluso si algunos procesos solo usan C1. Por tanto, el nuevo paquete `eios-price-procurement 0.1.0` incluye los **12 archivos Python canónicos de `eios/pricing/` y los dos C0 citados**, exactamente 14 módulos, sin duplicarlos de forma persistente en el repositorio.

El generador `tools/build_eios_price_distribution.py` crea un staging efímero desde el código existente, audita mediante AST todas las importaciones internas (incluidas relativas), construye un wheel estándar y valida su contenido físico y metadatos. El manifiesto `packaging/eios-price-procurement/pyproject.toml` declara Python >=3.11 y únicamente Pydantic >=2,<3. Ni el Motor, ni Excel, ni `eios-mvp`, ni dependencias de la interfaz pasan a ser requisitos del módulo PRICE.

**Tipo de reutilización acreditable:** PRICE para compras/adquisiciones; **NO** autoridad de precio universal para Ventas. `PriceIntelligenceInput` mantiene su dependencia expresa de `PurchaseOperation`, `DecisionContext` y `EvidenceValidation`.

## 2. AUDITAR — LA COBERTURA NO PUEDE QUEDAR OCULTA

No se confunden tres estados:

1. **`PR_AVAILABLE` en C1:** indicación analítica resultante de los datos y declaraciones metodológicas aportados, no aprobación de un precio ni certificación documental.
2. **`PriceCoverageReport.COMPLETE`:** verificación de las seis dimensiones económicas declaradas mediante `company_coverage` y un `expected_company_id` proporcionado por el llamante. No certifica por sí misma identidad ni autenticidad documental externa.
3. **Autoridad empresarial:** permanece fuera del paquete y del Motor neutral; no se habilitan firma, ejecución operativa, QTG u O1 como plugins.

Las pruebas de F5.4 hacen funcionar el **cálculo canónico real** con dos referencias sintéticas de 10,00 y 12,00 euros; su mediana no ponderada es 11,00 euros y el contrato produce `PR_AVAILABLE` porque se declaran temporalidad, representatividad y suficiencia. En el **mismo caso**, la puerta de cobertura documental estricta rechaza la ejecución por falta de normalización y pruebas económicas de las seis dimensiones. Un perfil de otra empresa también se rechaza. Sin referencias, PRICE devuelve `PR_NOT_JUSTIFIABLE`, con valor nulo: no se inventa un precio.

La instalación con el Motor se prueba con dos puertas diferentes: la ejecución de PRICE con cobertura insuficiente devuelve `FAILED` en el Motor; la ejecución con referencias ausentes da resultado técnico `PARTIALLY_COMPLETED` y la carencia `PRICE_NOT_JUSTIFIABLE`. En ambos casos: `decision_authority=False`, `operational_path=FORBIDDEN` y `provenance_status=UNVERIFIED_ADAPTER_RESPONSIBILITY`.

## 3. DEPURAR — PRUEBAS DE DISTRIBUCIÓN E INTEGRACIÓN

- `tests/test_f5_4_optional_price_distribution.py`: manifiesto y transiciones del grafo, byte a byte de las fuentes al staging, importaciones internas inesperadas rechazadas, contenido adversario del wheel, dependencias prohibidas, incompatibilidad de ruedas superpuestas y unicidad de `run_price_intelligence`.
- `tools/verify_f5_4_optional_price.py`: dos venvs nuevos y separados, instalados **fuera del checkout**, sin `PYTHONPATH`, con `python -I`:
  - **PRICE solo:** sin Motor, ERP, Excel ni vertical completo.
  - **PRICE + kernel:** sin rutas físicas repetidas; se verifica que el kernel devuelve estados técnicos, no dictámenes comerciales.
- Se compara SHA-256 de los **14 módulos del wheel** contra los archivos canónicos del repositorio y después contra cada archivo instalado.
- La CI añade build y verificación F5.4 **después** de las regresiones Python, SQL, F4.3/F4.4, y la construcción/instalación F5.3.

Comandos de referencia, desde la raíz del repositorio:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_tco_distribution.py --output dist/tco
python tools/build_eios_price_distribution.py --output dist/price
python tools/verify_f5_4_optional_price.py --price-dir dist/price --kernel-dir dist/kernel --tco-dir dist/tco
```

**No se modifican** `eios/pricing`, `eios/core`, PRICE C1, documentos/SQL, Centro de Parámetros, `eios-kernel`, cálculos TCO, `eios-mvp` ni las aplicaciones.

## 4. AUDITAR 2 — RIESGO ESTRUCTURAL DETECTADO (NO SILENCIAR)

El nuevo wheel PRICE y el wheel TCO de F5.3 necesitan ambos **el mismo archivo físico `eios/core/models.py`**. Aunque inicialmente sus bytes sean idénticos, dos distribuciones que reclaman la misma ruta no se pueden instalar/desinstalar de modo confiable en un mismo entorno (colisión de titularidad de archivos).

**Política F5.4:**

- ✅ PRICE solo; ✅ PRICE + `eios-kernel`, siempre en entornos independientes del vertical `eios-mvp`.
- ✅ TCO solo y TCO + `eios-kernel` siguen validados por F5.3.
- ❌ **PRICE + TCO en un mismo entorno: NO COMPATIBLE EN ESTA VERSIÓN.** El verificador exige detectar exactamente la ruta compartida, compara sus bytes y activa un guard fail-closed. No intenta una instalación conjunta que aparente éxito.
- ❌ PRICE + `eios-mvp`: tampoco recomendado por rutas y contratos solapados.
- La identidad de empresa provista por el consumidor **no** equivale a autenticación; solo un intake/evidencia admitido puede convertir datos en hechos de trabajo.

**Siguiente unidad propuesta F5.5:** separar el contrato compartido C0 en una distribución de contratos única, usada como dependencia por los wheels PRICE y TCO, con migración compatible, sin copias de `PurchaseOperation`, y verificaciones aisladas `kernel + contratos + PRICE + TCO`. No basta con declarar una dependencia de metadatos: hay que eliminar físicamente el archivo duplicado de los wheels y probar migración.

## 5. CERRAR → MATERIALIZAR → CI

F5.4 exige CI completa SUCCESS en HEAD exacto de PR, auditoría de diff, merge controlado, CI postintegración SUCCESS sobre SHA exacto de `main`, manteniendo ruta operativa bloqueada.

Al cerrar solo se podrá afirmar:
- `price_optional_procurement_distribution=VERIFIED`;
- `price_kernel_coinstallation=VERIFIED`;
- `price_documentary_fail_closed=VERIFIED`;
- `price_tco_coinstallation=BLOCKED_BY_SHARED_C0_MODELS`;
- `price_cross_domain_neutrality=NOT_PROVEN`.

La portabilidad del Motor **no exige convertir PRICE en un sistema que elija o apruebe precios por defecto**.

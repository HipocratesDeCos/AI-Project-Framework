# EIOS — F4.3 · DISTRIBUCIÓN INDEPENDIENTE DEL MOTOR

**Fecha:** 2026-11-16  
**Base:** main @ 1983fa9ac34adcc4429d4e136507d8f5885a84b1 (PR #599; F4.2.2 cerrada; CI postmerge #43933964231 SUCCESS).  
**Estado:** implementación candidata en rama; el cierre exige pruebas reales y CI de la PR, seguidas de CI postmerge.  
**Meta:** un artefacto Python instalable **sin distribuir EIOS Compras** y sin crear otro ejecutor.

## 1. DISEÑAR — FRONTERA DEL ARTEFACTO

La distribución anterior eios-mvp incluye eios.* y openpyxl; por tanto no constituye un motor portable. El núcleo físico eios/core contiene módulos de Compras, por lo que NO se incluye en bloque.

Se adopta una distribución nueva, eios-kernel 0.1.0, con **solo dos módulos canónicos**:

- eios/kernel/execution.py: ejecución neutral ya estabilizada en F4.2.1.
- eios/parameters/center.py: contrato del Centro de Parámetros independiente de SQL, aplicación y modelos de Compras.

La distribución utiliza el espacio de nombres Python eios y conserva sus rutas públicas actuales. No se incluye eios/parameters/__init__.py, porque actualmente importa resolution, company_resolution_api y version_binding, que a su vez dependen de eios.core.models y otros contratos todavía no extraídos. La API portable de configuración es explícitamente eios.parameters.center, **no** la importación pública completa de eios.parameters.

Se excluyen eios.core, eios.company_*, eios.frontend, eios.finance, eios.rules, eios.pricing, eios.parameters.local_finance_version_source y demás aplicaciones e integraciones. No se altera ningún cálculo, modelo de compras, contrato del Centro existente, firma, prueba antigua ni fuente histórica. El puente heredado de F4.2.2 queda intacto en eios-mvp y físicamente fuera de este wheel.

## 2. AUDITAR — CONSTRUCCIÓN SIN COPIAR IMPLEMENTACIONES AL REPOSITORIO

- packaging/eios-kernel/pyproject.toml define la identidad del paquete, Python >=3.11 y exclusivamente pydantic>=2,<3 como dependencia de ejecución.
- tools/build_eios_kernel_distribution.py construye una carpeta temporal PEP 517 **a partir de los archivos canónicos** existentes, audita todas sus importaciones Python mediante AST y rechaza cualquier import interno eios.* nuevo, incluso antes de construir.
- Tras crear el wheel se audita el contenido real del ZIP: exactamente los dos módulos, un METADATA válido y una única dependencia Pydantic.
- No se guarda una segunda copia permanente de execution.py. No se modifica el pyproject.toml de eios-mvp. El wheel de eios-kernel es una **distribución independiente para entornos independientes**, no se recomienda instalarlo junto a eios-mvp mientras este último siga instalando el mismo path de módulos.

Comandos del repositorio en Python 3.11+:

    python -m pip install "setuptools>=64" "wheel>=0.42"
    python tools/build_eios_kernel_distribution.py --output dist/kernel
    python tools/verify_eios_kernel_distribution.py --wheel-dir dist/kernel

El segundo verificador crea un entorno virtual nuevo sin site-packages globales, instala el wheel con dependencias, abandona el directorio del repositorio y ejecuta un flujo tipado de un dominio ajeno a Compras. Verifica ausencia de eios.core, del adaptador financiero y de openpyxl/streamlit, y confirma que QTG sigue bloqueado y que ningún resultado obtiene autoridad de decisión.

## 3. DEPURAR — PRUEBAS Y LIMITACIONES

tests/test_f4_3_kernel_distribution.py cubre manifiesto de fuentes, copias exactas, imports prohibidos, inspección de wheels adversarios, dependencias adicionales y conservación del proyecto anterior.

La ejecución aislada real se incorpora a .github/workflows/tests.yml tras las regresiones Python y los tres controles SQL previos.

**Límites expresos:**
- Este wheel acredita solo el kernel técnico y el contrato básico de configuración. La lectura histórica con versión y evidencia depende todavía de eios.core.models y **no se anuncia como API genérica portable**.
- La procedencia continúa en manos de los adaptadores; el núcleo mantiene provenance_status=UNVERIFIED_ADAPTER_RESPONSIBILITY, decision_authority=False, operational_path=FORBIDDEN.
- No se autoriza ejecución operacional, firma, autenticación ni integración con un ERP.
- F4.4 debe demostrar dos consumidores realmente independientes instalando el **mismo wheel**. Que un smoke test aislado pase no basta para cerrar portabilidad multi-proyecto.

## 4. AUDITAR 2 Y CRITERIOS DE CIERRE

Requisitos: CI de PR SUCCESS (suite Python, SQL C0, Versioning, Centro de Parámetros, build y smoke en venv), diff acotado, revisión del wheel real, merge controlado y CI postmerge SUCCESS sobre SHA exacto.

Solo entonces: standalone_kernel_distribution=VERIFIED; legacy_eios_mvp_unchanged=VERIFIED; cross_project_portability=NOT_PROVEN hasta F4.4.

**No marcar F4.3 cerrada por la mera creación del PR.**

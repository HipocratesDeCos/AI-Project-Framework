# EIOS — F5.10 · KIT DE INCORPORACIÓN Y CERTIFICACIÓN TÉCNICA PORTABLE

**Fecha:** 17/11/2026. **Baseline:** `main @ d2c958f578c00b07fcdf618360cf47ce08191366` (F5.9 cerrada y CI postintegración #44052611603 SUCCESS).  
**Estado de este documento:** candidato. El cierre exige CI de PR en SHA exacto, merge y CI postintegración en el SHA exacto de `main`.

## 1. DISEÑAR — OBJETIVO CONCRETO

F5.9 ya había demostrado **un tercer proyecto** (mantenimiento industrial, además de Compras y Ventas) instalado con cuatro módulos neutrales independientes. Su prueba aún se preparaba desde el repositorio EIOS. F5.10 materializa un **artefacto transferible** que un desarrollador puede extraer y validar fuera del repositorio, sin modificar los módulos internos del Motor.

Producto: `EIOS_F5_10_Neutral_Onboarding_Kit.zip`.

**Contenido admitido:** `manifest.json`, `requirements.lock`, `certify_deployment.py`, `README.md` y `wheels/` con cuatro wheels neutrales existentes, el ejemplo externo `eios-maintenance-example==0.1.0` y dependencias binarias Pydantic para la plataforma de construcción. El kit **no** incluye el código del repositorio, PRICE, TCO, modelos de Compras, UI, SQL, documentos reales ni credenciales.

## 2. AUDITAR — DISTRIBUCIÓN FÍSICA Y CIERRE DE DEPENDENCIAS

Se reutilizan los generadores y auditores ya verificados, sin duplicar algoritmos ni volver a empaquetar módulos a mano:

- `eios-kernel==0.1.0`
- `eios-input-contracts==0.1.0`
- `eios-capability-catalog==0.1.0`
- `eios-catalog-governance==0.1.0`

El consumidor sintético de mantenimiento continúa como distribución independiente. `tools/build_f5_10_release_kit.py` verifica los wheels anteriores y construye el del consumidor desde su fuente canónica F5.9. Durante la **construcción** descarga las ruedas binarias de `pydantic>=2,<3` y dependencias transitivas admitidas, registrando versiones exactas, rutas, tamaños y SHA-256 en un manifiesto. Genera `requirements.lock` con las versiones y el hash específico de **cada wheel**, incluidos los de terceros.

**Importante:** la construcción no es hermética entre fechas porque la resolución inicial de Pydantic puede cambiar. El **ZIP resultante sí fija exactamente los bytes que instalará** y se verifica sin consultar la red. No se debe equiparar esta reproducibilidad de instalación con una compilación reproducible bit a bit en distintas fechas y máquinas.

El ZIP es **específico de plataforma y versión menor de Python**; el de CI corre en Ubuntu con Python 3.12. Para Windows, construir el ZIP en Windows; no alterar etiquetas de plataforma para instalar wheels de otra arquitectura.

## 3. DEPURAR — INSTALADOR EXTERNO, SIN REPOSITORIO Y SIN RED

`tools/f5_10_certify_deployment.py` se distribuye dentro del ZIP como `certify_deployment.py`. **Solo utiliza librería estándar** hasta la creación del entorno; no importa módulos EIOS ni archivos del repositorio.

Operación:

1. Valida estructura, formato, propósito sintético, inventario y ausencia de ruedas/archivos extra, ruta de cada wheel, hashes, tamaño, nombre/versión extraída de `METADATA`, Python/plataforma compatibles y correspondencia exacta del archivo `requirements.lock`.
2. Si no hay errores, crea un entorno virtual **nuevo** en una ubicación elegida y fuera del propio ZIP.
3. Instala desde `wheels/` con `pip --no-index --find-links --require-hashes --only-binary=:all:`. No se permite descargar de índices ni buscar dependencias no presentes.
4. Ejecuta `pip check`, comprueba las versiones instaladas, los hashes de **todos** los módulos Python neutrales y del proyecto externo y constata que no estén instalados módulos específicos de Compras.
5. Invoca el consumidor desde fuera del checkout con `python -I`; exige `PARTIALLY_COMPLETED` por evidencia de inspección faltante y, tras una deshabilitación autorizada **solo sintéticamente**, `COMPLETED` de la capacidad técnica restante. Comprueba el bloqueo de autorizaciones ajenas, versiones obsoletas, permisos insuficientes y manipulación de una copia del historial.
6. **Solo tras superar** el procedimiento escribe `technical_certification.json`, con versión de plataforma/Python, distribuciones, SHA del manifiesto, evidencia del ejemplo y `production_authorized=false`, `operational_path=FORBIDDEN`.

El certificador rechaza reutilizar una carpeta de salida existente para no sobrescribir ni confundir evidencia anterior.

## 4. AUDITAR 2 — TAMPER Y LIMITACIONES REALES

`tools/verify_f5_10_release_kit.py` descomprime de forma controlada el ZIP, rechaza nombres de archivo inseguros, duplicaciones, enlaces simbólicos y tamaños excesivos, ejecuta el certificador **empaquetado** en **dos entornos nuevos independientes** y exige resultados idénticos.

Ejecuta además casos negativos, antes de crear un entorno:

- modificar bytes de un wheel, con hash antiguo;
- alterar `requirements.lock`;
- eliminar un wheel del inventario;
- añadir un wheel o paquete no declarado;
- falsificar el propósito del manifiesto;
- entregar una huella de manifiesto externa incorrecta.

`tests/test_f5_10_release_kit.py` incluye verificaciones unitarias de manifiesto y plataforma, rutas inseguras de ZIP, módulos neutrales, referencias documentales y rechazo de paquetes ajenos. La CI conserva la suite completa Python/SQL y F4/F5.3–F5.9.

**Límites y amenazas no resueltas:**

- Los SHA-256 **no son firmas digitales**. Si alguien controla tanto los binarios como el manifiesto, puede recalcularlo. Para defenderse de ello se permite comparar `--expected-manifest-sha256` contra una huella entregada por un **canal independiente confiable**, que F5.10 no provisiona.
- No se autentica al responsable empresarial ni se certifica un sistema productivo. El `AuthorizationGrant` del ejemplo es sintético.
- No se ensayan datos operacionales reales, persistencia SQL multiusuario, Kubernetes, contenedores, red ni tolerancia a fallos distribuidos.
- Una instalación completada valida el **ejemplo incluido**, no otros paquetes arbitrarios. El proceso para un nuevo proyecto se especifica en el README, pero requerirá reglas propias, pruebas adversarias propias y autorización real por su sistema externo.

## 5. CERRAR → MATERIALIZAR → CI

Comandos para construir el ZIP en la plataforma de destino desde una copia autorizada del repositorio:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_input_contracts_distribution.py --output dist/inputs
python tools/build_eios_capability_catalog_distribution.py --output dist/catalog
python tools/build_eios_catalog_governance_distribution.py --output dist/governance
python tools/build_f5_10_release_kit.py --kernel-dir dist/kernel --inputs-dir dist/inputs --catalog-dir dist/catalog --governance-dir dist/governance --output dist/release-kit
python tools/verify_f5_10_release_kit.py --kit-dir dist/release-kit
```

Después de extraer el ZIP, sin repositorio:

```powershell
python .\certify_deployment.py --kit .
python .\certify_deployment.py --kit . --output ..\eios-certificacion-f510
```

La CI anexa el ZIP como artefacto **EIOS-F5-10-Neutral-Onboarding-Kit**, con retención de 14 días, después de superar la prueba de los dos despliegues aislados. No se publican credenciales ni documentos de empresas.

## 6. CRITERIO DE CIERRE Y CONTINUIDAD

La unidad será **CERRADA** si el flujo completo supera GitHub Actions sobre el HEAD exacto de PR, el diff no modifica módulos canónicos o de negocio cerrados, la PR se fusiona y el mismo flujo supera CI sobre el SHA exacto de `main`.

**F5.10 acredita** la posibilidad técnica de transferir e instalar en otra ubicación un paquete modular neutral, ejecutar un proyecto de ejemplo independiente y detectar incoherencias de versión o archivos antes de instalar.

**NO acredita** operaciones reales ni certificación completa de seguridad, autenticación de proveedores/usuarios, confianza criptográfica en el distribuidor, portabilidad Windows mediante la CI Ubuntu o admisión comercial de nuevas empresas.

**Próximo frente sugerido después de F5.10:** contrastar un adaptador externo real (p. ej., datos de una empresa obtenidos con autorización) y separar formalmente: certificación de instalación, validez documental, permisos de usuarios y admisión operativa. Evitar reinventar el Motor o duplicar reglas ya cerradas.

# EIOS · KIT DE INCORPORACIÓN TÉCNICA F5.10

**Alcance:** demostración sintética de instalación modular y de integración de un nuevo proyecto. **No es una autorización operativa ni una certificación de seguridad empresarial.**

Este kit agrupa los cuatro módulos EIOS neutrales, un consumidor independiente de mantenimiento y las ruedas binarias Pydantic necesarias para **instalar sin conexión a Internet** en la **misma combinación de sistema operativo, arquitectura y versión menor de Python con la que se construyó**. No contiene el repositorio, PRICE, TCO, bases de datos, credenciales ni módulos de Compras/Ventas.

## INSTALACIÓN Y COMPROBACIÓN

El ZIP contiene `manifest.json`, `requirements.lock`, `certify_deployment.py`, esta guía y la carpeta `wheels/`. Extraiga el contenido en un directorio nuevo, **no dentro de una copia del repositorio EIOS**.

En **PowerShell**, desde el directorio donde haya extraído el ZIP:

```powershell
python .\certify_deployment.py --kit .
python .\certify_deployment.py --kit . --output ..\eios-certificacion-f510
Get-Content ..\eios-certificacion-f510\technical_certification.json
```

En Linux/macOS:

```bash
python3 certify_deployment.py --kit .
python3 certify_deployment.py --kit . --output ../eios-certificacion-f510
cat ../eios-certificacion-f510/technical_certification.json
```

El segundo comando crea un entorno virtual nuevo, instala **solo** las ruedas hash-bloqueadas del kit con `--no-index --require-hashes`, verifica `pip check`, versiones y los bytes de cada módulo importado y ejecuta el proyecto de mantenimiento sintético. Rechaza una carpeta de salida ya existente.

**Resultado esperado:** `status=TECHNICAL_ONBOARDING_PASS`, `production_authorized=false`, `operational_path=FORBIDDEN` y la demostración de mantenimiento con una capacidad completada y otra sin evaluar por falta documental.

Si el sistema operativo, la arquitectura o la versión menor de Python son distintos, el certificador **bloquea** la instalación. El kit de CI se construye para Ubuntu y Python 3.12; para utilizar Windows, se debe **construir otro kit sobre Windows** (véanse los comandos de desarrollo siguientes) y superar sus pruebas allí. No cambie las etiquetas de plataforma ni el manifiesto para evitar este control.

El manifiesto y los archivos están unidos por hashes SHA-256, pero **no están firmados**. Si un tercero puede alterar el paquete completo, puede recalcular las huellas. Para verificar contra un inventario obtenido por un canal independiente de confianza, añada:

```powershell
python .\certify_deployment.py --kit . --expected-manifest-sha256 <SHA256_CONFIRMADO_EXTERNAMENTE>
```

La comprobación de hashes detecta incoherencias del paquete recibido; no acredita identidad del proveedor ni autoriza operaciones.

## INCORPORAR UN PROYECTO NUEVO

1. Cree **su propio paquete Python** fuera de `eios/` y defina un modelo Pydantic con sus campos empresariales. El ejemplo `eios_maintenance_example` es una muestra autónoma, no una plantilla de reglas económicas.
2. Declare dependencias exactas: `eios-kernel==0.1.0`, `eios-input-contracts==0.1.0`, `eios-capability-catalog==0.1.0` y `eios-catalog-governance==0.1.0` (más Pydantic). No instale `eios-mvp` en el mismo entorno de estos paquetes independientes.
3. Declare el `KernelContext` completo; registre cada capacidad con `CapabilityInputSpec` y `CapabilityInputEnvelope`, exactamente el modelo y la versión de esquema que su proyecto admite. Cree productores propios con resultados técnicos `KernelCapabilityResult`.
4. Defina un `CapabilityCatalog` con versiones explícitas de capacidades y compatibilidad de esquemas. **No** aplique una compatibilidad automática por numeración o fechas.
5. Implemente **fuera del Motor** un proveedor real de autenticación y autorización para la función que emite `AuthorizationGrant`. El ejemplo incluido utiliza un aprobador **sintético** exclusivamente para pruebas.
6. Registre selecciones de versiones mediante `commit_catalog_change`; use `load_governed_state` y `bind_governed_plan` para preparar invocadores y `execute_kernel` para ejecutar. Verifique que el Motor conserva `decision_authority=False` y `operational_path=FORBIDDEN`.
7. Construya un nuevo kit para su paquete **y sus propias reglas/adaptadores**, audite las dependencias y los hashes, pruebe los cambios de esquema y versión, revocaciones, proyectos ajenos y ausencia de evidencia documental. **F5.10 solo certifica automáticamente el consumidor de ejemplo incluido**; no concede un sello automático a paquetes externos arbitrarios.

## CONSTRUIR EL KIT EN LA PLATAFORMA DE DESTINO

Sobre una copia autorizada de EIOS actualizada a F5.10, con Python y `pip`:

```powershell
python -m pip install "setuptools>=64" "wheel>=0.42"
python tools/build_eios_kernel_distribution.py --output dist/kernel
python tools/build_eios_input_contracts_distribution.py --output dist/inputs
python tools/build_eios_capability_catalog_distribution.py --output dist/catalog
python tools/build_eios_catalog_governance_distribution.py --output dist/governance
python tools/build_f5_10_release_kit.py --kernel-dir dist/kernel --inputs-dir dist/inputs --catalog-dir dist/catalog --governance-dir dist/governance --output dist/release-kit
```

**La preparación** requiere descargar Pydantic y sus dependencias binarias. **La instalación del ZIP ya construido** no requiere acceso a la red: se bloquea `pip --index` y las ruedas están incluidas. No se han validado instaladores gráficos, servidores de producción, Docker multiusuario ni distribución en Windows mediante la CI de Ubuntu.

## SIGNIFICADO DEL CERTIFICADO

El archivo `technical_certification.json` prueba únicamente que ese paquete instaló las versiones y los archivos declarados, que el consumidor sintético ejecutó los controles previstos y que la ruta operacional sigue prohibida. Contiene la huella del manifiesto y la versión de plataforma/Python. No es evidencia de aprobación de un usuario real, autenticación de documentos, prueba de resistencia frente a un atacante ni decisión de compra, venta o mantenimiento.

**No copie este certificado sintético a otro proyecto para considerarlo certificado.** Cada nueva aplicación exige su propia validación del adaptador y de las fuentes.

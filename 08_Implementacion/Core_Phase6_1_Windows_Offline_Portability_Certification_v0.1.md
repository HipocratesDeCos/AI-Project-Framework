# EIOS — F6.1 · CERTIFICACIÓN DEL KIT NEUTRAL EN WINDOWS

**Fecha:** 17/11/2026. **Baseline:** `main @ bb4313bcaf49574642473a429e3a53d60eba0c97` (F5.10 integrada, CI de main #44055955050 SUCCESS).
**Estado:** EN VALIDACIÓN. Cerrar exclusivamente tras CI de PR SUCCESS sobre HEAD exacto, revisión de alcance, merge y CI postmerge SUCCESS en `main`.

## 1. DISEÑAR — QUÉ SE CIERRA

F5.10 entrega un ZIP neutral instalable **sin red** y certifica dos instalaciones físicas aisladas en Ubuntu/Python 3.12. Este resultado **no certifica Windows**: el ZIP incorpora ruedas binarias construidas para el SO, arquitectura y versión menor de Python del constructor. F6.1 introduce una prueba específica en un ejecutor real de GitHub Actions `windows-latest`, con Python 3.12.

**Objetivo:** que un nuevo proyecto Windows pueda recibir el mismo núcleo neutral y una evidencia técnica de incorporación reproducible, sin recurrir al repositorio durante la instalación.

## 2. AUDITAR — MANTENER INTACTO EL MOTOR

Solo se añade un trabajo a `.github/workflows/tests.yml`: `f6_1_windows_portability`.

- **Dependencia:** `needs: test`; el trabajo Windows solo comienza cuando pasan todos los controles anteriores de Linux, incluidas pruebas Python, SQL, regresiones PRICE/TCO, catálogo, gobierno, tercer dominio y F5.10.
- **Construcción Windows:** crea desde el código canónico los cuatro wheels neutrales de kernel, contratos de entrada, catálogo y gobierno. No crea ruedas de Compras, Ventas, PRICE ni TCO.
- **ZIP específico:** reaprovecha `tools/build_f5_10_release_kit.py`. La resolución y descarga de dependencias se ejecutan en Windows; el paquete no se disfraza como multiplataforma.
- **Certificación:** reaprovecha `tools/verify_f5_10_release_kit.py` para extraer el ZIP fuera del checkout, realizar **dos instalaciones offline independientes**, contrastar recibos y rechazar manipulación del paquete/manifest/lock.
- **Identidad:** exige en el manifiesto `platform=win32`, `python_minor=3.12`, arquitectura igual al ejecutor y propósito `SYNTHETIC_TECHNICAL_ONBOARDING_ONLY`.
- **Artefacto:** `EIOS-F6-1-Windows-Onboarding-Kit-Python312` (retención de 14 días). Su ZIP interno conserva el nombre F5.10 ya certificado; el identificador exterior evita confundir plataformas.

Este trabajo de CI y este documento **no alteran** `eios/`, `tools/f5_10_*`, contratos, algoritmos financieros, admisión, autoridades ni bases de datos.

## 3. DEPURAR — CRITERIOS FAIL-CLOSED

| Caso | Condición obligatoria |
| --- | --- |
| Alguna regresión Linux/SQL falla | Windows no puede declarar cierre del workflow. |
| Un wheel se altera, falta o se añade | El preflight falla antes de crear un entorno. |
| El lock o el manifiesto se altera | No se emite certificación. |
| Una instalación descarga paquetes de Internet | Prohibido por `--no-index` y `PIP_NO_INDEX=1` en el certificador. |
| El SO, la arquitectura o Python menor son diferentes | Rechazo explícito del preflight. |
| Las dos instalaciones difieren | No se publica como verificado el resultado de F6.1. |
| Se intenta tomar una decisión operativa | `production_authorized=false` y `operational_path=FORBIDDEN` siguen obligatorios. |

## 4. AUDITAR 2 — EVIDENCIA A COMPROBAR

1. Ejecución `EIOS Tests` de la PR en su SHA exacto, con **dos trabajos verdes**: `test` (Ubuntu/SQL) y `f6_1_windows_portability` (Windows).
2. Resultado Windows `F5_10_PORTABLE_EXTERNAL_DEPLOYMENT_SUCCESS`, con dos instalaciones y casos adversarios en un Windows real del runner.
3. Manifiesto Windows/Python 3.12 coherente con el ejecutor.
4. Artefacto Windows retenido y separado del artefacto Ubuntu existente.
5. Diff limitado a CI y documentación; **ningún módulo canónico modificado**.
6. CI postmerge de ambos trabajos sobre el SHA exacto de `main`.

Hasta completar ambas CI, el estado es **candidato**, no `CERRADA`.

## 5. USO EN OTRO PROYECTO WINDOWS

En la ejecución correcta de GitHub Actions, descargar el artefacto llamado `EIOS-F6-1-Windows-Onboarding-Kit-Python312`, extraer el ZIP interno en una carpeta nueva fuera del repositorio y usar **Python 3.12** en Windows de arquitectura compatible:

```powershell
python .\certify_deployment.py --kit .
python .\certify_deployment.py --kit . --output ..\eios-certificacion-windows
Get-Content ..\eios-certificacion-windows\technical_certification.json
```

Solo usar `--expected-manifest-sha256` si la huella fue recibida **por un canal realmente independiente y confiable**. Los SHA-256 no equivalen a una firma digital.

**Límite:** `windows-latest` certifica el sistema del runner para Python 3.12 y su arquitectura; no cubre otras versiones de Python, procesadores, estaciones de trabajo con políticas empresariales restrictivas, autenticación de usuarios, datos reales ni sistemas productivos.

## 6. CONTINUIDAD DESPUÉS DE F6.1

**F6.2 — Contrato de incorporación de un adaptador empresarial externo:** diseñar una entrada tipada neutral (origen, entidad, versión, calidad, identidad empresarial, ámbito de ejecución y permisos) y un conjunto de pruebas sintéticas adversarias que no permitan presentar documentos inventados como reales. No integrar información comercial real hasta contar con una empresa, autorización y custodia adecuadas. F6.2 no debe duplicar el Motor ni promover unilateralmente la ruta operacional.

# EIOS — F4.4 · DOS CONSUMIDORES INDEPENDIENTES, UN ÚNICO MOTOR

**Fecha:** 2026-11-16
**Baseline:** main @ c577a9fdb6986c717de7625ccc651ac190e431ea, F4.3; CI postmerge #43936516644 SUCCESS.
**Unidad:** F4.4 — demostrar reutilización del artefacto eios-kernel, sin reescribir cálculos de Compras/Ventas ni cambiar el motor.
**Estado:** candidato sujeto a CI completa y reconciliación postmerge.

## 1. DISEÑAR — QUÉ SE DEBE DEMOSTRAR

Un único wheel eios-kernel 0.1.0, compilado **una vez** desde los archivos canónicos existentes, se instala en dos entornos Python limpios e independientes. Cada consumidor define su contrato de negocio y sus invocadores; ambos usan los mismos bytes para eios.kernel.execution y eios.parameters.center.

- **Consumidor Compras:** modelo tipado PurchaseDraft con cantidad, artículo, proveedor y precio de referencia. Catálogo local ficticio BUY-RESERVE, política purchase-policy-v1. Dos capacidades locales demuestran ejecución completa, traza y aislamiento del payload.
- **Consumidor Ventas:** modelo tipado SalesOffer con cliente, artículo, oferta y plazo. Catálogo local ficticio SALES-TERMS, política sales-policy-v7. Dos capacidades locales demuestran resultado parcial con evidencia pendiente sin transformarlo en decisión autorizada.

**Son dos programas/adaptadores mínimos de prueba, no las aplicaciones EIOS Compras y EIOS Ventas de producción.** No se simulan cuentas anuales reales, autorizaciones empresariales ni un ERP; ninguno de los programas toma decisiones económicas. La evidencia permite sostener portabilidad del **núcleo técnico publicado en el wheel**, no afirmar que el sistema EIOS completo ya sea universal.

## 2. AUDITAR — ESTRUCTURA DEL CAMBIO

- tests/fixtures/f4_4_consumers/purchasing/consumer.py: ejecutable autónomo de Compras.
- tests/fixtures/f4_4_consumers/sales/consumer.py: ejecutable autónomo de Ventas.
- tools/verify_f4_4_two_consumers.py: utiliza el auditor de wheel de F4.3, calcula SHA256 de cada módulo dentro del wheel, crea dos directorios y dos venvs separados, instala el **mismo path de wheel** en ambos y ejecuta cada programa con Python aislado (-I) desde fuera del checkout.
- tests/test_f4_4_two_consumers.py: contratos estructurales, identidades y políticas distintas, imports permitidos y respuestas adversarias.
- .github/workflows/tests.yml: incorpora nueva prueba tras suite Python, SQL y construcción/instalación F4.3.

Se mantiene sin cambios el código bajo eios/, el pyproject.toml del proyecto anterior, las reglas, precios, decisiones, datos empresariales y SQL.

## 3. DEPURAR — CRITERIOS CONTRACTUALES

El verificador exige para **cada** consumidor:

1. Versión 0.1.0 del paquete eios-kernel instalado en un entorno virtual propio, sin instalaciones globales, sin PYTHONPATH, fuera del repositorio.
2. SHA256 de eios/kernel/execution.py y eios/parameters/center.py **idénticos a los bytes del mismo wheel original**.
3. Identidad de proyecto y versión de política distintas por consumidor. La versión y la política no son inferidas por el Motor: se suministran en el contexto y el plan.
4. Rechazo de una entrada con empresa extranjera **en el adaptador**, antes de invocar (el kernel NO autentica empresas).
5. Rechazo de decision_id o scenario_id contradictorios **en el kernel** y bloqueo previo de QTG, O1 y capacidades ausentes.
6. Aislamiento por copia del payload entre capacidades; una mutación local no altera la siguiente capacidad ni el objeto de entrada.
7. Centro de Parámetros aportado por puertos locales propios, selección del contexto propio y rechazo de cambios sin autorización.
8. decision_authority=False, operational_path=FORBIDDEN y ausencia de módulos de la aplicación, openpyxl y fuentes financieras particulares.

La salida del verificador incluye estados técnicos diferenciados: COMPLETED para Compras y PARTIALLY_COMPLETED para Ventas por evidencia sintética pendiente. Ninguno equivale a aceptación comercial o autorización operacional.

## 4. AUDITAR 2 — LÍMITES Y RIESGOS QUE PERSISTEN

- **Portabilidad de la biblioteca técnica:** demostrable con dos procesos independientes y un wheel único si la CI culmina SUCCESS. No autoriza anunciar capacidad empresarial multiempresa completa.
- **Autenticación y autorización:** no se acreditan ni se derivan de project_id; los controles de alcance de los fixtures son solo puertas de adaptación de demostración. Se requiere fuente de identidad confiable para uso real.
- **Módulos fuera del paquete mínimo:** PRICE, FIN, TCO, Rules, Decision Twin, versionado histórico ligado a eios.core.models, Quality Gate, frontend, integraciones ERP/SQL, adaptadores financieros. No son portables automáticamente por esta fase.
- **Distribución:** no se ha publicado a índice privado ni a PyPI; el wheel se construye y prueba en CI. No instalar junto a eios-mvp en el mismo entorno mientras se compartan rutas físicas bajo eios.
- **Aislamiento:** se comprueban dos instalaciones y se rechazan datos ajenos en cada adaptador; no constituye una auditoría de ciberseguridad ni prueba de aislamiento entre organizaciones en infraestructura compartida.
- **Soporte a dominios nuevos:** exige adaptadores que suministren contratos Pydantic, invocadores, fuentes y políticas; el Motor no puede decidir por sí solo.

## 5. CIERRE → MATERIALIZAR → CI

Para cerrar F4.4, exigir:

1. Diff limitado a pruebas, fixtures, documentación y CI; sin retocar algoritmos cerrados.
2. CI PR SUCCESS sobre HEAD exacto: regresión Python, validaciones SQL, F4.3 y F4.4.
3. Merge controlado, seguido de CI main SUCCESS sobre SHA exacto.
4. Registrar: kernel_technical_cross_domain_portability=VERIFIED y full_eios_business_portability=NOT_PROVEN.

**Conclusión condicionada:** dos consumidores mínimos pueden demostrar que el mismo núcleo técnico puede integrarse en tipos de proyecto diferentes, sin duplicar el motor. Esto no cierra automáticamente las capacidades sectoriales de EIOS.

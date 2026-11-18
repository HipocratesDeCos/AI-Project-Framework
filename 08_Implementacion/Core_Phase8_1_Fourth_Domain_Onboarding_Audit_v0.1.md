# EIOS — F8.1 · AUDITORÍA DE ARRANQUE DE UN CUARTO DOMINIO

**Fecha:** 2026-11-18  
**Baseline inmutable de auditoría:** `main @ a4bfbd0a08d7755c5f24e136f421f09c6821d351`  
**Estado:** AUDITORÍA DOCUMENTAL COMPLETADA; PR/CI Y VALIDACIÓN PRÁCTICA PENDIENTES.  
**Clasificación:** evidencia de diseño, NO certificación técnica del cuarto dominio ni cierre formal de F8.1.

## 1. Pregunta y límite

¿Puede crearse y certificarse un cuarto consumidor independiente utilizando solamente las distribuciones neutrales EIOS 0.1.0 y documentación pública, sin copiar código del repositorio ni alterar el núcleo? Distinguir **instalación y certificación del kit** de **certificación del proyecto externo**. No generar un dominio artificial para justificar trabajo ni crear una nueva API por estética.

Esta revisión es de código y documentación a SHA exacto; **no equivale a haber ejecutado una prueba externa fresca**.

## 2. Elementos cubiertos que NO deben reimplementarse

- F4: `eios.kernel.execution` y consumidores externos.
- F5.6: `eios.input_contracts`, modelo tipado e identidad contextual.
- F5.7: `eios.capability_catalog`, versiones explícitas y compatibilidad de esquemas sin inferencia por SemVer.
- F5.8: `eios.catalog_governance`, selección autorizada y ledger por proyecto.
- F5.9: consumidor de mantenimiento empaquetado, instalado y ejecutado independientemente.
- F5.10/F6.1: kit offline específico de plataforma, Python minor, hashes y ejecución del ejemplo.
- F6.2–F6.11: adaptadores externos, controles sintéticos de ciclo y cierre de la fase.
- F7.1–F7.6: API, matriz `REJECT_UNLISTED`, migración, deprecación, identidad y cierre.

La combinación neutral certificada sigue siendo exactamente `eios-kernel==0.1.0`, `eios-input-contracts==0.1.0`, `eios-capability-catalog==0.1.0` y `eios-catalog-governance==0.1.0`.

## 3. Evidencia y hallazgo

**E1 — distribución portable existente.** `tools/build_f5_10_release_kit.py` agrupa las cuatro ruedas neutrales, dependencias bloqueadas y `eios-maintenance-example==0.1.0`; preserva un manifiesto de hashes. `tests/fixtures/f5_10_deployment_kit/README.md` enseña a crear un proyecto separado, pero declara explícitamente: F5.10 certifica automáticamente **solo** el consumidor de ejemplo.

**E2 — certificador anclado a un consumidor específico.** `tools/f5_10_certify_deployment.py` exige `SAMPLE = {"eios-maintenance-example": "0.1.0"}`, define `MODULES` con el paquete de mantenimiento, rechaza inventarios extra y ejecuta `python -I -m eios_maintenance_example.consumer`. Cambiar el nombre del ejemplo dentro de un ZIP no da un certificado válido.

**E3 — consumidor de referencia no es plantilla universal.** `tests/fixtures/f5_9_maintenance_consumer/src/eios_maintenance_example/consumer.py` tiene modelo, productores, versiones, catálogo y autorizador de prueba sintético propio. Copiarlo cambiando identificadores no acredita independencia del dominio.

**Hallazgo F8.1-H01 (material; alcance: herramientas EXTERNAS, no núcleo):** no existe en el procedimiento F5.10 un certificador parametrizable y neutral para el paquete del cuarto dominio. La validación de F5.10 **no puede reutilizarse como un certificado de cualquier consumidor** sin diseñar controles propios. Es una limitación reconocida, no una regresión ni defecto de F5.10.

**Hallazgo F8.1-H02 (mejora condicional):** el procedimiento de construcción/admisión de un nuevo consumidor está documentado por pasos, pero no constituye una plantilla de validación automatizada que detecte de forma estandarizada imports privados, dependencia del checkout, versiones sin fijar y falso aumento de autoridad. Comprobar primero si los verificadores de F5.9 y F6.2 ya pueden cubrirlo mediante una reutilización externa pequeña antes de añadir herramientas.

## 4. Separación de responsabilidades

| Necesidad | Titular |
|---|---|
| Ejecución, contratos, catálogo, gobierno | APIs neutrales existentes; NO modificar |
| Empaquetado e instalación de wheels neutrales | F5.10/F6.1; NO duplicar |
| Modelo, productores, reglas y trazabilidad del caso | Nuevo vertical |
| Autenticación real, firmas, identidad documental y admisión operacional | Infraestructura y autoridad externa; NO simular |
| Validación técnica de un consumidor independiente arbitrario | Posible utilidad EXTERNA post-F7 sujeta a prueba |

Queda excluido crear un gestor dinámico de plugins, API nueva, SDK invasivo, instalación online, auto-descubrimiento, permisos reales, certificación productiva, UI, nuevas capacidades de negocio, 0.2.0 artificial o alteraciones de F4–F7.

## 5. Test de decisión para la siguiente unidad (no ejecutado aún)

**P1 — positivo:** un nuevo paquete con un modelo y dos productores que no representan Compra/Venta/Mantenimiento, dependencias exactas y imports públicos, instala fuera del checkout y ejecuta datos exclusivamente sintéticos con estados observables sin autorizar decisiones.

**P2 — negativo:** rechazar dependencia de `eios.core`, `eios.pricing`, `eios.tco`, `eios.company_app`, importación desde checkout, versión mezclada o no declarada, esquema no registrado y productor faltante.

**P3 — adversario:** rechazar reutilización de ledger cruzado, autorizador ausente/booleano/scope incorrecto, modificación de wheel/lock/manifest, elevación de `decision_authority` o `operational_path`, e intento de presentar certificado de mantenimiento como certificado del cuarto dominio.

**P4 — independencia:** entradas y resultados idénticos en dos directorios limpios separados, sin estado, datos ni código compartidos de verticales; Windows Python 3.12 y Linux cuando exista paquete compatible para cada plataforma.

**P5 — no-regresión:** mantener F4–F7 íntegros; `git diff -- eios/` vacío; verificar hashes e identidad de release certificada.

**Decisión binaria después de ejecutar:** si se obtiene P1–P5 reutilizando herramientas y documentación existentes, NO implementar F8.2. Si un paso común resulta imposible sin reconstruir lógica de verificación o acceder al checkout, justificar el mínimo verificador EXTERNO reutilizable y únicamente entonces abrir implementación.

## 6. Estado y autorización

- `production_authorized=false`
- `decision_authority=false`
- `real_pilot_admitted=false`
- `operational_path=FORBIDDEN`
- `REFERENCE_OPERATIONAL_SIMULATION` sigue siendo sintético.

**No declarar F8.1 cerrada sin PR integrada, CI premerge en SHA exacto y CI postmerge de main en SHA exacto**. La integración de este documento no acredita por sí sola P1–P5. Mantener una única prioridad: evitar duplicar las barreras ya certificadas, documentar el problema y comprobarlo de forma externa.



## 8. EXPERIMENTO EXTERNO DEL CUARTO DOMINIO (CANDIDATO)

Se materializa un cuarto consumidor sintético, **gestión energética**, con dos capacidades propias (observación de demanda máxima y comprobación de soporte documental del contador). No contiene reglas de Compras, Ventas ni Mantenimiento.

Artefactos del candidato:
- `tests/fixtures/f8_1_energy_consumer/pyproject.toml`, `src/eios_energy_example/{__init__,consumer}.py`: distribución independiente `eios-energy-example==0.1.0`.
- `tools/verify_f8_1_fourth_domain.py`: **harness experimental específico de F8.1**, NO certificador general.
- `.github/workflows/tests.yml`: ejecuciones Linux y Windows sobre el ZIP F5.10 **sin modificar su contenido**, montando un lock externo para la nueva distribución.

El experimento verifica SHA del wheel frente a fuente, imports públicos por AST, instalación `pip --no-index --require-hashes`, `pip check`, ejecución `python -I` en dos entornos separados, invariantes `decision_authority=false` / `operational_path=FORBIDDEN`, entradas no documentadas, autorización sintética falsa, ledger cruzado, cambio de esquema sin gobernar, capacidad no registrada, binding ausente y ledger alterado.

El **ejemplo de mantenimiento no se instala** en los entornos del cuarto dominio: se extraen los wheels del kit intacto y se utiliza un lock nuevo (externo al kit) que fija solo el motor neutral, dependencias y consumidor energético. No se reemite `technical_certification.json` de F5.10 como certificación del cuarto dominio.

**Limitación experimental importante:** rechazar un wheel alterado se comprueba mediante divergencia SHA-256 del binario; la validación no acredita autenticidad de un distribuidor independiente. La ejecución repetida prueba aislamiento técnico del consumidor, no concurrencia ni producción multiusuario.

El experimento requiere CI premerge completa; los resultados de la prueba deben obtenerse de los pasos F8.1 específicos, no inferirse del PASS de las regresiones históricas. **No declarar F8.1 cerrada sin evidencia de Linux y Windows, auditar fallo/depuración y CI postmerge cuando corresponda**.

## 7. AUDITAR 2 — CONTRASTE DE VERIFICADORES REALES

La auditoría de segunda pasada comprueba directamente la implementación de los verificadores existentes:

- `tools/verify_f5_9_third_domain.py` fija `PROJECT_NAME = "eios-maintenance-example"`, `PROJECT_MODULES` y `FIXTURE_ROOT`; su función `check()` exige `consumer == "maintenance"`, un ledger de nombre concreto y estados predeterminados. **No es una CLI genérica de certificación**, aunque algunas funciones auxiliares puedan ser reutilizables tras una adaptación externa auditada.
- `tools/verify_f6_2_external_company_adapter.py` fabrica y ejecuta el adaptador de referencia `eios_company_adapter_example.demo`, espera dos empresas sintéticas, dos ledgers y una firma de resultado específica. **No valida paquetes empresariales arbitrarios**.
- `tools/f5_10_certify_deployment.py` fija `SAMPLE`, `MODULES` y la ejecución de mantenimiento, rechazando wheels adicionales o inventarios no listados. Mantener intacto este certificador es necesario para que F5.10 conserve su identidad de release.
- `.github/workflows/tests.yml` conserva pruebas Linux y Windows de esas fronteras previas; una CI verde no prueba automáticamente las nuevas pruebas P1–P5.

**AUDITAR 2 (documental): PASS con hallazgo acotado F8.1-H01; NO acredita todavía el ejercicio P1–P5.**

### Decisión de mínimo cambio

Existe una justificación delimitada para **estudiar** un verificador externo del consumidor, reutilizando los auditores de wheels y el mecanismo de instalación hash-locked, sin tocar `eios/` ni modificar el kit F5.10. Su eventual materialización sigue condicionada a probar primero que un cuarto dominio realmente necesita ese verificador. Evitar un SDK nuevo, loader dinámico o generador de proyectos antes de esa evidencia.

### Gate actual de cierre

- Auditoría documental 1: completada.
- Auditoría documental 2: completada, con resultado condicionado.
- P1–P5 sobre un cuarto dominio: **NO EJECUTADAS**.
- CI premerge del documento: ejecución #44264440227 SUCCESS sobre `d2a7bcfe4a6e87f12945308281f18fef540a0f08` (SHA anterior a este apéndice; requiere nueva CI).
- Estado de F8.1: **ABIERTA — NO CERRAR**.

No afirmar que una prueba de mantenimiento o de adaptador equivale a un cuarto dominio ni promover ninguna autorización operacional.

# EIOS — ACTA DE CIERRE TÉCNICO DEL MOTOR NEUTRAL 0.1.0

**Fecha:** 18/11/2026  
**Estado:** CANDIDATO DE ACEPTACIÓN; **NO CERRADO** hasta CI pre-merge y post-merge del SHA exacto.  
**Baseline de desarrollo auditada:** `main @ 80b0c368bd3da8b4c369a0f9ae9a6c85258d8167`  
**Alcance:** núcleo técnico neutro, distribuciones públicas 0.1.0, contratos, release/governance y portabilidad sintética. **No** implica disponibilidad o seguridad operativa empresarial.

## 1. Objeto

Congelar el alcance de la versión **EIOS Motor neutral 0.1.0**. Conservar las fronteras y las APIs ya aprobadas y trasladar toda nueva funcionalidad sectorial a paquetes consumidores externos. No abrir una F8.2 por defecto ni reescribir F4–F7.

## 2. Inventario de versión del Motor

Conjunto **exacto**, certificado como baseline; la coincidencia de SemVer por sí sola no implica compatibilidad:

- `eios-kernel==0.1.0` → `eios.kernel.execution`.
- `eios-input-contracts==0.1.0` → `eios.input_contracts`.
- `eios-capability-catalog==0.1.0` → `eios.capability_catalog`.
- `eios-catalog-governance==0.1.0` → `eios.catalog_governance`.

Políticas: `REJECT_UNLISTED` para combinaciones no registradas; migraciones en entornos paralelos con rollback anchor; deprecaciones solo según estado y evidencia; identidades de código fuente y artefacto de release separadas por plataforma. La release candidate se identifica como `EIOS_MOTOR_RC_0_1_0`. Una RC técnica no equivale a producción.

## 3. Base de evidencias — fases cerradas

| Tramo | Evidencia |
|---|---|
| F4 | Kernel neutral, aislamiento y ejecución independiente |
| F5.1–F5.10 | Paquetes modulares; consumidores Procurement, Sales y Maintenance; ZIP offline con hashes |
| F6.1–F6.11 | Portabilidad Windows, adaptadores externos, custodia sintética, safe-stop, idempotencia y cierre formal |
| F7.1–F7.6 | API pública, matriz de compatibilidad, política de migración, lifecycle, identidad, cierre formal |
| F8.1 | Cuarto dominio externo `eios-energy-example==0.1.0`, con dos capacidades, bindings, ledger y escenarios adversarios |

Prueba EIOS cuarto dominio: PR [#629](https://github.com/HipocratesDeCos/AI-Project-Framework/pull/629), candidato `e3ced473d998f744250d98dd3bb7c5db462f8f6a`, CI PR `#44273502407` **SUCCESS** en Linux y Windows Python 3.12; merged `main @ 80b0c368bd3da8b4c369a0f9ae9a6c85258d8167`. La CI post-merge sobre el SHA de main **no estaba disponible para lectura en esta auditoría**: no inferir SUCCESS de una consulta vacía.

## 4. Fronteras que siguen expresamente prohibidas

- `synthetic_only=true`.
- `production_authorized=false`.
- `decision_authority=false`.
- `real_pilot_admitted=false`.
- `operational_path=FORBIDDEN`.

Ni la certificación offline ni la aprobación de un ledger con un *test double* sintético crean autoridad real. Las fuentes de datos, verificación documental, autenticación empresarial, permisos y pilotos operacionales corresponden a componentes externos y aprobaciones específicas futuras.

## 5. Auditoría final: comprobaciones de aceptación

- [x] `main` coincide con el merge conocido de F8.1 (consulta del 18/11/2026).
- [x] PR #629 merged; F8.1 Linux y Windows con CI premerge positiva.
- [x] Sin cambios en `eios/` derivados de F8.1 (comparación `a4bfbd0...80b0c368`).
- [x] Workflows conservan gates F7.6, F8.1, Linux y Windows.
- [x] Identificados los cuatro contratos y políticas públicas sin ampliar versión.
- [ ] Confirmar `SUCCESS` de **push/CI post-merge** sobre `80b0c368bd3da8b4c369a0f9ae9a6c85258d8167` con URL e ID del run.
- [ ] Confirmar CI pre-merge de **esta PR de cierre** en su candidato SHA exacto.
- [ ] Integrar PR de cierre solo tras CI satisfactoria, revisión del diff y sin modificar `eios/`.
- [ ] Confirmar CI de **push post-merge** sobre el nuevo HEAD exacto `main` de esta PR.
- [ ] Registrar SHA final y URL del run postmerge en el acta/hilo de PR y declarar aceptación formal del Motor.

**REGLA DE BLOQUEO:** no cambiar este estado a CERRADO ni presentar EIOS 0.1.0 como finalizado en ausencia de esos dos gates post-merge verificables. No inventar IDs de runs.

## 6. Decisión funcional y congelación

No se detecta necesidad demostrada de modificar las APIs del Motor para incorporar un cuarto proyecto. El desarrollo funcional del **núcleo neutral 0.1.0** se considera **completo para su alcance sintético y técnico**. Se aplica congelación de superficie pública: futuros cambios requieren evidencia de defecto, fallo de compatibilidad o una release explícitamente gobernada. No modificar en caliente ni elevar autoridad.

El harness de F8.1 es una verificación **de ejemplo**, no un certificador genérico productivo. La compatibilidad futura de versiones nuevas sigue sin probarse en una migración real, dado que solo 0.1.0 está admitida.

## 7. Siguiente paso después del cierre

Iniciar **un proyecto consumidor externo** sobre EIOS 0.1.0, fuera de `eios/`, eligiendo un caso empresarial acotado (por ejemplo, Compras o Tesorería). El primer entregable del consumidor será un **contrato de entrada, un caso de datos sintéticos realista y una validación completa de un flujo con resultados comprensibles**. Este trabajo no es una nueva fase del Motor.

La habilitación de pilotos reales y producción requiere un programa de admisión y seguridad empresarial separado. No deben confundirse el cierre técnico del Motor, la funcionalidad de una app y la aceptación productiva.

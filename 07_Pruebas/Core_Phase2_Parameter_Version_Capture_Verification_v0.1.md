# EIOS — FASE 2.4 · VERIFICACIÓN DE COHERENCIA DE CAPTURA DE PARÁMETROS

**Fecha:** 2026-11-16  
**Base:** fase 2.3, PR #583 → PR #582 → PR #581; `main @ 2c2807c` intacta.  
**Unidad:** comparación de una selección empresarial completa y documentada con un `DecisionInputPackage` (DIP) ya capturado.

## 1. Hallazgo de arquitectura y límite verificable

La configuración histórica del `ParameterConfigurationCenter` contiene `configuration_id`, empresa, parámetro, valor, tipo, unidad y vigencia. **No contiene una asociación persistida, autenticada y consultable con `DecisionContext.parameters_version`.**

`ResolvedConfiguration` adjunta la versión del contexto de la ejecución. El `DecisionInputPackage` conserva una copia inmutable de la selección y una huella de contenido SHA-256, pero el propio contrato aclara que esa huella **no autentica** el productor, la empresa ni el origen del histórico.

Por ello **no es legítimo** concluir «esta configuración perteneció realmente a la versión V en el registro autorizado» solo porque coincidan cadenas, valores y hashes. La fase 2.4 no fabrica esa garantía ni crea un segundo centro/registro de versiones.

## 2. Implementación acotada y reutilizable

Nuevo módulo `eios/parameters/version_capture_verification.py`, exportado por `eios.parameters`:

```python
verify_company_parameter_capture(
    lookup: CompanyParameterLookup,
    package: DecisionInputPackage,
    context: DecisionContext,
) -> ParameterCaptureVerification
```

La función es **pura de solo lectura** y falla de modo cerrado mediante `ParameterCaptureVerificationError.code` cuando observa:

1. Discrepancia en decisión, escenario, versión, snapshot de datos o versión de reglas entre `DecisionContext`, `CompanyParameterLookup` y DIP.
2. Empresa o fecha efectiva diferente.
3. Diferencia de selección, duplicación, orden ambiguo o captura con configuraciones ausentes.
4. Ausencia de cobertura documental completa de F2.3.
5. Cambio en cualquier campo de `ResolvedConfiguration` — incluido valor, identidad, unidad, tipo, vigencia y versión — respecto a la copia DIP.
6. Evidencia de parámetro ausente, adicional, duplicada o distinta de la evidencia validada por F2.3. Las evidencias no paramétricas de la compra pueden permanecer en el DIP.

Los fallos no ofrecen valores por defecto, no activan parámetros y no ejecutan reglas. La comparación del contexto incluye `rules_version`, disponible en el DIP y el contexto de referencia aunque F2.3 no lo exponía en su informe.

El resultado conserva la huella del **DIP completo**, no produce un nuevo `parameters_version` ni asigna otro identificador de versión a cada parámetro.

## 3. Declaraciones de confianza deliberadamente restringidas

Tras superar todos los controles:

- `capture_status=MATCHED_DIP_CAPTURE_ONLY`: toda la selección documental coincide con una misma captura.
- `version_attestation=HISTORICAL_VERSION_NOT_ATTESTED`: ninguna autoridad histórica independiente fue consultada.
- `origin_attestation=NOT_EXTERNALLY_AUTHENTICATED`.
- `decision_authority=False`, `operational_path=FORBIDDEN`.

Esta fase **no demuestra atomicidad transaccional** del Centro: el contrato expone lecturas por parámetro, y el DIP puede producirse durante cambios concurrentes de origen. Solo se acredita correspondencia con el material realmente capturado. Un productor con acceso a los objetos de entrada puede recrear tanto DIP como evidencia con versiones inventadas; la coincidencia no es una firma.

## 4. Pruebas de aceptación

`tests/test_parameter_version_capture_verification.py` cubre:

- Dos parámetros válidos, y selección equivalente en empresa distinta con IDs de configuración compartidos.
- Cambio de valor manteniendo `configuration_id`, selección parcial y orden distinto.
- Versión de parámetros, versión de reglas y `data_snapshot_id` divergentes.
- Diferencia de fecha de aplicación.
- Evidencia ausente o sustituida.
- Separación de copias, huella DIP estable y no activación automática.
- Aislamiento de las fases 1 y 2.1–2.3: no se modifica código de cálculo, SQL, UI, QTG, PRICE, FIN, STK, MGE, PAG o autorización.

**Cierre técnico condicionado:** la fase puede aprobarse únicamente cuando la ejecución completa de CI y SQL Server sobre el HEAD de su rama resulte satisfactoria, se inspeccione el diff y la PR siga en borrador.

## 5. Continuidad pendiente — auténtica atestación histórica

Para alcanzar `HISTORICAL_VERSION_ATTESTED` es necesario identificar **una fuente existente de autoridad**, independiente del llamante, capaz de demostrar de manera inmutable y verificable que el conjunto completo de configuraciones estuvo asociado a `parameters_version`, con empresa, instante de corte y procedencia. El `ParameterConfigurationCenter` actual no ofrece ese contrato. No debe activarse esa etiqueta ni modificarse la política de admisión hasta incorporar y auditar esa capacidad dentro de la arquitectura canónica, sin duplicar el versionado.

No hay certificación del Motor completo ni autorización operacional derivada de esta fase.

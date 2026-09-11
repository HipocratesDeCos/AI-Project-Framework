# EIOS — E2E EXECUTION BOUNDARY · IMPLEMENTATION CONTRACT

**Versión:** 1.0
**Estado:** CERRADO Y MATERIALIZADO — AUDIT 2 SUPERADA / CI EJECUTABLE VERIFICADA
**Baseline original de implementación:** `7ba6a19883aed29506d4374fbabe51644bfaac09`
**Snapshot ejecutable certificado:** `9cffd1cbb939f1b3fc480ceca1cb462f71a37cdb`
**CI ejecutable:** GitHub Actions #554 — SUCCESS

## 1. Alcance

Materializar exclusivamente la capa de coordinación entre U1/U1.1 y capacidades analíticas previamente autorizadas. No sustituye O1, O2, O3 ni ningún motor.

## 2. Catálogo autorizado

La invocación requiere un catálogo explícito `capability -> invoker`. La ausencia de una capacidad en el catálogo impide iniciar el plan completo. No existe descubrimiento dinámico.

El catálogo es externo a la lógica de negocio del boundary y debe ser inmutable durante una ejecución. O1 no forma parte del catálogo analítico.

La implementación materializada preserva un snapshot del catálogo para cada ejecución, de forma que una mutación externa posterior no modifica qué invocador utiliza un plan ya iniciado.

## 3. Plan

`ExecutionPlan` debe contener exclusivamente capacidades declaradas en el catálogo y conservar su orden contractual. El plan se valida completamente antes de invocar la primera capacidad.

No se permite modificar el plan durante la ejecución ni derivar orden desde resultados.

La implementación materializada verifica antes de la primera invocación que todas las capacidades requeridas existan y sean invocadores válidos. O1 queda bloqueado como capacidad del plan analítico.

## 4. Identidad y contexto

La ejecución recibe `PurchaseOperation` y `DecisionContext` canónicos. Deben coincidir `decision_id` y `scenario_id`.

Se preservan `rules_version`, `parameters_version` y `data_snapshot_id`. No se crea `decision_version`, `decision_fingerprint` ni otra identidad paralela.

La política/versión de ejecución autorizada debe quedar explícita en el contexto contractual de la ejecución y no puede inventarse por defecto.

Cada capacidad recibe una copia aislada de las entradas canónicas; una capacidad no puede alterar el contexto observado por otra capacidad ni los objetos originales del caller.

## 5. Estados

El resultado final usa los estados técnicos del contrato E2E. Una ejecución síncrona puede devolver únicamente el estado terminal; `READY/RUNNING` son estados conceptuales de transición y no deben fingirse como resultados finales.

Reglas terminales:

- `BLOCKED`: no se inicia ninguna capacidad por precondición estructural conocida.
- `FAILED`: fallo técnico explícito.
- `PARTIALLY_COMPLETED`: resultado parcial, no evaluable, no terminal o bloqueado de una capacidad después de iniciar.
- `COMPLETED`: todas las capacidades del plan producen resultados contractualmente completos y disponibles.

Una capacidad que declare `COMPLETED` sin `result_available=True` no constituye un resultado completo.

Ningún estado técnico expresa una conclusión empresarial.

## 6. Errores

Una excepción de un invocador termina la coordinación como `FAILED` y conserva los resultados ya obtenidos. No se convierte en conclusión de negocio.

El motivo técnico debe ser reproducible y limitado a la información necesaria; no se ejecuta recuperación heurística ni reintento implícito.

`FAILED` exige una causa explícita. La identidad de la capacidad devuelta debe coincidir con la capacidad planificada; una discrepancia es un fallo de integridad técnica.

## 7. Resultados y trazabilidad

Cada invocador debe devolver `CapabilityExecution`. El boundary conserva orden, estado, `trace_references` y `unresolved_items`.

Las referencias se agregan de forma determinista. O1 continúa siendo responsable de `DecisionSupportPackage` y no forma parte del catálogo analítico del boundary.

## 8. Inmutabilidad y determinismo

La entrada, el plan y el catálogo no se mutan como consecuencia de la coordinación. Con la misma entrada, catálogo, plan y versiones, el orden y la clasificación técnica deben ser reproducibles.

La materialización protege además las entradas de una capacidad frente a mutaciones producidas por otra capacidad durante la misma ejecución.

## 9. Exclusiones

Sin persistencia, SQL, API pública, SSO, compra real, negociación automática, scoring, ranking, optimización, selección, recomendación, aprendizaje o modificación de reglas/parámetros/RDM.

La integración O4→O2→O3 queda fuera de este contrato.

## 10. Aceptación

La implementación debe demostrar como mínimo:

1. plan válido y orden estable;
2. catálogo incompleto bloquea antes de ejecutar;
3. identidad inconsistente rechazada;
4. excepción técnica produce `FAILED`;
5. estados parciales no se transforman en conclusión empresarial;
6. trazas y limitaciones preservadas;
7. entrada/plan/catálogo inmutables;
8. política/versión explícitas;
9. ausencia de ranking, scoring, selección u optimización;
10. compatibilidad de resultados con O1.

**Este contrato no amplía la autoridad empresarial de EIOS.**

## 11. Estado de materialización

La implementación está materializada en:

```text
eios/core/execution_boundary.py
tests/test_execution_boundary.py
```

Audit 2 final se registra en:

```text
08_Implementacion/E2E_Execution_Boundary_Audit_2_v1.0.md
```

El cierre se registra en:

```text
08_Implementacion/E2E_Execution_Boundary_Closure_v1.0.md
```

El snapshot ejecutable `9cffd1cbb939f1b3fc480ceca1cb462f71a37cdb` satisface la matriz contractual y obtuvo `EIOS Tests #554: SUCCESS`.

Los cambios posteriores de esta rama hasta el cierre son exclusivamente documentales y requieren CI propio antes de integración.

## 12. Dictamen

**E2E EXECUTION BOUNDARY v1.0: CERRADO Y MATERIALIZADO.**

**Audit 2:** SUPERADA — 0 bloqueos.  
**Código:** MATERIALIZADO.  
**Tests:** MATERIALIZADOS.  
**CI ejecutable:** VERIFICADA SATISFACTORIAMENTE.  
**CI de cierre documental:** PENDIENTE antes de integración.  
**Autoridad empresarial nueva:** NINGUNA.

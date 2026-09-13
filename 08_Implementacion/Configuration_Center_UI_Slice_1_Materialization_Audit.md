# EIOS — Configuration Center UI Slice 1 — Materialization Audit

**Fecha:** 2026-09-13  
**Estado:** DEPURADA — PENDIENTE DE CI FINAL

## 1. Objeto

Auditar la implementación materializada contra el contrato cerrado, no solo el diseño previo.

## 2. Hallazgo M1 — errores de lectura no representados explícitamente

La primera materialización de `load_detail()` y `load_history()` delegaba correctamente al backend, pero propagaba `ParameterConfigurationError` como excepción sin conservarla en el estado del controlador.

Esto era más débil que la frontera UI cerrada, que exige error explícito y código trazable.

### Corrección

Se incorporó estado observable al controlador:

- `state`;
- `error_code`.

Las lecturas ahora:

- capturan únicamente `ParameterConfigurationError`;
- retornan `None` ante fallo;
- registran `state = ERROR`;
- preservan el código original;
- no convierten fallo en datos parciales.

Los flujos de cambio registran asimismo sus estados `VALIDATING`, `AWAITING_CONFIRMATION`, `REVALIDATING`, `APPLYING`, `APPLIED`, `FORBIDDEN`, `CONFLICT`, `VALIDATION_FAILED` o `ERROR`.

## 3. Pruebas añadidas

Se añadieron pruebas específicas para:

- fallo de detalle con `PARAMETER_NOT_FOUND`;
- fallo de histórico con `INVALID_COMPANY_SCOPE`;
- conservación de `state` y `error_code`;
- mantenimiento de las pruebas previas de revocación, conflicto y escritura fail-closed.

## 4. Reauditoría

Tras M1:

- no existe acceso directo a catálogo, autorización o repositorio;
- no se fabrican parámetros, empresas ni identidad;
- actor/empresa/parámetro permanecen ligados al contexto;
- la propuesta pendiente no contiene identificadores sustituibles;
- la revalidación previa a escritura permanece obligatoria;
- solo una `Configuration` retornada por el backend puede producir `APPLIED`;
- las lecturas fallidas ya no quedan fuera de la semántica observable de UI.

## 5. Dictamen

**MATERIALIZACIÓN COHERENTE CON EL CONTRATO — SIN BLOQUEADORES CONOCIDOS.**

El cierre físico continúa condicionado a CI SUCCESS pre-merge, reconciliación con `main`, merge protegido por SHA y CI SUCCESS postintegración.

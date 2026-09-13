# EIOS — Configuration Center UI Slice 1 — Audit 1

**Fecha:** 2026-09-13  
**Baseline de diseño:** `1f9e0e7da142db61f75f52c734cc6074f360a119`  
**Dictamen:** APTO PARA DEPURACIÓN — 3 reajustes, 0 bloqueos

## Hallazgos

### A1 — El contexto no demuestra confianza por su nombre
`AuthorizedConfigurationUIContext` no debe presentarse como prueba criptográfica o autenticación. Es un carrier inmutable cuya procedencia debe estar garantizada por el integrador aguas arriba. El controlador debe rechazar campos vacíos, pero no afirmar identidad.

### A2 — La propuesta pendiente debe estar ligada al contexto
Una propuesta validada no puede aceptar `company_id`, `parameter_id` ni `actor` en `confirm_and_apply`. Estos campos deben quedar capturados del contexto original e inmutables para impedir sustitución entre validación y aplicación.

### A3 — Revalidación y apply no deben capturar excepciones como éxito
`ParameterConfigurationError` debe mapearse a un resultado de fallo con código original. Solo una `Configuration` efectivamente retornada por `apply_change` puede producir `APPLIED`.

## Comprobaciones transversales

- `ParameterConfigurationCenter` sigue siendo autoridad ejecutable de validación/aplicación.
- `apply_change` ya revalida y delega atomicidad al repositorio; el slice no reemplaza esa defensa.
- no se introducen catálogo enumerado, identidad, permisos, SQL, reglas, CRC, excepciones ni simulación.
- no se toca ningún componente decisional cerrado.

**Resultado:** incorporar A1–A3 y pasar Audit 2 antes de código.

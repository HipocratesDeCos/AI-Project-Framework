# EIOS — UI Field ↔ Component Mapping v0.1

**Estado:** DISEÑO
**Baseline:** `9f5db07d55b9665286f6a8ef821ad7046b232a98`

Define la representación visual de los campos canónicos sin alterar semántica, autoridad o estado.

## Tipos base
`text`, `number`, `currency`, `date`, `datetime`, `select`, `textarea`, `badge`, `readonly_metric`, `evidence_list`, `config_control`.

## Reglas
- `INPUT`: editable según validación.
- `READONLY`: visible y no editable.
- `CALCULATED`: solo lectura y requiere autoridad de cálculo.
- `DECISION`: salida controlada.
- `TRACE`: trazabilidad no editable.
- `CONFIG`: edición restringida.

## Salvaguarda STK
La representación visual no autoriza cálculo de M01–M10 ni parámetros pendientes.

## Gate
DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI.

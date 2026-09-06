# EIOS — UI Field ↔ Component Mapping v0.1

**Estado:** DISEÑO
**Baseline:** `9f5db07d55b9665286f6a8ef821ad7046b232a98`
**Fecha:** 2026-09-06

## 1. Propósito

Definir cómo cada campo canónico del Registro Maestro se representa en la pantalla de interacción, sin alterar su semántica, autoridad o estado.

## 2. Tipos de componente autorizados

| Tipo | Uso |
|---|---|
| `text` | Identificadores, nombres y texto corto |
| `number` | Magnitudes numéricas introducidas o mostradas |
| `currency` | Importes monetarios |
| `date` | Fechas |
| `datetime` | Fecha/hora de trazabilidad |
| `select` | Catálogos cerrados |
| `textarea` | Explicaciones y observaciones |
| `badge` | Estados/resultados |
| `readonly_metric` | Métricas calculadas o de contexto |
| `evidence_list` | Evidencia y trazabilidad |
| `config_control` | Parámetros de configuración autorizados |

## 3. Regla de mapeo

Cada campo debe conservar su `Field_ID`, nombre canónico y estado (`INPUT`, `READONLY`, `CALCULATED`, `DECISION`, `TRACE`, `CONFIG`). El componente visual nunca cambia la autoridad del campo.

## 4. Reglas por estado

- `INPUT`: editable según las condiciones de validación.
- `READONLY`: visible, no editable por el usuario en la evaluación.
- `CALCULATED`: solo lectura; requiere autoridad para el cálculo correspondiente.
- `DECISION`: salida controlada del motor de evaluación.
- `TRACE`: información de trazabilidad, no entrada de decisión.
- `CONFIG`: editable únicamente dentro del contexto autorizado de configuración.

## 5. Salvaguarda STK

Un campo relacionado con STK puede representarse como `readonly_metric` o `evidence_list` únicamente cuando exista dato autorizado. El mapeo visual no autoriza el cálculo de M01–M10 ni sus parámetros pendientes.

## 6. Catálogo de decisión

El componente de resultado solo puede representar:

1. `COMPRAR`
2. `NEGOCIAR`
3. `COMPRAR CONDICIONADO`
4. `NO COMPRAR`
5. `INFORMACIÓN INSUFICIENTE`

No se admite un sexto resultado ni texto libre como sustituto del estado canónico.

## 7. Regla de implementación

Antes de implementar un componente debe existir correspondencia verificable con un campo canónico o con un elemento de interacción expresamente autorizado por el contrato funcional. No se crean campos implícitos para satisfacer necesidades visuales.

## 8. Gate

Este documento es un artefacto de **DISEÑO**. Debe pasar por AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI antes de considerarse parte del baseline operativo.

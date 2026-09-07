# EIOS — Contrato de Interacción UI v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA
**Baseline:** `254d4962caee1141ab84e91cf715e7939b2e5b6b`
**Fecha:** 2026-09-07

## 1. Propósito

Definir el contrato observable entre la pantalla de interacción y los componentes autorizados: eventos, validaciones, estados y transiciones. No implementa lógica de negocio ni crea nuevos campos.

## 2. Autoridad

El `UI_Field_Registry_v0.1.md` mantiene la autoridad semántica de los campos. `UI_Field_Component_Mapping_v0.2.md` mantiene la autoridad sobre la representación componente-campo. `UI_Interaction_Screen_Specification_v0.1.md` mantiene la autoridad sobre la estructura y orden de la pantalla.

Este contrato únicamente formaliza la interacción permitida entre esas capas.

## 3. Eventos de usuario

| Evento | Condición | Acción UI | Resultado permitido |
|---|---|---|---|
| `INPUT_CHANGE` | Campo editable | Actualizar valor de presentación | Validación del campo |
| `INPUT_BLUR` | Campo editable abandonado | Ejecutar validación visual | Error o valor válido |
| `SUBMIT_EVALUATION` | Entradas mínimas válidas | Solicitar evaluación autorizada | `EVALUATING` |
| `CANCEL` | Flujo activo | Abandonar edición/evaluación | Estado previo seguro |
| `RETRY` | Error técnico recuperable | Reintentar operación autorizada | `EVALUATING` |
| `EXPAND_SECTION` | Sección disponible | Mostrar contenido | Sin cambio semántico |
| `COLLAPSE_SECTION` | Sección expandida | Ocultar contenido | Sin cambio semántico |
| `VIEW_TRACE` | Trazabilidad disponible | Mostrar evidencia | Sin edición |

## 4. Validación

La validación de UI solo puede comprobar restricciones ya definidas por el dominio o por el tipo de campo. No puede crear reglas de negocio nuevas.

Clases mínimas:

- `REQUIRED`: entrada obligatoria ausente.
- `TYPE`: tipo/formato incompatible.
- `RANGE`: valor fuera de rango autorizado.
- `DEPENDENCY`: dependencia de entrada ya definida no satisfecha.
- `SYSTEM`: error técnico.

## 5. Transiciones

```text
INITIAL
  ↓ entrada
INPUT_REQUIRED
  ↓ entradas válidas
READY
  ↓ SUBMIT_EVALUATION
EVALUATING
  ├── resultado válido ──→ RESULT
  ├── datos insuficientes → INSUFFICIENT_DATA
  └── error técnico ─────→ ERROR

ERROR ── RETRY ──→ EVALUATING
```

`CANCEL` no produce un resultado de negocio.

## 6. Componentes y eventos

- `INPUT`: puede emitir `INPUT_CHANGE` e `INPUT_BLUR`.
- `READONLY`: no emite cambios de valor.
- `CALCULATED`: no es editable y solo presenta valores autorizados.
- `DECISION`: solo presenta decisiones autorizadas.
- `TRACE`: solo lectura.
- `CONFIG`: edición restringida conforme a la configuración autorizada.

## 7. Errores y datos insuficientes

`ERROR` representa una condición técnica o de validación; `INSUFFICIENT_DATA` representa ausencia de información suficiente para continuar. Ninguno de ambos estados crea campos auxiliares ni sustituye un `Field_ID`.

## 8. STK

La interacción UI nunca puede convertir un valor STK en autorización para calcular M01–M10. Si falta metodología autorizada, el componente debe limitarse a la representación del dato disponible o a su estado de indisponibilidad.

## 9. Trazabilidad

Las acciones relevantes deben conservar referencia al contexto de evaluación y a la versión de los componentes cuando dicha trazabilidad esté definida por el sistema. `VIEW_TRACE` es exclusivamente de consulta.

## 10. Salvaguardas

Este contrato no crea `Field_ID`, `Test_ID`, fórmulas, reglas de negocio ni nuevas autoridades. La implementación posterior deberá respetar el contrato sin ampliar su alcance.

**Siguiente gate: AUDITAR.**
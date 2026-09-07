# EIOS — Contrato Implementable de UI v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA
**Baseline:** `fe57fc8d34cfc6f99ccad5887dfd3a5db62af5fe`
**Fecha:** 2026-09-07

## 1. Propósito

Transformar las autoridades UI cerradas en una especificación directamente implementable, sin introducir semántica de negocio, nuevos campos, fórmulas ni autoridad paralela.

## 2. Fuentes de autoridad

1. `UI_Field_Registry_v0.1.md` — identidad y semántica de campo.
2. `UI_Field_Component_Mapping_v0.2.md` — componente autorizado.
3. `UI_Interaction_Screen_Specification_v0.1.md` — estructura y orden.
4. `UI_Interaction_Functional_Contract_v0.1.md` — eventos, estados y transiciones.

La implementación no puede elevar una capa inferior sobre una autoridad superior.

## 3. Contrato de componente

Cada componente implementado debe poder trazarse a un `Field_ID` o a un componente estructural autorizado por la especificación de pantalla.

| Tipo | Entrada | Salida | Editable | Persistencia semántica |
|---|---|---|---|---|
| INPUT | usuario | valor validado | Sí | Según Field_ID |
| READONLY | sistema | valor presentado | No | Según Field_ID |
| CALCULATED | sistema autorizado | resultado | No | Según Field_ID |
| DECISION | evaluación autorizada | decisión | No | Según catálogo |
| TRACE | sistema | evidencia/contexto | No | Según trazabilidad |
| CONFIG | usuario autorizado | parámetro | Restringida | Según configuración |

## 4. Props mínimos

Los componentes deben recibir únicamente propiedades necesarias para su función autorizada:

- identidad del campo/componente;
- valor o estado autorizado;
- estado de validación cuando corresponda;
- habilitación/visibilidad derivada del estado de UI;
- metadatos de trazabilidad cuando estén definidos.

No se introducen props que representen reglas de negocio ocultas.

## 5. Eventos

Los eventos implementables son los definidos por el contrato funcional:

`INPUT_CHANGE`, `INPUT_BLUR`, `SUBMIT_EVALUATION`, `CANCEL`, `RETRY`, `EXPAND_SECTION`, `COLLAPSE_SECTION`, `VIEW_TRACE`.

Cada evento debe tener un único destino funcional autorizado y no puede calcular resultados de negocio directamente desde el componente visual.

## 6. Validación

La UI implementará únicamente las clases autorizadas:

`REQUIRED`, `TYPE`, `RANGE`, `DEPENDENCY`, `SYSTEM`.

Las validaciones `RANGE` y `DEPENDENCY` requieren una restricción preexistente y no pueden inventarse en la capa de presentación.

## 7. Máquina de estados UI

Estados implementables:

`INITIAL`, `INPUT_REQUIRED`, `READY`, `EVALUATING`, `RESULT`, `INSUFFICIENT_DATA`, `ERROR`.

Las transiciones se obtienen exclusivamente del contrato funcional. Los estados son efímeros de UI y no se convierten en `Field_ID`.

## 8. Separación de responsabilidades

```text
Componente visual
      ↓ evento
Controlador de interacción
      ↓
Operación autorizada
      ↓
Resultado / estado UI
      ↓
Renderizado
```

El componente visual no ejecuta reglas de negocio ni fórmulas financieras.

## 9. STK

La implementación puede representar valores STK autorizados, pero ningún componente puede utilizar STK para inferir o generar metodología de M01–M10. Si no existe metodología autorizada, se muestra el estado correspondiente sin cálculo inventado.

## 10. Trazabilidad

Las acciones de evaluación y las salidas relevantes deben conservar las referencias de trazabilidad definidas por el contrato funcional. La UI no puede alterar retrospectivamente la evidencia.

## 11. Criterio de implementación

Una implementación será considerada conforme cuando cada componente, evento, transición y validación pueda remontarse a una autoridad documental existente y no exista comportamiento implícito fuera del contrato.

## 12. Salvaguardas

No se crean `Field_ID`, `Test_ID`, fórmulas, reglas de negocio ni autoridad cuantitativa STK. El contrato es implementable, pero no constituye todavía código de producción.

**Siguiente gate: AUDITAR.**
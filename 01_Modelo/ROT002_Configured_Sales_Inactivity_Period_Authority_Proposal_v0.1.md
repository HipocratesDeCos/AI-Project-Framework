# EIOS — ROT002 Configured Sales-Inactivity Period Authority Proposal v0.1

**Baseline:** `main @ 1287590303b785df976547fd3da38c6f26caad1c`  
**Fecha:** 22/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA / NO VIGENTE  
**Regla afectada:** `R-ROT-002 — Producto sin rotación`  
**Gate:** `ROT-G01`

## 1. Propósito

Proponer una autoridad mínima y explícita para resolver la expresión normativa de `R-ROT-002`:

> “No existen ventas durante el periodo configurado.”

La propuesta no modifica todavía el Catálogo de Parámetros, no cierra `ROT-G01`, no autoriza código y no asigna un valor empresarial por defecto.

## 2. Restricciones heredadas

Se preservan íntegramente:

- `Rotation_Track_A_Methodological_Closure_v0.1.md`;
- `Rotation_Methodological_Audit_2_Final_v0.3.md`;
- `SalesActivityWindowEvidence`;
- ausencia de filas ≠ cero ventas;
- suma neta cero ≠ ausencia de ventas;
- ventana parcial ≠ ventana completa;
- ventas ≠ consumo;
- ventas ≠ demanda;
- rotación ≠ cobertura;
- Track A no aplica excepciones;
- Track A no produce decisión.

## 3. Hallazgo

No existe en el Catálogo MVP ningún parámetro `P-ROT-*`.

Tampoco existe evidencia documental que autorice reutilizar:

- `P-STK-006` — periodo para calcular consumo;
- `P-PYE-001` — horizonte de proyección;
- parámetros PRE/DAT;
- otra ventana temporal de un dominio distinto.

Por tanto, si `R-ROT-002` debe consumir un “periodo configurado” desde el Centro de Parametrización, se requiere un parámetro dedicado o una fuente de configuración alternativa expresamente autorizada.

## 4. Propuesta de identificador canónico

Se propone, sujeto a aprobación humana:

```text
P-ROT-001
```

Nombre propuesto:

```text
Periodo de inactividad de ventas
```

Función exclusiva propuesta:

> Definir la longitud temporal de la ventana utilizada para evaluar `R-ROT-002`.

`P-ROT-001` no gobernaría `R-ROT-001` ni definiría una métrica general de rotación.

## 5. Unidad propuesta

Se propone:

```text
días
```

Razón técnica:

- permite una frontera temporal exacta;
- evita introducir reglas de clipping de meses;
- es compatible con `date` y ventanas inclusivas deterministas;
- permite a cada empresa configurar 30, 90, 180, 365 u otro valor sin cambiar código.

Los valores anteriores son únicamente ejemplos técnicos y **no se autorizan como defaults**.

## 6. Valor empresarial

No se propone valor inicial obligatorio.

Estado propuesto en Catálogo:

```text
Valor inicial: Pendiente / definido por empresa
Estado: Pendiente de validación empresarial
```

El core debe poder existir aunque no haya configuración vigente.

Si el parámetro requerido no está resuelto/evidenciado:

```text
R-ROT-002 → NOT_EVALUABLE
```

Nunca se aplicará un default silencioso.

## 7. Tipo de valor

Se propone:

```text
INTEGER positivo
```

Restricción:

```text
period_days >= 1
```

No se autorizan:

- cero;
- negativos;
- decimales;
- alias textuales;
- conversión implícita desde meses/años.

## 8. Fecha base propuesta

Se propone vincular:

```text
evaluation_date = PurchaseOperation.operation_date
```

Motivo:

- evita crear una segunda fecha de evaluación;
- liga la ventana a la operación exacta;
- permite reproducibilidad.

Esta igualdad es **propuesta**, no autoridad vigente hasta aprobación.

## 9. Semántica de ventana propuesta

Con `period_days` resuelto:

```text
window_end = evaluation_date
window_start = evaluation_date - (period_days - 1 días)
```

La ventana es inclusiva:

```text
window_start <= sale_event_date <= window_end
```

Ejemplo meramente técnico:

```text
period_days = 1
→ window_start = window_end = evaluation_date
```

No se propone ninguna semántica para ventas válidas; esa responsabilidad permanece en `source_semantics_ref`.

## 10. Binding con Centro de Parametrización

La futura materialización deberá consumir:

```text
ResolvedConfiguration(P-ROT-001)
+
Evidence de configuración
```

y exigir coherencia con:

- `DecisionContext.parameters_version`;
- empresa/scope autorizado;
- vigencia en la fecha efectiva aplicable;
- operación/contexto evaluados.

No se acepta un entero desprendido como autoridad.

## 11. Binding con SalesActivityWindowEvidence

La futura evaluación deberá comprobar que el carrier factual corresponde exactamente a:

```text
article_id = PurchaseOperation.article_id
evaluation_date = PurchaseOperation.operation_date
window_start = ventana derivada de P-ROT-001
window_end = PurchaseOperation.operation_date
window_authority_ref = referencia reproducible a la configuración autorizada
```

Además deberá conservar:

- `source_ref`;
- `source_semantics_ref`;
- `completeness_ref`;
- `evidence_refs`;
- `trace_refs`.

## 12. Mapeo factual propuesto hacia R-ROT-002

Sin resolver todavía excepciones:

```text
ZERO_VALID_SALES_DEMONSTRATED
→ condición factual satisfecha

SALES_ACTIVITY_PRESENT
→ condición factual no satisfecha

NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
→ NOT_EVALUABLE
```

No se infiere `FALSE` desde ausencia de evidencia.

## 13. Metadata de la regla

Se conserva literalmente la Matriz de Reglas:

```text
R-ROT-002
Effect: R1 — CONDICIONANTE
Severity: ALTA
Resultado documental: NO COMPRAR salvo excepción
```

Esta propuesta no autoriza escalada R0.

Tampoco implementa excepciones.

La relación exacta entre el resultado documental `NO COMPRAR`, el metadata técnico y futuras excepciones deberá quedar explícita en el contrato de regla antes de materialización.

## 14. Dependencias RDM propuestas

Tras autorización y materialización deberán poder demostrarse, como mínimo:

```text
R-ROT-002
├── PARAMETER → P-ROT-001
├── EVIDENCE  → SalesActivityWindowEvidence
├── CONTEXT/DATA → identidad/fecha de la PurchaseOperation exacta
└── EVIDENCE → configuración resuelta/evidenciada
```

La dependencia de `SalesActivityWindowEvidence` ya está registrada como `EVIDENCE / CONFIRMED`; no debe duplicarse.

## 15. No alcanza

Esta propuesta no resuelve:

- `R-ROT-001`;
- `ROT-G02`;
- `ROT-G03`;
- fórmula de rotación;
- umbral de baja rotación;
- excepciones de `R-ROT-002`;
- fuente empresarial universal de ventas;
- semántica de devoluciones/anulaciones/abonos;
- scoring/ranking;
- decisión humana.

## 16. Gates propuestos

```text
ROT002-PERIOD-G01 → dedicated configuration identity
ROT002-PERIOD-G02 → positive integer days
ROT002-PERIOD-G03 → no default
ROT002-PERIOD-G04 → PurchaseOperation.operation_date binding
ROT002-PERIOD-G05 → inclusive deterministic window
ROT002-PERIOD-G06 → ResolvedConfiguration + Evidence
ROT002-PERIOD-G07 → SalesActivityWindowEvidence exact-window binding
ROT002-PERIOD-G08 → missing/invalid config => NOT_EVALUABLE
```

## 17. Decisión humana requerida

Para convertir esta propuesta en autoridad se requiere aprobar o corregir expresamente:

1. creación de `P-ROT-001`;
2. nombre “Periodo de inactividad de ventas”;
3. unidad `días`;
4. entero positivo;
5. ausencia de default empresarial;
6. `PurchaseOperation.operation_date` como `evaluation_date`;
7. fórmula inclusiva de ventana;
8. alcance exclusivo inicial sobre `R-ROT-002`.

## 18. Estado

**ROT002 Configured Sales-Inactivity Period Authority Proposal v0.1 — PROPUESTA / NO VIGENTE.**

No se modifica código ni catálogo hasta autorización.

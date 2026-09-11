# EIOS — FINANCE BASIC · METHODOLOGICAL DESIGN v0.1

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA  
**Fecha:** 11/09/2026  
**Baseline:** EIOS Vertical MVP  
**Rama de trabajo:** `fin/finance-basic-methodology-v0.1`  
**Ámbito:** Capa 4 — Finanzas Básica

---

## 1. Propósito

Definir la frontera metodológica mínima de la Capa 4 — Finanzas Básica para que EIOS pueda representar y analizar, de forma trazable y sin inventar política financiera, el impacto de una propuesta de compra sobre la situación financiera disponible.

Este documento es un diseño metodológico en auditoría. No constituye todavía contrato técnico ni autoriza implementación cuantitativa.

---

## 2. Autoridades y fuentes de entrada

El diseño se subordina a:

- `00_Gobierno/Matriz_Autoridad_Documental.md`;
- `00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`;
- `01_Modelo/Especificacion_funcional.md`;
- `03_Arquitectura/Architecture_Blueprint.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `04_Reglas/Evidence_Contract.md`;
- `04_Reglas/Rule_Dependency_Matrix.md`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- `02_Parametros/Centro_Parametrizacion.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`.

En caso de discrepancia prevalece la autoridad documental correspondiente.

---

## 3. Frontera de responsabilidad

Finance Basic analiza consecuencias financieras de una propuesta ya identificada.

Puede:

- conservar un snapshot financiero con fecha de referencia;
- representar tesorería evidenciada;
- representar pagos y cobros futuros evidenciados dentro de un horizonte autorizado;
- representar el desembolso o calendario de pago asociado a la propuesta cuando esté evidenciado;
- construir una proyección de tesorería únicamente con componentes cuya inclusión esté autorizada y trazable;
- consumir métricas financieras ya demostradas cuando su metodología no pertenezca a esta capa;
- exponer hechos/resultados analíticos para evaluación posterior de reglas.

No puede:

- inventar saldos, cobros, pagos, vencimientos o financiación;
- asumir que una ausencia equivale a cero;
- fijar parámetros empresariales definitivos;
- crear una fórmula de fondo de maniobra no autorizada;
- crear una fórmula de margen de seguridad financiera no autorizada;
- definir por inferencia la métrica `capacidad financiera prevista`;
- producir `COMPRAR`, `NEGOCIAR`, `COMPRAR CONDICIONADO` o `NO COMPRAR`;
- resolver conflictos entre reglas;
- ejecutar financiación, cobros, pagos o compras;
- transformar alternativas financieras en órdenes operativas.

---

## 4. Principios obligatorios

### FIN-P01 — No data ≠ zero

La ausencia de una magnitud financiera no se sustituye por cero.

### FIN-P02 — Evidencia antes que cálculo

Una magnitud solo interviene cuantitativamente cuando existe evidencia suficiente de su identidad, importe, fecha/periodo y ámbito aplicable.

### FIN-P03 — Temporalidad explícita

Toda proyección debe identificar como mínimo `as_of_date` y el horizonte aplicable.

### FIN-P04 — Hecho ≠ política

Un saldo o flujo observado es un hecho. Un umbral, tolerancia o criterio de suficiencia es política/configuración y debe proceder de su autoridad.

### FIN-P05 — Análisis ≠ regla

Finance Basic produce consecuencias financieras. Las reglas `R-FIN-*` conservan la autoridad sobre su condición, efecto, severidad y resultado.

### FIN-P06 — No decisión

Una consecuencia financiera desfavorable no constituye por sí misma una decisión empresarial.

### FIN-P07 — No compensación implícita

No se compensan riesgos financieros mediante precio, margen, stock u otras señales favorables dentro de Finance Basic. La consolidación pertenece a CRC.

### FIN-P08 — Versionado y reconstruibilidad

Los valores y parámetros consumidos deben poder relacionarse con el `DecisionContext`/snapshot/versiones aplicables.

---

# 5. FIN-M01 — Snapshot financiero

## 5.1 Definición

El análisis parte de un estado financiero identificable para una fecha de referencia.

Debe conservar, cuando exista:

```text
company_scope
as_of_date
data_snapshot_id
currency
source_references
```

El snapshot no implica que todas las magnitudes necesarias estén disponibles.

## 5.2 Invariante

Datos procedentes de fechas o empresas distintas no se fusionan silenciosamente como un único snapshot.

---

# 6. FIN-M02 — Tesorería evidenciada

## 6.1 Definición

`treasury_current` representa la posición de tesorería disponible para el análisis cuando su importe, fecha y fuente están suficientemente evidenciados.

## 6.2 Tratamiento

- dato demostrado → puede utilizarse dentro de su ámbito y fecha;
- dato ausente o insuficiente → no se sustituye por cero;
- datos incompatibles → se conserva la contradicción y no se selecciona silenciosamente uno de ellos.

## 6.3 Límite

FIN-M02 no redefine qué cuentas, instrumentos o saldos componen jurídicamente/contablemente la tesorería. Esa composición requiere autoridad documental o fuente de datos aplicable.

---

# 7. FIN-M03 — Flujos futuros de pago y cobro

## 7.1 Función

Representar obligaciones de pago y cobros previstos que puedan afectar al horizonte financiero de la propuesta.

Cada flujo cuantitativo debe conservar como mínimo:

```text
flow_id
flow_type = PAYMENT | COLLECTION
amount
currency
due_date
source_ref
evidence_state
```

La nomenclatura anterior describe la información mínima conceptual y no constituye todavía un schema técnico.

## 7.2 Controles de configuración existentes

El catálogo reconoce:

- `P-FIN-005` — considerar pagos futuros;
- `P-FIN-006` — considerar cobros previstos.

Ambos mantienen relación compuesta confirmada con `R-FIN-001`.

Su existencia no autoriza a fabricar flujos que no estén evidenciados.

## 7.3 Horizonte

`P-FIN-001` identifica el horizonte de pagos, pero su consumidor individual permanece pendiente de identificación documental en la matriz parámetro↔regla vigente.

Por tanto:

- puede reconocerse como parámetro financiero existente;
- no se asigna en este diseño por inferencia a una regla adicional;
- su función operativa exacta dentro de la metodología queda pendiente de auditoría/autoridad.

---

# 8. FIN-M04 — Impacto financiero de la propuesta

## 8.1 Función

Representar el flujo financiero atribuible a la compra propuesta cuando importe y condiciones temporales estén demostrados.

La compra no se convierte automáticamente en un desembolso inmediato.

Debe respetarse, cuando exista evidencia:

- importe exigible;
- fecha o calendario de pago;
- plazo de pago;
- condiciones de pago;
- descuentos aplicables efectivamente demostrados;
- otros ajustes cuya autoridad ya exista.

## 8.2 Prohibiciones

No se permite:

- inferir una fecha de pago inexistente;
- aplicar un descuento meramente posible como si estuviera concedido;
- asumir financiación no confirmada;
- anticipar o diferir el pago por conveniencia del cálculo.

---

# 9. FIN-M05 — Proyección de tesorería

## 9.1 Relación conceptual de diseño

La arquitectura y el MED exigen analizar:

```text
SITUACIÓN ACTUAL
      ↓
IMPACTO DE LA COMPRA
      ↓
SITUACIÓN PROYECTADA
```

Para tesorería, el diseño propone una composición exclusivamente aritmética sobre hechos previamente autorizados:

```text
projected_treasury
=
current_evidenced_treasury
+ evidenced_inflows_in_scope
- evidenced_outflows_in_scope
- evidenced_purchase_outflows_in_scope
```

**Estado de esta relación:** PROPUESTA METODOLÓGICA SUJETA A AUDITORÍA. No queda autorizada por la mera publicación de este diseño.

## 9.2 Condiciones de evaluabilidad

La proyección solo puede presentarse cuantitativamente cuando las magnitudes necesarias para el alcance elegido estén suficientemente demostradas.

Un flujo desconocido que sea necesario para la proyección no se transforma en cero.

## 9.3 No duplicación

Un mismo pago o cobro no puede incorporarse más de una vez por aparecer en varias fuentes.

---

# 10. FIN-M06 — Fondo de maniobra

## 10.1 Autoridad existente

El catálogo reconoce:

`P-FIN-003 — Fondo de maniobra mínimo`

con relación directa confirmada a `R-FIN-002`.

El MED y la Especificación Funcional exigen considerar fondo de maniobra.

## 10.2 Gap metodológico

La documentación vigente revisada no define dentro de una metodología financiera especializada:

- fórmula autorizada;
- composición de partidas;
- fecha de medición;
- tratamiento del impacto de la compra;
- tratamiento de vencimientos/financiación vinculada.

Por tanto, este diseño **no crea** dicha fórmula.

Hasta que exista autoridad suficiente, Finance Basic solo puede consumir un valor de fondo de maniobra ya demostrado por una fuente/metodología competente; no recalcularlo por inferencia.

---

# 11. FIN-M07 — Margen de seguridad financiera

## 11.1 Autoridad existente

El catálogo reconoce:

`P-FIN-004 — Margen mínimo de seguridad financiera`

con relación directa confirmada a `R-FIN-003`.

## 11.2 Gap metodológico

No se ha demostrado todavía una definición cuantitativa única de la magnitud evaluada contra ese umbral.

No se autoriza inferir que el margen sea automáticamente:

- porcentaje de tesorería;
- porcentaje de liquidez;
- porcentaje de fondo de maniobra;
- diferencia porcentual respecto de cualquier otra magnitud.

Finance Basic no calculará esta métrica hasta que su definición quede autorizada.

---

# 12. FIN-M08 — Capacidad financiera prevista

## 12.1 Autoridad existente

La matriz de parámetros confirma relaciones compuestas:

```text
P-FIN-002 → R-FIN-001
P-FIN-005 → R-FIN-001
P-FIN-006 → R-FIN-001
```

`R-FIN-001` evalúa riesgo de incapacidad de pago.

## 12.2 Gap metodológico

La expresión `capacidad financiera prevista` está reconocida, pero su función cuantitativa completa no está definida de forma especializada en las fuentes revisadas.

No se autoriza identificarla automáticamente con:

- tesorería proyectada;
- liquidez;
- fondo de maniobra;
- saldo neto de flujos;
- ratio creado por implementación.

La metodología deberá cerrar esta identidad antes de un contrato técnico de Finance Basic o de Rules que dependa de ella.

---

# 13. FIN-M09 — Salida hacia reglas y capas posteriores

Finance Basic debe entregar hechos/resultados analíticos, no decisiones.

Como mínimo debe mantener separadas las siguientes categorías conceptuales cuando estén disponibles:

```text
financial_snapshot
current_treasury
future_payments
future_collections
purchase_financial_impact
projected_treasury
working_capital_reference
financial_safety_margin_reference
unresolved_financial_items
source/evidence references
```

La lista es conceptual y no define todavía clases, campos físicos ni estados de API.

Las reglas consumen únicamente aquello cuya dependencia esté demostrada en RDM y matrices especializadas.

---

# 14. Relación con reglas financieras

## R-FIN-001

Autoridad de regla: `Matriz_Reglas_MVP.md`.

Finance Basic no produce `NO COMPRAR`. Debe proporcionar únicamente las consecuencias/datos autorizados necesarios para que la regla pueda evaluarse.

La identidad exacta de `capacidad financiera prevista` permanece gap de metodología.

## R-FIN-002

Consume el criterio de fondo de maniobra y `P-FIN-003` según autoridad vigente.

Finance Basic no determina por sí mismo si el resultado debe ser `NO COMPRAR` o `COMPRAR CONDICIONADO`; esa semántica pertenece a la regla/CRC y requiere resolver cualquier rama todavía ambigua antes de implementación de Rules.

## R-FIN-003

Consume el concepto de margen de seguridad financiera y `P-FIN-004`.

Finance Basic no decide la escalada R1→R0 ni si una condición es resoluble; esas responsabilidades no se infieren desde esta capa.

---

# 15. Relación con reglas de pago

Las reglas `R-PAG-001` y `R-PAG-002` conservan su autoridad independiente.

Finance Basic puede exponer el impacto temporal/económico de las condiciones de pago ya evidenciadas, pero no:

- negocia el plazo;
- convierte `P-PAG-*` en parámetros FIN;
- crea una condición de compra;
- duplica la lógica de las reglas PAG.

---

# 16. Tratamiento de ausencia y contradicción

Hasta que exista un contrato técnico específico, el diseño preserva los principios generales:

```text
missing financial fact ≠ 0
missing evidence ≠ FALSE
contradictory evidence ≠ automatic selection
analysis result ≠ business decision
```

Toda contradicción material deberá conservar fuentes, valores y contexto y deberá impedir una falsa precisión cuando afecte al análisis.

---

# 17. Dependencias que NO se infieren

Este diseño no crea automáticamente:

- `P-FIN-001 → R-FIN-*` cuando la relación no esté demostrada;
- nuevas dependencias DATA/EVIDENCE/COMPONENT en RDM;
- fórmulas de `working_capital`;
- fórmula de `financial_safety_margin`;
- identidad de `financial_capacity_forecast`;
- nuevos parámetros;
- nuevos estados de Assessment;
- nuevos resultados CRC.

---

# 18. Gaps de autoridad a auditar

| Gap | Materia | Estado de diseño |
|---|---|---|
| FIN-G01 | Función exacta de `P-FIN-001` en la metodología y consumidor operativo | OPEN |
| FIN-G02 | Definición/composición autorizada de tesorería | OPEN |
| FIN-G03 | Autoridad de la fórmula de proyección de tesorería propuesta en FIN-M05 | OPEN |
| FIN-G04 | Fórmula/composición de fondo de maniobra y tratamiento post-compra | OPEN |
| FIN-G05 | Definición cuantitativa de margen de seguridad financiera | OPEN |
| FIN-G06 | Identidad cuantitativa de capacidad financiera prevista | OPEN |
| FIN-G07 | Dependencias DATA concretas por regla financiera | OPEN |
| FIN-G08 | Evidencias concretas requeridas por regla financiera | OPEN |
| FIN-G09 | Criticidad/Evaluability_Impact de dependencias financieras en RDM | OPEN |
| FIN-G10 | Semántica de ramas alternativas/escaladas de `R-FIN-002` y `R-FIN-003` para Rules | OPEN fuera de Finance Basic |

Los gaps no autorizan defaults ni inferencias.

---

# 19. Criterio de entrada a contrato técnico

Finance Basic solo podrá pasar a contrato técnico cuantitativo cuando una auditoría confirme, como mínimo:

1. frontera de autoridad limpia;
2. variables financieras identificadas sin duplicar reglas;
3. tratamiento temporal definido;
4. metodología de proyección autorizada;
5. significado de fondo de maniobra suficiente para el alcance MVP;
6. significado de margen de seguridad financiera suficiente para el alcance MVP;
7. identidad de capacidad financiera prevista;
8. dependencias/evidencias críticas suficientes para evitar falsa evaluabilidad;
9. parámetros consumidos trazables y versionados;
10. ausencia de decisión/recomendación automática dentro de Finance Basic.

---

# 20. Estado

**FINANCE BASIC METHODOLOGICAL DESIGN v0.1**

- Diseño inicial: MATERIALIZADO.
- Auditoría 1: PENDIENTE.
- Autorización metodológica: NO CONCEDIDA por este documento.
- Contrato técnico: NO AUTORIZADO.
- Implementación cuantitativa: NO AUTORIZADA.

Siguiente gate obligatorio:

**AUDITAR** este diseño contra Gobierno ↔ MED ↔ Catálogo ↔ Matriz Parámetro-Regla ↔ Matriz de Reglas ↔ Evidence ↔ RDM ↔ Architecture Blueprint ↔ CRC ↔ C0/Assessment.
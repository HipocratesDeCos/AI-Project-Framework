# EIOS — ROT002 Sales Activity Upstream Source Authority Proposal v0.1

**Baseline:** `main @ 9caccbdb02459a72d08eaa8b49df3c406fa793ff`  
**Fecha:** 23/09/2026  
**Estado:** PROPUESTA — NO AUTORIZADA / NO VIGENTE  
**Ámbito:** semántica upstream de actividad de ventas para `SalesActivityWindowEvidence`  
**Regla relacionada:** `R-ROT-002`

## 1. Problema

Track A ya dispone de:

```text
DecisionInputPackage
+
P-ROT-001
+
Evidence de configuración
+
SalesActivityWindowEvidence
```

y de una frontera física provenance-safe integrada por PR #312.

Permanece sin autoridad la transformación upstream que permite afirmar:

```text
SALES_ACTIVITY_PRESENT
```

o:

```text
ZERO_VALID_SALES_DEMONSTRATED
```

La metodología ROT exige que:

- la fuente esté autorizada;
- su semántica esté identificada;
- exista cobertura suficiente de toda la ventana;
- ausencia de filas no equivalga a cero ventas;
- no exista netting implícito;
- ROT no redefina factura, devolución, abono, anulación ni reconocimiento de venta.

## 2. Principio propuesto

Se propone separar tres autoridades:

```text
A. FUENTE
B. SEMÁNTICA
C. COMPLETITUD
```

Una determinación ROT concluyente requerirá las tres.

Ninguna de ellas puede inferirse desde el nombre de una tabla, fichero, ERP, factura o consulta.

## 3. Autoridad de fuente

Se propone que la entrada upstream identifique una fuente factual mediante:

```text
source_ref
```

El valor referencia una extracción, dataset, ledger, vista o sistema concreto.

Por sí solo:

```text
source_ref != autoridad semántica
source_ref != prueba de completitud
```

## 4. Autoridad semántica

Se propone que:

```text
source_semantics_ref
```

referencie una autoridad empresarial explícita que determine qué registros constituyen una **venta válida** para Track A.

Esa autoridad deberá definir, como mínimo:

1. qué hecho empresarial se considera venta;
2. qué fecha gobierna la inclusión temporal;
3. cómo se trata una anulación;
4. cómo se trata una devolución;
5. cómo se trata una nota de abono;
6. si existe o no netting;
7. si una venta posteriormente revertida sigue contando como evento histórico;
8. qué scope empresarial/establecimiento/canal queda incluido;
9. cómo se vincula el artículo.

Hasta que estos puntos no estén aprobados, EIOS no debe decidir por inferencia que una factura, línea de pedido, albarán, ticket, asiento o movimiento equivalga a venta válida.

## 5. Autoridad de completitud

Se propone que:

```text
completeness_ref
```

referencie una demostración explícita de cobertura suficiente para:

```text
article_id
+
window_start
+
window_end
+
scope aplicable
```

La completitud no se deduce de:

- consulta sin resultados;
- respuesta vacía;
- número cero;
- ausencia de error;
- extracción parcial;
- fecha máxima disponible desconocida;
- existencia de una tabla.

## 6. Dos pruebas distintas

### 6.1 Presencia

Para:

```text
SALES_ACTIVITY_PRESENT
```

se propone exigir al menos un evento individual demostrado como venta válida por la autoridad semántica, dentro de la ventana exacta y scope aplicable.

La prueba positiva de presencia no requiere demostrar ausencia en el resto de la ventana.

### 6.2 Ausencia

Para:

```text
ZERO_VALID_SALES_DEMONSTRATED
```

se propone exigir simultáneamente:

```text
semántica de venta válida autorizada
+
cobertura completa demostrada
+
ausencia de eventos válidos en toda la ventana
```

Una consulta que devuelve cero filas sin prueba de cobertura no es suficiente.

## 7. Estados no concluyentes

Se propone conservar:

```text
NOT_EVIDENCED
CONFLICTING_DATA
NOT_DETERMINABLE
```

cuando falte cualquiera de:

- autoridad de fuente;
- autoridad semántica;
- completitud requerida;
- identidad de artículo;
- binding temporal;
- resolución de contradicciones.

Estos estados no equivalen a FALSE ni a cero ventas.

## 8. Contradicciones

Si existen fuentes o evidencias incompatibles:

```text
CONFLICTING_DATA
```

salvo que exista una autoridad específica de resolución.

No se propone resolver contradicciones por:

- recencia;
- mayor cantidad;
- prioridad de sistema;
- suma neta;
- mayoría de registros.

## 9. Carrier upstream propuesto

Se propone reservar el nombre técnico:

```text
SalesActivitySourceEvidence
```

como carrier factual upstream mínimo.

Su propósito sería demostrar únicamente:

```text
article_id
window_start
window_end
source_ref
source_semantics_ref
completeness_ref
valid_sale_evidence_refs
trace_refs
coverage_state
```

No contendría:

- Assessment;
- resultado de regla;
- NO COMPRAR;
- excepción;
- score;
- rotación;
- demanda;
- consumo.

## 10. coverage_state propuesto

Se propone:

```text
COMPLETE
PARTIAL
NOT_DEMONSTRATED
CONFLICTING
```

Semántica:

- `COMPLETE`: cobertura de toda la ventana y scope demostrada;
- `PARTIAL`: cobertura explícitamente parcial;
- `NOT_DEMONSTRATED`: no existe prueba suficiente de cobertura;
- `CONFLICTING`: pruebas de cobertura incompatibles.

Esta taxonomía pertenece únicamente a la cobertura upstream y no reemplaza C0 Evidence.

## 11. valid_sale_evidence_refs

Se propone que:

```text
valid_sale_evidence_refs
```

contenga referencias a evidencias de eventos ya calificados como ventas válidas por la autoridad `source_semantics_ref`.

La frontera ROT no recalifica por sí misma documentos comerciales.

Por tanto:

```text
valid_sale_evidence_refs != raw rows
```

y:

```text
valid_sale_evidence_refs != cantidades netas
```

## 12. Derivación propuesta

Se propone:

```text
if valid_sale_evidence_refs no vacío
and identidad/ventana/semántica válidas:
    SALES_ACTIVITY_PRESENT
```

Para ausencia:

```text
if coverage_state == COMPLETE
and valid_sale_evidence_refs vacío
and identidad/ventana/semántica válidas
and ausencia queda demostrada por completeness_ref:
    ZERO_VALID_SALES_DEMONSTRATED
```

En cualquier otro caso:

```text
NOT_EVIDENCED
/
CONFLICTING_DATA
/
NOT_DETERMINABLE
```

según la evidencia disponible.

## 13. Prohibiciones

Esta propuesta no autoriza:

- considerar factura = venta;
- considerar pedido = venta;
- considerar albarán = venta;
- considerar ticket = venta;
- considerar ingreso contable = venta;
- restar devoluciones automáticamente;
- compensar abonos;
- netear cantidades;
- usar stock/consumo como proxy;
- usar demanda como proxy;
- usar ausencia de filas como prueba de cero;
- inventar una prioridad entre fuentes.

## 14. Decisiones humanas requeridas

Para convertir esta propuesta en autoridad vigente se requiere aprobación expresa de:

1. separación `source_ref / source_semantics_ref / completeness_ref`;
2. principio presencia positiva vs ausencia demostrada;
3. carrier upstream `SalesActivitySourceEvidence`;
4. taxonomía `coverage_state`;
5. `valid_sale_evidence_refs` como eventos ya calificados upstream;
6. prohibición de recalificar documentos comerciales dentro de ROT;
7. mantenimiento de contradicciones sin resolución implícita.

La definición concreta de qué documento o hecho constituye una venta válida puede aprobarse en una autoridad empresarial posterior y no necesita inventarse en esta unidad.

## 15. Estado

**ROT002 Sales Activity Upstream Source Authority Proposal v0.1 — PROPUESTA / NO VIGENTE.**

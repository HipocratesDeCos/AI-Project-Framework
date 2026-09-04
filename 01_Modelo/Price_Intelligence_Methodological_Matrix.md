# EIOS — MATRIZ METODOLÓGICA PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Versión:** 1.1  
**Estado:** CERRADA — METODOLOGÍA  
**Naturaleza:** autoridad metodológica de PR  
**Implementación:** MATERIALIZADA EN C1 — `08_Implementacion/Price_Intelligence_Implementation_Contract.md` v1.3

## 1. Propósito

Esta matriz establece la metodología normativa para determinar el Precio de Referencia (PR), preservando separación entre datos, evidencia, reglas, evaluación y decisión.

No modifica C0, QTG, CRC, arquitectura ni tests existentes.

## 2. Definición

PR es el precio de transacción comparable, normalizado y trazable, derivado de un conjunto de referencias históricas seleccionadas mediante criterios explícitos de comparabilidad y representatividad, sujeto a evaluación de suficiencia.

PR no es PO, PMR, PPV, TCO ni una decisión empresarial.

## 3. Secuencia obligatoria

```text
EVIDENCIA AUTORIZADA
→ IDENTIFICACIÓN
→ DEDUPLICACIÓN
→ COMPARABILIDAD
→ NORMALIZACIÓN
→ TEMPORALIDAD
→ REPRESENTATIVIDAD
→ SELECCIÓN
→ SUFICIENCIA
→ AGREGACIÓN
→ PR
```

Ninguna etapa posterior puede corregir retrospectivamente una deficiencia de una etapa anterior.

## 4. Identidad y deduplicación

Los duplicados documentales de una misma transacción no incrementan N. Debe distinguirse entre N_raw, N_unique, N_comparable, N_representative y N_selected.

La existencia de varias representaciones documentales de una misma transacción no crea observaciones económicas independientes.

## 5. Comparabilidad

La comparabilidad precede a la representatividad. Debe existir identidad económica suficiente, evidencia y trazabilidad. Las diferencias de unidad, cantidad, moneda o condiciones comerciales solo pueden resolverse mediante reglas de normalización autorizadas.

Estados conceptuales: `COMPARABLE`, `NO_COMPARABLE`, `PENDING`.

Una referencia `NO_COMPARABLE` o `PENDING` no puede entrar en el conjunto seleccionado como si fuera comparable.

## 6. Normalización

Una transformación solo se aplica cuando es económicamente válida, reproducible, suficientemente informada y autorizada. No existe normalización implícita.

Comprende, cuando proceda: unidad, cantidad, moneda, impuestos, transporte, descuentos, rappels y condiciones comerciales.

La ausencia de información necesaria para una normalización no se sustituye por cero, media, estimación ni valor por defecto.

## 7. Temporalidad

La temporalidad determina pertinencia, no peso automático. Los parámetros temporales existentes conservan su autoridad propia. No se introduce decaimiento temporal implícito.

La antigüedad no genera por sí misma una ponderación de precio.

## 8. Representatividad

Estados exclusivos:

```text
REPRESENTATIVE
NON_REPRESENTATIVE
INDETERMINATE
```

La representatividad es contextual: se refiere a la realidad económica ordinaria de la evaluación de compra concreta, no a una propiedad absoluta del precio histórico.

### 8.1 Criterios observables obligatorios

Una referencia comparable puede clasificarse como `REPRESENTATIVE` únicamente cuando **todos los criterios aplicables siguientes estén satisfechos y no exista un criterio negativo documentado**:

**REP-01 — Contexto económico ordinario**  
La transacción pertenece al mismo contexto económico relevante de la compra evaluada: producto/concepto comparable, alcance comercial pertinente y condiciones que permitan interpretar el precio dentro de la misma realidad económica.

**REP-02 — Condiciones comerciales ordinarias**  
No existe evidencia documentada de que el precio esté condicionado materialmente por una circunstancia extraordinaria o excepcional ajena a la operación ordinaria.

**REP-03 — Ausencia de anomalía transaccional conocida**  
No existe evidencia documentada de devolución, error de facturación, corrección extraordinaria, liquidación, operación promocional excepcional, compensación extraordinaria, compra de emergencia, incidencia excepcional u otra circunstancia que distorsione materialmente el precio respecto de la operación ordinaria.

**REP-04 — Cantidad y alcance económicamente interpretables**  
La cantidad, unidad y alcance de la operación pueden interpretarse económicamente sin que exista una circunstancia conocida que distorsione materialmente el precio. No se requiere utilizar frecuencia ni proveedor habitual para esta determinación.

**REP-05 — Evidencia suficiente**  
La evidencia disponible permite sustentar los criterios anteriores y la identidad económica de la transacción. La mera existencia del precio no basta.

**REP-06 — Sin contradicción material no resuelta**  
No existe una contradicción material no resuelta que impida determinar qué precio y condiciones corresponden efectivamente a la transacción.

### 8.2 Clasificación

`REPRESENTATIVE`:

- todos los criterios aplicables están satisfechos;
- no existe condición negativa documentada;
- la evidencia permite sostener la clasificación.

`NON_REPRESENTATIVE`:

- existe al menos una circunstancia negativa documentada que distorsiona materialmente la representación de la operación ordinaria.

`INDETERMINATE`:

- no existe evidencia suficiente para afirmar representatividad;
- tampoco existe evidencia suficiente para afirmar no representatividad.

La ausencia de evidencia positiva no se convierte en `NON_REPRESENTATIVE`; conduce a `INDETERMINATE` cuando impide concluir.

### 8.3 Prohibiciones

No se utiliza frecuencia, precio mínimo, último precio, proveedor habitual ni score para determinar representatividad.

Tampoco se clasifica una referencia como representativa por su cercanía al PR resultante o por conveniencia para una decisión posterior.

## 9. Selección

Solo las referencias comparables y `REPRESENTATIVE` son potencialmente seleccionables. `NON_REPRESENTATIVE` e `INDETERMINATE` no aportan evidencia positiva al conjunto seleccionado.

La selección debe realizarse antes de conocer el resultado agregado y no puede modificarse para obtener un PR deseado.

## 10. Suficiencia

La suficiencia no se determina exclusivamente mediante N. Requiere conjuntamente:

1. referencias seleccionadas comparables;
2. representatividad determinada;
3. normalización válida cuando corresponda;
4. evidencia y trazabilidad suficientes;
5. ausencia de contradicciones materiales no resueltas que afecten al conjunto;
6. contexto temporal aplicable;
7. una base de observaciones económicamente defendible.

### 10.1 Umbral mínimo de multiplicidad

Para evitar que una única transacción se convierta por defecto en benchmark de mercado:

```text
N_SELECTED = 0 → NOT_JUSTIFIABLE
N_SELECTED = 1 → como máximo LIMITED
N_SELECTED >= 2 → puede ser SUFFICIENT, pero no lo garantiza
```

Por tanto, `N_SELECTED >= 2` es condición necesaria para `SUFFICIENT`, pero nunca condición suficiente por sí sola.

No se introduce un umbral superior universal: la suficiencia debe considerar también la calidad, homogeneidad, representatividad, temporalidad y limitaciones del conjunto.

Estados:

- `SUFFICIENT`: se satisfacen todas las condiciones aplicables y existe base de observaciones suficiente para el contexto.
- `LIMITED`: existe una base económica defendible para producir PR, pero existe una limitación explícita que impide clasificar el conjunto como plenamente suficiente.
- `NOT_JUSTIFIABLE`: no existe una base económica suficientemente defendible para producir PR.

`N=0 → NOT_JUSTIFIABLE` y `PR_VALUE = null`.

`N=1` no implica automáticamente suficiencia y queda limitado a `LIMITED` como máximo.

`P-PRE-006` conserva exclusivamente la autoridad que ya posee sobre `R-HIS-002`; no constituye el umbral de suficiencia de PR.

## 11. Outliers

Outlier no equivale a error ni a no representatividad. No existe eliminación automática por magnitud. Una referencia solo queda fuera por una causa metodológica previamente definida y trazable.

La condición de outlier puede conservarse como atributo explicativo sin alterar por sí misma la selección.

## 12. Contradicciones

Una diferencia de precio no constituye por sí misma contradicción. Una contradicción material no resuelta no puede convertirse en una observación artificial mediante promedio, último precio, prioridad arbitraria o score.

Si una contradicción es reconciliable mediante regla autorizada, la reconciliación debe quedar trazada. Si no lo es, la evidencia afectada no puede sostener el cálculo.

## 13. Ponderación

El MVP no utiliza ponderación implícita. No se asignan pesos derivados automáticamente de recencia, frecuencia, proveedor habitual, volumen, confianza QTG o conveniencia empresarial.

## 14. Agregación

El método de agregación del MVP es la **mediana no ponderada** de los precios normalizados correspondientes al conjunto seleccionado.

La mediana no decide comparabilidad, representatividad ni selección. No elimina outliers y no resuelve contradicciones.

## 15. No compensación

Ninguna dimensión compensa automáticamente una deficiencia crítica de otra.

```text
N alto + mala comparabilidad ≠ PR suficiente
Evidencia alta + representatividad indeterminada ≠ representativa
Muchos datos + contradicción no resuelta ≠ contradicción resuelta
```

## 16. QTG ↔ PR

QTG mantiene autoridad sobre calidad y confianza de evidencia. PR mantiene autoridad sobre comparabilidad económica, representatividad contextual, selección y agregación.

`QTG confidence ≠ PR representativeness ≠ PR sufficiency`.

La confianza QTG no se convierte en peso de precio.

## 17. Salida conceptual

El resultado PR debe transportar, como mínimo conceptualmente:

```text
PR_VALUE
PR_STATUS
PR_LIMITATIONS
REFERENCE_SET
AGGREGATION_METHOD
METHODOLOGY_VERSION
TRACE
```

La estructura física definitiva queda para la materialización del contrato C1. Esta matriz no prescribe todavía nombres, tipos ni serialización física de campos.

Invariante:

```text
PR_STATUS = NOT_JUSTIFIABLE
⇒ PR_VALUE = null
```

## 18. Separación de decisión

PR no decide comprar, negociar, aceptar, rechazar ni aprobar. Las capas posteriores determinan cómo consumen el resultado y sus limitaciones.

## 19. No-alcance

Esta matriz no define PO, PMR, PPV, TCO, negociación, decisión empresarial, ejecución automática, modificación de C0 ni tests de implementación.

## 20. Invariantes finales

- `PR = comparable + normalizado + trazable`.
- `COMPARABLE ≠ REPRESENTATIVE`.
- `REPRESENTATIVE ≠ SUFFICIENT`.
- `EVIDENCE ≠ REPRESENTATIVENESS`.
- `N ≠ SUFFICIENCY`.
- `OUTLIER ≠ ERROR`.
- `CONTRADICTION ≠ OUTLIER`.
- duplicado documental no crea transacción nueva.
- `N=0 → NOT_JUSTIFIABLE`.
- `N=1 → como máximo LIMITED`.
- `N>=2` es necesario, pero no suficiente, para `SUFFICIENT`.
- no normalización implícita.
- no ponderación implícita en MVP.
- no selección retrospectiva.
- no fallback silencioso.
- no modificación de C0.

## 21. Estado de cierre

La metodología conceptual de Price Intelligence queda cerrada con esta revisión. La implementación C1 queda materializada y auditada mediante los registros de `07_Pruebas`. El presente cambio únicamente reconcilia el estado documental y no modifica la metodología normativa.
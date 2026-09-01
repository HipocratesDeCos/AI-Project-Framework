# EIOS — MATRIZ METODOLÓGICA PRICE INTELLIGENCE

**Fase:** 8.5 — Price Intelligence  
**Estado:** CERRADA — METODOLOGÍA  
**Naturaleza:** autoridad metodológica de PR  
**Implementación:** pendiente de fase posterior  

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

## 5. Comparabilidad

La comparabilidad precede a la representatividad. Debe existir identidad económica suficiente, evidencia y trazabilidad. Las diferencias de unidad, cantidad, moneda o condiciones comerciales solo pueden resolverse mediante reglas de normalización autorizadas.

Estados conceptuales: `COMPARABLE`, `NO_COMPARABLE`, `PENDING`.

## 6. Normalización

Una transformación solo se aplica cuando es económicamente válida, reproducible, suficientemente informada y autorizada. No existe normalización implícita.

Comprende, cuando proceda: unidad, cantidad, moneda, impuestos, transporte, descuentos, rappels y condiciones comerciales.

## 7. Temporalidad

La temporalidad determina pertinencia, no peso automático. Los parámetros temporales existentes conservan su autoridad propia. No se introduce decaimiento temporal implícito.

## 8. Representatividad

Estados: `REPRESENTATIVE`, `NON_REPRESENTATIVE`, `INDETERMINATE`.

`REPRESENTATIVE` requiere evidencia suficiente de que la transacción refleja la realidad económica ordinaria del contexto evaluado, sin distorsión material conocida.

`NON_REPRESENTATIVE` requiere evidencia suficiente de una circunstancia que haga que la operación no represente dicha realidad ordinaria.

`INDETERMINATE` significa que la evidencia no permite determinar justificadamente ninguna de las dos.

No se utiliza frecuencia, precio mínimo, último precio, proveedor habitual ni score para determinar representatividad.

## 9. Selección

Solo las referencias comparables y `REPRESENTATIVE` son potencialmente seleccionables. `NON_REPRESENTATIVE` e `INDETERMINATE` no aportan evidencia positiva al conjunto seleccionado.

La selección debe realizarse antes de conocer el resultado agregado y no puede modificarse para obtener un PR deseado.

## 10. Suficiencia

La suficiencia no se determina exclusivamente mediante N. Considera conjuntamente cantidad, comparabilidad, representatividad, evidencia, consistencia y contexto.

`P-PRE-006` conserva exclusivamente la autoridad que ya posee sobre `R-HIS-002`; no constituye un umbral universal de PR. Los parámetros existentes no se reutilizan como umbrales PR sin autoridad explícita.

Estados:

- `SUFFICIENT`: se satisfacen las condiciones metodológicas aplicables.
- `LIMITED`: existe una base económica defendible para producir PR, pero existe una limitación metodológica explícita.
- `NOT_JUSTIFIABLE`: no existe una base económica suficientemente defendible para producir PR.

`N=0 → NOT_JUSTIFIABLE` y `PR_VALUE = null`.

`N=1` no implica automáticamente suficiencia. Puede producir `LIMITED` únicamente cuando exista una base económica defendible.

## 11. Outliers

Outlier no equivale a error ni a no representatividad. No existe eliminación automática por magnitud. Una referencia solo queda fuera por una causa metodológica previamente definida y trazable.

## 12. Contradicciones

Una diferencia de precio no constituye por sí misma contradicción. Una contradicción material no resuelta no puede convertirse en una observación artificial mediante promedio, último valor, prioridad arbitraria o score.

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
- `N=1` no implica suficiencia.
- no normalización implícita.
- no ponderación implícita en MVP.
- no selección retrospectiva.
- no fallback silencioso.
- no modificación de C0.

## 21. Estado de cierre

La metodología conceptual de Price Intelligence queda cerrada con esta matriz. La implementación y los tests quedan deliberadamente fuera de este cierre.

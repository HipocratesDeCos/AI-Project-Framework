# EIOS — Price Intelligence Implementation Contract

## 1. Identidad

**Documento:** Price Intelligence Implementation Contract  
**Versión:** 0.2  
**Estado:** AUDITADO 1 — PENDIENTE DE AUDITORÍA 2  
**Baseline:** EIOS Vertical MVP  
**Autoridad metodológica:** `01_Modelo/Price_Intelligence_Methodological_Matrix.md`  
**Autoridad arquitectónica:** `03_Arquitectura/Architecture_Blueprint.md`  
**Ubicación:** `08_Implementacion/Price_Intelligence_Implementation_Contract.md`

## 2. Propósito

Define la frontera técnica mínima para materializar Price Intelligence / Precio de Referencia (PR) sin redefinir su metodología.

No constituye una nueva autoridad funcional. La metodología de PR permanece en `01_Modelo/Price_Intelligence_Methodological_Matrix.md`.

La implementación debe materializar únicamente semántica previamente autorizada.

## 3. Posición arquitectónica

El flujo funcional es:

```text
Decision Input Package
        ↓
Quality & Trust
        ↓
Price Intelligence / PR
        ↓
TCO
```

La arquitectura reconoce Price Intelligence como Capa 1 y QTG como control anterior. Assurance, trazabilidad y versionado atraviesan el flujo.

## 4. Frontera con C0 y QTG

Price Intelligence recibe el contexto y los datos autorizados del flujo existente. No crea un contexto paralelo y no redefine:

- `InputContract`;
- `DecisionContext`;
- `Evidence`;
- `EvidenceValidation`;
- `Assessment`;
- `Trace`.

La implementación no modifica C0 para resolver necesidades de PR.

La evidencia conserva los estados y semántica definidos por `Evidence_Contract.md` y C0. `GAP` no se convierte en evidencia demostrada ni en valor de precio.

QTG mantiene autoridad sobre calidad/confianza de evidencia. PR mantiene autoridad sobre su metodología económica. QTG confidence no es ponderación de precio ni representatividad.

## 5. Entrada lógica

La entrada de PR debe poder identificar, cuando corresponda:

```text
DecisionContext
PurchaseOperation / propuesta de compra
referencias históricas autorizadas
Evidence / referencias de evidencia
parámetros temporales autorizados, cuando sean aplicables
referencias de trazabilidad existentes
```

La implementación no crea identificadores paralelos para sustituir `decision_id`, `scenario_id`, `data_snapshot_id`, `rules_version` o `parameters_version`.

PR no adquiere autoridad propia sobre las reglas de evaluación. Cuando una regla existente determine la admisibilidad o disponibilidad de una referencia, se consume su resultado autorizado; no se redefine la regla dentro de pricing.

## 6. Referencia lógica y frontera de identidad

Una referencia histórica es una observación económica procedente de una fuente autorizada.

La implementación **no introduce una nueva identidad empresarial persistente para la transacción**. Cuando exista una identidad de origen, se conserva. Si la implementación necesita una clave técnica interna para operar sobre la colección, esta clave es auxiliar, determinista y no adquiere semántica empresarial ni sustituye la identidad de origen.

La representación lógica puede requerir, cuando estén disponibles y sean aplicables:

```text
source transaction identity
article / economic identity
supplier identity, cuando sea pertinente
quantity
unit
unit_price
currency
operation_date
commercial conditions, cuando sean relevantes
source / evidence references
traceability references
```

Ningún campo se interpreta como criterio metodológico por el mero hecho de existir.

## 7. Pipeline obligatorio

La implementación debe respetar este orden:

```text
INPUT
→ IDENTIFICATION
→ DEDUPLICATION
→ COMPARABILITY
→ NORMALIZATION
→ TEMPORAL RELEVANCE
→ REPRESENTATIVENESS
→ SELECTION
→ SUFFICIENCY
→ AGGREGATION
→ PR RESULT
```

Una etapa posterior no puede corregir retrospectivamente una deficiencia de una etapa anterior.

## 8. Identidad y deduplicación

Los duplicados documentales de una misma transacción no incrementan el conjunto económico de observaciones.

Debe poder distinguirse conceptualmente:

```text
N_RAW
N_UNIQUE
N_COMPARABLE
N_REPRESENTATIVE
N_SELECTED
```

La deduplicación debe ser determinista y trazable. No se permite deducir que dos transacciones son distintas únicamente porque aparezcan en documentos diferentes.

## 9. Comparabilidad

Estados:

```text
COMPARABLE
NO_COMPARABLE
PENDING
```

La comparabilidad requiere identidad económica suficiente y evidencia/trazabilidad adecuadas. Una diferencia normalizable solo puede resolverse mediante una transformación autorizada.

Una referencia `NO_COMPARABLE` o `PENDING` no puede entrar en el conjunto seleccionado como si fuera comparable.

## 10. Normalización

No existe normalización implícita.

Solo pueden aplicarse transformaciones que sean:

- económicamente válidas;
- reproducibles;
- suficientemente informadas;
- autorizadas por la metodología vigente.

No se introducen automáticamente ajustes de unidad, cantidad, moneda, impuestos, transporte, descuentos, rappels o condiciones comerciales.

La ausencia de información necesaria para una normalización no se sustituye por cero, media, estimación ni valor por defecto.

## 11. Temporalidad

La temporalidad determina pertinencia, no peso automático.

Los parámetros temporales existentes conservan su autoridad y significado. La implementación no introduce decaimiento temporal ni ponderación por antigüedad.

## 12. Representatividad

Estados exclusivos:

```text
REPRESENTATIVE
NON_REPRESENTATIVE
INDETERMINATE
```

La clasificación es criterial y explicable. No se implementa un `representativeness_score`.

No se determina representatividad mediante:

- frecuencia;
- mínimo/máximo;
- último precio;
- proveedor habitual;
- score;
- proximidad al PR deseado.

`INDETERMINATE` no equivale a `REPRESENTATIVE`.

## 13. Selección

Solo las referencias que hayan superado las condiciones de comparabilidad y estén clasificadas como `REPRESENTATIVE` pueden integrar el conjunto seleccionado.

La selección es previa a la agregación y no puede depender del resultado que produzca la agregación.

No existe selección retrospectiva para aproximar un precio objetivo o favorecer una decisión empresarial.

## 14. Suficiencia

Estados:

```text
SUFFICIENT
LIMITED
NOT_JUSTIFIABLE
```

La suficiencia no es equivalente a N.

Reglas mínimas:

```text
N_SELECTED = 0
→ NOT_JUSTIFIABLE
→ PR_VALUE = null
```

`N_SELECTED = 1` no implica automáticamente `SUFFICIENT`. Una única referencia solo puede producir un resultado `LIMITED` cuando exista una base económica defendible y las limitaciones queden explícitas.

No se reutilizan parámetros existentes como umbrales universales de PR sin autoridad específica.

## 15. Outliers

Un outlier no es automáticamente un error ni una referencia no representativa.

La implementación no elimina observaciones únicamente por distancia respecto del conjunto.

Una exclusión requiere una causa metodológica autorizada y trazable.

## 16. Contradicciones

Una diferencia de precio no constituye por sí sola contradicción.

Una contradicción material no resuelta no puede transformarse mediante:

```text
average
last value
arbitrary priority
score
fallback
```

en un valor único artificial.

Cuando una contradicción pueda reconciliarse mediante una regla autorizada, la reconciliación debe conservarse en trazabilidad. Si no puede reconciliarse, la evidencia afectada no puede sostener el cálculo.

## 17. Ponderación

El MVP no utiliza ponderación.

No se introducen pesos por:

- recencia;
- frecuencia;
- proveedor;
- volumen;
- QTG confidence;
- conveniencia empresarial.

## 18. Agregación

El método MVP es:

```text
MEDIANA NO PONDERADA
```

Se aplica exclusivamente sobre el conjunto seleccionado y sobre precios normalizados válidos.

La mediana no decide comparabilidad, representatividad, suficiencia ni exclusión.

## 19. Contrato de salida C1

La salida lógica mínima es:

```text
PR_RESULT
├── PR_VALUE
├── PR_STATUS
├── PR_LIMITATIONS
├── REFERENCE_SET
├── AGGREGATION_METHOD
├── METHODOLOGY_VERSION
└── TRACE
```

`TRACE` representa referencias a los mecanismos de trazabilidad existentes y no crea una nueva entidad `Trace` paralela al contrato C0.

Semántica mínima:

```text
PR_STATUS = NOT_JUSTIFIABLE
⇒ PR_VALUE = null
```

`PR_RESULT` no constituye una decisión empresarial ni una recomendación de compra.

La serialización, nombres definitivos de tipos y persistencia física quedan sujetos al cierre de este contrato antes de implementación ejecutable.

## 20. Versionado y trazabilidad

El resultado debe poder reconstruirse respecto de:

- identidad de decisión;
- escenario, cuando corresponda;
- snapshot de datos;
- versión metodológica;
- referencias seleccionadas;
- transformaciones de normalización;
- exclusiones justificadas;
- método de agregación.

La implementación no crea un sistema de versionado paralelo al `DecisionContext`/`Decision Versioning` existente.

## 21. No alcance

Este contrato no define ni implementa:

- PO;
- PMR;
- PPV;
- TCO;
- negociación;
- decisión empresarial;
- nuevos parámetros;
- nuevas reglas;
- cambios en C0;
- tests.

## 22. Invariantes

1. `PR = comparable + normalizado + trazable`.
2. `COMPARABLE ≠ REPRESENTATIVE`.
3. `REPRESENTATIVE ≠ SUFFICIENT`.
4. `N ≠ SUFFICIENCY`.
5. `OUTLIER ≠ ERROR`.
6. `CONTRADICTION ≠ OUTLIER`.
7. Duplicado documental no crea una observación económica nueva.
8. `N_SELECTED = 0 → NOT_JUSTIFIABLE`.
9. `N_SELECTED = 1` no implica suficiencia.
10. No existe normalización implícita.
11. No existe ponderación implícita en MVP.
12. No existe selección retrospectiva.
13. No existe fallback silencioso.
14. No se modifica C0.
15. QTG confidence no se convierte en peso de precio.
16. `NOT_JUSTIFIABLE → PR_VALUE = null`.

## 23. Estado

Este documento queda en **AUDITADO 1 — PENDIENTE DE AUDITORÍA 2**. No autoriza todavía código ejecutable ni modificación de tests.
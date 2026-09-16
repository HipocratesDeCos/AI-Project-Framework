# EIOS — PRE Temporal Dependency Reconciliation — Depuration v0.1

## Estado

**Fase:** DEPURAR  
**Unidad:** PRE-TEMP-DEP-01  
**Base:** Design v0.1 + Audit 1 v0.1.

## 1. Precisión semántica principal

La relación autorizada queda formulada de forma estricta:

```text
P-PRE-001
→ configura el horizonte temporal usado para interpretar “reciente”
→ en la condición de R-PRE-001.
```

No significa:

```text
P-PRE-001
→ selecciona la referencia comparable
→ determina representatividad
→ determina suficiencia
→ calcula/agrega PR
→ decide NEGOCIAR
```

Cada una de esas responsabilidades permanece en su autoridad correspondiente.

## 2. Frontera PRICE ↔ regla PRE

Price Intelligence/PR conserva su metodología cerrada e independiente. La presente unidad solo alinea el mapa documental de dependencias de `R-PRE-001` con una decisión temporal ya resuelta.

La ausencia actual de un bridge ejecutable de `R-PRE-001` en el catálogo técnico no se presenta como cerrada ni se resuelve mediante esta unidad.

## 3. Valor de configuración

El valor `3 meses` de `P-PRE-001` continúa siendo un valor inicial de catálogo pendiente de validación. No se eleva a política empresarial definitiva, estándar universal ni constante de código.

## 4. Clasificación RDM depurada

Se mantiene:

- `Dependency_Type = PARAMETER`;
- `Evidence_Status = CONFIRMED`;
- `Criticality = PENDING`;
- `Evaluability_Impact = PENDING`;
- `Fallback = NONE`;
- `Affected_Component = NONE`.

La fuente demostrativa será `01_Modelo/Price_Intelligence_Specification_Gaps.md`, concretamente `GAP-PI-TEMP-01`.

## 5. Exclusiones explícitas

Permanecen fuera de alcance:

- `P-PRE-002` y cualquier consumidor no demostrado;
- cambios en `P-PRE-004 → R-PRE-001`;
- cambios en `P-PRE-005 → R-PRE-002`;
- implementación de `R-PRE-001`/`R-PRE-002`;
- nueva política de evidencia;
- nuevas reglas de comparabilidad, representatividad, suficiencia, agregación o CRC;
- cambios de código o tests ejecutables.

## 6. Resultado de depuración

El diseño queda reducido a una reconciliación documental mínima y trazable de una sola relación ya autorizada:

```text
P-PRE-001 → R-PRE-001
```

No se detecta necesidad de ampliar el alcance antes de Audit 2.

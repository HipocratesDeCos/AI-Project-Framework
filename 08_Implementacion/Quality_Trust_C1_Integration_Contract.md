# EIOS — Quality & Trust → Price Intelligence Integration Contract

## 1. Identidad

**Documento:** Quality & Trust → Price Intelligence Integration Contract  
**Versión:** 1.0  
**Estado:** CERRADO  
**Baseline de origen:** `1c39aa740867ae3c0f9f3f5f40dfa9d54ba5ea3b`  
**Autoridad arquitectónica:** `03_Arquitectura/Architecture_Blueprint.md`  
**Ubicación:** `08_Implementacion/Quality_Trust_C1_Integration_Contract.md`

## 2. Propósito

Define exclusivamente la integración física entre la Capa 0 — Quality & Trust y la Capa 1 — Price Intelligence.

No redefine QTG, Price Intelligence, C0, evidencia, metodología de PR ni decisión empresarial.

## 3. Flujo

```text
Quality & Trust
      ↓
QualityTrustResult
      ↓
Integration Gate
      ↓
Price Intelligence
```

## 4. Regla de ejecución

1. Se evalúa QTG sobre los `QualityCheck` suministrados.
2. `APTO` permite ejecutar C1.
3. `APTO_CON_ADVERTENCIAS` permite ejecutar C1.
4. `NO_APTO` impide ejecutar C1.
5. La integración no recalcula ni modifica el resultado QTG.
6. La integración no convierte estados QTG en estados de Price Intelligence.
7. La integración no transforma `QualityConfidence` en peso, score o parámetro económico.

## 5. Preservación

Cuando C1 se ejecuta, el `QualityTrustResult` debe permanecer disponible para la capa superior que componga la ejecución.

C1 no recibe el resultado QTG como dato metodológico de Price Intelligence salvo que una interfaz superior lo transporte como metadato de assurance sin alterar el contrato C1.

## 6. Detención

Si `status = NO_APTO`, la integración termina antes de ejecutar C1.

No debe fabricarse un `PriceIntelligenceResult` para representar la detención.

## 7. Errores e incertidumbre

La integración no interpreta ni corrige estados QTG. En particular, `INDETERMINATE`, contradicciones y ausencia de evidencia permanecen según el contrato QTG y no se convierten silenciosamente en `FALSE`, `NO_APTO`, score o valor por defecto.

## 8. Fronteras

La integración no:

- modifica C0;
- crea evidencia;
- valida evidencia;
- crea `DecisionContext`;
- crea identidades empresariales;
- modifica reglas de C1;
- modifica la selección de referencias;
- modifica la agregación PR;
- produce una decisión empresarial;
- crea un sistema paralelo de trazabilidad o versionado.

## 9. Invariantes

- QTG se ejecuta antes que C1.
- `NO_APTO` bloquea C1.
- `APTO` y `APTO_CON_ADVERTENCIAS` permiten C1.
- El resultado QTG se conserva.
- C1 conserva su contrato físico independiente.
- La integración no altera la semántica de ningún estado de QTG ni C1.
- La integración es determinista para las mismas entradas.

## 10. Tests contractuales mínimos

La implementación debe demostrar al menos:

- `APTO → C1 ejecutado`.
- `APTO_CON_ADVERTENCIAS → C1 ejecutado`.
- `NO_APTO → C1 no ejecutado`.
- Resultado QTG conservado cuando C1 se ejecuta.
- No conversión de confianza QTG en ponderación de C1.
- No modificación de C0.
- No fabricación de resultado PR cuando QTG bloquea la ejecución.

## 11. Estado de cierre

**INTEGRACIÓN QTG → C1 — CONTRATO FÍSICO: CERRADO.**

Este contrato materializa únicamente la relación arquitectónica ya aprobada entre Capa 0 y Capa 1. No introduce semántica funcional nueva.

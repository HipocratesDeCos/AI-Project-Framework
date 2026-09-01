# EIOS — CRC-MVP Implementation Contract

## 1. Identidad

**Documento:** CRC-MVP Implementation Contract  
**Versión:** 1.1  
**Estado:** CERRADO Y MATERIALIZADO  
**Baseline:** EIOS Vertical MVP  
**Ubicación:** `08_Implementacion/CRC_MVP_Implementation_Contract.md`

---

## 2. Propósito

Este documento materializa exclusivamente el subconjunto de `CRC` suficientemente definido para implementación en el Vertical MVP.

No constituye una nueva autoridad funcional ni amplía la autoridad de CRC. Su objetivo es traducir a un contrato técnico mínimo las invariantes ya establecidas por las autoridades funcionales y arquitectónicas.

`CRC-MVP` consolida resultados ya producidos por capas anteriores. No constituye un segundo motor de reglas, calidad, evidencia, viabilidad o escenarios.

---

## 3. Frontera funcional

El flujo autorizado es:

```text
Assessment[]
    +
contexto/versionado autorizado
    +
metadatos normativos de Rule
    ↓
CRC-MVP
    ↓
resultado consolidado de EIOS
    ↓
recomendación para el decisor
```

CRC-MVP no crea ni recalcula:

```text
Evidence
Quality & Trust
Rule
Assessment
Viability
Scenario
Decision Twin
Negotiation
PMR
Exception
Override
Business Decision
```

---

## 4. Entrada

La entrada lógica mínima es:

```text
assessments: Assessment[]
decision_context: DecisionContext
```

El runtime debe poder resolver cada `Assessment.rule_id` contra una definición de `Rule` compatible con `decision_context.rules_version`.

La información normativa de `Rule` puede ser una dependencia del runtime y no debe duplicarse innecesariamente dentro de `Assessment`.

### 4.1 Integridad de regla

Si `rule_id` no puede resolverse, o la definición de regla no es compatible con `rules_version`, CRC no debe inferir un `effect`, `severity` o resultado por defecto.

El fallo debe tratarse como error de integridad de contexto.

---

## 5. Semántica de Assessment

CRC consume el resultado individual sin reinterpretarlo.

```text
EVALUABLE + TRUE
EVALUABLE + FALSE
NOT_EVALUABLE + None
```

Se conserva la invariante:

```text
NOT_EVALUABLE ≠ FALSE
```

Y también:

```text
FALSE ≠ NO COMPRAR
NOT_EVALUABLE ≠ NO COMPRAR
```

CRC no modifica retrospectivamente el `Assessment` original.

---

## 6. Metadatos normativos de Rule

`effect` y `severity` pertenecen a la definición normativa de la regla.

CRC los consume para resolver y explicar resultados, pero no los redefine.

Invariante:

```text
EFFECT ≠ SEVERITY
```

No está permitido derivar automáticamente:

```text
HIGH severity → R0
CRITICAL severity → R0
```

El efecto R0/R1/R2/R3 debe proceder de la autoridad de la regla.

---

## 7. Resolución de efectos

CRC-MVP utiliza los efectos autorizados:

```text
R0 = BLOQUEO
R1 = CONDICIONANTE
R2 = NEGOCIACIÓN
R3 = INFORMATIVA
```

Cuando existan efectos incompatibles, se aplica la precedencia normativa definida por CRC.

La resolución no utiliza compensación automática mediante puntuación.

No se permite:

```text
R0 - R1 - R2 - R3
Σ señales favorables
score → override
ranking → override
```

---

## 8. No duplicación causal

La cantidad de resultados coincidentes no aumenta por sí misma la fuerza normativa de una restricción.

Por tanto:

```text
R0(A) + R0(B) + R0(C)
```

produce un bloqueo consolidado con múltiples motivos trazables, no tres niveles acumulativos de bloqueo.

La multiplicidad aumenta información explicativa y trazabilidad, no autoridad normativa.

---

## 9. Factores relevantes

`relevant_factors` representa información contextual o explicativa utilizada para comprender el resultado consolidado.

No constituye una fuente autónoma de autoridad.

Por tanto:

```text
relevant_factor ≠ rule
relevant_factor ≠ effect
relevant_factor ≠ override
```

Los factores relevantes no pueden compensar ni anular un efecto autorizado.

---

## 10. Motivo dominante

`dominant_reason` identifica el motivo que explica principalmente el resultado consolidado conforme a la jerarquía de resolución autorizada.

No debe calcularse mediante:

```text
score
weight
utility
frequency alone
severity alone
```

El motivo dominante es explicativo y debe poder trazarse hasta los resultados y reglas que participaron en la consolidación.

---

## 11. Resultado consolidado

`consolidated_result` pertenece al dominio de resultados oficiales de CRC:

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

El resultado consolidado es una salida de EIOS y no una decisión empresarial ejecutada.

```text
consolidated_result
    ≠
business_decision
    ≠
execution
```

---

## 12. Viability Frontier

CRC puede consumir el resultado de Viability Frontier cuando forme parte del contexto autorizado.

No puede redefinir la viabilidad ni recalcularla.

Se conserva expresamente:

```text
VIABLE ≠ COMPRAR
```

La viabilidad no constituye por sí sola una orden ni una recomendación automática de compra.

---

## 13. Scenarios / Decision Twin

CRC puede consumir información de escenarios o comparaciones ya producidas por las capas autorizadas.

No crea, modifica ni recalcula escenarios.

Un resultado perteneciente a un escenario histórico no adquiere autoridad normativa sobre un escenario posterior por herencia o acumulación.

```text
historical state ≠ active restriction
```

---

## 14. Excepciones y override

CRC-MVP no crea excepciones ni ejecuta overrides.

Una excepción solo puede existir cuando una autoridad competente la haya definido explícitamente.

No se permite inferir una excepción a partir de:

- factores favorables;
- señales R2/R3;
- cantidad de Assessment;
- scoring;
- conveniencia comercial;
- decisión esperada del usuario.

Un `R0` no puede ser anulado implícitamente por CRC-MVP.

---

## 15. Quality & Trust / Evidence / RDM

CRC consume estados o resultados producidos por las autoridades correspondientes.

No constituye un segundo motor para:

```text
Quality & Trust
Evidence Contract
Rule Dependency Matrix
```

En particular, CRC no redefine la admisibilidad de evidencia, no recalcula calidad de datos y no inventa dependencias de reglas.

---

## 16. Historial y escenarios sucesivos

Los resultados deben evaluarse en el contexto al que pertenecen.

Para:

```text
S1 → S2 → S3
```

los resultados exclusivos de S1 no se acumulan automáticamente en S2 o S3.

El historial se conserva para trazabilidad, no como restricción normativa heredada.

---

## 17. Trazabilidad

El resultado consolidado debe conservar referencias suficientes para reconstruir:

```text
Assessment participantes
Rule asociadas
resultado individual
precedencia aplicada
motivo dominante
factores relevantes
contexto/versionado
```

CRC no reescribe los objetos de origen para conseguir trazabilidad.

---

## 18. Salida mínima

La salida conceptual mínima de CRC-MVP es:

```text
CRCResult
├── consolidated_result
├── dominant_reason
├── relevant_factors
├── conflicts
└── traceability
```

Los siguientes elementos quedan fuera de la materialización actual por no disponer de autoridad estructural suficiente:

```text
conditions
negotiation_signals
information_signals
exception
override
price_maximum_recommendation
selected_alternative
score
ranking
```

Su exclusión no niega su posible existencia futura; evita introducir estructura física no autorizada.

---

## 19. Invariantes ejecutables

### I-CRC-01 — Rule integrity

Todo `Assessment` debe resolverse contra una `Rule` compatible con `rules_version`.

### I-CRC-02 — Assessment preservation

CRC no modifica ni reinterpreta retrospectivamente el `Assessment`.

### I-CRC-03 — Effect / Severity separation

`effect` y `severity` no son intercambiables.

### I-CRC-04 — Authorized precedence

Los conflictos se resuelven mediante precedencia autorizada, no mediante scoring compensatorio.

### I-CRC-05 — No multiplicity amplification

La cantidad de resultados no aumenta por sí misma la autoridad de una restricción.

### I-CRC-06 — No historical accumulation

Un resultado histórico no se convierte automáticamente en restricción de otro escenario.

### I-CRC-07 — No authority creation

CRC no crea reglas, efectos, excepciones, overrides ni restricciones nuevas.

### I-CRC-08 — Viability separation

`VIABLE` no equivale a `COMPRAR` y CRC no redefine Viability.

### I-CRC-09 — Non-executable recommendation

La salida CRC no ejecuta una decisión empresarial.

### I-CRC-10 — Traceability

El resultado consolidado debe mantener trazabilidad hasta los resultados y contexto que lo originaron.

---

## 20. Errores mínimos

El comportamiento de error debe ser explícito ante:

```text
- rule_id inexistente
- rules_version incompatible
- metadata normativa ausente para resolver effect
- Assessment estructuralmente inválido
- combinación de estados incompatible con el contrato
```

No se permiten valores por defecto silenciosos que puedan convertir una ausencia de información en una restricción o resultado inventado.

---

## 21. Exclusiones de seguridad

CRC-MVP no implementará:

```text
- scoring global
- ranking de alternativas
- selección automática de alternativa
- compensación de R0 mediante señales positivas
- creación de R0 por acumulación
- cálculo de Quality & Trust
- evaluación de evidencia
- cálculo de Viability
- generación/evaluación de escenarios
- cálculo de PMR
- creación de excepciones
- override automático
- ejecución de compras
- decisión empresarial
```

Estas exclusiones forman parte del contrato técnico y no son funcionalidades pendientes que puedan inferirse durante la implementación.

---

## 22. Estado de materialización

La implementación mínima definida por este contrato está materializada en:

```text
eios/core/crc_mvp.py
tests/test_crc_mvp.py
```

La implementación mantiene las invariantes del contrato, incluida la integridad de `rule_id`/`rules_version`, separación `effect`/`severity`, precedencia R0→R1→R2→R3, no amplificación por multiplicidad, tratamiento explícito de `NOT_EVALUABLE`, ausencia de scoring/ranking/selección y trazabilidad mediante `DecisionContext`.

La verificación CI de la implementación forma parte del estado materializado del MVP. Las exclusiones de la sección 21 permanecen vigentes.

## 23. Dictamen de cierre

```text
DICTAMEN: CERRADO Y MATERIALIZADO
Tipo de cambio: DOCUMENTACIÓN DE IMPLEMENTACIÓN
Cambios técnicos derivados: NINGUNO
Código CRC: MATERIALIZADO
Tests CRC: MATERIALIZADOS
CI: VERIFICADA SATISFACTORIAMENTE
```

Método aplicado:

```text
DISEÑAR → AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI
```

No se autoriza implementar las capacidades excluidas en este documento hasta que exista autoridad documental y/o metodológica suficiente.

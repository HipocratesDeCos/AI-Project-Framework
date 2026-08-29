# EIOS — Assessment / Individual Result Contract

## 1. Identidad

**Documento:** Assessment / Individual Result Contract  
**Versión:** 1.0  
**Estado:** IMPLEMENTADO DOCUMENTALMENTE  
**Baseline:** EIOS Vertical MVP  
**Ubicación:** `08_Implementacion/Assessment_Individual_Result_Contract.md`

---

## 2. Propósito

Este documento materializa en la fase de implementación el contrato cerrado para el resultado individual de evaluación.

En EIOS:

> **Assessment = Individual Result**

El documento describe el contrato de implementación ya definido y no constituye una nueva autoridad funcional ni introduce una nueva capacidad del sistema.

La autoridad de los conceptos empresariales, reglas, parámetros, arquitectura y resolución de conflictos permanece en sus documentos especializados conforme a la Matriz de Autoridad Documental.

---

## 3. Correspondencia con el modelo de implementación

El objeto `Assessment` representa el resultado de la evaluación de **una regla individual** sobre un contexto determinado.

Su contrato material es:

```text
Assessment
├── rule_id
├── status
├── outcome
├── evidence_ids
└── reason
```

La implementación debe conservar la correspondencia entre este contrato documental y el modelo físico existente.

No se define aquí una estructura alternativa ni se autoriza la incorporación de campos adicionales por inferencia documental.

---

## 4. Semántica del resultado

### 4.1 Evaluación evaluable

Cuando la regla puede evaluarse con la información disponible:

```text
status = EVALUABLE
outcome = TRUE | FALSE
```

El valor de `outcome` representa exclusivamente el resultado booleano de la evaluación de la regla individual.

### 4.2 Evaluación no evaluable

Cuando la evidencia o información requerida no permite evaluar la regla:

```text
status = NOT_EVALUABLE
outcome = None
```

La ausencia de evidencia no puede transformarse en `FALSE` por conveniencia de implementación.

Por tanto:

```text
NOT_EVALUABLE ≠ FALSE
```

---

## 5. Frontera semántica

`Assessment` es un resultado individual de evaluación. No es una decisión empresarial consolidada.

Por tanto:

```text
Assessment
    ≠ Decision
    ≠ Recommendation
    ≠ CRC Resolution
```

Asimismo:

```text
FALSE ≠ NO COMPRAR
NOT_EVALUABLE ≠ NO COMPRAR
```

Los resultados empresariales consolidados pertenecen a las capas posteriores definidas por la arquitectura y las reglas correspondientes.

---

## 6. Relación con la definición de regla

`Assessment` registra el resultado de aplicar una regla; no redefine la regla.

Los atributos normativos de la regla, incluidos cuando corresponda:

- `effect`;
- `severity`;
- prioridades;
- excepciones;
- demás atributos de comportamiento;

permanecen bajo la autoridad documental de la definición de reglas.

No deben duplicarse como responsabilidades propias de `Assessment`.

---

## 7. Evidencia

`evidence_ids` identifica la evidencia utilizada o requerida para sustentar la evaluación individual.

La evidencia y sus criterios de suficiencia, calidad, antigüedad y trazabilidad permanecen bajo la autoridad de la documentación especializada de evidencia.

La ausencia o insuficiencia de evidencia requerida debe reflejarse mediante la semántica `NOT_EVALUABLE` cuando corresponda; no mediante una conversión implícita a `FALSE`.

---

## 8. Trace y reproducibilidad

`Assessment` y `Trace` son responsabilidades distintas.

```text
Assessment
    ↓
resultado individual de evaluación

Trace
    ↓
contexto material necesario para reproducibilidad
```

La existencia de información de trazabilidad en el flujo de ejecución no convierte `Trace` en parte del contrato semántico de `Assessment`.

No se autoriza fusionar ambos conceptos documental ni técnicamente por conveniencia.

---

## 9. Identidad de la regla y versionado

`rule_id` identifica la regla que produjo el resultado.

La interpretación de la regla se realiza dentro del contexto de versión correspondiente. En el flujo C0, la versión de la regla debe ser coherente con `DecisionContext.rules_version`.

Esto permite reproducir qué definición de regla fue utilizada sin introducir un campo de versión adicional en `Assessment`.

```text
Assessment.rule_id
        +
DecisionContext.rules_version
        ↓
interpretación inequívoca de la regla aplicada
```

---

## 10. Reason

`reason` proporciona la explicación asociada al resultado individual de la evaluación dentro del alcance definido para el Assessment.

No debe utilizarse para introducir una recomendación empresarial, una decisión consolidada ni una resolución de conflictos que corresponda a otra capa.

---

## 11. Límites explícitos del contrato

Los siguientes conceptos **no forman parte del contrato de `Assessment`**:

```text
effect
severity
recommendation
decision
priority
dominant_reason
exception
negotiation_condition
scenario
viability
confidence
score
```

Su exclusión del contrato no implica que dichos conceptos no existan en EIOS. Significa únicamente que su responsabilidad pertenece a otras capas documentales o funcionales.

---

## 12. Relación con CRC

Cuando varias evaluaciones individuales deban combinarse para obtener un resultado consolidado, `Assessment` proporciona resultados individuales a la capa correspondiente.

La resolución de conflictos no pertenece a `Assessment`.

En particular, `Assessment` no determina por sí mismo:

- la regla dominante;
- la severidad consolidada;
- la aplicación de excepciones;
- el resultado empresarial final.

Estas responsabilidades permanecen en la capa de resolución de conflictos y en las autoridades funcionales correspondientes.

---

## 13. Relación con C0

Este contrato documental describe el estado de implementación de C0 y debe permanecer alineado con el flujo:

```text
Input Contract
      ↓
DecisionContext
      ↓
Evidence
      ↓
Evidence Validation
      ↓
Rule
      ↓
Assessment
      ↓
Trace
```

La materialización de este documento no amplía dicho flujo.

No incorpora responsabilidades de:

- Decision;
- Scenario;
- Negotiation;
- Negotiation Ladder;
- CRC como motor adicional;
- LLM;
- persistencia;
- API;
- MCP;
- Apps SDK;
- SQL Server como dependencia de ejecución.

---

## 14. Reglas de implementación documental

1. `Assessment` debe representar una evaluación individual y no una decisión consolidada.
2. `EVALUABLE` debe producir `TRUE` o `FALSE`.
3. `NOT_EVALUABLE` debe producir `None` en `outcome`.
4. La insuficiencia de evidencia no debe convertirse implícitamente en `FALSE`.
5. Los atributos normativos de la regla no deben duplicarse dentro de `Assessment`.
6. `Trace` permanece separado de `Assessment`.
7. `rule_id` identifica la regla aplicada y la versión se determina mediante el contexto de reglas correspondiente.
8. Ningún contenido de este documento puede utilizarse para redefinir la autoridad de documentos superiores o especializados.
9. Cualquier ampliación futura del contrato requiere un cambio de alcance/versionado formalmente aprobado.

---

## 15. Criterio de cierre documental

La materialización se considera correcta cuando:

- el contrato documental coincide con el `Assessment` implementado;
- no se introducen campos ficticios;
- no se introduce semántica decisional nueva;
- se conserva la distinción `NOT_EVALUABLE` / `FALSE`;
- se conserva la separación entre `Assessment`, `Rule`, `Trace` y `CRC`;
- el documento no requiere modificaciones técnicas para cumplirlo.

---

## 16. Estado

**DICTAMEN:** MATERIALIZADO

**Tipo de cambio:** DOCUMENTACIÓN ÚNICAMENTE

**Cambios técnicos derivados:** NINGUNO

**Baseline C0:** NO ALTERADO

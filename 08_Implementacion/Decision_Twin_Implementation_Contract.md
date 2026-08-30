# EIOS — Decision Twin Implementation Contract

## 1. Identidad

**Documento:** Decision Twin Implementation Contract  
**Versión:** 1.0.4  
**Estado:** EN VALIDACIÓN — contrato técnico de implementación  
**Baseline:** EIOS Vertical MVP  
**Ubicación:** `08_Implementacion/Decision_Twin_Implementation_Contract.md`

---

## 2. Propósito

Este contrato define la frontera mínima de implementación de `Decision Twin` sin redefinir su contrato funcional.

La autoridad conceptual permanece en `05_Motor/Decision_Twin.md`.

`Decision Twin` representa y compara alternativas ya disponibles en el flujo EIOS. No crea una nueva autoridad normativa, decisional, de viabilidad, de escenarios, de negociación ni de resolución.

---

## 3. Principio de materialización mínima

La implementación materializa únicamente información cuyo significado ya esté autorizado por las capas anteriores.

No se introducen por inferencia:

- reglas;
- parámetros;
- dependencias;
- evidencia nueva;
- restricciones de viabilidad;
- escenarios;
- scores;
- rankings;
- funciones de utilidad;
- selección automática;
- decisión empresarial.

La implementación no puede convertir una capacidad de representación o comparación en una capacidad de selección o decisión.

---

## 4. Objeto lógico

El objeto lógico de implementación es una **alternativa decisional representada** junto con los resultados y consecuencias autorizados que permitan su comparación.

Conceptualmente:

```text
Alternative
├── representation reference
├── scenario reference
├── viability result
├── associated results
├── known consequences
└── traceability references
```

Estos elementos representan información ya producida por las autoridades correspondientes; Decision Twin no los recalcula.

La autoridad funcional no define actualmente una identidad persistente propia para `Alternative`. Por tanto, esta implementación no introduce todavía un `Alternative_ID` ni presupone que la alternativa deba constituir una entidad física independiente.

---

## 5. Separación de identidades

Deben conservarse separadas las identidades que ya poseen autoridad documental:

```text
Scenario_ID       → identifica escenario
Decision_ID       → identifica unidad decisional cuando corresponda
```

`Alternative` es actualmente una opción representada para comparación, no una identidad funcional formalmente definida por este contrato.

Por tanto:

```text
Scenario_ID ≠ Alternative
Alternative ≠ Decision_ID
```

`Scenario_ID` no adquiere automáticamente semántica de alternativa, y ninguna identidad existente puede reutilizarse como `Alternative_ID` por conveniencia física.

Si una futura necesidad técnica exige una identidad propia de alternativa, deberá justificarse y especificarse mediante autoridad documental antes de su materialización física.

---

## 6. Entrada mínima

La implementación puede recibir:

- referencia al escenario evaluado, cuando exista;
- referencia de representación de la alternativa, cuando sea necesaria y esté definida por la capa correspondiente;
- resultado de `Viability Frontier`;
- resultados de evaluación ya producidos;
- consecuencias conocidas ya determinadas;
- referencias de trazabilidad.

La ausencia de un elemento opcional no se convierte en un valor ficticio ni en una conclusión negativa.

---

## 7. Flujo con Viability y Scenario Engine

`Decision Twin` consume resultados ya producidos por las autoridades anteriores y no los determina.

El flujo arquitectónico aplicable a la representación de alternativas es:

```text
Assessment
    ↓
Viability Frontier
    ↓
Scenario Engine
    ↓
Escenario evaluado
    ↓
Alternativa representada
    ↓
Decision Twin
```

Cuando una alternativa requiere una hipótesis, modificación o recálculo, dicha operación regresa al `Scenario Engine`:

```text
Decision Twin
      ↓
hipótesis / alternativa a evaluar
      ↓
Scenario Engine
      ↓
escenario evaluado
      ↓
Decision Twin
```

`Decision Twin` no determina ni recalcula la viabilidad y no genera, modifica ni recalcula escenarios como mecanismo propio.

No puede transformar:

```text
VIABLE                  → COMPRAR
VIABLE CON CONDICIONES  → COMPRAR CONDICIONADO
NOT_EVALUABLE           → NO COMPRAR
NOT_VIABLE              → decisión empresarial automática
```

La semántica de los estados de viabilidad permanece bajo `Viability Frontier`; la decisión empresarial permanece bajo las autoridades posteriores y el decisor humano.

---

## 8. Comparación

La implementación debe permitir comparar dos o más alternativas disponibles sin convertir la comparación en selección.

La comparación puede exponer diferencias en:

- resultados;
- viabilidad;
- condiciones;
- consecuencias conocidas;
- riesgos ya determinados;
- referencias de trazabilidad.

La comparación no genera por sí misma una alternativa preferente.

---

## 9. No selección

No se implementarán como comportamiento implícito:

- ranking automático;
- scoring;
- ponderaciones;
- función de utilidad;
- optimización;
- elección de alternativa preferente;
- recomendación empresarial.

```text
COMPARAR ≠ SELECCIONAR
SELECCIONAR ≠ DECIDIR
```

Cualquier autoridad futura de selección deberá disponer de un contrato independiente.

---

## 10. Escenarios

`Decision Twin` no crea, modifica ni recalcula escenarios.

Las hipótesis que requieran evaluación formal regresan al `Scenario Engine`.

El historial de un escenario no se convierte en una restricción normativa de una alternativa posterior.

---

## 11. Assessment y Evidence

`Assessment` conserva exclusivamente el resultado individual de una regla.

`Decision Twin` no crea, modifica ni consolida `Assessment`.

La evidencia continúa bajo su contrato especializado. Decision Twin solo conserva referencias necesarias para trazabilidad y no determina suficiencia, admisibilidad o validez de evidencia.

---

## 12. Parámetros y dependencias

Los parámetros continúan bajo su autoridad propia.

Un valor concreto de una alternativa no modifica un parámetro del sistema.

La `Rule Dependency Matrix` conserva la autoridad sobre dependencias demostradas. Decision Twin no descubre, crea, elimina ni modifica dependencias.

---

## 13. Consecuencias

Solo pueden representarse consecuencias ya producidas o autorizadas por la capa que corresponda.

Decision Twin no inventa consecuencias normativas ni sustituye cálculos, reglas o evaluaciones.

Una consecuencia representada mantiene referencia a su fuente cuando esta exista.

---

## 14. Trazabilidad

La trazabilidad de `Decision Twin` se limita a conservar referencias a las fuentes ya existentes. No se crea un segundo mecanismo de Trace.

Cuando una alternativa proceda de un escenario evaluado, la referencia contextual puede conservar `Scenario_ID` cuando esté disponible. Esta referencia no convierte al escenario en identidad de la alternativa.

Cuando existan resultados C0 asociados, podrán conservarse sus referencias ya existentes, como `trace_id` o `input_fingerprint`, sin recalcularlos ni redefinir su semántica.

No se presume que un único `trace_id` sea suficiente para representar todos los resultados de una alternativa. Si una alternativa requiere múltiples resultados trazables, la implementación deberá conservar las referencias correspondientes sin convertirlas en una nueva autoridad de evidencia.

Cadena mínima:

```text
Decision Twin
      ↓
Alternative representation
      ↓
Scenario / Viability / Assessment
      ↓
Rule / Evidence / source authority
```

La trazabilidad es informativa y no modifica la autoridad de las capas referenciadas.

---

## 15. Decision Versioning

Cuando una alternativa forme parte de un estado decisional versionado, Decision Twin puede conservar la referencia al `Decision_ID` o al contexto versionado correspondiente.

No crea una segunda política de versionado ni sobrescribe estados históricos.

La continuidad histórica permanece bajo `Decision Versioning`.

---

## 16. CRC y recomendación

Decision Twin no sustituye a CRC.

No consolida conflictos ni determina el motivo dominante de una recomendación.

Tampoco genera por sí mismo:

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

Los resultados empresariales consolidados permanecen bajo las autoridades posteriores definidas por el MED, CRC y la arquitectura autorizada.

---

## 17. Invariantes de implementación

La implementación deberá conservar como invariantes:

1. una comparación no puede crear una selección automática;
2. una alternativa no puede convertirse en una decisión por su mera representación;
3. un resultado de viabilidad no puede cambiar de semántica al entrar en Decision Twin;
4. una hipótesis no puede modificar parámetros globales;
5. un escenario previo no puede imponer restricciones por mera continuidad histórica;
6. información redundante no puede crear un nuevo peso decisional por conteo;
7. ausencia de información opcional no puede producir valores ficticios;
8. trazabilidad no puede adquirir autoridad decisional;
9. un único `trace_id` no se presume suficiente para todos los resultados de una alternativa;
10. una referencia de trazabilidad no puede sustituir al objeto fuente ni alterar su ciclo de vida.

---

## 18. Límites físicos

Este contrato no fija todavía:

- esquema SQL;
- tipos físicos;
- índices;
- API;
- serialización concreta;
- estrategia de almacenamiento;
- mecanismo de selección futura.

Estos elementos solo podrán definirse después de cerrar sus requisitos técnicos y demostrar que no introducen autoridad funcional nueva.

---

## 19. Dependencias previas al DDL o implementación física

Antes de materializar persistencia específica deberán estar demostrados:

1. si `Alternative` requiere identidad persistente propia;
2. si la relación con `Scenario_ID` es necesaria y, en tal caso, su cardinalidad y opcionalidad;
3. referencias necesarias a resultados de viabilidad;
4. referencias de trazabilidad;
5. necesidad real de persistencia frente a representación transitoria;
6. patrones de acceso que justifiquen índices;
7. relación con Decision Versioning sin duplicar su autoridad.

La ausencia de estos cierres impide inferir un modelo físico definitivo.

---

## 20. Auditoría de cierre provisional

El contrato ha sido contrastado contra:

- `05_Motor/Decision_Twin.md`;
- `05_Motor/Viability_Frontier.md`;
- `05_Motor/Viability_Scenario_Engine.md`;
- `08_Implementacion/Assessment_Individual_Result_Contract.md`;
- `08_Implementacion/Decision_Versioning_Implementation_Contract.md`;
- `06_SQL/Decision_Versioning_Physical_Model.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`.

Resultado:

- no se crea autoridad paralela;
- comparación queda separada de selección;
- viabilidad queda separada de decisión;
- Scenario Engine conserva la autoridad sobre hipótesis y recálculo;
- Assessment permanece individual;
- evidencia permanece bajo su contrato;
- parámetros y dependencias no son modificados;
- versionado no se duplica;
- trazabilidad reutiliza referencias existentes y no crea un segundo Trace;
- persistencia física no se anticipa sin evidencia técnica suficiente.

**DICTAMEN: CONTRATO ALINEADO; MATERIALIZACIÓN FÍSICA AÚN NO AUTORIZADA.**

---

## 21. Estado

```text
CONTRATO FUNCIONAL                  CERRADO
FRONTERA DE AUTORIDAD               CERRADA
ENTRADA/SALIDA                      CERRADA
SEPARACIÓN DE VIABILITY             CERRADA
SEPARACIÓN DE SCENARIO ENGINE       CERRADA
SEPARACIÓN DE ASSESSMENT/EVIDENCE   CERRADA
SEPARACIÓN DE SELECCIÓN/DECISIÓN    CERRADA
IDENTIDAD DE ALTERNATIVE             PENDIENTE DE JUSTIFICACIÓN
RELACIÓN SCENARIO ↔ ALTERNATIVE      PENDIENTE DE JUSTIFICACIÓN
TRAZABILIDAD FÍSICA                 PENDIENTE DE DISEÑO
PERSISTENCIA FÍSICA                 PENDIENTE
DDL                                 PENDIENTE
IMPLEMENTACIÓN DE CÓDIGO            PENDIENTE
```

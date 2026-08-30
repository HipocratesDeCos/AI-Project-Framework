# EIOS — Decision Twin Implementation Contract

## 1. Identidad

**Documento:** Decision Twin Implementation Contract  
**Versión:** 1.0  
**Estado:** CERRADO — Contrato técnico de implementación  
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
├── identity
├── scenario reference
├── viability result
├── associated results
├── known consequences
└── traceability references
```

Estos elementos representan información ya producida por las autoridades correspondientes; Decision Twin no los recalcula.

---

## 5. Separación de identidades

Deben conservarse separadas:

```text
Scenario_ID       → identifica escenario
Alternative_ID    → identifica alternativa representada
Decision_ID       → identifica unidad decisional cuando corresponda
```

Ninguna de estas identidades sustituye a las demás.

Un escenario puede dar lugar a una alternativa representada, pero `Scenario_ID` no adquiere automáticamente semántica de `Alternative_ID`.

---

## 6. Entrada mínima

La implementación puede recibir:

- referencia al escenario evaluado, cuando exista;
- identidad de la alternativa;
- resultado de `Viability Frontier`;
- resultados de evaluación ya producidos;
- consecuencias conocidas ya determinadas;
- referencias de trazabilidad.

La ausencia de un elemento opcional no se convierte en un valor ficticio ni en una conclusión negativa.

---

## 7. Viability Frontier

`Decision Twin` consume el resultado de `Viability Frontier` y no lo determina.

```text
Assessment
    ↓
Viability Frontier
    ↓
Viability Result
    ↓
Decision Twin
```

No puede transformar:

```text
VIABLE              → COMPRAR
VIABLE CON CONDICIONES → COMPRAR CONDICIONADO
NOT_EVALUABLE       → NO COMPRAR
NOT_VIABLE          → decisión empresarial automática
```

La semántica de los cuatro estados permanece bajo `Viability Frontier`.

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

Las hipótesis que requieran evaluación formal regresan al `Scenario Engine`:

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

La representación debe permitir reconstruir la procedencia de la información comparada sin crear una segunda autoridad de evidencia.

Cadena mínima:

```text
Decision Twin
      ↓
Alternative
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
8. trazabilidad no puede adquirir autoridad decisional.

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

1. identificador técnico de alternativa;
2. relación física con escenario, cuando proceda;
3. referencias necesarias a resultados de viabilidad;
4. referencias de trazabilidad;
5. necesidad real de persistencia frente a representación transitoria;
6. patrones de acceso que justifiquen índices;
7. relación con Decision Versioning sin duplicar su autoridad.

La ausencia de estos cierres impide inferir un modelo físico definitivo.

---

## 20. Auditoría de cierre

El contrato ha sido contrastado contra:

- `05_Motor/Decision_Twin.md`;
- `05_Motor/Viability_Frontier.md`;
- `08_Implementacion/Assessment_Individual_Result_Contract.md`;
- `08_Implementacion/Decision_Versioning_Implementation_Contract.md`;
- `06_SQL/Decision_Versioning_Physical_Model.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`.

Resultado de la auditoría:

- no se crea autoridad paralela;
- comparación queda separada de selección;
- viabilidad queda separada de decisión;
- escenarios permanecen bajo Scenario Engine;
- Assessment permanece individual;
- evidencia permanece bajo su contrato;
- parámetros y dependencias no son modificados;
- versionado no se duplica;
- persistencia física no se anticipa sin evidencia técnica suficiente.

**DICTAMEN: CONTRATO DE IMPLEMENTACIÓN CERRADO PARA DISEÑO TÉCNICO.**

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
PERSISTENCIA FÍSICA                 PENDIENTE DE DISEÑO
DDL                                 PENDIENTE
IMPLEMENTACIÓN DE CÓDIGO            PENDIENTE
```

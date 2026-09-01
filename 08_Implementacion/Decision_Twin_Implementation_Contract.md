# EIOS — Decision Twin Implementation Contract

## 1. Identidad

**Documento:** Decision Twin Implementation Contract  
**Versión:** 1.1  
**Estado:** CERRADO — contrato técnico de implementación  
**Baseline:** EIOS Vertical MVP  
**Ubicación:** `08_Implementacion/Decision_Twin_Implementation_Contract.md`

## 2. Propósito

Este contrato define la frontera mínima de implementación de `Decision Twin` sin redefinir su contrato funcional.

La autoridad conceptual permanece en `05_Motor/Decision_Twin.md`.

`Decision Twin` representa y compara alternativas ya disponibles en el flujo EIOS. No crea una nueva autoridad normativa, decisional, de viabilidad, de escenarios, de negociación ni de resolución.

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

## 4. Objeto lógico

El objeto lógico de implementación es una **alternativa decisional representada** junto con los resultados y consecuencias autorizados que permitan su comparación.

Conceptualmente:

```text
Alternative representation
├── representation reference
├── scenario reference, when available
├── viability result
├── associated results
├── known consequences
└── traceability references
```

Estos elementos representan información ya producida por las autoridades correspondientes; Decision Twin no los recalcula.

La autoridad funcional no define una identidad persistente propia para `Alternative`. Por tanto, la implementación MVP no introduce un `Alternative_ID` ni presupone que la alternativa deba constituir una entidad física independiente.

## 5. Separación de identidades

Deben conservarse separadas las identidades que ya poseen autoridad documental:

```text
Scenario_ID       → identifica escenario
Decision_ID       → identifica unidad decisional cuando corresponda
```

`Alternative` es una opción representada para comparación, no una identidad funcional persistente definida por este contrato.

Por tanto:

```text
Scenario_ID ≠ Alternative
Alternative ≠ Decision_ID
```

`Scenario_ID` no adquiere automáticamente semántica de alternativa, y ninguna identidad existente puede reutilizarse como `Alternative_ID` por conveniencia física.

Si una futura necesidad técnica exige una identidad propia de alternativa, deberá justificarse y especificarse mediante autoridad documental antes de su materialización física.

## 6. Entrada mínima

La implementación recibe:

- referencia al escenario evaluado, cuando exista;
- referencia de representación de la alternativa, cuando sea necesaria y esté definida por la capa correspondiente;
- resultado de `Viability Frontier`;
- resultados de evaluación ya producidos;
- consecuencias conocidas ya determinadas;
- referencias de trazabilidad.

La ausencia de un elemento opcional no se convierte en un valor ficticio ni en una conclusión negativa.

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

Cuando una alternativa requiere una hipótesis, modificación o recálculo, dicha operación regresa al `Scenario Engine`.

`Decision Twin` no determina ni recalcula la viabilidad y no genera, modifica ni recalcula escenarios como mecanismo propio.

No puede transformar estados de viabilidad en decisiones empresariales.

La semántica de los estados de viabilidad permanece bajo `Viability Frontier`; la decisión empresarial permanece bajo las autoridades posteriores y el decisor humano.

## 8. Comparación

La implementación permite comparar dos o más alternativas disponibles sin convertir la comparación en selección.

La comparación puede exponer diferencias en:

- resultados;
- viabilidad;
- condiciones;
- consecuencias conocidas;
- riesgos ya determinados;
- referencias de trazabilidad.

La comparación no genera por sí misma una alternativa preferente.

## 9. No selección

No se implementan como comportamiento implícito:

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

## 10. Escenarios

`Decision Twin` no crea, modifica ni recalcula escenarios.

Las hipótesis que requieran evaluación formal regresan al `Scenario Engine`.

## 11. Assessment y Evidence

`Assessment` conserva exclusivamente el resultado individual de una regla.

`Decision Twin` no crea, modifica ni consolida `Assessment`.

La evidencia continúa bajo su contrato especializado. Decision Twin solo conserva referencias necesarias para trazabilidad y no determina suficiencia, admisibilidad o validez de evidencia.

## 12. Parámetros y dependencias

Los parámetros continúan bajo su autoridad propia.

Un valor concreto de una alternativa no modifica un parámetro del sistema.

La `Rule Dependency Matrix` conserva la autoridad sobre dependencias demostradas. Decision Twin no descubre, crea, elimina ni modifica dependencias.

## 13. Consecuencias

Solo pueden representarse consecuencias ya producidas o autorizadas por la capa que corresponda.

Decision Twin no inventa consecuencias normativas ni sustituye cálculos, reglas o evaluaciones.

Una consecuencia representada mantiene referencia a su fuente cuando esta exista.

## 14. Trazabilidad

La trazabilidad de `Decision Twin` se limita a conservar referencias a las fuentes ya existentes. No se crea un segundo mecanismo de Trace.

Cuando una alternativa proceda de un escenario evaluado, la referencia contextual puede conservar `Scenario_ID` cuando esté disponible. Esta referencia no convierte al escenario en identidad de la alternativa.

Cuando existan resultados C0 asociados, podrán conservarse sus referencias ya existentes, como `trace_id` o `input_fingerprint`, sin recalcularlos ni redefinir su semántica.

No se presume que un único `trace_id` sea suficiente para representar todos los resultados de una alternativa. Si una alternativa requiere múltiples resultados trazables, la implementación conserva las referencias correspondientes sin convertirlas en una nueva autoridad de evidencia.

## 15. Decision Versioning

Cuando una alternativa forme parte de un estado decisional versionado, Decision Twin puede conservar la referencia al `Decision_ID` o al contexto versionado correspondiente.

No crea una segunda política de versionado ni sobrescribe estados históricos.

La continuidad histórica permanece bajo `Decision Versioning`.

## 16. CRC y recomendación

Decision Twin no sustituye a CRC.

No consolida conflictos ni determina el motivo dominante de una recomendación.

Tampoco genera por sí mismo los resultados empresariales consolidados.

Estos permanecen bajo las autoridades posteriores definidas por el MED, CRC y la arquitectura autorizada.

## 17. Invariantes de implementación

La implementación conserva como invariantes:

1. una comparación no puede crear una selección automática;
2. una alternativa no puede convertirse en una decisión por su mera representación;
3. un resultado de viabilidad no puede cambiar de semántica al entrar en Decision Twin;
4. una hipótesis no puede modificar parámetros globales;
5. un escenario previo no puede imponer restricciones por mera continuidad histórica;
6. información redundante no puede crear un nuevo peso decisional por conteo;
7. ausencia de información opcional no puede producir valores ficticios;
8. trazabilidad no puede adquirir autoridad decisional;
9. un único `trace_id` no se presume suficiente para todos los resultados de una alternativa;
10. una referencia de trazabilidad no puede sustituir al objeto fuente ni alterar su ciclo de vida;
11. dos alternativas simultáneas no pueden distinguirse mediante una identidad física inventada por conveniencia;
12. la multiplicidad de alternativas no constituye por sí misma un requisito de persistencia.

## 18. Límites físicos

Para el Vertical MVP, `Decision Twin` no requiere una entidad SQL persistente propia de `Alternative`.

No se materializa una tabla `eios.alternative` ni un `Alternative_ID` mientras no exista un requisito funcional que exija conservar una identidad independiente de las referencias ya disponibles.

Tampoco se crean índices específicos de `Decision Twin` para una entidad que no existe físicamente.

Los datos que deban conservar continuidad histórica permanecen bajo las estructuras de `Decision Versioning` y las autoridades fuente correspondientes.

Este contrato no fija API ni serialización concreta.

## 19. Dependencias de una futura persistencia

Una futura persistencia específica solo podrá plantearse si se demuestra, mediante requisito o caso de uso verificable:

1. necesidad de reconstruir una alternativa como entidad independiente;
2. necesidad de distinguir múltiples alternativas más allá del contexto ya disponible;
3. identidad y ciclo de vida de esa entidad;
4. relación con `Scenario_ID`, si existe;
5. referencias de trazabilidad necesarias;
6. necesidad real de almacenamiento frente a representación transitoria;
7. patrones de acceso que justifiquen índices;
8. relación con Decision Versioning sin duplicar su autoridad.

La ausencia de cualquiera de estos elementos impide inferir persistencia física.

## 20. Estado de materialización

La implementación ejecutable del Vertical MVP está materializada en `eios/core/decision_twin.py` y `eios/core/decision_twin_engine.py`, con cobertura en los tests específicos de Decision Twin.

La implementación actual es de representación/comparación en memoria y no requiere persistencia SQL propia de `Alternative`.

Por tanto, no existe un estado pendiente de implementación para el contrato actual. La ausencia de DDL específico es una decisión de frontera física, no una carencia de materialización.

## 21. Auditoría de cierre

El contrato ha sido contrastado contra:

- `05_Motor/Decision_Twin.md`;
- `05_Motor/Viability_Frontier.md`;
- `05_Motor/Viability_Scenario_Engine.md`;
- `08_Implementacion/Assessment_Individual_Result_Contract.md`;
- `08_Implementacion/Decision_Versioning_Implementation_Contract.md`;
- `05_Motor/Modelo_Empresarial_Decision.md`;
- implementación ejecutable y tests de Decision Twin.

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
- `Alternative` no se convierte artificialmente en entidad persistente;
- no se justifican índices propios de una entidad inexistente;
- C0 permanece intacto.

**DICTAMEN: CONTRATO DE IMPLEMENTACIÓN CERRADO Y MATERIALIZADO; NO PROCEDE DDL ESPECÍFICO PARA `Alternative` EN EL VERTICAL MVP.**

## 22. Estado

```text
CONTRATO FUNCIONAL                  CERRADO
FRONTERA DE AUTORIDAD               CERRADA
ENTRADA/SALIDA                      CERRADA
SEPARACIÓN DE VIABILITY             CERRADA
SEPARACIÓN DE SCENARIO ENGINE       CERRADA
SEPARACIÓN DE ASSESSMENT/EVIDENCE   CERRADA
SEPARACIÓN DE SELECCIÓN/DECISIÓN    CERRADA
IDENTIDAD DE ALTERNATIVE             CERRADA: no persistente en MVP
RELACIÓN SCENARIO ↔ ALTERNATIVE      CERRADA: contextual/opcional
TRAZABILIDAD                         CERRADA: referencias existentes
PERSISTENCIA DE ALTERNATIVE          CERRADA: no requerida en MVP
DDL ESPECÍFICO ALTERNATIVE           NO PROCEDE
IMPLEMENTACIÓN DE CÓDIGO             MATERIALIZADA
TESTS                                MATERIALIZADOS
CI                                   VERIFICADA
```

## Historial

### v1.1

Corrección documental post-materialización. Se actualiza el estado de implementación para reflejar el código ejecutable y los tests existentes. Se mantiene la decisión de no crear persistencia SQL específica para `Alternative`. No se modifica el contrato funcional ni se añade autoridad.

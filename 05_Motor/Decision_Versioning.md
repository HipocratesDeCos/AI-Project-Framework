# Decision Versioning

## EIOS — Enterprise Intelligent Operations System

**Estado:** CERRADO — Diseño documental  
**Fase:** 8 — Implementación Técnica  
**Naturaleza:** Capacidad de continuidad histórica del estado decisional EIOS

---

# 1. Propósito

Decision Versioning define la capacidad de EIOS para conservar la continuidad histórica de los **estados decisionales de EIOS** y las referencias necesarias para permitir su reconstrucción.

Su finalidad es garantizar que un estado decisional anterior pueda ser identificado y relacionado con el contexto, escenario, datos y versiones de componentes que correspondían a dicho estado.

Decision Versioning no constituye un nuevo motor de decisión ni una nueva autoridad funcional.

---

# 2. Principio fundamental

Decision Versioning debe distinguir estrictamente entre:

1. **estado decisional EIOS**;
2. **recomendación generada por EIOS**;
3. **decisión empresarial humana**.

EIOS puede analizar, evaluar, consolidar y recomendar.

La decisión empresarial final permanece fuera de la autoridad de Decision Versioning y de EIOS cuando corresponda al decisor humano.

Por tanto:

```text
EIOS
  ↓
evaluación
  ↓
consolidación
  ↓
recomendación
  ↓
decisor humano
  ↓
decisión empresarial
```

Decision Versioning conserva la continuidad histórica del estado decisional EIOS; no convierte la recomendación en decisión humana.

---

# 3. Definición de Decision_ID

`Decision_ID` identifica la **unidad decisional EIOS** a la que pertenecen el contexto, la entrada y las evaluaciones asociadas.

No identifica por sí mismo:

- al CEO;
- al decisor humano;
- la persona que aprueba una compra;
- el acto empresarial final.

La identidad de la unidad decisional EIOS debe permanecer diferenciada de la identidad de la decisión empresarial humana.

C0 utiliza `decision_id` como parte de la identidad contextual de una evaluación y exige su coherencia entre `InputContract` y `DecisionContext`.

Por tanto, Decision Versioning reutiliza `Decision_ID` y no redefine su significado.

---

# 4. Estado decisional EIOS

Un estado decisional representa el contexto identificable de EIOS correspondiente a un momento determinado del proceso decisional.

Conceptualmente puede incluir referencias a:

- `Decision_ID`;
- `Scenario_ID`;
- `Data_Snapshot_ID`;
- `Rules_Version`;
- `Parameters_Version`;
- `Forecast_Version`, cuando resulte aplicable;
- `RFP_Version`, cuando resulte aplicable;
- `EIOS_Version`;
- `Timestamp`;
- `User`;
- referencias a resultados y trazas pertinentes.

Estos elementos permiten relacionar el estado decisional con los artefactos y versiones que participaron en él.

La presencia de una referencia no implica que Decision Versioning adquiera la autoridad sobre el artefacto referenciado.

---

# 5. Versionado sin duplicación de autoridades

Decision Versioning no crea sistemas paralelos para versionar componentes que ya disponen de autoridad propia.

En particular:

```text
Scenario Version
    ≠
Decision State Version
```

```text
Rules Version
    ≠
Decision State Version
```

```text
Parameters Version
    ≠
Decision State Version
```

Decision Versioning conserva referencias a esas versiones cuando forman parte del estado decisional.

La autoridad sobre cada componente permanece en su correspondiente capa o artefacto.

---

# 6. Relación con C0

C0 mantiene la autoridad sobre la evaluación que ejecuta.

C0 proporciona mecanismos de reproducibilidad que incluyen, según corresponda:

- `DecisionContext`;
- `Decision_ID`;
- `Scenario_ID`;
- `Rules_Version`;
- `Parameters_Version`;
- `Data_Snapshot_ID`;
- `InputContract`;
- `input_fingerprint`;
- `Trace`.

Decision Versioning puede utilizar estas referencias para reconstruir el estado decisional al que perteneció una evaluación.

Decision Versioning:

- no ejecuta C0;
- no redefine `Trace`;
- no genera un segundo `Trace`;
- no redefine `input_fingerprint`;
- no genera un segundo fingerprint para sustituir al de C0;
- no modifica el contrato de C0.

---

# 7. Fingerprint

El `input_fingerprint` identifica criptográficamente el `InputContract` evaluado por C0.

No constituye por sí mismo una versión del estado decisional.

Por tanto:

```text
input_fingerprint
    ↓
identidad del InputContract
```

no:

```text
input_fingerprint
    ↓
Decision Version
```

Decision Versioning puede conservar o referenciar el fingerprint producido por C0 cuando sea necesario para la reconstrucción.

No introduce un mecanismo alternativo de fingerprinting sin autoridad documental específica.

---

# 8. Trace

`Trace` representa la trazabilidad de la evaluación realizada por C0.

No representa por sí mismo el estado decisional completo.

Decision Versioning puede mantener una referencia a las trazas pertinentes, pero no asume su generación, semántica ni gobierno.

La relación conceptual es:

```text
Decision State
      │
      └── referencias C0
              ├── input_fingerprint
              └── Trace
```

y no:

```text
Decision Versioning
      ↓
genera Trace
```

---

# 9. Data Snapshot

`Data_Snapshot_ID` forma parte del contexto decisional utilizado por C0.

Decision Versioning puede conservar la referencia al snapshot correspondiente.

No crea un concepto paralelo de snapshot ni redefine el significado de `Data_Snapshot_ID`.

La capacidad de reconstrucción dependerá de que el artefacto histórico referenciado permanezca disponible conforme a la autoridad responsable de dicho artefacto.

---

# 10. Reconstrucción histórica

La finalidad del versionado es permitir responder, para un estado decisional determinado:

> ¿Qué contexto decisional EIOS existía en ese momento?

La reconstrucción puede requerir relacionar:

```text
Decision_ID
      ↓
Scenario_ID
      ↓
Data_Snapshot_ID
      ↓
Rules_Version
Parameters_Version
Forecast_Version
RFP_Version
EIOS_Version
      ↓
Timestamp
      ↓
User
      ↓
referencias de evaluación
      ├── input_fingerprint
      └── Trace
```

Decision Versioning conserva las referencias necesarias para posibilitar esta reconstrucción.

---

# 11. Salvaguarda de reconstrucción

La existencia de una referencia histórica no garantiza por sí sola que el artefacto referenciado continúe físicamente disponible.

Por tanto, Decision Versioning **no debe prometer recuperación histórica absoluta** cuando las autoridades correspondientes hayan perdido, eliminado o dejado inaccesibles los artefactos necesarios.

La obligación de Decision Versioning es:

> conservar las referencias necesarias para permitir la reconstrucción del estado decisional.

La recuperación efectiva dependerá de la disponibilidad de los artefactos históricos referenciados.

Esta distinción es obligatoria.

---

# 12. Continuidad histórica

Los cambios relevantes en el contexto decisional no deben destruir la capacidad de identificar estados anteriores.

Un nuevo estado decisional debe poder distinguirse conceptualmente de un estado precedente sin sobrescribir su significado histórico.

Decision Versioning conserva la continuidad:

```text
Estado A
   ↓
Estado B
   ↓
Estado C
```

sin asumir que los estados anteriores deben modificarse para reflejar cambios posteriores.

---

# 13. Recomendación y decisión humana

La recomendación de EIOS no equivale a la decisión empresarial.

Por tanto:

```text
Resultado / recomendación EIOS
          ≠
Decisión humana
```

Decision Versioning puede conservar la referencia al estado en el que se produjo una recomendación.

No debe interpretar automáticamente que:

- `COMPRAR` significa que se compró;
- `NEGOCIAR` significa que se negoció;
- `COMPRAR CONDICIONADO` significa que se autorizó;
- `NO COMPRAR` significa que se rechazó;
- `INFORMACIÓN INSUFICIENTE` significa que el decisor rechazó la operación.

La actuación posterior del decisor pertenece a una dimensión distinta.

---

# 14. User

`User` representa al usuario asociado al estado registrado.

No debe interpretarse automáticamente como:

- decisor;
- CEO;
- aprobador;
- propietario de la decisión;
- responsable jurídico de la operación.

La semántica de roles de usuario no se amplía mediante Decision Versioning.

---

# 15. Timestamp

`Timestamp` identifica temporalmente el estado registrado.

Los detalles físicos de:

- formato;
- precisión;
- zona horaria;
- origen del reloj;
- almacenamiento;

quedan fuera del diseño conceptual y deberán definirse en la implementación autorizada correspondiente.

---

# 16. Límites de autoridad

Decision Versioning **NO**:

- evalúa reglas;
- genera evidencias;
- crea escenarios;
- versiona escenarios;
- gobierna reglas;
- gobierna parámetros;
- calcula viabilidad;
- consolida conflictos;
- genera recomendaciones;
- ejecuta compras;
- toma decisiones empresariales;
- sustituye a CRC;
- sustituye a C0;
- redefine `Trace`;
- redefine `input_fingerprint`;
- crea snapshots alternativos;
- crea una segunda jerarquía de autoridad.

---

# 17. Relación con Assurance

Decision Versioning proporciona continuidad histórica y referencias de reconstrucción.

Assurance puede utilizar esta capacidad para verificar:

- qué contexto existía;
- qué escenario se utilizaba;
- qué datos fueron referenciados;
- qué versiones de componentes estaban vigentes;
- qué evaluación fue realizada;
- cuándo ocurrió;
- qué usuario estaba asociado.

Decision Versioning no sustituye las funciones propias de Assurance.

---

# 18. Relación con Decision Twin

Decision Twin y Decision Versioning tienen funciones complementarias.

Decision Versioning conserva la continuidad histórica del estado decisional.

Decision Twin puede utilizar dicha continuidad y sus referencias para reproducir o explorar contextos decisionales conforme a su propio contrato.

Decision Versioning no absorbe las responsabilidades de Decision Twin.

---

# 19. Principios de integridad

### 19.1 No apropiación de autoridad

Ninguna referencia conservada por Decision Versioning transfiere la autoridad del artefacto referenciado.

### 19.2 No duplicación

No se crean mecanismos paralelos de versionado, fingerprint, snapshot o trace cuando ya existen autoridades establecidas.

### 19.3 No confusión entre EIOS y decisión humana

La identidad de la unidad decisional EIOS no se utiliza para representar automáticamente la decisión empresarial humana.

### 19.4 Reconstrucción basada en referencias

La reconstrucción se basa en referencias históricas a artefactos y versiones existentes.

### 19.5 Preservación histórica

Los estados anteriores deben permanecer distinguibles y reconstruibles en la medida permitida por la disponibilidad de sus artefactos históricos.

---

# 20. Modelo conceptual cerrado

```text
                         DECISION_ID
                              │
                              ▼
                   UNIDAD DECISIONAL EIOS
                              │
                              ▼
                    ESTADO DECISIONAL
                              │
          ┌───────────────────┼───────────────────┐
          │                   │                   │
          ▼                   ▼                   ▼
     Scenario_ID       Data_Snapshot_ID      Versiones
          │                   │                   │
          ▼                   ▼                   ▼
 Scenario Engine          Datos           Rules / Parameters
                                              / Forecast / RFP
                              │
                              ▼
                             C0
                              │
                    ┌─────────┴─────────┐
                    ▼                   ▼
             Input Fingerprint        Trace
                    │                   │
                    └─────────┬─────────┘
                              ▼
                    RECONSTRUCCIÓN HISTÓRICA
                              │
                              ▼
                     RECOMENDACIÓN EIOS
                              │
                              ▼
                     DECISOR HUMANO
                              │
                              ▼
                    DECISIÓN EMPRESARIAL
```

---

# 21. Criterio de cierre

El diseño de Decision Versioning se considera cerrado cuando:

1. `Decision_ID` se interpreta como identidad de la unidad decisional EIOS.
2. Se mantiene separada la recomendación EIOS de la decisión humana.
3. Se reutilizan las capacidades de reproducibilidad existentes en C0.
4. No se introduce un fingerprint paralelo.
5. No se introduce un snapshot paralelo.
6. No se introduce un Trace paralelo.
7. Las versiones de escenarios, reglas, parámetros y demás componentes permanecen bajo sus respectivas autoridades.
8. Las referencias históricas permiten plantear la reconstrucción del estado decisional.
9. No se garantiza recuperación cuando los artefactos históricos referenciados ya no estén disponibles.
10. No se introduce ninguna nueva autoridad funcional no respaldada por la arquitectura.

---

# 22. Estado

**DISEÑO DOCUMENTAL: CERRADO**

No se autoriza mediante este documento ninguna implementación física concreta.

La materialización y cualquier eventual implementación deberán someterse posteriormente a la secuencia de gobierno establecida para Fase 8.

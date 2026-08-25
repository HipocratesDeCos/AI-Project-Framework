# EIOS — DSS FUNCTIONAL ARCHITECTURE

## Arquitectura Funcional del Decision Support System

**Versión:** 1.1  
**Estado:** OFICIAL — BASELINE  
**Ámbito:** EIOS Vertical MVP — Decision & Negotiation Intelligence para compras  
**Autoridad:** Arquitectura funcional DSS

---

# 1. PROPÓSITO

Este documento define la **arquitectura funcional del DSS de EIOS Vertical MVP**, estableciendo cómo fluye una decisión de compra desde la entrada del usuario hasta la decisión empresarial del CEO.

Define:

- fronteras funcionales;
- flujo de información;
- Pantalla 1;
- contrato de entrada;
- procesamiento del motor;
- resultado base;
- Pantalla 2;
- variables de escenario;
- Scenario Engine;
- Viability;
- alternativas;
- Decision Twin;
- Negotiation;
- Negotiation Ladder;
- CRC;
- Decision Package;
- salida al CEO;
- trazabilidad;
- Assurance transversal.

No define fórmulas, reglas concretas, parámetros concretos, SQL, APIs ni implementación técnica.

---

# 2. RELACIÓN CON LA ARQUITECTURA EIOS

La jerarquía documental es:

```text
SALVAGUARDA
     ↓
ARCHITECTURE BLUEPRINT
     ↓
DSS FUNCTIONAL ARCHITECTURE
     ↓
ESPECIFICACIÓN FUNCIONAL
     ↓
REGLAS / MOTOR / IMPLEMENTACIÓN
```

El presente documento **desarrolla funcionalmente** el `Architecture_Blueprint.md`, pero no lo sustituye.

Tampoco sustituye la Salvaguarda, la Especificación Funcional, el Modelo Empresarial de Decisión, las Reglas ni el Centro de Parametrización.

---

# 3. PRINCIPIO FUNCIONAL CENTRAL

> **EIOS recibe hechos y evidencia, procesa la información mediante sus componentes decisionales, permite modificar hipótesis controladas para generar escenarios, compara alternativas viables y entrega una recomendación trazable al decisor humano.**

Principio de control humano:

> **EIOS analiza, simula, explica y recomienda; el CEO decide.**

---

# 4. FLUJO FUNCIONAL EXTREMO A EXTREMO

```text
PANTALLA 1
    ↓
DATOS + EVIDENCIA
    ↓
DECISION INPUT PACKAGE
    ↓
QUALITY & TRUST
    ↓
PRICE
    ↓
TCO
    ↓
STOCK / DEMANDA
    ↓
FINANZAS
    ↓
PROVEEDOR / RIESGO
    ↓
VIABILITY FRONTIER
    ↓
RESULTADO BASE
    ↓
PANTALLA 2
    ↓
VARIABLES DE ESCENARIO
    ↓
SCENARIO ENGINE
    ↓
VIABILITY
    ↓
ALTERNATIVAS VIABLES
    ↓
DECISION TWIN
    ↓
COMPARACIÓN
    ↓
NEGOTIATION
    ↓
NEGOTIATION LADDER
    ↓
CRC
    ↓
RESULTADO / RECOMENDACIÓN EIOS
    ↓
DECISION PACKAGE
    ↓
CEO
    ↓
DECISIÓN EMPRESARIAL
```

**Assurance, trazabilidad y versionado atraviesan todo el flujo.**

---

# 5. SEPARACIÓN DE RESPONSABILIDADES

| Elemento | Función |
|---|---|
| **Dato** | Representa un hecho |
| **Evidencia** | Sustenta un dato o afirmación |
| **Parámetro** | Configura el comportamiento autorizado |
| **Regla** | Determina una evaluación |
| **Variable de escenario** | Representa una hipótesis |
| **Cálculo** | Resultado derivado |
| **Resultado** | Evaluación producida por EIOS |
| **Recomendación** | Resultado decisional consolidado |
| **Decisión** | Determinación empresarial del CEO |

---

# 6. PANTALLA 1 — ENTRADA

Pantalla 1 representa la **propuesta de compra real**.

Puede recoger:

### Identificación
- artículo;
- código;
- familia;
- proveedor;
- fecha;
- identificador de decisión.

### Compra
- cantidad;
- unidad;
- precio;
- importe;
- descuentos;
- rappels;
- transporte;
- otros costes;
- condiciones comerciales.

### Logística
- entrega;
- plazo;
- condiciones logísticas.

### Finanzas
- plazo de pago;
- forma de pago;
- condiciones financieras.

### Evidencia
- oferta;
- presupuesto;
- documento proveedor;
- referencia;
- fuente;
- fecha.

Pantalla 1 **no modifica reglas ni parámetros estructurales y no produce la decisión**.

---

# 7. DECISION INPUT PACKAGE

Pantalla 1 proporciona datos y evidencia.

EIOS incorpora además la información empresarial y la parametrización vigente:

```text
PANTALLA 1
    │
    ├── DATOS
    └── EVIDENCIA
          │
          ├──────────────┐
          ▼              ▼
DATOS EMPRESARIALES   PARAMETRIZACIÓN
          │              │
          └──────┬───────┘
                 ▼
       DECISION INPUT PACKAGE
```

Los parámetros son resueltos desde el **Centro de Parametrización**, no introducidos libremente desde Pantalla 1.

El paquete debe ser identificable y trazable.

---

# 8. QUALITY & TRUST

El paquete de entrada pasa por Quality & Trust antes de la evaluación correspondiente.

Estados funcionales:

```text
APTO
APTO CON ADVERTENCIAS
NO APTO
```

La calidad insuficiente de información crítica no debe transformarse silenciosamente en un valor falso o supuesto.

---

# 9. MOTOR ANALÍTICO

Las capas analíticas principales son:

```text
PRICE
  ↓
TCO
  ↓
STOCK / DEMANDA
  ↓
FINANZAS
  ↓
PROVEEDOR / RIESGO
```

Son **componentes del motor**, no necesariamente pantallas.

El motor produce una evaluación inicial de la operación.

---

# 10. VIABILITY FRONTIER

La operación se evalúa respecto de sus restricciones y condiciones de viabilidad.

```text
EVALUACIÓN BASE
      ↓
VIABILITY FRONTIER
```

Estados posibles:

- viable;
- viable con condiciones;
- no viable;
- no evaluable.

Principio:

> **Viable ≠ Comprar.**

La viabilidad no constituye por sí misma una decisión empresarial.

---

# 11. RESULTADO BASE

El Resultado Base representa la situación de la operación **bajo las condiciones reales actuales**.

Puede contener:

- resultado de Quality & Trust;
- precio;
- TCO;
- stock;
- impacto financiero;
- proveedor/riesgo;
- viabilidad;
- alertas;
- restricciones;
- confianza;
- motivos principales.

### Regla

> **El Resultado Base no constituye por sí mismo la recomendación final.**

Todavía pueden existir escenarios, negociación, excepciones y consolidación CRC.

---

# 12. PANTALLA 2 — SIMULACIÓN

Pantalla 2 es una **interfaz de simulación controlada**.

Su pregunta funcional es:

> **¿Qué pasa si cambio esta condición?**

No modifica:

- históricos;
- evidencias;
- reglas;
- parámetros estructurales;
- salvaguardas;
- resultados anteriores.

Modifica exclusivamente **hipótesis autorizadas de escenario**.

---

# 13. VARIABLES DE ESCENARIO

Podrán ser simulables, cuando estén autorizadas:

- precio;
- cantidad;
- descuento;
- rappel;
- plazo de pago;
- condiciones financieras;
- entrega;
- plazo de entrega;
- condiciones logísticas;
- otras variables negociables.

Cada variable debe disponer, cuando corresponda, de:

- valor base;
- valor simulado;
- unidad;
- rango;
- restricciones;
- autorización;
- origen;
- versión.

---

# 14. SCENARIO INPUT SET

Pantalla 2 genera:

```text
SCENARIO INPUT SET
│
├── Variable
├── Valor base
├── Valor simulado
├── Unidad
├── Restricciones
├── Usuario
├── Fecha/hora
└── Versión
```

El escenario constituye una nueva representación de hipótesis.

**No sobrescribe la operación real.**

---

# 15. SCENARIO ENGINE

El Scenario Engine:

- crea escenarios;
- versiona escenarios;
- conserva escenarios anteriores;
- recalcula;
- identifica diferencias;
- mantiene trazabilidad.

```text
ESCENARIO BASE
      ↓
HIPÓTESIS MODIFICADAS
      ↓
NUEVO ESCENARIO
      ↓
RECALCULACIÓN
      ↓
RESULTADO DEL ESCENARIO
```

Un cambio de escenario puede afectar a varias capas del motor.

---

# 16. VIABILITY DE ESCENARIOS

Cada escenario debe ser evaluado respecto de las restricciones aplicables.

```text
ESCENARIO
   ↓
EVALUACIÓN
   ↓
VIABILITY
```

Solo los escenarios admisibles pueden continuar como alternativas.

---

# 17. ALTERNATIVAS

La arquitectura distingue:

**Escenario ≠ Alternativa.**

```text
ESCENARIOS
    ↓
VIABILITY
    ↓
ALTERNATIVAS VIABLES
```

Una alternativa es una opción susceptible de comparación y decisión.

---

# 18. DECISION TWIN

El Decision Twin representa dinámicamente la operación y sus escenarios.

Su función es permitir evaluar las consecuencias de modificar condiciones.

Recibe:

```text
ALTERNATIVAS VIABLES
        +
RESULTADOS
        +
CRITERIOS APLICABLES
```

Y permite:

- comparar;
- identificar diferencias;
- analizar consecuencias;
- estudiar ventajas y desventajas;
- preparar la negociación.

### No es:

- un segundo motor;
- un gemelo digital empresarial completo;
- una autoridad decisional;
- un sustituto de la CRC.

---

# 19. EVALUACIÓN Y COMPARACIÓN

Las alternativas pueden compararse según los criterios y reglas aplicables.

La comparación puede considerar:

- TCO;
- impacto financiero;
- stock;
- riesgo;
- condiciones comerciales;
- condiciones logísticas;
- robustez;
- negociación.

### Regla arquitectónica

> **6.2 no establece una fórmula definitiva de scoring decisional.**

Una puntuación auxiliar podrá existir si es definida y aprobada por la autoridad correspondiente.

Los bloqueos críticos **no pueden compensarse automáticamente mediante una puntuación**.

---

# 20. NEGOTIATION INTELLIGENCE

EIOS puede proporcionar inteligencia para negociación:

- objetivos;
- primera petición;
- concesiones;
- reciprocidad;
- variables negociables;
- intercambios de valor;
- fallback;
- walk-away.

EIOS **no ejecuta autónomamente la negociación** en el Vertical MVP.

---

# 21. NEGOTIATION LADDER

La negociación puede estructurarse:

```text
OBJETIVO
   ↓
PRIMERA PETICIÓN
   ↓
CONCESIÓN 1
   ↓
CONCESIÓN 2
   ↓
FALLBACK
   ↓
WALK-AWAY
```

Cada escalón debe respetar restricciones, reglas y salvaguardas.

---

# 22. CRC

La CRC realiza el **control y consolidación final del resultado EIOS**.

Recibe:

- datos;
- evidencia;
- parámetros aplicados;
- reglas;
- resultados;
- escenarios;
- alternativas;
- negociación;
- excepciones;
- trazabilidad.

La CRC produce el resultado/recomendación EIOS dentro de las categorías establecidas:

```text
COMPRAR
NEGOCIAR
COMPRAR CONDICIONADO
NO COMPRAR
INFORMACIÓN INSUFICIENTE
```

### Distinción fundamental

```text
CRC
 ↓
RESULTADO / RECOMENDACIÓN EIOS
 ↓
CEO
 ↓
DECISIÓN EMPRESARIAL
```

La CRC **no sustituye al CEO**.

---

# 23. DECISION PACKAGE

El resultado consolidado se presenta mediante un `Decision Package`.

Incluye, según corresponda:

- recomendación;
- alternativa preferente;
- alternativas comparadas;
- impacto económico;
- impacto financiero;
- impacto operativo;
- riesgos;
- condiciones;
- negociación;
- confianza;
- alertas;
- supuestos;
- trazabilidad.

El Decision Package es una **representación ejecutiva del resultado**, no una decisión autónoma.

---

# 24. SALIDA AL CEO

El CEO debe recibir prioritariamente:

1. recomendación;
2. alternativa preferente;
3. motivos;
4. impacto;
5. riesgos;
6. condiciones;
7. confianza;
8. alertas.

El detalle puede consultarse bajo demanda.

```text
EIOS
 ↓
ANALIZA
 ↓
SIMULA
 ↓
COMPARA
 ↓
EXPLICA
 ↓
RECOMIENDA
 ↓
CEO
 ↓
DECIDE
```

---

# 25. CONTRATOS FUNCIONALES

### Pantalla 1 → EIOS

```text
DATOS + EVIDENCIA
        ↓
DECISION INPUT PACKAGE
```

### EIOS → Pantalla 2

```text
RESULTADO BASE
+
VARIABLES SIMULABLES
+
RESTRICCIONES
```

### Pantalla 2 → Scenario Engine

```text
VARIABLES DE ESCENARIO
```

### Scenario Engine → Decision Twin

```text
ESCENARIOS EVALUADOS
+
RESULTADOS DE VIABILITY
```

### Decision Twin → Negotiation

```text
ALTERNATIVAS VIABLES
+
RESULTADOS COMPARABLES
```

### Negotiation → CRC

```text
ALTERNATIVAS
+
ESTRATEGIA
+
NEGOTIATION LADDER
+
CONDICIONES
```

### CRC → CEO

```text
RESULTADO EIOS
+
DECISION PACKAGE
```

---

# 26. TRAZABILIDAD

Una decisión debe poder reconstruirse mediante:

```text
Decision_ID
Scenario_ID
Data_Snapshot_ID
Rules_Version
Parameters_Version
Forecast_Version
RFP_Version
EIOS_Version
Timestamp
User
```

La pregunta que debe poder responderse es:

> **Qué se decidió, con qué datos, evidencia, reglas, parámetros y versión, cuándo y por quién.**

---

# 27. ASSURANCE TRANSVERSAL

Assurance **no es una fase**.

Atraviesa:

```text
PANTALLA 1
   │
QUALITY & TRUST
   │
MOTOR
   │
ESCENARIOS
   │
DECISION TWIN
   │
NEGOCIACIÓN
   │
CRC
   │
CEO
```

Incluye, según corresponda:

- Quality & Trust;
- Data Lineage & Provenance;
- Evidence Contract;
- Decision Versioning;
- trazabilidad;
- control de overrides;
- fail-safe;
- validación;
- monitorización.

---

# 28. RESPONSABILIDADES

```text
USUARIO
  ↓
Introduce hechos y evidencia
  ↓
EIOS
  ↓
Valida / calcula / simula / compara
  ↓
USUARIO AUTORIZADO
  ↓
Modifica hipótesis
  ↓
EIOS
  ↓
Recalcula / explica / recomienda
  ↓
CRC
  ↓
Consolida resultado EIOS
  ↓
CEO
  ↓
Decide
```

---

# 29. FRONTERAS ARQUITECTÓNICAS

### Usuario

Puede:

- introducir datos;
- aportar evidencia;
- consultar;
- simular;
- comparar;
- revisar;
- utilizar inteligencia de negociación.

### Usuario no puede desde el DSS

- modificar reglas;
- alterar históricos;
- modificar salvaguardas;
- sobrescribir evidencias;
- alterar resultados anteriores;
- cambiar parámetros estructurales sin autorización.

### EIOS

Puede:

- validar;
- calcular;
- simular;
- evaluar;
- comparar;
- explicar;
- recomendar.

No puede en el Vertical MVP:

- decidir autónomamente;
- ejecutar automáticamente una compra;
- ejecutar autónomamente una negociación.

---

# 30. LÍMITES DEL DOCUMENTO

No define:

- fórmulas de Price;
- fórmula PMR;
- fórmula detallada TCO;
- forecasting;
- reglas concretas;
- catálogo de parámetros;
- fórmula de scoring;
- SQL;
- APIs;
- arquitectura técnica de frontend;
- diseño visual;
- algoritmos de optimización.

Estos elementos pertenecen a sus respectivas fuentes de autoridad.

---

# 31. PRINCIPIOS CONGELADOS

1. Pantalla 1 representa la realidad inicial.
2. Pantalla 1 no decide.
3. El motor recibe un contexto estructurado.
4. Quality & Trust precede a la evaluación cuando corresponda.
5. Las capas analíticas son componentes del motor.
6. Pantalla 2 es una interfaz de simulación.
7. Las simulaciones modifican hipótesis, no realidad.
8. Los escenarios son versionables.
9. Viable ≠ Comprar.
10. Escenario ≠ Alternativa.
11. Decision Twin ≠ segundo motor.
12. No se establece scoring decisional en 6.2.
13. Los bloqueos críticos no se compensan mediante scoring.
14. Negotiation utiliza alternativas viables.
15. CRC consolida el resultado EIOS.
16. Decision Package no sustituye al CEO.
17. EIOS recomienda.
18. CEO decide.
19. Assurance es transversal.
20. Toda decisión relevante debe ser reconstruible.

---

# 32. ESTADO DOCUMENTAL

**Documento:** `DSS_Functional_Architecture.md`  
**Versión:** 1.1  
**Ámbito:** EIOS Vertical MVP  
**Autoridad:** Arquitectura funcional DSS  
**Estado:** **OFICIAL — BASELINE**  
**Ubicación:** `03_Arquitectura/DSS_Functional_Architecture.md`

Documento aprobado dentro del proceso de gobierno documental de EIOS.

---

# 33. PRINCIPIO FINAL

> **EIOS transforma una propuesta de compra en una decisión estructurada mediante análisis, simulación, comparación y negociación asistida, manteniendo trazabilidad, control humano y separación entre realidad, hipótesis y decisión.**

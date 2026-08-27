# Negotiation Intelligence

## 1. Identidad y propósito

`Negotiation Intelligence` es el componente especializado de EIOS responsable de **razonar, determinar y justificar el contenido negociador** a partir de información, evidencia, escenarios, resultados, restricciones y límites procedentes de fuentes autorizadas.

Su finalidad es transformar información relevante para la negociación en **contenido negociador determinado y justificado**, manteniendo trazabilidad sobre las bases que sustentan dicho razonamiento.

Negotiation Intelligence puede analizar:

- posiciones;
- variables negociables;
- intercambio de valor;
- concesiones;
- contraprestaciones;
- trade-offs;
- alternativas;
- BATNA;
- ZOPA cuando resulte evaluable;
- sensibilidad;
- robustez;
- reciprocidad;
- condiciones de negociación;
- señales e inferencias negociadoras.

Negotiation Intelligence **no constituye un componente decisional autónomo**.

No decide, no aprueba, no ejecuta y no activa Strategy.

---

# 2. Posición arquitectónica

Negotiation Intelligence pertenece al dominio especializado de negociación dentro del motor EIOS.

Su posición funcional es:

```text
Viability Frontier
        ↓
Scenario Engine
        ↓
Decision Twin
        ↓
Negotiation Intelligence
        ↓
Negotiation Ladder
        ↓
Capa de Resolución de Conflictos
        ↓
Autoridad decisional
```

Esta secuencia representa relaciones funcionales y de información; no concede a NI autoridad sobre los componentes precedentes ni posteriores.

---

# 3. Responsabilidad principal

La responsabilidad principal de Negotiation Intelligence es:

> **determinar qué contenido negociador está justificado dadas las condiciones, evidencias, resultados y restricciones disponibles.**

Esto incluye determinar y justificar, cuando proceda:

- movimientos negociadores;
- primera petición;
- concesiones;
- contraprestaciones;
- intercambios entre variables;
- paquetes;
- alternativas;
- fallback;
- condiciones negociadoras;
- conveniencia relativa de distintas vías negociadoras.

La determinación se realiza dentro de las fronteras de autoridad de EIOS.

---

# 4. Variables negociables

Negotiation Intelligence puede trabajar con múltiples dimensiones simultáneamente.

Entre ellas pueden encontrarse:

- precio;
- volumen;
- plazo;
- condiciones de pago;
- servicio;
- garantías;
- compromisos;
- condiciones contractuales;
- otras variables formalmente disponibles para la negociación.

La existencia de una variable no implica que pueda modificarse libremente.

Su negociabilidad depende de las reglas, restricciones, evidencia, parámetros y límites aplicables.

---

# 5. Intercambio de valor

La inteligencia negociadora analiza la relación entre lo que EIOS concede y aquello que puede obtener a cambio.

Conceptualmente:

```text
Concesión propia
      ↓
coste / impacto
      ↕
Contraprestación
      ↓
valor obtenido
```

Una concesión no debe analizarse aisladamente cuando su justificación depende de una contraprestación.

Negotiation Intelligence puede determinar que una concesión solo resulta razonable:

- si existe una contraprestación suficiente;
- bajo determinadas condiciones;
- dentro de un rango concreto;
- o como parte de un paquete.

---

# 6. Trade-offs y paquetes

NI puede determinar intercambios entre variables negociables.

Ejemplos:

```text
precio ↔ plazo
precio ↔ volumen
precio ↔ condiciones de pago
servicio ↔ compromiso
descuento ↔ volumen
```

También puede determinar paquetes de condiciones cuando el valor negociador dependa de la combinación de varias variables.

Un paquete no debe confundirse con un escenario formal.

Si una combinación requiere evaluación formal:

```text
NI
 ↓
hipótesis / contenido negociador
 ↓
Scenario Engine
 ↓
escenario formal
 ↓
evaluación
 ↓
NI
```

---

# 7. Negociabilidad

Negotiation Intelligence puede analizar la negociabilidad de una condición utilizando:

- evidencia disponible;
- comportamiento histórico;
- condiciones del proveedor;
- restricciones conocidas;
- alternativas;
- resultados de escenarios;
- relaciones entre variables.

La negociabilidad constituye una **conclusión analítica**, no una garantía de aceptación por la contraparte.

Debe distinguirse entre:

- negociabilidad observada;
- negociabilidad inferida;
- negociabilidad estimada;
- negociabilidad desconocida.

---

# 8. BATNA y alternativas

NI puede utilizar BATNA y alternativas como elementos de razonamiento.

Debe distinguirse entre:

- alternativa confirmada;
- alternativa estimada;
- alternativa hipotética;
- alternativa no evaluable.

Una hipótesis no adquiere condición de hecho por ser utilizada en el razonamiento.

La existencia o valor de una alternativa debe mantener referencia a su evidencia o fuente correspondiente.

---

# 9. ZOPA

Negotiation Intelligence puede utilizar una ZOPA cuando exista información suficiente para inferirla o determinarla conforme a las fuentes aplicables.

La ZOPA puede constituir:

- un resultado conocido;
- una estimación;
- un rango probable;
- una hipótesis.

Su grado de certeza debe conservarse.

La ZOPA **no sustituye a Viability Frontier** ni modifica sus límites.

---

# 10. Concesiones y reciprocidad

NI puede determinar:

- qué concesiones resultan negociacionalmente razonables;
- cuándo una concesión debería estar condicionada;
- qué contraprestación debería solicitarse;
- qué combinación de concesiones presenta mejor relación de valor.

El principio de reciprocidad implica que una concesión puede estar vinculada a una contraprestación.

```text
Concesión
   ↕
Condición
   ↕
Contraprestación
```

La determinación de estos elementos pertenece a NI.

Su representación secuencial pertenece a Negotiation Ladder.

---

# 11. Primera petición

Negotiation Intelligence puede determinar la primera petición cuando exista base suficiente para ello.

La determinación puede considerar:

- objetivo;
- posición inicial;
- alternativas;
- condiciones de mercado;
- BATNA;
- ZOPA;
- sensibilidad;
- restricciones;
- resultados de escenarios;
- evidencia disponible.

Negotiation Ladder únicamente representa la primera petición dentro de la estructura negociadora.

---

# 12. Sensibilidad negociadora

NI puede analizar cómo cambia la conveniencia de una vía negociadora cuando varían determinadas condiciones.

Puede estudiar, por ejemplo:

- variación del precio;
- variación del plazo;
- variación del volumen;
- variación de las condiciones de pago;
- modificación de una contraprestación;
- modificación de una restricción.

Cuando la modificación requiera la construcción o evaluación de un nuevo escenario formal, debe utilizarse el Scenario Engine.

---

# 13. Robustez

Una recomendación negociadora puede evaluarse respecto de su robustez.

La robustez analiza si el contenido negociador mantiene su conveniencia ante variaciones razonables de las condiciones relevantes.

Debe distinguirse:

```text
resultado estable
      ≠
resultado cierto
```

La robustez no elimina la incertidumbre.

---

# 14. Señales e inferencias negociadoras

NI puede utilizar señales relativas a:

- poder de negociación;
- urgencia;
- dependencia;
- flexibilidad;
- disposición a conceder;
- sensibilidad ante determinadas variables.

Estas señales deben distinguirse de hechos confirmados.

Toda inferencia relevante debe conservar:

- origen;
- evidencia;
- nivel de confianza;
- naturaleza de la inferencia.

No debe presentarse una inferencia como hecho.

---

# 15. Límites y restricciones

Negotiation Intelligence puede **utilizar y analizar** límites y restricciones procedentes de fuentes con autoridad correspondiente.

Puede determinar sus implicaciones negociadoras.

No puede:

- crear un límite;
- determinar un límite;
- modificar un límite;
- ampliar un límite;
- reducir un límite;
- sustituir la autoridad que lo establece.

La relación correcta es:

```text
Autoridad competente
        ↓
      LÍMITE
        ↓
       NI
        ↓
interpreta consecuencias
negociadoras
```

El límite conserva siempre su fuente de autoridad.

---

# 16. Viability Frontier

Negotiation Intelligence consume la información proporcionada por `Viability_Frontier.md`.

Puede utilizarla para determinar la conveniencia negociadora de una alternativa.

Por tanto:

```text
Viability Frontier
       ↓
determina viabilidad
       ↓
Negotiation Intelligence
       ↓
determina conveniencia negociadora
```

NI no modifica la frontera ni transforma una condición no viable en viable.

---

# 17. Scenario Engine

NI puede producir:

- hipótesis;
- alternativas;
- propuestas de combinación;
- necesidades de evaluación.

Pero no crea el escenario formal.

Cuando sea necesaria una evaluación:

```text
NI
 ↓
hipótesis negociadora
 ↓
Scenario Engine
 ↓
Scenario_ID
 ↓
evaluación
 ↓
resultado
 ↓
NI
```

La identificación, formalización, evaluación y versionado del escenario pertenecen al Scenario Engine.

---

# 18. Decision Twin

NI consume resultados y consecuencias producidos por Decision Twin.

Puede interpretarlos desde la perspectiva negociadora.

No:

- reproduce el Twin;
- recalcula sus resultados;
- modifica sus alternativas;
- sustituye su representación.

```text
Decision Twin
      ↓
resultado / consecuencia
      ↓
Negotiation Intelligence
      ↓
interpretación negociadora
```

---

# 19. Negotiation Ladder

La frontera con `Negotiation_Ladder.md` es inmutable:

> **Negotiation Intelligence determina el contenido negociador; Negotiation Ladder estructura, representa y ordena secuencialmente ese contenido.**

NI puede determinar:

- qué movimiento resulta justificado;
- qué concesión resulta conveniente;
- qué contraprestación corresponde;
- qué fallback debe considerarse;
- qué condiciones deben cumplirse.

Ladder puede:

- representar esos elementos;
- estructurarlos;
- ordenarlos;
- representar sus transiciones;
- representar el fallback;
- representar el walk-away.

Ladder no puede modificar el contenido sustantivo determinado por NI.

---

# 20. Strategy

El contenido producido por NI no constituye automáticamente una Strategy.

NI puede aportar inteligencia y contenido negociador para una estrategia, pero no:

- crea Strategy como autoridad autónoma;
- gobierna Strategy;
- activa Strategy;
- ejecuta Strategy.

```text
Contenido negociador
        ≠
Strategy
        ≠
Decisión
```

---

# 21. Resolución y decisión

Negotiation Intelligence produce razonamiento y contenido.

No resuelve conflictos de autoridad entre resultados.

No sustituye a la `Capa_resolucion_conflictos`.

Tampoco constituye la decisión empresarial final.

```text
NI
 ↓
contenido / recomendación
 ↓
resolución correspondiente
 ↓
autoridad decisional
```

---

# 22. Adaptación negociadora

La inteligencia negociadora puede actualizarse cuando aparece nueva información.

La adaptación sigue un ciclo controlado:

```text
respuesta externa
      ↓
nuevo contexto
      ↓
nuevo escenario si procede
      ↓
evaluación
      ↓
Negotiation Intelligence
      ↓
nuevo contenido negociador
      ↓
Negotiation Ladder
```

Una nueva respuesta no autoriza a NI a modificar directamente límites, reglas o escenarios.

---

# 23. Salidas

La salida principal de NI es:

## Contenido negociador determinado y justificado

Puede contener:

```text
├── objetivo negociador
├── primera petición
├── movimientos
├── concesiones
├── contraprestaciones
├── trade-offs
├── paquetes
├── alternativas
├── fallback
├── condiciones
├── análisis de conveniencia
├── justificación
├── evidencia de soporte
├── nivel de confianza
└── referencias de trazabilidad
```

Estos elementos constituyen **contenido**, no una Ladder.

---

# 24. Trazabilidad

Todo contenido negociador material debe poder rastrearse hasta sus fundamentos.

La trazabilidad debe permitir reconstruir:

```text
Evidencia
   ↓
Datos
   ↓
Reglas / parámetros
   ↓
Escenario / resultado
   ↓
Razonamiento NI
   ↓
Contenido negociador
```

Cuando una conclusión sea inferida o estimada, dicha naturaleza debe conservarse.

La trazabilidad no convierte una inferencia en un hecho.

---

# 25. Confianza e incertidumbre

NI debe diferenciar:

- hecho;
- dato observado;
- inferencia;
- estimación;
- hipótesis;
- recomendación.

La confianza asociada a una conclusión debe conservarse cuando resulte relevante.

Una recomendación con alta confianza no constituye una decisión automática.

---

# 26. Invariantes

1. NI razona sobre negociación.
2. NI determina contenido negociador.
3. NI justifica su contenido.
4. NI conserva trazabilidad.
5. NI distingue hechos, inferencias, estimaciones e hipótesis.
6. NI puede utilizar límites autorizados.
7. NI no crea límites.
8. NI no modifica límites.
9. NI no determina viabilidad.
10. NI no genera escenarios formales.
11. NI no sustituye Decision Twin.
12. NI no estructura Ladder.
13. NI no modifica sustantivamente contenido mediante Ladder.
14. NI no crea Strategy autónoma.
15. NI no gobierna Strategy.
16. NI no decide.
17. NI no aprueba.
18. NI no ejecuta.
19. Una hipótesis negociadora no es automáticamente un escenario.
20. Una recomendación no es automáticamente una decisión.

---

# 27. Exclusiones

Quedan fuera de Negotiation Intelligence:

- generación formal de escenarios;
- evaluación formal de escenarios;
- determinación de viabilidad;
- creación o modificación de límites;
- estructura representacional de Ladder;
- ordenación puramente estructural de Ladder;
- resolución de conflictos de autoridad;
- aprobación;
- decisión empresarial;
- ejecución;
- gobierno de Strategy;
- activación de Strategy.

---

# 28. Relaciones documentales

Negotiation Intelligence mantiene relaciones con:

- `00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`
- `00_Gobierno/Matriz_Autoridad_Documental.md`
- `01_Modelo/Modelo_Empresarial_Decision.md`
- `03_Arquitectura/Architecture_Blueprint.md`
- `04_Reglas/Matriz_Reglas_MVP.md`
- `04_Reglas/Evidence_Contract.md`
- `05_Motor/Viability_Frontier.md`
- `05_Motor/Scenario_Engine.md`
- `05_Motor/Decision_Twin.md`
- `05_Motor/Negotiation_Ladder.md`
- `05_Motor/Capa_resolucion_conflictos.md`
- `05_Motor/Decision_Versioning.md`

Estas referencias **no delegan autoridad** a NI sobre los dominios cuya fuente oficial sea otro documento.

---

# 29. Regla de no absorción

Negotiation Intelligence no podrá adquirir responsabilidades pertenecientes a otros componentes mediante extensiones semánticas de:

- análisis;
- recomendación;
- interpretación;
- optimización;
- adaptación.

En particular:

> **Analizar una decisión no equivale a tomarla.**

> **Analizar viabilidad no equivale a determinarla.**

> **Proponer una hipótesis no equivale a crear un escenario.**

> **Determinar contenido negociador no equivale a estructurar la Ladder.**

> **Interpretar un límite no equivale a establecerlo.**

---

# 30. Estado documental

**APROBADO — Documento materializado tras auditoría de regresión pre-commit.**

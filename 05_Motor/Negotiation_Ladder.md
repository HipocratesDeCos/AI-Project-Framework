# Negotiation_Ladder

## 1. Identidad y propósito

`Negotiation Ladder` es el componente especializado de EIOS responsable de **estructurar, representar y ordenar secuencialmente contenido negociador previamente determinado**.

Su función es convertir contenido negociador en una representación estructurada mediante escalones, relaciones, transiciones y rutas.

No determina por sí misma el contenido sustantivo de la negociación.

---

# 2. Frontera arquitectónica

La frontera con `Negotiation Intelligence` es inmutable:

> **Negotiation Intelligence determina el contenido negociador; Negotiation Ladder estructura, representa y ordena secuencialmente ese contenido.**

Por tanto:

```text
Negotiation Intelligence
        │
        │ contenido determinado
        ▼
Negotiation Ladder
        │
        │ estructura / representación
        ▼
Ladder negociadora
```

La transformación realizada por Ladder es **estructural, no sustantiva**.

---

# 3. Responsabilidad principal

Ladder puede:

- estructurar escalones;
- representar movimientos;
- representar condiciones;
- ordenar secuencialmente contenido previamente determinado;
- representar transiciones;
- representar rutas alternativas;
- representar fallback;
- representar walk-away;
- mantener trazabilidad.

No puede definir ni modificar el contenido sustantivo de los elementos que representa.

---

# 4. Escalones

Cada escalón representa un elemento de contenido negociador previamente determinado por `Negotiation Intelligence` o procedente de una fuente con autoridad correspondiente.

Un escalón puede representar:

- objetivo;
- petición;
- movimiento;
- concesión;
- contraprestación;
- condición;
- alternativa;
- fallback;
- límite;
- walk-away.

Ladder no crea estos elementos sustantivamente.

---

# 5. Objetivo

Ladder puede representar el objetivo negociador previamente determinado.

No determina:

- cuál debe ser el objetivo;
- su conveniencia;
- su valor económico;
- su justificación estratégica.

---

# 6. Primera petición

Ladder representa la primera petición determinada por `Negotiation Intelligence` o por la autoridad correspondiente.

No determina cuál debe ser la primera petición.

---

# 7. Concesiones

Ladder representa concesiones previamente determinadas.

Puede mostrar:

```text
Petición
   ↓
Concesión 1
   ↓
Concesión 2
```

La magnitud, conveniencia y condiciones sustantivas de cada concesión pertenecen a NI.

---

# 8. Reciprocidad

Ladder puede representar la relación:

```text
Concesión
    ↕
Condición
    ↕
Contraprestación
```

No determina si una concesión resulta conveniente ni cuál debe ser la contraprestación.

---

# 9. Fallback

Ladder representa como `fallback` la alternativa negociadora previamente determinada por NI o por la autoridad competente.

No determina:

- cuál es el mejor fallback;
- su valor;
- sus condiciones sustantivas.

---

# 10. Límites

Ladder puede utilizar y representar límites procedentes de una fuente con autoridad.

No puede:

- crear límites;
- determinar límites;
- modificar límites;
- ampliarlos;
- reducirlos;
- reinterpretarlos sustantivamente.

La regla es:

```text
Autoridad competente
        ↓
      LÍMITE
        ↓
     Ladder
        ↓
 REPRESENTACIÓN
```

---

# 11. Walk-away

Ladder puede representar un límite autorizado mediante una condición `walk-away`.

La representación:

- no crea el límite;
- no modifica el límite;
- no amplía el límite;
- no reduce el límite.

Debe conservar exactamente el alcance y las condiciones de la fuente autorizada.

```text
Límite autorizado
       ↓
Representación
       ↓
WALK-AWAY
```

---

# 12. Walk-away multidimensional

Un límite puede depender simultáneamente de varias variables.

Por ejemplo:

```text
Si precio = X
→ condición de pago = Y

Si precio = Z
→ condición de pago = W
```

Ladder puede representar esta función.

No determina los valores de X, Y, Z o W.

---

# 13. Condiciones no negociables

Ladder puede representar restricciones o condiciones que no deben ser cruzadas.

Su existencia y autoridad proceden de la fuente correspondiente.

Ladder no puede convertir una condición representada en una nueva regla.

---

# 14. Tipos de petición

Ladder puede clasificar y representar peticiones según su naturaleza, por ejemplo:

- económica;
- financiera;
- logística;
- cantidad;
- riesgo;
- combinada.

La clasificación es representacional.

No implica autoridad para determinar el contenido de la petición.

---

# 15. Secuencia

Ladder establece y mantiene la **estructura secuencial de representación** de movimientos y condiciones previamente determinados.

Puede representar:

```text
A → B → C → D
```

No puede cambiar estratégicamente:

```text
A → B → C
```

por:

```text
A → C → B
```

porque considere que la segunda secuencia es negociacionalmente superior.

La optimización estratégica de la secuencia no pertenece a Ladder.

---

# 16. Transiciones

Una transición representa la relación estructural entre escalones.

Puede estar condicionada por:

- respuesta;
- condición;
- resultado;
- evento negociador;
- requisito previamente definido.

La condición sustantiva de transición debe proceder de la fuente correspondiente.

---

# 17. Rutas alternativas

Ladder puede representar varias rutas:

```text
              Escalón A
             /         \
            B           C
            |           |
            D           E
             \         /
               Fallback
```

La existencia y contenido de las rutas proceden de la inteligencia negociadora o de la autoridad correspondiente.

Ladder organiza su representación.

No selecciona estratégicamente una ruta por iniciativa propia.

---

# 18. Escenarios

Ladder puede referenciar escenarios formalmente existentes.

No:

- crea escenarios;
- modifica escenarios;
- evalúa escenarios;
- recalcula escenarios;
- sustituye al Scenario Engine.

```text
Scenario Engine
       ↓
escenario formal
       ↓
Ladder
       ↓
referencia / representación
```

---

# 19. Viabilidad

Ladder puede representar resultados de viabilidad ya determinados.

No determina la viabilidad.

Una condición representada en una Ladder no adquiere por ello condición de viable.

---

# 20. Decision Twin

Ladder puede representar referencias a alternativas y resultados provenientes de Decision Twin.

No recalcula ni modifica el Twin.

---

# 21. Negotiation Intelligence

La relación contractual es:

```text
NI
 ↓
determina contenido
 ↓
Ladder
 ↓
estructura y representa
```

Ladder no devuelve autoridad sustantiva a NI ni sustituye su razonamiento.

Si el contenido debe modificarse por razones negociadoras, debe producirse una nueva determinación por NI.

---

# 22. Adaptación

Una Ladder puede cambiar cuando cambia el contenido negociador autorizado.

El ciclo correcto es:

```text
Respuesta externa
       ↓
nuevo contexto
       ↓
evaluación correspondiente
       ↓
NI
       ↓
nuevo contenido
       ↓
Ladder actualizada
```

Ladder no se modifica estratégicamente a sí misma.

---

# 23. Evidencia y trazabilidad

Cada elemento representado debería conservar referencias a:

- contenido de origen;
- escenario;
- datos;
- evidencia;
- reglas;
- parámetros;
- resultados;
- nivel de confianza.

La trazabilidad debe permitir reconstruir el origen del contenido.

---

# 24. Calidad y confianza

Ladder puede representar el estado de confianza asociado al contenido recibido.

Por ejemplo:

```text
ALTA
MEDIA
BAJA
NO EVALUABLE
```

La representación de confianza no permite a Ladder convertir una evidencia débil en un límite duro.

---

# 25. Relación con Strategy

Una Ladder estructurada no constituye por sí misma una Strategy.

Ladder no:

- crea Strategy;
- gobierna Strategy;
- activa Strategy;
- modifica Strategy autónomamente;
- ejecuta Strategy.

```text
Ladder
  ≠
Strategy
```

---

# 26. Resolución y decisión

Ladder no resuelve conflictos de autoridad.

No aprueba.

No decide.

No ejecuta.

Su salida es una representación estructurada del contenido negociador.

---

# 27. Salida

La salida de Ladder es una **estructura negociadora representada**, que puede contener:

```text
├── escalones
├── movimientos
├── condiciones
├── secuencia
├── transiciones
├── rutas alternativas
├── concesiones representadas
├── contraprestaciones representadas
├── fallback representado
├── límites representados
├── walk-away representado
└── trazabilidad
```

---

# 28. Invariantes

1. Ladder estructura.
2. Ladder representa.
3. Ladder ordena secuencialmente.
4. Ladder no determina contenido sustantivo.
5. Ladder no modifica contenido sustantivo.
6. Ladder puede representar concesiones.
7. Ladder puede representar contraprestaciones.
8. Ladder puede representar fallback.
9. Ladder puede representar límites autorizados.
10. Ladder puede representar walk-away.
11. Ladder no crea límites.
12. Ladder no modifica límites.
13. Ladder no determina viabilidad.
14. Ladder no genera escenarios formales.
15. Ladder no evalúa escenarios.
16. Ladder no crea Strategy.
17. Ladder no gobierna Strategy.
18. Ladder no decide.
19. Ladder no aprueba.
20. Ladder no ejecuta.
21. La secuencia representada no constituye por sí misma una decisión estratégica.
22. Una representación de walk-away no constituye una nueva determinación del límite.

---

# 29. Exclusiones

Quedan fuera:

- determinación del contenido negociador;
- determinación de conveniencia negociadora;
- optimización estratégica de la secuencia;
- creación de escenarios;
- evaluación de escenarios;
- determinación de viabilidad;
- creación de límites;
- modificación de límites;
- determinación autónoma de fallback;
- decisión de abandono;
- creación de Strategy;
- gobierno de Strategy;
- decisión;
- aprobación;
- ejecución.

---

# 30. Relaciones documentales

La Ladder mantiene referencias hacia:

- `00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`
- `00_Gobierno/Matriz_Autoridad_Documental.md`
- `03_Arquitectura/Architecture_Blueprint.md`
- `DSS_Functional_Architecture.md`
- `Modelo_Empresarial_Decision.md`
- `05_Motor/Viability_Frontier.md`
- `05_Motor/Scenario_Engine.md`
- `05_Motor/Decision_Twin.md`
- `05_Motor/Negotiation_Intelligence.md`
- `05_Motor/Capa_resolucion_conflictos.md`
- `05_Motor/Decision_Versioning.md`
- `04_Reglas/Evidence_Contract.md`
- `04_Reglas/Matriz_Reglas_MVP.md`

Las referencias no transfieren a Ladder la autoridad de los documentos citados.

---

# 31. Estado documental

**APROBADO — Documento materializado tras auditoría de regresión pre-commit.**

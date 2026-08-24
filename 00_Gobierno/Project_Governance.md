# PROJECT GOVERNANCE

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.1  
**Estado:** APROBADO  
**Documento:** Gobierno del proyecto  
**Última actualización:** 24/08/2026

---

# 1. PROPÓSITO

Definir las normas de gobierno del proyecto EIOS para garantizar:

- estabilidad;
- coherencia;
- trazabilidad;
- continuidad;
- control documental;
- escalabilidad;
- integridad de las decisiones.

Este documento regula **cómo se gobierna EIOS**.

No sustituye al `Project_Charter.md`, `Project_Context.md`, `Matriz_Autoridad_Documental.md`, Salvaguarda Vertical MVP ni a la documentación especializada.

---

# 2. PRINCIPIOS DE GOBIERNO

EIOS se gobernará mediante los siguientes principios:

1. **Una única fuente oficial de documentación versionada.**
2. **Toda decisión relevante debe quedar documentada.**
3. **Una propuesta no es una decisión vigente hasta su aprobación.**
4. **Una decisión aprobada debe quedar reflejada en el documento que corresponda.**
5. **Una decisión congelada no puede modificarse silenciosamente.**
6. **Todo cambio relevante debe conservar trazabilidad.**
7. **Los documentos especializados son responsables de sus respectivos dominios de autoridad.**
8. **La conversación sirve como espacio de trabajo, pero no constituye por sí misma autoridad normativa.**
9. **El proyecto debe poder recuperarse sin depender del historial de conversaciones.**
10. **La simplicidad documental es preferible a la duplicación de información.**

---

# 3. FUENTE OFICIAL

La documentación versionada almacenada en el repositorio oficial de GitHub constituye la **fuente oficial de documentación del proyecto EIOS**.

El repositorio oficial es:

`HipocratesDeCos/AI-Project-Framework`

Las conversaciones, notas de trabajo, borradores y discusiones:

- sirven para analizar;
- sirven para proponer;
- sirven para cuestionar;
- sirven para validar;

pero **no sustituyen la documentación oficial**.

Una decisión discutida en conversación no se considera vigente hasta que haya sido aprobada y documentada en el lugar correspondiente.

---

# 4. AUTORIDAD DOCUMENTAL

La autoridad entre documentos se determina mediante:

`00_Gobierno/Matriz_Autoridad_Documental.md`

Esta matriz constituye la referencia oficial para resolver conflictos documentales.

Cuando exista una discrepancia:

```text
DOCUMENTO EN CONFLICTO
        ↓
MATRIZ DE AUTORIDAD
        ↓
DOCUMENTO CON MAYOR AUTORIDAD
        ↓
APLICACIÓN DEL CRITERIO OFICIAL
```

Ningún documento subordinado puede contradecir una decisión establecida por un documento de mayor autoridad.

La autoridad documental debe mantenerse separada de la simple antigüedad del archivo.

---

# 5. DOCUMENTOS DE GOBIERNO PRINCIPALES

Dentro de `00_Gobierno/` se consideran documentos fundamentales:

```text
00_Gobierno/
├── Project_Charter.md
├── Project_Context.md
├── Project_Governance.md
├── Matriz_Autoridad_Documental.md
├── EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md
└── EIOS_Assurance_Framework.md
```

Cada documento tiene una función diferente.

### Project Charter

Define la identidad, propósito, visión, alcance y límites fundamentales del proyecto.

### Project Context

Conserva el contexto esencial necesario para recuperar la continuidad del proyecto.

### Project Governance

Define las reglas mediante las que se gobierna el proyecto y su documentación.

### Matriz de Autoridad Documental

Determina qué documento prevalece cuando existe una discrepancia.

### Salvaguarda Vertical MVP

Establece las restricciones y decisiones congeladas aplicables al Vertical MVP.

### Assurance Framework

Define el marco transversal de assurance del sistema.

---

# 6. CICLO DE DECISIÓN

Toda decisión relevante deberá seguir, como mínimo, este ciclo:

```text
IDEA
  ↓
ANÁLISIS
  ↓
PROPUESTA
  ↓
CUESTIONAMIENTO
  ↓
CONTRASTE
  ↓
MEJORA
  ↓
VALIDACIÓN
  ↓
APROBACIÓN
  ↓
DOCUMENTACIÓN
  ↓
IMPLEMENTACIÓN
```

No toda idea debe convertirse en una decisión.

No toda propuesta debe aprobarse.

La aprobación convierte una propuesta en una decisión válida dentro del ámbito correspondiente.

La documentación convierte dicha decisión en conocimiento recuperable y trazable.

La implementación debe respetar la documentación aprobada.

---

# 7. ESTADOS DE UNA DECISIÓN

Las decisiones relevantes deberán distinguir, como mínimo, entre:

### 🟡 PROPUESTA

Idea o modificación pendiente de validación.

No constituye criterio oficial.

### 🟢 APROBADA

La propuesta ha sido aceptada y puede incorporarse a la documentación oficial.

### 🔒 CONGELADA

La decisión ha quedado establecida como restricción o criterio que no puede modificarse de forma ordinaria.

Cualquier cambio sobre una decisión congelada deberá seguir el procedimiento correspondiente.

### ⚪ OBSOLETA / SUSTITUIDA

Una decisión anterior deja de estar vigente porque ha sido sustituida formalmente por otra.

---

# 8. CONTROL DE CAMBIOS

Todo cambio relevante deberá permitir responder a cuatro preguntas:

1. **¿Qué ha cambiado?**
2. **¿Por qué ha cambiado?**
3. **¿Qué autoridad lo ha aprobado?**
4. **¿Qué versión o contenido anterior sustituye?**

Los cambios deberán quedar reflejados en el documento afectado.

No es obligatorio duplicar el contenido histórico dentro del documento si GitHub conserva adecuadamente el historial de versiones.

## 8.1. IDENTIFICACIÓN DE CAMBIOS

Los cambios relevantes deberán identificarse mediante un `CHANGE-ID` único.

Formato:

```text
EIOS-CHG-001
EIOS-CHG-002
EIOS-CHG-003
...
```

El `CHANGE-ID` identifica el cambio gobernado y no sustituye al número de versión del documento, al commit SHA ni al Baseline-ID.

Cuando el cambio se implemente mediante Git, el `CHANGE-ID` deberá quedar asociado al commit correspondiente.

Los identificadores de cambio no se reutilizarán.

## 8.2. BASELINE DEL PROYECTO

Un Baseline representa un estado formalmente establecido y validado del proyecto EIOS en un momento determinado.

Cada Baseline tendrá un identificador único:

```text
EIOS-BL-001
EIOS-BL-002
EIOS-BL-003
...
```

El Baseline identifica el estado formal resultante y no sustituye al CHANGE-ID, al número de versión ni al commit SHA.

Cada Baseline deberá quedar asociado a un commit SHA concreto del repositorio oficial.

No todo commit constituye un Baseline.

Un Baseline solo podrá establecerse cuando los cambios incluidos hayan sido completados, validados y comprobados respecto a las dependencias y restricciones aplicables.

Cuando resulte conveniente, podrá utilizarse un Git Tag con el mismo identificador del Baseline.

La asociación:

```text
Baseline-ID → Commit SHA
```

deberá permitir reconstruir el estado del proyecto correspondiente al Baseline.

Los identificadores de Baseline no se reutilizarán ni eliminarán como consecuencia de la creación de Baselines posteriores.

---

# 9. REGLA DE SUSTITUCIÓN DOCUMENTAL

Cuando se apruebe una nueva versión de un documento:

1. se conserva el documento bajo el mismo nombre oficial cuando corresponda;
2. se actualiza su número de versión;
3. se sustituye el contenido anterior;
4. se mantiene el historial mediante el sistema de control de versiones;
5. se verifica que no existan referencias rotas;
6. se genera, cuando sea útil, una copia descargable de la versión aprobada.

No se crearán archivos paralelos únicamente para conservar versiones antiguas si GitHub ya proporciona trazabilidad suficiente.

Ejemplo:

```text
Project_Context.md
```

pasa de:

```text
v1.0
```

a:

```text
v2.0
```

sin crear necesariamente:

```text
Project_Context_v1.0.md
Project_Context_v2.0.md
```

La versión oficial continúa siendo:

`Project_Context.md`

---

# 10. DOCUMENTOS CONGELADOS

Un documento o apartado marcado como **CONGELADO** no puede modificarse como parte de una simple mejora documental.

Antes de modificarlo deberá:

1. identificarse la decisión que se pretende cambiar;
2. justificar el motivo;
3. evaluar el impacto;
4. comprobar las dependencias afectadas;
5. aprobar formalmente el cambio;
6. actualizar la documentación correspondiente;
7. conservar la trazabilidad del cambio.

La existencia de una nueva idea o una preferencia de implementación no constituye por sí misma autorización para modificar una decisión congelada.

---

# 11. RELACIÓN ENTRE DOCUMENTACIÓN Y IMPLEMENTACIÓN

La implementación debe seguir la documentación aprobada.

La secuencia preferente será:

```text
LÓGICA DE NEGOCIO
       ↓
REGLA / ESPECIFICACIÓN
       ↓
DOCUMENTACIÓN
       ↓
VALIDACIÓN
       ↓
IMPLEMENTACIÓN
       ↓
PRUEBA
       ↓
VALIDACIÓN FINAL
```

No debe desarrollarse una pieza importante únicamente a partir de una conversación o interpretación informal cuando la lógica de negocio todavía no está suficientemente definida.

---

# 12. DOCUMENTACIÓN ESPECIALIZADA

Cada dominio debe tener su propia documentación especializada.

Ejemplos:

- parámetros;
- reglas;
- motor;
- evidencia;
- negociación;
- arquitectura;
- datos;
- interfaces;
- assurance.

Los documentos de contexto no deben duplicar exhaustivamente el contenido de dichos documentos.

Cuando un concepto especializado tenga una fuente oficial, esa fuente prevalece sobre una descripción resumida incluida en documentos de contexto.

---

# 13. TRAZABILIDAD

Las decisiones relevantes deberán mantener trazabilidad entre:

```text
NECESIDAD
   ↓
DECISIÓN
   ↓
DOCUMENTO
   ↓
VERSIÓN
   ↓
IMPLEMENTACIÓN
   ↓
RESULTADO
```

Cuando sea necesario, deberá poder reconstruirse qué criterio estaba vigente en el momento de una determinada decisión.

Esto es especialmente importante para:

- reglas;
- parámetros;
- cálculos;
- decisiones;
- excepciones;
- configuración;
- salvaguardas.

---

# 14. CONTINUIDAD DEL PROYECTO

EIOS debe poder continuar aunque:

- cambie la conversación;
- se inicie un nuevo chat;
- se incorpore otra persona;
- se utilice otra IA;
- transcurra un periodo prolongado sin trabajar en el proyecto.

Para ello, el conocimiento esencial debe quedar documentado.

`Project_Context.md` actúa como documento de recuperación del contexto.

La recuperación del proyecto deberá apoyarse prioritariamente en la documentación oficial y no en la memoria de una conversación concreta.

---

# 15. CONTROL DE COHERENCIA

Antes de aprobar un cambio relevante deberá comprobarse, cuando corresponda:

- compatibilidad con `Project_Charter.md`;
- compatibilidad con `Project_Context.md`;
- compatibilidad con `Matriz_Autoridad_Documental.md`;
- compatibilidad con la Salvaguarda Vertical MVP;
- impacto sobre Assurance;
- impacto sobre documentos especializados;
- existencia de contradicciones;
- referencias documentales afectadas.

No se debe aprobar un cambio aislado que provoque una contradicción conocida en otra capa del sistema.

---

# 16. GESTIÓN DE VERSIONES

El número de versión deberá reflejar la importancia del cambio documental.

### Versión mayor

Ejemplo:

`v2.0`

Utilizar cuando exista un cambio estructural, conceptual o de contenido suficientemente relevante.

### Versión menor

Ejemplo:

`v2.1`

Utilizar para ampliaciones o mejoras que no alteren la estructura fundamental ni la autoridad del documento.

### Corrección

Ejemplo:

`v2.0.1`

Puede utilizarse para correcciones menores de redacción, formato, referencias o errores que no cambien el contenido conceptual.

El criterio exacto podrá adaptarse al sistema de versionado del proyecto, pero nunca deberá utilizarse el número de versión para ocultar cambios sustanciales.

---

# 17. GESTIÓN DE OBSOLESCENCIA

Un documento no debe eliminarse simplemente porque exista una versión posterior.

La sustitución ordinaria consiste en:

```text
VERSIÓN ANTERIOR
       ↓
NUEVA VERSIÓN APROBADA
       ↓
MISMO ARCHIVO OFICIAL
       ↓
HISTORIAL DE GITHUB
```

Un documento podrá eliminarse cuando exista una decisión expresa de gobierno que determine que ya no debe formar parte del repositorio.

La eliminación no debe utilizarse para ocultar decisiones anteriores.

---

# 18. REGLA SOBRE DUPLICACIÓN

Debe evitarse mantener el mismo criterio en varios documentos como si todos fueran fuentes de autoridad.

Cuando un concepto tenga una fuente oficial:

- otros documentos pueden resumirlo;
- pueden enlazarlo;
- pueden contextualizarlo;

pero no deben redefinirlo de forma independiente.

La duplicación de lógica es una fuente de contradicciones y debe minimizarse.

---

# 19. CONTROL DE REFERENCIAS

Cuando un documento cambie de nombre, ubicación o función deberá revisarse el resto del repositorio para detectar referencias afectadas.

Especial atención a:

- rutas;
- nombres de archivos;
- enlaces;
- dependencias;
- documentos de autoridad;
- referencias cruzadas.

Una actualización documental no se considera completamente cerrada si deja referencias internas críticas rotas.

---

# 20. CIERRE DE UNA SESIÓN DE TRABAJO

Al finalizar una sesión significativa deberá determinarse:

1. qué decisiones se han tomado;
2. cuáles han sido aprobadas;
3. qué documentos deben actualizarse;
4. qué cambios quedan pendientes;
5. qué elementos han quedado congelados;
6. cuál es el siguiente punto de trabajo.

No es necesario registrar cada conversación.

Debe conservarse únicamente el conocimiento necesario para mantener la continuidad y trazabilidad del proyecto.

---

# 21. REGLA DE NO REGRESIÓN

Una modificación no debe degradar una capacidad, garantía o restricción previamente aprobada sin una decisión explícita que lo autorice.

Antes de aceptar una modificación relevante debe comprobarse:

```text
¿Mejora?
¿Mantiene?
¿O degrada?
```

Si degrada una garantía existente, debe tratarse como un cambio sustancial y someterse al procedimiento de aprobación correspondiente.

---

# 22. GOBIERNO DEL EIOS VERTICAL MVP

El EIOS Vertical MVP está sujeto a su Salvaguarda específica.

La Salvaguarda constituye una restricción de gobierno sobre el alcance y comportamiento definido del Vertical.

Por tanto:

```text
PROPUESTA
   ↓
VALIDACIÓN
   ↓
COMPATIBILIDAD CON SALVAGUARDA
   ↓
APROBACIÓN
   ↓
DOCUMENTACIÓN
```

Una propuesta que contradiga una restricción congelada no puede incorporarse directamente al Vertical MVP.

Debe seguir el procedimiento de modificación correspondiente.

---

# 23. REGLA DE ESCALADO

Cuando una decisión afecte a varias capas del proyecto deberá analizarse transversalmente antes de aprobarse.

Ejemplo:

```text
Cambio de parámetro
      ↓
Regla
      ↓
Motor
      ↓
Recomendación
      ↓
Interfaz
      ↓
Trazabilidad
```

No debe considerarse un cambio como local si sus consecuencias afectan a otras capas.

---

# 24. RESPONSABILIDAD DE LA DOCUMENTACIÓN

Cada documento debe tener un propósito claro y una autoridad identificable.

Antes de crear un nuevo `.md` deberá comprobarse:

1. si el contenido ya existe;
2. si puede incorporarse a un documento existente;
3. si necesita convertirse en documento especializado;
4. qué autoridad tendrá;
5. dónde debe ubicarse.

**Crear documentos sin necesidad debe evitarse.**

---

# 25. REGLA DE SIMPLICIDAD

La documentación debe ser:

- clara;
- suficiente;
- mantenible;
- trazable;
- no redundante.

EIOS no debe convertirse en un sistema documental más complejo que el propio sistema que pretende gobernar.

La documentación debe ayudar al proyecto, no convertirse en una carga.

---

# 26. CRITERIO FINAL DE GOBIERNO

Ante cualquier duda sobre una modificación, debe aplicarse este orden:

```text
1. ¿Qué se quiere cambiar?
        ↓
2. ¿Qué documento tiene autoridad?
        ↓
3. ¿Está aprobado o congelado?
        ↓
4. ¿Qué dependencias afecta?
        ↓
5. ¿Existe contradicción?
        ↓
6. ¿Debe aprobarse formalmente?
        ↓
7. ¿Está documentado?
        ↓
8. ¿Está implementado correctamente?
```

---

# 27. PRINCIPIO FUNDAMENTAL

> **En EIOS, ninguna decisión importante debe depender de la memoria de una conversación.**

Debe existir una fuente documental oficial, una autoridad identificable y una trazabilidad suficiente para comprender:

**qué se decidió, por qué se decidió, cuándo se decidió y qué versión lo representa.**

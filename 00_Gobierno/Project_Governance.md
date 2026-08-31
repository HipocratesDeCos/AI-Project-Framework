# PROJECT GOVERNANCE

## EIOS — Enterprise Intelligent Operations System

**Versión:** 2.2  
**Estado:** APROBADO  
**Documento:** Gobierno del proyecto  
**Última actualización:** 31/08/2026

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
└── EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md
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

Cuando un documento especializado haya sido formalmente retirado, eliminado o sustituido, las referencias de gobierno que lo presenten como documento vigente deberán actualizarse en consecuencia.

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

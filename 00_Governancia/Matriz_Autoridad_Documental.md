# MATRIZ DE AUTORIDAD DOCUMENTAL

## EIOS — Enterprise Intelligent Operations System

**Versión:** 1.0  
**Estado:** MVP — Propuesta para aprobación  
**Ubicación:** `00_Governancia/Matriz_Autoridad_Documental.md`

---

# 1. Propósito

La Matriz de Autoridad Documental establece qué documento constituye la fuente oficial de referencia para cada tipo de decisión, definición o conocimiento dentro del proyecto EIOS.

Su objetivo es evitar que diferentes documentos definan de forma distinta un mismo concepto y garantizar que la evolución del proyecto mantenga una única interpretación coherente.

Esta matriz no sustituye al contenido de los documentos.

Determina cuál de ellos tiene autoridad cuando existe una discrepancia.

---

# 2. Principio fundamental

> **Un concepto debe tener una única fuente oficial de autoridad.**

Los demás documentos pueden:

- resumirlo;
- utilizarlo;
- referenciarlo;
- explicarlo desde otra perspectiva;

pero no deben redefinirlo de forma independiente.

Cuando exista una contradicción, debe prevalecer la fuente oficial definida en esta matriz.

---

# 3. Alcance

Esta matriz regula la autoridad entre los documentos funcionales, empresariales, arquitectónicos y de inteligencia de EIOS.

No regula:

- la autoridad de los usuarios sobre las decisiones empresariales;
- la configuración concreta de una empresa;
- los permisos de ejecución de la aplicación;
- la legislación aplicable;
- las fuentes externas de datos.

Estos aspectos se gobiernan mediante los documentos y mecanismos correspondientes.

---

# 4. Niveles de autoridad

La autoridad documental se organiza por dominio.

No existe un único documento que tenga autoridad absoluta sobre todos los aspectos de EIOS.

La autoridad depende del concepto que se esté tratando.

## Nivel A — Gobierno e identidad

Define qué es EIOS, su alcance, límites y gobierno documental.

## Nivel B — Modelo empresarial

Define cómo debe entenderse una decisión empresarial dentro de EIOS.

## Nivel C — Arquitectura

Define cómo se organiza técnicamente el sistema y cómo circulan los datos.

## Nivel D — Inteligencia

Define parámetros, reglas, configuración y resolución de conflictos.

## Nivel E — Experiencia de usuario

Define cómo se presenta la información y las decisiones al usuario.

---

# 5. Matriz principal de autoridad

| Dominio | Fuente oficial | Autoridad sobre |
|---|---|---|
| Identidad del proyecto | `00_Governancia/Project_Charter.md` | Nombre oficial, propósito, visión, alcance y límites |
| Usuarios y objetivos de negocio | `00_Governancia/Project_Charter.md` | Usuarios objetivo y objetivos generales |
| Contexto y continuidad | `00_Governancia/Project_Context.md` | Estado del proyecto, contexto de continuidad y orientación para recuperar el trabajo |
| Gobierno documental | `00_Governancia/Project_Governance.md` | Normas de gobierno, control y evolución documental |
| Autoridad entre documentos | `00_Governancia/Matriz_Autoridad_Documental.md` | Resolución de contradicciones documentales |
| Necesidades funcionales | `01_Negocio/Especificacion_funcional.md` | Necesidades y comportamiento funcional visible |
| Modelo empresarial de decisión | `04_Inteligencia/Modelo_Empresarial_Decision.md` | Conceptos empresariales, lógica general de decisión y significado de la decisión |
| Parámetros | `04_Inteligencia/Catalogo_Parametros_MVP.md` | Definición, identificación y naturaleza de los parámetros |
| Configuración | `04_Inteligencia/Centro_Parametrizacion.md` | Valores configurables, vigencia, edición, permisos y gobierno de parámetros |
| Reglas | `04_Inteligencia/Matriz_Reglas_MVP.md` | Condiciones, evaluación y resultados de las reglas |
| Resolución de conflictos | `04_Inteligencia/Capa_resolucion_conflictos.md` | Resolución de resultados contradictorios entre reglas |
| Arquitectura | `03_Arquitectura/Architecture_Blueprint.md` | Arquitectura lógica, componentes y flujo de datos |
| Organización arquitectónica | `03_Arquitectura/Master_Project_Map.md` | Mapa oficial del proyecto, una vez consolidado |
| Presentación | `05_Aplicacion/05_LEEME_Como_se_presenta.md` y futura especificación de interfaz | Forma de presentación al usuario |
| Operación | `06_Operaciones/06_LEEME_Como_funciona_en_produccion.md` | Funcionamiento operativo en producción |
| Desarrollo | `07_Desarrollo/07_LEEME_Como_se_construye.md` | Criterios y proceso de construcción |
| Pruebas | `08_Pruebas/08_LEEME_Como_verificamos_que_funciona.md` | Verificación y validación del sistema |

---

# 6. Regla de precedencia

Cuando dos documentos entren en conflicto, se aplicará el siguiente procedimiento:

### Paso 1 — Identificar el concepto en conflicto

Determinar exactamente qué concepto está siendo definido de forma diferente.

Ejemplos:

- nombre del proyecto;
- precio máximo recomendado;
- parámetro financiero;
- regla de stock;
- resultado de una decisión;
- flujo de datos.

### Paso 2 — Identificar su dominio

Determinar si el concepto pertenece a:

- gobierno;
- negocio;
- modelo empresarial;
- arquitectura;
- parámetros;
- configuración;
- reglas;
- resolución de conflictos;
- presentación;
- operaciones;
- desarrollo;
- pruebas.

### Paso 3 — Consultar la fuente oficial

La fuente indicada en la Matriz de Autoridad Documental será la referencia principal.

### Paso 4 — No corregir automáticamente

Una contradicción no debe corregirse automáticamente por el sistema.

Primero debe determinarse si:

1. la fuente oficial contiene la definición correcta;
2. la fuente oficial necesita ser modificada;
3. el documento secundario contiene una referencia obsoleta;
4. existe una decisión empresarial nueva todavía no formalizada.

### Paso 5 — Registrar la decisión

Cuando la contradicción requiera una decisión de diseño o negocio, deberá registrarse antes de modificar los documentos afectados.

---

# 7. Relación entre documentos de Inteligencia

Los documentos de `04_Inteligencia` tienen responsabilidades diferentes.

La relación oficial es:

```text
MODELO EMPRESARIAL DE DECISIÓN
            │
            ▼
     ¿Qué debe decidir EIOS?
            │
            ▼
CATÁLOGO DE PARÁMETROS
            │
            ▼
¿Qué variables necesita EIOS?
            │
            ▼
CENTRO DE PARAMETRIZACIÓN
            │
            ▼
¿Qué valores y criterios están vigentes?
            │
            ▼
MATRIZ DE REGLAS
            │
            ▼
¿Qué condiciones se evalúan?
            │
            ▼
CAPA DE RESOLUCIÓN DE CONFLICTOS
            │
            ▼
¿Cómo se resuelven resultados incompatibles?
            │
            ▼
DECISIÓN FINAL

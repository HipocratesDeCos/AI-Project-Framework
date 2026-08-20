# CENTRO DE PARAMETRIZACIÓN

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP  
**Última actualización:** 20/08/2026

---

# 1. PROPÓSITO

El Centro de Parametrización es el componente destinado a permitir que una empresa configure y adapte los criterios utilizados por EIOS para analizar y recomendar decisiones de compra.

Su objetivo es permitir que los criterios empresariales puedan modificarse sin necesidad de alterar el código de la aplicación.

El sistema deberá partir de valores estándar editables.

---

# 2. OBJETIVO

Permitir que una persona autorizada pueda:

- consultar los parámetros actuales;
- comprender qué significa cada parámetro;
- modificar sus valores cuando tenga autorización;
- establecer límites;
- definir periodos de referencia;
- consultar el historial de modificaciones;
- revisar la vigencia de configuraciones;
- comprender el impacto previsto de un cambio.

La activación o desactivación de reglas y la gestión de excepciones quedan sometidas a las restricciones de autoridad establecidas en este documento y en la documentación oficial de reglas y CRC.

---

# 3. PRINCIPIO FUNDAMENTAL

La configuración debe estar controlada por criterios humanos.

EIOS puede realizar cálculos y aplicar reglas, pero la empresa debe conservar el control sobre:

- qué considera aceptable;
- qué considera arriesgado;
- qué situaciones requieren negociación;
- qué situaciones bloquean una compra;
- qué excepciones son admisibles.

Las recomendaciones de EIOS no constituyen por sí mismas cambios de política empresarial.

---

# 4. SEPARACIÓN ENTRE MOTOR Y CONFIGURACIÓN

El motor de decisión y los parámetros deberán mantenerse conceptualmente separados.

### Motor

Define:

> Cómo funciona la lógica.

### Configuración

Define:

> Con qué valores y criterios debe funcionar para una empresa concreta.

La parametrización no podrá utilizarse para modificar silenciosamente la lógica estructural del motor ni para anular salvaguardas de autoridad superior.

---

# 5. CATEGORÍAS DE PARAMETRIZACIÓN

Inicialmente se contemplan las siguientes categorías:

1. Compras
2. Precios
3. Histórico
4. Stock
5. Rotación
6. Rentabilidad
7. Finanzas
8. Proveedores
9. Pagos
10. Reglas de decisión
11. Prioridades
12. Excepciones
13. Fiabilidad de datos
14. Alertas
15. Seguridad y permisos

La lista podrá evolucionar durante el desarrollo.

---

# 6. PARÁMETROS DE COMPRAS

Podrán configurarse criterios relacionados con:

- cantidad mínima;
- cantidad máxima;
- cantidad económica;
- tolerancias de cantidad;
- plazo máximo de entrega;
- condiciones de compra;
- proveedores alternativos;
- condiciones especiales.

---

# 7. PARÁMETROS DE REFERENCIA DE PRECIOS

El sistema deberá permitir establecer:

- periodo de referencia;
- antigüedad máxima;
- número mínimo de operaciones;
- utilización de última compra;
- utilización de media histórica;
- utilización de media ponderada;
- utilización de operaciones comparables;
- utilización de proveedores alternativos.

Ejemplo:

### Periodo principal de comparación

Valor estándar:

**3 meses**

Valores posibles:

- 1 mes;
- 3 meses;
- 6 meses;
- 12 meses;
- 24 meses.

---

# 8. ANTIGÜEDAD DE LOS DATOS

Debe poder establecerse hasta qué antigüedad un dato puede utilizarse como referencia.

Ejemplo:

### Antigüedad máxima

**12 meses**

La modificación de este parámetro puede afectar directamente a las recomendaciones de precio.

---

# 9. COMPARABILIDAD

El sistema deberá permitir establecer qué condiciones deben coincidir para considerar dos compras comparables.

Podrán contemplarse:

- artículo;
- proveedor;
- cantidad;
- fecha;
- condiciones de pago;
- descuentos;
- rappels;
- otras condiciones comerciales.

---

# 10. STOCK

Podrán parametrizarse:

- stock mínimo;
- stock máximo;
- stock objetivo;
- stock de seguridad;
- días de cobertura;
- tolerancia de exceso;
- nivel de riesgo de rotura;
- periodo utilizado para calcular consumo.

---

# 11. ROTACIÓN

Podrán configurarse criterios para clasificar los productos según su rotación.

Los valores deberán ser editables por empresa cuando formen parte del catálogo MVP correspondiente.

---

# 12. PROYECCIÓN DE STOCK

La configuración podrá establecer:

- periodo de proyección;
- método de cálculo de demanda;
- utilización de ventas históricas;
- utilización de pedidos pendientes;
- utilización de compras previstas;
- consideración del plazo de entrega.

El objetivo es determinar si una compra puede evitar una rotura, llegar demasiado tarde, generar exceso o resultar innecesaria.

---

# 13. RENTABILIDAD

Podrán configurarse:

- margen mínimo en euros;
- margen mínimo porcentual;
- margen objetivo;
- tolerancia;
- impacto máximo de descuentos;
- impacto máximo de rappels.

El sistema deberá mostrar claramente si un parámetro está expresado en euros, porcentaje, unidades, días o meses.

---

# 14. FINANZAS

Podrán configurarse criterios relacionados con:

- tesorería mínima;
- fondo de maniobra;
- liquidez;
- pagos próximos;
- horizonte temporal;
- nivel de riesgo financiero aceptable.

La configuración financiera tendrá especial relevancia porque una compra que comprometa la capacidad de atender pagos podrá ser considerada no viable.

Los parámetros financieros críticos estarán sujetos a controles reforzados de autorización, trazabilidad y vigencia.

---

# 15. REGLAS DE DECISIÓN

Cada regla deberá disponer conceptualmente de:

- identificador;
- nombre;
- descripción;
- categoría;
- condición;
- valor de referencia;
- resultado;
- prioridad;
- severidad;
- estado;
- posibilidad de excepción.

La definición y evaluación de las reglas pertenece a `04_Reglas/Matriz_Reglas_MVP.md`.

---

# 16. TIPOS DE RESULTADO

Una regla podrá contribuir a uno de los siguientes resultados:

### COMPRAR

### NEGOCIAR

### COMPRAR CONDICIONADO

### NO COMPRAR

La resolución consolidada y el resultado `INFORMACIÓN INSUFICIENTE` por insuficiencia de evidencia corresponden a las reglas y a la CRC según su autoridad.

---

# 17. PRIORIDAD

Las reglas pueden disponer de un nivel de prioridad.

La prioridad **no constituye autoridad de resolución**.

| Prioridad | Nivel | Ejemplo |
|---|---|---|
| 1 | Crítica | Riesgo financiero grave |
| 2 | Muy alta | Margen insuficiente |
| 3 | Alta | Riesgo importante de stock |
| 4 | Media | Precio superior al objetivo |
| 5 | Baja | Diferencia histórica menor |

La jerarquía definitiva pertenece a la documentación de reglas y CRC. El Centro no podrá redefinirla unilateralmente.

---

# 18. BLOQUEO

Algunas reglas podrán tener capacidad de bloqueo.

Una regla de bloqueo no deberá quedar anulada simplemente porque existan varias reglas favorables.

El Centro de Parametrización no podrá convertir mediante un parámetro ordinario una restricción crítica o no anulable en una condición permisiva.

---

# 19. EXCEPCIONES

Las excepciones deberán ser previamente definidas, explícitas y trazables.

El parámetro `RGL-006` no autoriza por sí mismo cualquier excepción.

Una excepción crítica o que afecte a una salvaguarda deberá estar autorizada por la fuente documental competente.

---

# 20. CONFLICTO ENTRE REGLAS

El Centro podrá mostrar y administrar los parámetros que sean necesarios para reglas configurables, pero **no define la metodología de resolución de conflictos**.

Cuando varias reglas produzcan resultados diferentes:

```text
REGLAS
  ↓
EVALUACIÓN
  ↓
CRC
  ↓
RESULTADO CONSOLIDADO
```

La autoridad sobre la resolución corresponde a la CRC.

---

# 21. PRECIO MÁXIMO RECOMENDADO

El sistema deberá permitir configurar los criterios que intervienen en la determinación del precio máximo recomendado.

Podrán considerarse:

- última compra;
- compras recientes;
- periodo histórico;
- precio ponderado;
- operaciones comparables;
- proveedores alternativos;
- margen;
- condiciones de pago;
- descuentos;
- rappels.

No se establecerá una fórmula definitiva mientras no exista una especificación aprobada.

---

# 22. TOLERANCIAS

Muchos parámetros podrán permitir una tolerancia.

Ejemplo:

Precio máximo: 17,80 €  
Tolerancia: 3 %

La tolerancia no podrá utilizarse para superar una salvaguarda crítica.

---

# 23. ALERTAS

Podrán existir diferentes niveles de alerta:

### Informativa

No modifica la recomendación.

### Advertencia

Requiere atención.

### Crítica

Puede modificar o bloquear la recomendación cuando así lo determine una regla con autoridad para ello.

---

# 24. VALORES ESTÁNDAR

EIOS deberá disponer de una configuración inicial estándar.

Los valores estándar deberán considerarse:

> PUNTO DE PARTIDA

y no:

> VERDAD EMPRESARIAL.

Cada empresa podrá adaptarlos cuando el parámetro sea configurable y no esté protegido por una restricción superior.

---

# 25. EXPLICACIÓN DE CADA PARÁMETRO

Cada parámetro deberá mostrar:

- nombre;
- valor actual;
- unidad;
- valor estándar;
- descripción;
- impacto de modificarlo.

El usuario deberá poder comprender qué controla el parámetro y qué consecuencias puede producir su modificación.

---

# 26. EDICIÓN VISUAL

El Centro de Parametrización deberá diseñarse pensando en usuarios no técnicos.

La interfaz deberá priorizar:

- claridad;
- sencillez;
- lectura rápida;
- explicación;
- edición directa;
- prevención de errores.

No deberá parecer una pantalla de programación.

---

# 27. CAMBIO DE PARÁMETROS

Antes de guardar un cambio importante, el sistema debería mostrar:

### Valor anterior

### Nuevo valor

### Consecuencia prevista

El usuario deberá confirmar el cambio cuando corresponda al nivel de autorización requerido.

---

# 28. HISTORIAL

Los cambios deberán conservar:

- parámetro;
- valor anterior;
- nuevo valor;
- fecha;
- usuario;
- motivo;
- empresa;
- estado.

No deberá perderse la configuración anterior.

---

# 29. VIGENCIA

Cada configuración podrá disponer de:

- fecha de inicio;
- fecha de finalización;
- estado.

Estados posibles:

- borrador;
- pendiente de aprobación;
- activa;
- programada;
- sustituida;
- archivada.

---

# 30. SIMULACIÓN

La simulación de cambios queda como evolución del sistema y fuera del alcance operativo del MVP inicial.

Cuando se implemente, deberá permitir modificar temporalmente un parámetro sin aplicarlo y observar su posible efecto.

---

# 31. CONFIGURACIÓN POR EMPRESA

EIOS deberá poder utilizar diferentes configuraciones para diferentes empresas.

Cada empresa podrá disponer de:

- parámetros propios;
- tolerancias propias;
- políticas financieras propias;
- criterios propios de operación;
- reglas propias cuando estén expresamente autorizadas.

La configuración deberá quedar aislada entre empresas.

Las restricciones de autoridad y las salvaguardas comunes no podrán ser anuladas por una configuración empresarial ordinaria.

---

# 32. CAMBIOS DE POLÍTICA EMPRESARIAL

El sistema deberá permitir modificar los criterios cuando cambie la política empresarial, siempre que el parámetro sea configurable y la modificación esté autorizada.

El cambio no deberá destruir el histórico anterior.

---

# 33. PERMISOS

No todos los usuarios deberán tener capacidad para modificar todos los parámetros.

Deberán contemplarse diferentes niveles de permiso.

### Consulta

Puede visualizar.

### Operativo

Puede modificar determinados parámetros no críticos.

### Responsable

Puede modificar parámetros relevantes dentro de su ámbito autorizado.

### Administrador

Puede gestionar la configuración dentro de los límites de autoridad establecidos por EIOS.

Los parámetros críticos requieren controles adicionales de autorización, trazabilidad y vigencia.

---

# 34. TRAZABILIDAD

Una decisión de EIOS deberá poder relacionarse con la configuración vigente en el momento en que fue tomada.

Debe ser posible responder:

> ¿Qué parámetros y reglas estaban activos cuando EIOS recomendó esta compra?

---

# 35. SEGURIDAD

Los cambios de configuración deberán quedar registrados.

Las modificaciones críticas deberán requerir autorización según el nivel de permiso correspondiente.

No se permitirá modificar silenciosamente una regla que pueda alterar decisiones empresariales importantes.

Los parámetros ordinarios no podrán:

- desactivar reglas críticas;
- anular restricciones no anulables;
- habilitar excepciones no autorizadas;
- convertir información insuficiente en una recomendación favorable.

---

# 36. PRINCIPIO DE NO SATURACIÓN

El Centro de Parametrización puede contener una gran cantidad de posibilidades, pero no deberá mostrarlas todas simultáneamente.

La interfaz deberá organizarse por categorías.

El usuario deberá poder profundizar únicamente cuando lo necesite.

---

# 37. PRINCIPIO DE EXPLICABILIDAD

Cada parámetro debe responder a tres preguntas:

1. ¿Qué controla?
2. ¿Cuál es su valor actual?
3. ¿Qué ocurre si lo modifico?

Esta información deberá estar disponible directamente desde la interfaz.

---

# 38. PRINCIPIO DE CONTROL HUMANO

EIOS no debe modificar automáticamente parámetros empresariales críticos.

Las recomendaciones del sistema no equivalen a cambios de política.

Las modificaciones importantes deberán requerir intervención humana autorizada.

---

# 39. PRINCIPIO DE TRAZABILIDAD

Toda modificación relevante deberá poder reconstruirse.

EIOS deberá conservar:

> quién cambió qué, cuándo, de qué valor a qué valor y por qué.

---

# 40. EVOLUCIÓN PREVISTA

El Centro de Parametrización podrá evolucionar hacia un sistema capaz de:

- simular configuraciones;
- comparar configuraciones;
- crear escenarios;
- programar cambios;
- analizar el impacto histórico;
- analizar el impacto previsto;
- identificar reglas conflictivas;
- detectar parámetros posiblemente incoherentes.

Estas funcionalidades no forman parte del MVP inicial salvo las capacidades expresamente aprobadas en la documentación vigente.

---

# 41. MVP

La primera versión deberá centrarse en:

1. Visualizar parámetros.
2. Editar parámetros autorizados.
3. Mostrar unidades.
4. Mostrar explicación.
5. Mostrar valores estándar.
6. Registrar cambios.
7. Mantener histórico.
8. Controlar vigencia.
9. Aplicar permisos.
10. Preservar trazabilidad.

La activación/desactivación de reglas, prioridades y excepciones no se considera una autorización genérica: únicamente podrá realizarse cuando la autoridad documental correspondiente lo permita.

La simulación avanzada queda fuera del MVP inicial.

---

# 42. ESTADO ACTUAL

**Versión:** 0.2  
**Estado:** APROBADO  
**Baseline:** EIOS Vertical MVP

**Dependencias principales:**

- `01_Modelo/Especificacion_funcional.md`;
- `02_Parametros/Catalogo_Parametros_MVP_v0.2.md`;
- `02_Parametros/Matriz_Parametros_Reglas_MVP.md`;
- `04_Reglas/Matriz_Reglas_MVP.md`;
- `05_Motor/Capa_resolucion_conflictos.md`;
- `00_Gobierno/Matriz_Autoridad_Documental.md`;
- `00_Gobierno/EIOS_Vertical_MVP_Salvaguarda_2026-08-16.md`.

La autoridad sobre los valores configurables corresponde a este documento y al catálogo de parámetros; la autoridad sobre reglas y resolución de conflictos corresponde a sus documentos especializados.

Las decisiones D-01 a D-08 del `Decision_Log_Parametros_MVP.md` forman parte de la base de gobierno de esta versión.

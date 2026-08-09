# CENTRO DE PARAMETRIZACIÓN

## EIOS — Enterprise Intelligent Operations System

**Versión:** 0.1  
**Estado:** En desarrollo  
**Última actualización:** 09/08/2026

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
- modificar sus valores;
- activar o desactivar determinadas reglas;
- establecer límites;
- definir periodos de referencia;
- establecer prioridades;
- definir excepciones;
- consultar el historial de modificaciones.

---

# 3. PRINCIPIO FUNDAMENTAL

La configuración debe estar controlada por criterios humanos.

EIOS puede realizar cálculos y aplicar reglas, pero la empresa debe conservar el control sobre:

- qué considera aceptable;
- qué considera arriesgado;
- qué situaciones requieren negociación;
- qué situaciones bloquean una compra;
- qué excepciones son admisibles.

---

# 4. SEPARACIÓN ENTRE MOTOR Y CONFIGURACIÓN

El motor de decisión y los parámetros deberán mantenerse conceptualmente separados.

### Motor

Define:

> Cómo funciona la lógica.

### Configuración

Define:

> Con qué valores y criterios debe funcionar para una empresa concreta.

Esto permitirá adaptar EIOS a diferentes empresas sin reconstruir el sistema.

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

Descripción:

> Determina el periodo máximo durante el cual una compra histórica puede considerarse una referencia válida para determinadas comparaciones.

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

Ejemplo conceptual:

### Alta rotación

Más de X unidades o ventas durante el periodo definido.

### Rotación media

Entre X e Y.

### Baja rotación

Menos de Y.

### Sin rotación

Sin ventas durante el periodo establecido.

Los valores deberán ser editables por empresa.

---

# 12. PROYECCIÓN DE STOCK

La configuración deberá permitir establecer:

- periodo de proyección;
- método de cálculo de demanda;
- utilización de ventas históricas;
- utilización de pedidos pendientes;
- utilización de compras previstas;
- consideración del plazo de entrega.

El objetivo es determinar si una compra puede:

- evitar una rotura;
- llegar demasiado tarde;
- generar exceso;
- resultar innecesaria.

---

# 13. RENTABILIDAD

Podrán configurarse:

- margen mínimo en euros;
- margen mínimo porcentual;
- margen objetivo;
- tolerancia;
- impacto máximo de descuentos;
- impacto máximo de rappels.

El sistema deberá mostrar claramente si un parámetro está expresado en:

- euros;
- porcentaje;
- unidades;
- días;
- meses.

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

---

# 16. TIPOS DE RESULTADO

Una regla podrá contribuir a uno de los siguientes resultados:

### COMPRAR

### NEGOCIAR

### COMPRAR CONDICIONADO

### NO COMPRAR

---

# 17. PRIORIDAD

Las reglas deberán poder disponer de un nivel de prioridad.

Ejemplo:

| Prioridad | Nivel | Ejemplo |
|---|---|---|
| 1 | Crítica | Riesgo financiero grave |
| 2 | Muy alta | Margen insuficiente |
| 3 | Alta | Riesgo importante de stock |
| 4 | Media | Precio superior al objetivo |
| 5 | Baja | Diferencia histórica menor |

La escala definitiva queda pendiente de validación.

---

# 18. BLOQUEO

Algunas reglas podrán tener capacidad de bloqueo.

Ejemplo:

### Regla

> La compra compromete la capacidad de atender pagos.

### Resultado

**NO COMPRAR**

Una regla de bloqueo no deberá quedar anulada simplemente porque existan varias reglas favorables.

---

# 19. EXCEPCIONES

Las reglas podrán disponer de excepciones previamente definidas.

Ejemplo:

### Regla

> No comprar si existe exceso de stock.

### Excepción

> Existe pedido confirmado de cliente.

### Resultado

> La regla de exceso de stock queda mitigada.

Las excepciones deberán ser explícitas y trazables.

---

# 20. CONFLICTO ENTRE REGLAS

El Centro de Parametrización deberá permitir definir cómo actuar cuando varias reglas produzcan resultados diferentes.

Ejemplo:

- precio favorable;
- margen favorable;
- exceso de stock;
- pedido confirmado;
- tesorería suficiente.

La configuración deberá permitir establecer qué reglas tienen mayor peso o capacidad de bloqueo.

La metodología definitiva queda pendiente de diseño.

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

No se establecerá inicialmente una fórmula definitiva hasta validar el modelo con casos reales.

---

# 22. TOLERANCIAS

Muchos parámetros deberán permitir una tolerancia.

Ejemplo:

Precio máximo:

17,80 €

Tolerancia:

3 %

Esto permitirá diferenciar entre:

> Diferencia aceptable

y

> Diferencia que requiere negociación.

---

# 23. ALERTAS

Podrán configurarse diferentes niveles de alerta.

### Informativa

No modifica la recomendación.

### Advertencia

Requiere atención.

### Crítica

Puede modificar o bloquear la recomendación.

---

# 24. VALORES ESTÁNDAR

EIOS deberá disponer de una configuración inicial estándar.

Los valores estándar deberán considerarse:

> PUNTO DE PARTIDA

y no:

> VERDAD EMPRESARIAL.

Cada empresa podrá adaptarlos.

---

# 25. EXPLICACIÓN DE CADA PARÁMETRO

Cada parámetro deberá mostrar:

### Nombre

### Valor actual

### Unidad

### Valor recomendado/estándar

### Descripción

### Impacto de modificarlo

Ejemplo:

### Antigüedad máxima de referencia

**Valor actual:** 12 meses

**Unidad:** meses

**Valor estándar:** 12 meses

**Descripción:**

Determina hasta qué antigüedad se consideran válidas determinadas compras históricas.

**Si aumenta:**

EIOS podrá utilizar más datos históricos, pero aumenta el riesgo de utilizar precios menos representativos de la situación actual.

**Si disminuye:**

Las referencias serán más recientes, pero puede existir menor cantidad de datos disponibles.

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

Ejemplo:

> Margen mínimo

20 % → 25 %

> Este cambio puede provocar que determinadas operaciones actualmente clasificadas como "COMPRAR" pasen a "NEGOCIAR".

El usuario deberá confirmar el cambio.

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

Como evolución del sistema, se contempla una función:

## SIMULAR CAMBIO

Permitiría modificar temporalmente un parámetro sin aplicarlo y observar su posible efecto.

Ejemplo:

Margen mínimo actual:

20 %

Simulación:

25 %

Resultado:

> 14 operaciones históricas cambiarían de "COMPRAR" a "NEGOCIAR".

Esta funcionalidad deberá desarrollarse posteriormente.

---

# 31. CONFIGURACIÓN POR EMPRESA

EIOS deberá poder utilizar diferentes configuraciones para diferentes empresas.

Cada empresa podrá disponer de:

- reglas propias;
- parámetros propios;
- tolerancias propias;
- prioridades propias;
- excepciones propias;
- políticas financieras propias.

La configuración deberá quedar aislada entre empresas.

---

# 32. CAMBIOS DE POLÍTICA EMPRESARIAL

El sistema deberá permitir modificar los criterios cuando cambie la política empresarial.

Ejemplos:

- aumentar el margen mínimo;
- reducir el stock máximo;
- exigir mejores plazos de pago;
- reducir el nivel de riesgo financiero aceptado;
- cambiar el periodo de referencia de precios.

El cambio no deberá destruir el histórico anterior.

---

# 33. PERMISOS

No todos los usuarios deberán tener capacidad para modificar todos los parámetros.

Deberán contemplarse diferentes niveles de permiso.

Ejemplo conceptual:

### Consulta

Puede visualizar.

### Operativo

Puede modificar determinados parámetros.

### Responsable

Puede modificar reglas y parámetros relevantes.

### Administrador

Puede gestionar toda la configuración.

La definición definitiva de permisos queda pendiente.

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

---

# 36. PRINCIPIO DE NO SATURACIÓN

El Centro de Parametrización puede contener una gran cantidad de posibilidades, pero no deberá mostrarlas todas simultáneamente.

La interfaz deberá organizarse por categorías.

Ejemplo:

COMPRAS
STOCK
PRECIOS
RENTABILIDAD
FINANZAS
REGLAS
EXCEPCIONES
SISTEMA

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

Estas funcionalidades no forman parte necesariamente de la primera versión.

---

# 41. MVP

La primera versión deberá centrarse en:

1. Visualizar parámetros.
2. Editar parámetros.
3. Mostrar unidades.
4. Mostrar explicación.
5. Mostrar valores estándar.
6. Activar/desactivar reglas.
7. Definir prioridades.
8. Definir excepciones básicas.
9. Registrar cambios.
10. Mantener histórico.

La simulación avanzada queda fuera del MVP inicial.

---

# 42. ESTADO ACTUAL

**Estado:** Diseño conceptual.

**Dependencias principales:**

- Modelo Empresarial de Decisión.
- Motor de reglas.
- Modelo de datos.
- Sistema de usuarios y permisos.

**Siguiente trabajo previsto:**

Definir el catálogo inicial de parámetros y reglas que serán configurables en el MVP.

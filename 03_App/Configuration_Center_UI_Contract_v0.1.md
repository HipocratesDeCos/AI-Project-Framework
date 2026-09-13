# EIOS — Configuration Center UI Contract v0.1

**Estado:** DISEÑO  
**Fecha:** 2026-09-13  
**Baseline físico:** `main @ 409d3a19d3cfcb217db431465189671b50c42dbc`  
**Autoridad funcional:** `02_Parametros/Centro_Parametrizacion.md`  
**Autoridad de parámetros:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`  
**Frontera técnica existente:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md`  
**Arquitectura UI:** `03_App/UI_Architecture_Contract_v0.1.md`

---

## 1. Propósito

Definir la interfaz MVP del Centro de Parametrización sin crear parámetros, reglas, fórmulas, permisos empresariales, excepciones ni autoridad decisional nueva.

La UI administra y representa configuración autorizada. No interpreta reglas ni calcula decisiones.

## 2. Perímetro MVP

La interfaz permite:

- seleccionar el ámbito empresarial disponible para el usuario;
- listar y buscar parámetros autorizados;
- filtrar por categoría cuando dicha clasificación esté disponible desde fuentes autorizadas;
- consultar identificador, nombre, descripción, valor actual, tipo/unidad, vigencia y restricciones disponibles;
- consultar histórico de cambios;
- iniciar edición únicamente cuando el servicio autorizado indique que el cambio está permitido;
- introducir un nuevo valor y, cuando proceda, vigencia y motivo;
- solicitar validación al servicio autorizado;
- mostrar valor anterior y nuevo antes de aplicar;
- requerir confirmación humana antes de ejecutar el cambio;
- aplicar el cambio mediante la frontera autorizada;
- mostrar resultado técnico, trazabilidad y estado final de la operación.

## 3. Exclusiones explícitas

Esta UI no autoriza ni implementa:

- creación de parámetros;
- eliminación de parámetros;
- creación o modificación estructural de reglas;
- activación/desactivación de reglas salvo futura autoridad explícita;
- edición de prioridades CRC;
- creación de excepciones;
- bypass de restricciones o salvaguardas;
- simulación de impacto avanzado;
- cálculo retrospectivo o prospectivo del efecto decisional de un cambio;
- autenticación o política corporativa de identidad;
- escritura directa en SQL;
- acceso directo desde Presentation a código de dominio;
- recomendación de compra ni decisión empresarial.

## 4. Arquitectura obligatoria

```text
Presentation
    ↓
Configuration UI Controller
    ↓
Authorized Configuration Service Boundary
    ↓
Centro de Parametrización materializado
    ↓
Persistencia / histórico autorizados
```

La Presentation no accede directamente a SQL, Catálogo, Rules ni CRC.

El Controller coordina estado de interacción y no reimplementa `validate_change(...)` ni `apply_change(...)`.

## 5. Pantallas / vistas MVP

### 5.1 Lista de parámetros

Debe mostrar como mínimo, cuando estén disponibles desde la autoridad:

- `parameter_id`;
- nombre;
- categoría;
- valor vigente;
- unidad/tipo;
- vigencia;
- indicador de restricción o capacidad de edición.

Debe permitir búsqueda por identificador/nombre y filtrado por categorías disponibles.

### 5.2 Detalle de parámetro

Debe mostrar:

- identidad del parámetro;
- descripción autorizada;
- valor vigente;
- unidad/tipo;
- valor estándar cuando exista en la autoridad;
- vigencia;
- explicación funcional disponible;
- histórico accesible;
- estado de editabilidad devuelto por la frontera autorizada.

### 5.3 Edición

La edición debe mostrar:

- valor actual;
- campo para nuevo valor compatible con el tipo autorizado;
- vigencia cuando la operación lo admita;
- motivo del cambio;
- advertencias o restricciones devueltas por el servicio.

La UI puede aplicar validaciones sintácticas básicas de entrada, pero la validez funcional definitiva corresponde al servicio autorizado.

### 5.4 Confirmación

Antes de aplicar un cambio se debe mostrar, como mínimo:

- parámetro;
- empresa/ámbito;
- valor anterior;
- nuevo valor;
- vigencia;
- motivo;
- advertencias/restricciones recibidas;
- identidad del actor cuando la frontera la proporcione.

El usuario debe confirmar explícitamente la operación.

### 5.5 Histórico

Debe permitir consultar entradas de histórico disponibles con:

- valor anterior;
- nuevo valor;
- actor;
- instante;
- motivo;
- ámbito empresarial;
- vigencia/estado cuando estén disponibles.

La UI es de solo lectura sobre el histórico.

## 6. Estados de interacción

Estados mínimos de UI:

```text
LOADING
READY
VIEWING
EDITING
VALIDATING
VALIDATION_FAILED
AWAITING_CONFIRMATION
APPLYING
APPLIED
FORBIDDEN
ERROR
```

Estos estados son efímeros de interfaz y no crean estados de dominio.

## 7. Regla de autorización

La UI no decide qué usuario puede cambiar qué parámetro.

La capacidad de editar/aplicar debe provenir de la frontera autorizada. Ante ausencia de autorización demostrada:

```text
FAIL CLOSED → solo lectura / FORBIDDEN
```

Un parámetro restringido no puede rebajarse a ordinario por lógica visual.

## 8. Regla de impacto previsto

`Centro_Parametrizacion.md` requiere explicar el impacto de modificar un parámetro, pero la simulación avanzada queda fuera del MVP.

Por tanto la UI puede mostrar:

- explicación descriptiva autorizada del parámetro;
- advertencias estáticas o semánticas existentes;
- restricciones comunicadas por el servicio.

No puede fabricar una predicción cuantitativa, recálculo histórico ni impacto sobre decisiones si no existe un productor autorizado específico.

Cuando ese productor no exista, deberá mostrarse una formulación equivalente a `impacto cuantitativo no disponible en este alcance`.

## 9. Vigencia

La UI debe preservar la semántica de vigencia de la frontera existente y no inventar una taxonomía paralela.

No debe permitir intervalos inválidos ni configuraciones activas incompatibles si el servicio las rechaza.

## 10. Tipado y unidades

La UI debe seleccionar el control de entrada a partir del tipo/unidad autorizados cuando estén disponibles.

La elección visual del control no altera la semántica del valor.

La validación funcional definitiva corresponde al Centro materializado.

## 11. Errores

La UI debe distinguir al menos las semánticas existentes:

- `PARAMETER_NOT_FOUND`;
- `INVALID_VALUE`;
- `INVALID_TYPE`;
- `INVALID_VALIDITY`;
- `UNAUTHORIZED_CHANGE`;
- `CONFLICTING_ACTIVE_CONFIGURATION`;
- `RESTRICTED_PARAMETER`;
- `INVALID_COMPANY_SCOPE`;
- fallo técnico no clasificado.

Ningún error técnico o de autorización puede transformarse en una modificación aplicada.

## 12. Trazabilidad

Después de un cambio aplicado, la UI debe mostrar o conservar referencias suficientes para relacionar la operación con:

- parámetro;
- empresa;
- actor;
- instante;
- valor anterior/nuevo;
- motivo;
- vigencia;
- identificador o referencia técnica de trazabilidad cuando exista.

La UI no reescribe histórico.

## 13. Accesibilidad y no saturación

- no depender exclusivamente de color;
- etiquetas persistentes;
- errores asociados al control afectado cuando sea posible;
- navegación por teclado en controles principales;
- separación clara entre consulta, edición y confirmación;
- categorías y búsqueda para evitar mostrar todos los parámetros simultáneamente;
- advertencias críticas visibles antes de confirmar.

## 14. Invariantes de interfaz

**CCUI-I01 — No autoridad nueva:** la UI no crea parámetros, reglas ni política.  
**CCUI-I02 — Service boundary:** toda lectura/escritura funcional pasa por la frontera autorizada.  
**CCUI-I03 — Fail closed:** sin autorización demostrada no hay edición.  
**CCUI-I04 — Human confirmation:** ningún cambio se aplica sin confirmación humana explícita.  
**CCUI-I05 — History immutable:** el histórico es representado, no reescrito.  
**CCUI-I06 — No simulation inference:** no se inventa impacto cuantitativo.  
**CCUI-I07 — Company isolation:** la UI no mezcla ámbitos empresariales.  
**CCUI-I08 — Type integrity:** no se convierte silenciosamente tipo/unidad.  
**CCUI-I09 — Error integrity:** un error nunca equivale a cambio aplicado.  
**CCUI-I10 — No decision:** la UI no produce resultados de compra.

## 15. Criterio de cierre de diseño

El diseño podrá cerrarse si una segunda auditoría demuestra que:

1. todas las interacciones tienen autoridad identificable;
2. no se crea semántica de reglas, parámetros, permisos o simulación;
3. la arquitectura respeta Presentation → Controller → Service;
4. el flujo de edición es fail-closed;
5. la trazabilidad e histórico permanecen no destructivos;
6. la UI puede implementarse sin modificar componentes decisionales cerrados.

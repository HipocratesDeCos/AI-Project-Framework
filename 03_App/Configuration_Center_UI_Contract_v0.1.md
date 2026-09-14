# EIOS — Configuration Center UI Contract v0.1

**Estado:** 🔒 CERRADO — DISEÑO UI MVP  
**Fecha:** 2026-09-13  
**Baseline físico:** `main @ 409d3a19d3cfcb217db431465189671b50c42dbc`  
**Estado posterior de integración:** PR #132 · CI #752/#753 SUCCESS · merge `6206df223f2f952977802300b2579f1e51e491d5`  
**Autoridad funcional:** `02_Parametros/Centro_Parametrizacion.md`  
**Autoridad de parámetros:** `02_Parametros/Catalogo_Parametros_MVP_v0.3.md`  
**Frontera técnica existente:** `08_Implementacion/Centro_Parametrizacion_Implementation_Contract.md`  
**Arquitectura UI:** `03_App/UI_Architecture_Contract_v0.1.md`

> **Precisión de estado:** este documento cierra el **diseño UI MVP**. No declara que toda la superficie aquí definida esté materializada ejecutablemente. El runtime demostrado actualmente permanece limitado al subconjunto **selected-context** cerrado en Slices 1–4 y su conformidad E2E.

---

## 1. Propósito

Definir la interfaz MVP del Centro de Parametrización sin crear parámetros, reglas, fórmulas, permisos empresariales, excepciones ni autoridad decisional nueva.

La UI administra y representa configuración autorizada. No interpreta reglas ni calcula decisiones.

## 2. Perímetro MVP

La interfaz permite:

- seleccionar únicamente ámbitos empresariales que la frontera autorizada entregue como accesibles;
- listar y buscar parámetros autorizados;
- filtrar por categoría cuando dicha clasificación esté disponible desde fuentes autorizadas;
- consultar identificador, nombre, descripción, valor actual, tipo/unidad, vigencia y restricciones disponibles;
- consultar histórico de cambios;
- iniciar edición únicamente cuando el servicio autorizado indique que el cambio está permitido;
- introducir un nuevo valor y, cuando proceda, vigencia y motivo;
- solicitar validación al servicio autorizado;
- mostrar valor anterior y nuevo antes de aplicar;
- requerir confirmación humana antes de ejecutar el cambio;
- revalidar contra el estado vigente inmediatamente antes de aplicar;
- aplicar el cambio mediante la frontera autorizada;
- mostrar resultado técnico, trazabilidad y estado final de la operación.

## 3. Exclusiones explícitas

Esta UI no autoriza ni implementa:

- creación o eliminación de parámetros;
- creación o modificación estructural de reglas;
- activación/desactivación de reglas salvo futura autoridad explícita;
- edición de prioridades CRC;
- creación de excepciones;
- bypass de restricciones o salvaguardas;
- simulación de impacto avanzado;
- cálculo retrospectivo o prospectivo del efecto decisional de un cambio;
- autenticación o política corporativa de identidad;
- elección libre o suplantación del actor de auditoría;
- introducción libre de `company_id` fuera de ámbitos autorizados;
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

## 5. Vistas MVP

### 5.1 Lista de parámetros

Debe mostrar, cuando la autoridad los proporcione:

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

- identidad y descripción autorizadas;
- valor vigente;
- unidad/tipo;
- valor estándar cuando exista;
- vigencia;
- explicación funcional disponible;
- histórico accesible;
- estado de editabilidad devuelto por la frontera autorizada.

### 5.3 Edición

Debe mostrar:

- valor actual;
- nuevo valor compatible con el tipo autorizado;
- vigencia cuando la operación lo admita;
- motivo del cambio;
- advertencias o restricciones devueltas por el servicio.

La UI puede realizar validación sintáctica de entrada, pero la validez funcional definitiva corresponde al servicio autorizado.

### 5.4 Confirmación

Antes de aplicar un cambio se muestra, como mínimo:

- parámetro;
- empresa/ámbito autorizado;
- valor anterior;
- nuevo valor;
- vigencia;
- motivo;
- advertencias/restricciones;
- actor únicamente como identidad obtenida de la frontera autorizada, nunca como dato libre editable.

La confirmación humana no sustituye la autorización del servicio.

Tras la confirmación y antes de aplicar, el Controller solicita una revalidación contra el estado vigente. Si el servicio informa conflicto o invalidez, la operación no se aplica.

### 5.5 Histórico

Debe permitir consultar entradas disponibles con valor anterior/nuevo, actor, instante, motivo, ámbito y vigencia/estado cuando existan. El histórico es de solo lectura.

## 6. Estados de interacción

```text
LOADING
READY
VIEWING
EDITING
VALIDATING
VALIDATION_FAILED
AWAITING_CONFIRMATION
REVALIDATING
APPLYING
APPLIED
FORBIDDEN
CONFLICT
ERROR
```

Son estados efímeros de UI y no crean estados de dominio.

## 7. Autorización, actor y empresa

La UI no decide permisos, no autentica al actor y no concede ámbitos empresariales.

- los ámbitos empresariales seleccionables proceden de la frontera autorizada;
- el actor de cambio procede del contexto confiable de dicha frontera o de una futura frontera de identidad autorizada;
- la UI no permite introducir ni sustituir libremente esos identificadores;
- ante ausencia de autorización demostrada: `FAIL CLOSED → solo lectura / FORBIDDEN`.

Un parámetro restringido no puede rebajarse a ordinario por lógica visual.

## 8. Explicación frente a simulación

La UI puede explicar qué controla un parámetro y mostrar advertencias semánticas existentes.

No puede afirmar qué operaciones históricas cambiarían de resultado, predecir nuevas recomendaciones, recalcular decisiones ni cuantificar impacto futuro sin un productor autorizado específico.

La explicación descriptiva no equivale a simulación. Si no existe productor de impacto autorizado, la interfaz debe comunicar que el impacto cuantitativo no está disponible en este alcance.

## 9. Vigencia y concurrencia

La UI preserva la semántica de vigencia existente y no inventa una taxonomía paralela.

No define locking ni versionado nuevos. Para evitar aplicar sobre estado obsoleto, exige revalidación inmediata previa a `apply_change(...)` y respeta cualquier `CONFLICTING_ACTIVE_CONFIGURATION` u otra respuesta de conflicto del servicio.

## 10. Tipado y unidades

El control visual puede derivarse del tipo/unidad autorizados cuando estén disponibles. La elección del control no altera semántica ni convierte silenciosamente unidades.

La validación funcional definitiva corresponde al Centro materializado.

## 11. Errores

La UI distingue las semánticas existentes: `PARAMETER_NOT_FOUND`, `INVALID_VALUE`, `INVALID_TYPE`, `INVALID_VALIDITY`, `UNAUTHORIZED_CHANGE`, `CONFLICTING_ACTIVE_CONFIGURATION`, `RESTRICTED_PARAMETER`, `INVALID_COMPANY_SCOPE` y fallos técnicos no clasificados.

Ningún error, conflicto o ausencia de autorización puede transformarse en modificación aplicada.

## 12. Trazabilidad

Después de un cambio aplicado, la UI debe representar referencias suficientes para relacionar la operación con parámetro, empresa, actor, instante, valores anterior/nuevo, motivo, vigencia y referencia técnica de trazabilidad cuando exista.

La UI no reescribe histórico.

## 13. Accesibilidad y no saturación

- no depender exclusivamente de color;
- etiquetas persistentes;
- errores asociados al control cuando sea posible;
- navegación por teclado en controles principales;
- separación clara entre consulta, edición y confirmación;
- categorías y búsqueda;
- advertencias críticas visibles antes de confirmar.

## 14. Invariantes de interfaz

**CCUI-I01 — No autoridad nueva:** la UI no crea parámetros, reglas ni política.  
**CCUI-I02 — Service boundary:** toda operación funcional pasa por la frontera autorizada.  
**CCUI-I03 — Fail closed:** sin autorización demostrada no hay edición.  
**CCUI-I04 — Human confirmation:** ningún cambio se aplica sin confirmación humana explícita.  
**CCUI-I05 — Trusted actor:** el actor no es un dato libre editable por Presentation.  
**CCUI-I06 — Authorized company scope:** la empresa no es un ámbito libre inventado por UI.  
**CCUI-I07 — Revalidation:** todo cambio se revalida contra estado vigente antes de aplicar.  
**CCUI-I08 — History immutable:** el histórico es representado, no reescrito.  
**CCUI-I09 — No simulation inference:** explicación no se convierte en simulación.  
**CCUI-I10 — Type integrity:** no se convierte silenciosamente tipo/unidad.  
**CCUI-I11 — Error integrity:** error/conflicto nunca equivale a cambio aplicado.  
**CCUI-I12 — No decision:** la UI no produce resultados de compra.

## 15. Criterio de cierre de diseño

El diseño podrá cerrarse si Audit 2 demuestra que todas las interacciones tienen autoridad identificable, no aparece semántica paralela, la arquitectura respeta Presentation → Controller → Service, edición y ámbitos son fail-closed, actor/empresa no son suplantables desde UI, existe revalidación previa a escritura y no se reabren componentes decisionales cerrados.

**Estado reconciliado:** este criterio fue satisfecho por Audit 2 y el cierre documental; PR #132 quedó integrado con CI #752/#753 en SUCCESS. Esta constatación no amplía la cobertura ejecutable más allá de lo demostrado posteriormente por las unidades selected-context.

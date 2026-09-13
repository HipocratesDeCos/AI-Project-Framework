# EIOS — Configuration Center UI Slice 2 — Implementation Contract v0.1

**Estado:** DEPURADO — PENDIENTE DE AUDITORÍA 2  
**Fecha:** 2026-09-13  
**Baseline:** `main @ 84b4d6cb9614069f63c2a98f6a63383fc14256a6`  
**Autoridad UI:** `03_App/Configuration_Center_UI_Contract_v0.1.md`  
**Dependencia cerrada:** `eios/frontend/visual/configuration_center.py` — Slice 1

## 1. Objeto

Materializar componentes presentacionales inmutables para representar el Configuration Center sin añadir autoridad, lógica de dominio ni nuevas fuentes de datos.

## 2. Entradas autorizadas

Slice 2 consume únicamente objetos ya producidos por capas autorizadas:

- `ConfigurationDetailViewModel`;
- secuencia de `ConfigurationHistoryItemViewModel`;
- `ChangeProposal` cuando Presentation ya dispone de la propuesta;
- `state` y `error_code` observables.

No accede a `ParameterConfigurationCenter`, catálogo, autorización, repositorio, SQL, Rules ni CRC.

## 3. Componentes

### 3.1 `ConfigurationDetailPanel`
Carrier visual del detalle autorizado. No renombra, interpreta ni recalcula valores.

### 3.2 `ConfigurationHistoryPanel`
Carrier visual de una secuencia inmutable de histórico. No agrega, reordena ni elimina entradas.

### 3.3 `ConfigurationChangeForm`
Carrier de campos editables de Presentation (`value`, `valid_from`, `valid_to`, `reason`). No valida funcionalmente.

### 3.4 `ConfigurationConfirmationPanel`
Representa exactamente un `ConfigurationDetailViewModel` y un `ChangeProposal` cuando el estado recibido es `AWAITING_CONFIRMATION`.

No acepta `company_id`, `parameter_id` ni `actor` duplicados o alternativos. De este modo la identidad visible procede del mismo detalle ya construido por Slice 1.

El panel no concede autorización ni ejecuta el cambio.

### 3.5 `ConfigurationStatusPanel`
Representa `state` y `error_code` literalmente, sin transformar error en éxito.

### 3.6 `ConfigurationCenterScreen`
Composición inmutable de los paneles anteriores. Su construcción no llama a motores ni servicios.

## 4. Frontera de confirmación

La existencia de `ConfigurationConfirmationPanel` no implica autorización ni aplicación.

El builder:

- crea panel de confirmación exclusivamente cuando `state == "AWAITING_CONFIRMATION"` y existe `ChangeProposal`;
- si `state == "AWAITING_CONFIRMATION"` y falta propuesta, falla cerrado mediante `ValueError`;
- en cualquier otro estado no crea panel de confirmación, aunque Presentation conserve una propuesta en edición;
- nunca llama a `confirm_and_apply()`.

## 5. Errores y ausencia de datos

- `detail=None` es representable cuando la capa coordinadora informa un estado de error;
- `history=None` significa histórico no disponible por fallo y no equivale a histórico vacío;
- `history=()` significa consulta válida sin entradas;
- `error_code` se conserva literalmente;
- `APPLIED` no puede generarse por Slice 2: solo se representa si llega desde Slice 1.

## 6. No inferencia

Slice 2 no calcula ni infiere nombres/categorías no existentes, impacto, permisos, empresa autorizada, identidad, severidad de errores, recomendaciones ni decisiones de compra.

## 7. Tests obligatorios

- detalle se conserva por identidad;
- histórico conserva orden y contenido;
- histórico `None` y vacío permanecen semánticamente distintos;
- formulario no valida ni transforma el valor;
- confirmación conserva exactamente detalle + propuesta;
- `AWAITING_CONFIRMATION` sin propuesta falla cerrado;
- propuesta presente en un estado distinto no produce panel de confirmación;
- estado/error se conservan literalmente;
- componentes no llaman motores/servicios ni aceptan identificadores alternativos de confirmación.

## 8. Invariantes

**CCUIS2-I01:** presentación pura; no llamadas de dominio.  
**CCUIS2-I02:** sin autoridad nueva.  
**CCUIS2-I03:** `None` ≠ vacío.  
**CCUIS2-I04:** confirmación visual ≠ autorización.  
**CCUIS2-I05:** confirmación reutiliza identidad del detalle, sin identificadores paralelos.  
**CCUIS2-I06:** panel de confirmación solo existe en `AWAITING_CONFIRMATION`.  
**CCUIS2-I07:** datos se preservan sin inferencia.  
**CCUIS2-I08:** error no se transforma en éxito.  
**CCUIS2-I09:** orden histórico preservado.  
**CCUIS2-I10:** no decisión de compra.

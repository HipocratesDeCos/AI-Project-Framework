# EIOS — Configuration Center UI Slice 2 — Implementation Contract v0.1

**Estado:** DISEÑO  
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
- `ChangeProposal` cuando Presentation ya dispone de la propuesta que está representando;
- `state` y `error_code` observables;
- booleano de confirmación pendiente cuando corresponda.

No accede a `ParameterConfigurationCenter`, catálogo, autorización, repositorio, SQL, Rules ni CRC.

## 3. Componentes

### 3.1 `ConfigurationDetailPanel`
Carrier visual del detalle autorizado. No renombra, interpreta ni recalcula valores.

### 3.2 `ConfigurationHistoryPanel`
Carrier visual de una secuencia inmutable de histórico. No agrega, ordena por criterio de negocio ni elimina entradas.

### 3.3 `ConfigurationChangeForm`
Carrier de campos editables de Presentation (`value`, `valid_from`, `valid_to`, `reason`). No valida funcionalmente.

### 3.4 `ConfigurationConfirmationPanel`
Representa el contexto visible y la propuesta que se solicita confirmar. Debe distinguir valor vigente y nuevo valor cuando ambos estén disponibles. No concede autorización ni ejecuta el cambio.

### 3.5 `ConfigurationStatusPanel`
Representa `state` y `error_code` sin transformar error en éxito.

### 3.6 `ConfigurationCenterScreen`
Composición inmutable de los paneles anteriores. Su construcción no llama a motores ni servicios.

## 4. Frontera de confirmación

La existencia de `ConfigurationConfirmationPanel` no implica que el cambio esté autorizado ni aplicado.

Solo puede representarse como pendiente si la capa coordinadora suministra explícitamente `awaiting_confirmation=True` junto con una propuesta. En caso contrario, el builder debe rechazar una composición incoherente en vez de inventar estado.

Slice 2 no llama a `confirm_and_apply()`.

## 5. Errores y ausencia de datos

- `detail=None` es representable cuando la capa coordinadora informa un estado de error.
- `history=None` significa histórico no disponible por fallo; no equivale a histórico vacío.
- `history=()` significa consulta válida sin entradas.
- `error_code` se conserva literalmente.
- `APPLIED` no puede generarse por Slice 2; solo se representa si llega desde Slice 1.

## 6. No inferencia

Slice 2 no calcula ni infiere:

- nombres/categorías no existentes;
- impacto de modificar parámetros;
- permisos;
- empresa autorizada;
- identidad;
- severidad de errores;
- recomendaciones;
- decisiones de compra.

## 7. Tests obligatorios

- detalle se conserva por identidad;
- histórico conserva orden y contenido;
- histórico `None` y vacío permanecen semánticamente distintos;
- formulario no valida ni transforma el valor;
- confirmación conserva propuesta exacta;
- no puede marcar confirmación pendiente sin propuesta;
- propuesta sin confirmación pendiente no se presenta como autorizada;
- estado/error se conservan literalmente;
- componentes no importan `eios.parameters.center` ni llaman motores/servicios.

## 8. Invariantes

**CCUIS2-I01:** presentación pura; no llamadas de dominio.  
**CCUIS2-I02:** sin autoridad nueva.  
**CCUIS2-I03:** `None` ≠ vacío.  
**CCUIS2-I04:** confirmación visual ≠ autorización.  
**CCUIS2-I05:** datos se preservan sin inferencia.  
**CCUIS2-I06:** error no se transforma en éxito.  
**CCUIS2-I07:** orden histórico preservado.  
**CCUIS2-I08:** no decisión de compra.

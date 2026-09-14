# EIOS-BL-003 — Baseline de continuidad Configuration Center UI

**Estado:** DISEÑO — PENDIENTE DE AUDITORÍA  
**Fecha:** 2026-09-14  
**Repositorio:** `HipocratesDeCos/AI-Project-Framework`  
**Rama de referencia:** `main`  
**SHA de referencia propuesto:** `b10c4cde6c4f52af04de0794493432961b745dca`  
**Baseline anterior:** `EIOS-BL-002 @ 1ada9415d0ef885f55419e4775c5976d3e75d08e`

---

## 1. Objeto

Establecer un nuevo punto formal de recuperación después del avance acumulado desde EIOS-BL-002, con foco en la reconciliación de gobierno y en la materialización del Configuration Center UI.

Este Baseline registra estado ya demostrado. No crea autoridad funcional, no declara finalizado el Vertical MVP y no sustituye contratos ni fuentes especializadas.

## 2. Magnitud del delta desde BL-002

Comparación física propuesta:

```text
1ada9415d0ef885f55419e4775c5976d3e75d08e
→
b10c4cde6c4f52af04de0794493432961b745dca
```

Resultado verificado:

- `ahead_by = 60` commits;
- `behind_by = 0`;
- reconciliaciones de Framework Map, Master Project Map, Project Context y Manual Maestro;
- cierre/reconciliación del propio BL-002;
- contrato UI del Configuration Center;
- tres slices ejecutables del Configuration Center UI;
- pruebas automatizadas asociadas;
- reconciliación de Project Context con el nuevo estado físico.

## 3. Estado relevante incorporado

### 3.1 Gobierno y navegación

El estado referenciado contiene reconciliaciones posteriores a BL-002 para:

- `Framework_Map.md`;
- `Master_Project_Map.md`;
- `Project_Context.md`;
- `Manual_Maestro_Proyecto_EIOS.md`;
- `EIOS-BL-002.md` postintegración;
- `Project_Context_Reconciliation_2026-09-14.md`.

### 3.2 Configuration Center UI Contract

Queda cerrado e integrado `03_App/Configuration_Center_UI_Contract_v0.1.md`.

Su alcance autoriza representación y gestión UI de configuración ya autorizada, pero no crea parámetros, reglas, excepciones, identidad, empresas, simulación ni decisión de compra.

### 3.3 Slice 1 — provenance-safe controller

Queda integrado `eios/frontend/visual/configuration_center.py` con:

- contexto empresa/parámetro/actor suministrado aguas arriba;
- detalle e histórico;
- propuesta de cambio;
- validación;
- confirmación humana;
- revalidación previa a escritura;
- aplicación exclusiva mediante `ParameterConfigurationCenter`;
- fail-closed y conservación de errores.

### 3.4 Slice 2 — presentación pura

Queda integrado `eios/frontend/visual/configuration_center_components.py` con carriers visuales inmutables para detalle, histórico, formulario, confirmación, estado y pantalla.

No llama motores/servicios ni crea autoridad.

### 3.5 Slice 3 — selected-context workflow

Queda integrado `eios/frontend/visual/configuration_center_workflow.py` con:

- refresh controlado;
- borrador local;
- preparación/confirmación/cancelación delegadas;
- coherencia estado ↔ pending;
- binding de la configuración aplicada al mismo contexto empresa/parámetro;
- actualización del detalle solo desde backend real;
- histórico no inventado y marcado `stale` tras aplicación;
- errores técnicos de workflow separados de errores de dominio.

## 4. Gates recientes

- PR #132 — Configuration Center UI Contract — CI pre/post SUCCESS;
- PR #133 — Slice 1 — CI #757 / #758 SUCCESS;
- PR #134 — Slice 2 — CI #759 / #760 SUCCESS;
- PR #135 — Slice 3 — CI #761 / #762 SUCCESS;
- PR #136 — Project Context reconciliation — CI #763 / #764 SUCCESS.

El SHA propuesto de BL-003 corresponde al `main` resultante tras PR #136 y validado por CI #764:

```text
b10c4cde6c4f52af04de0794493432961b745dca
```

## 5. Capacidades que este Baseline NO declara cerradas

Configuration Center UI no demuestra todavía:

- autenticación o resolución confiable de identidad;
- enumeración de empresas autorizadas;
- listado/búsqueda global de parámetros desde productor físico autorizado;
- creación o eliminación de parámetros;
- edición estructural de Rules o prioridades CRC;
- creación de excepciones;
- simulación cuantitativa del impacto de un parámetro;
- ejecución automática de una decisión empresarial.

## 6. Bloqueos transversales preservados

BL-003 no resuelve por inferencia:

- Quality & Trust Gate mientras falte un `Decision Input Package` físico, agregado y trazable;
- Supplier Risk valorativo mientras falten autoridad y política cuantitativa;
- Rotation donde continúen gaps de autoridad, dependencias, fórmula o umbral;
- Assurance / Shadow Mode sin una fuente autorizada de decisión humana de referencia y su gobierno;
- Profitability / MGE allí donde la semántica cuantitativa especializada siga sin autoridad suficiente.

## 7. Límites

Este Baseline:

- no declara terminado el MVP;
- no convierte la UI en autenticador;
- no autoriza un selector libre de empresa;
- no crea catálogo ejecutable de parámetros;
- no modifica reglas, parámetros, fórmulas ni umbrales;
- no convierte evidencia en valoración;
- no crea un decisor automático;
- no sustituye la matriz de autoridad ni las fuentes especializadas.

La decisión empresarial final permanece humana.

## 8. Método de establecimiento

```text
DISEÑAR       ✅ — este artefacto inicial
AUDITAR       ⏳
DEPURAR       ⏳
AUDITAR 2     ⏳
CERRAR        ⏳
MATERIALIZAR  ⏳
CI            ⏳
```

## 9. Criterio de validez propuesto

BL-003 solo podrá cerrarse si la auditoría demuestra que:

1. `b10c4cde...` está realmente validado por CI postintegración;
2. el delta desde BL-002 es físicamente `ahead=60`, `behind=0`;
3. no se presenta Configuration Center UI como una UI completa con productores aún inexistentes;
4. se conservan todos los bloqueos relevantes;
5. no se introduce autoridad funcional nueva;
6. el artefacto supera CI pre-merge, reconciliación de `main`, merge protegido y CI postintegración.

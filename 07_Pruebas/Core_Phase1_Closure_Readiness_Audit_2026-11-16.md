# EIOS — AUDITORÍA DE CIERRE TÉCNICO FASE 1 (PRICE / HIS003 / QTG)

**Fecha:** 2026-11-16  
**Baseline de partida:** `main @ fc7f2a19853c864e67d18e0945679ce4a56d9458`  
**Ámbito del cierre:** integridad económica, reproducibilidad de controles de procedencia y simulación de referencia; NO admisión operacional.  
**Decisión de cierre:** **CONDICIONADA** a CI final, aceptación del diff acumulado e integración controlada de PR apiladas.  
**Prohibición vigente:** `REFERENCE_OPERATIONAL_SIMULATION / SYNTHETIC_TEST_ONLY / operational_path=FORBIDDEN / decision_authority=False`.

## 1. Trabajo evaluado

| Unidad | PR | Objetivo verificable |
|---|---:|---|
| 1A | #575 | QTG sin controles aplicables => NO_APTO; PRICE no normaliza divisa/unidad sin conversión numérica documentada |
| 1A2 | #575 | Conversión histórica UNIT/CURRENCY con Decimal, fecha, regla, fuente, evidencias y trazas |
| 1B | #576 | Bases económicas documentadas para QUANTITY, TAX, TRANSPORT, DISCOUNT, SURCHARGE y COMMERCIAL |
| 1C | #577 | Entrada PRICE estricta opt-in por empresa y snapshot; rechaza cobertura económica insuficiente |
| 1D | #578 | Invocador O1 empresarial provenance-safe que no usa fallback del PRICE histórico |
| 1E | #579 | Reconstrucción independiente de PRICE y HIS003 sobre la misma compra/referencia; prueba HIS003 antes de PRICE |
| 1F | #580 | Asociación QTG sintética validada con la misma identidad DIP PRICE/HIS003, sin compartir autoridad |

Las PR están **apiladas**: `#575 → #576 → #577 → #578 → #579 → #580`. No interpretar el estado `mergeable` de una PR aislada como aceptación de la cadena.

## 2. Fronteras verificables

- PRICE solo publica `NORMALIZED` si ejecuta transformaciones autorizadas por sus contratos; conserva `PENDING` cuando faltan datos verificables.
- Las comparaciones económicas materiales declaradas requieren evidencia concordante; el perfil estricto de empresa exige las seis dimensiones soportadas por PRICE.
- El invocador enterprise exige igualdad completa de `PurchaseOperation` y `DecisionContext` antes de ejecutar C1.
- HIS003 se reejecuta con las **siete dimensiones comerciales propias** y evidencias originales; su `Assessment` no se convierte en estado PRICE ni decisión O1.
- QTG usa `ProjectionMaterialEnvelope` + `ProjectionQualityReceipt` + `ProjectionQualityConsumption`; se recompone el recibo. Una etiqueta `APTO` aislada no es prueba admisible.
- El nuevo vínculo QTG/PRICE/HIS003 pertenece a `SYNTHETIC_TEST / TEST_ONLY` y comprueba identidad de empresa, compra y contexto **desde el DIP del QTG**. Un QTG `NO_APTO` permanece visible; un QTG `APTO` sintético nunca concede efecto operacional.

## 3. Limitaciones explícitas que NO deben cerrarse por decreto

1. **Autenticación empresarial/usuarios**: `company_id`, `expected_company_id` y evidencias `VALID` siguen precisando una fuente confiable de identidad y admisión, fuera del núcleo analítico.
2. **Entrada estricta opt-in**: el integrador ERP/aplicación debe invocar la fábrica estricta; el motor histórico se conserva para regresiones y simulaciones.
3. **QTG operacional**: la asociación sintética NO reemplaza `operational_admission.py` ni `projection_quality_o1_binding.py`. La vía operacional exige expediente y autorizaciones reales independientes.
4. **Diferencias fiscales/comerciales**: no existen transformadores genéricos fiables para IVA, transporte, descuentos, rappels o recargos; el resultado continúa `PENDING` cuando no se acredita equivalencia o transformación autorizada.
5. **Multiempresa de producción**: permanecen fuera de este cierre seguridad por usuario, aislamiento de sesiones, concurrencia, conectores ERP, pruebas de carga y despliegue.
6. **Cobertura**: la CI comprueba regresiones pero todavía no representa una medición universal de cobertura, performance, ni una auditoría externa integral.

Estas limitaciones no invalidan las simulaciones sintéticas; **sí impiden declarar el Core listo para operaciones de cualquier empresa**.

## 4. Evidencia de aceptación y auditoría

- Baseline `main` antes de la fase: **2.966 passed**, CI de referencia.
- PR #575: **2.990 passed**; PR #576: **3.018 passed**; PR #577: **3.042 passed**; PR #578: **3.059 passed**; PR #579: **3.081 passed**, sin fallos en los HEAD validados.
- El delta acumulado hasta la PR #580 se concentra en módulos de PRICE, QTG, HIS003, pruebas y documentación; `company_app.py`, los datos empresariales y los esquemas de persistencia no se han alterado.
- La **PR #580 necesita CI verde en su HEAD final** y validación de regresiones negativas de separación de autoridad, recibos cruzados, empresas distintas y ausencia de evidencias.
- Las advertencias conocidas de CI anteriores (nueve) no constituyen un bloqueo nuevo por sí solas, pero deben conservarse registradas.

## 5. Orden seguro de integración

La auditoría establece el siguiente procedimiento, sin conceder autorización implícita de merge:

1. Verificar **CI final verde** y diff completo `main..HEAD(#580)`.
2. Confirmar que **no se han cambiado pruebas históricas** para esconder regresiones ni habilitado efecto operacional.
3. Integrar las PR **en el orden #575 → #576 → #577 → #578 → #579 → #580**, reorientando las bases de las PR apiladas cuando sea necesario, y verificando el resultado y la CI en `main`.
4. Reconciliar el SHA final de `main` y ejecutar otra vez toda la batería después de integrar.
5. Publicar el acta final solo si los criterios anteriores se cumplen.

**Resultado autorizado de esta fase, si se completa:** `CORE PHASE 1 — INTEGRIDAD SINTÉTICA Y CONTRATOS DE COMPARABILIDAD: CERRADO`.

**Resultado NO autorizado:** `CORE EIOS MULTIEMPRESA OPERACIONAL / SAAS: CERRADO`.

## 6. Decisión del auditor

La fase 1 puede aspirar a cierre técnico **circunscrito al Core analítico y sus regresiones sintéticas**. Ni una CI satisfactoria ni 3.000+ pruebas permiten sustituir la prueba operacional con expedientes reales y autorización de cada empresa.

El trabajo de las fases siguientes debe partir de este núcleo, no de una nueva reescritura. No se abre una refactorización general ni nuevas funcionalidades en este acta.

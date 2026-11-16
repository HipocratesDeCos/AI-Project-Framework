# EIOS — PRICE: invocador empresarial con admisión estricta (fase 1D)

**Estado:** implementación de alcance limitado, pendiente de verificación en CI y auditoría  
**Dependencias:** PR #575 (PRICE/QTG), #576 (bases económicas), #577 (cobertura económica por empresa)  
**Naturaleza:** adaptación desde el Core a O1; no habilita operaciones reales ni autoriza decisiones

## Hallazgo previo

El motor C1 ya ofrece `run_price_intelligence_for_company`, que verifica la cobertura económica declarada. Sin embargo, el contrato O1 existente `build_provenanced_price_invoker` utilizaba el motor histórico `run_price_intelligence` sin puerta empresarial. En consecuencia, la mera existencia de la API estricta no garantizaba que una aplicación integrada la utilizara.

## Implementación

Se incorpora una **fábrica explícita y separada**:

`eios.core.price_integration.build_provenanced_company_price_invoker(...)`

Recibe cuatro fuentes:

- `PriceIntelligenceInput` y `PriceIntelligenceAssessmentContext`;
- `PriceCompanyCoverageProfile`, con `company_id` y los datos/documentos declarados del perfil;
- `expected_company_id`, que debe proceder **de un adaptador de empresa autenticado por otra capa** y no de un campo editable por el cliente.

La fábrica valida los tipos, congela copias profundas de los tres contratos y construye un `PriceInvoker` compatible con `run_mvp_execution(..., price_invoker=...)`.

En cada invocación:

1. comprueba igualdad completa de `PurchaseOperation` y de todos los campos de `DecisionContext` con los datos de creación (igual que el invocador provenance-safe anterior);
2. exige `run_price_intelligence_for_company(...)` sin degradarse a `run_price_intelligence(...)`;
3. la puerta empresarial devuelve un informe `PriceCoverageReport` con faltantes; la ruta sin cobertura lanza `PriceCoverageError` **antes** de producir un resultado PRICE;
4. con cobertura documental completa se ejecuta el cálculo C1 normal y se adapta a `CapabilityExecution`, preservando trazas del perfil.

La ruta histórica `build_provenanced_price_invoker` permanece **sin cambios** para reproducibilidad de simulaciones y casos anteriores.

## Seguridad y autoridad

- Una función pública nueva **no obliga por sí sola a todos los productos a utilizarla**. Cada adaptador empresarial nuevo debe registrarla explícitamente y bloquear el uso de la ruta histórica para decisiones admitidas.
- `expected_company_id` no es una identidad autenticada por el motor. El nuevo invocador únicamente exige la coincidencia de la identidad declarada con el alcance que le suministra el sistema anfitrión; autenticación, permisos, auditoría de empresa y calidad de las fuentes corresponden al sistema de admisión.
- Un dictamen QTG `APTO` o HIS003 `COMPARABLE` **no sustituye** la cobertura económica PRICE. No se reutilizan tickets o resultados externos sin revalidación de sus productores.
- O1 coordina capacidades pero no concede autoridad operacional, ni permite al invocador registrar, aceptar o ejecutar compras.
- La ausencia de pruebas de autenticación real y de un conector empresarial hace que esta fábrica sea un contrato de integración, no una certificación multiempresa.

## Regresiones de aceptación

La unidad debe probar que:

- el invocador entrega una capacidad PRICE válida al O1 ya existente con datos sintéticos completos;
- recibe un contexto/compra distinto ⇒ rechazo antes de calcular;
- recibe empresa esperada diferente ⇒ rechazo de cobertura;
- falta alguna dimensión material ⇒ rechazo sin fallback;
- después de construirlo, mutar los objetos originales no cambia el resultado capturado;
- los contratos no tipados y el ID de empresa vacío se rechazan;
- las pruebas precedentes y SQL Server siguen superadas, sin modificar escenarios históricos.

## Pendiente para cerrar por completo la fase 1

1. Adaptador de ingesta real o explícitamente sintético que autentique las fuentes y ligue empresa/usuario/perfil a una identidad de ejecución.
2. Coordinación de recibos exactos de QTG y HIS003, reejecutados desde fuentes autorizadas; sin admitir etiquetas o resultados aislados.
3. Auditoría completa de las PR apiladas, aceptación y secuencia de integración independiente antes de declarar cerrado el Core.

No se modifican `company_app.py`, datos persistentes, reglas fiscales, escenarios sintéticos ni interfaces.

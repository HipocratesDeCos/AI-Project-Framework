# EIOS — CIERRE FASE 1: ASOCIACIÓN SINTÉTICA QTG / PRICE / HIS003 (v0.1)

**Rama:** `feat/core-phase1-qtg-price-his003-synthetic-bind-20261116`  
**Base:** PR #579, dependiente de #578 → #577 → #576 → #575  
**Estado:** implementación y pruebas de frontera en CI; no hay autorización operacional

## 1. Contexto verificado

EIOS ya ofrece dos autoridades independientes:

1. PRICE económico C1 + R-HIS-003 con reconstrucción conjunta de fuentes en `price_his003_reconciliation.py`.
2. QTG `PROJECTION_ONLY` con material `ProjectionMaterialEnvelope`, recibo `ProjectionQualityReceipt` y consumo `ProjectionQualityConsumption`. La comprobación `validate_projection_quality_consumption` reconstruye y compara los recibos originales; `run_reference_operational_simulation` ya enlaza QTG sintético a O1, mientras `projection_quality_o1_binding.py` solo acepta QTG operacional materialmente admitido.

Una etiqueta `APTO` no permite sustituir el recibo completo. Las vías sintéticas no se deben promover a operacional.

## 2. Unidad materializada

`eios/core/price_qtg_his003_synthetic_link.py` añade `link_synthetic_qtg_price_his003`, un enlace **estrictamente de prueba** para comprobar la correspondencia de las fuentes de ambas ramas.

- **Entrada QTG:** sobre `ProjectionMaterialEnvelope`, recibo y consumo generados por los productores existentes; NO se admite un resultado `QualityTrustResult` aislado.
- **Validación QTG:** se vuelve a ejecutar `validate_projection_quality_consumption(..., execution_mode="SYNTHETIC_TEST", consumption_scope="TEST_ONLY")`. Si el material/recibo/consumo no coincide, se rechaza.
- **Identidad DIP:** se reconstruyen `PurchaseOperation`, `DecisionContext` y `company_id` directamente de la captura del DIP encapsulada por el envelope; se comparan con la compra, el contexto y el perfil PRICE/HIS003 suministrados.
- **PRICE/HIS003:** se invoca `reconcile_price_and_his003`, que rehace las evidencias HIS003 antes de calcular PRICE. Su resultado es **técnico**: el QTG no concede suficiencia comercial ni precio por sí mismo.
- **Salida:** `SyntheticPriceHistoryQTGLink`, con huellas SHA-256 de material, recibo, consumo, compra y contexto; estado y confianza QTG reales, resultado PRICE/HIS003 separado, `execution_mode=SYNTHETIC_TEST`, `consumption_scope=TEST_ONLY`, `operational_path=FORBIDDEN`, `decision_authority=False`.

Las fuentes de QTG describen la **calidad de la proyección**, no la confianza documental de los precios históricos. La coincidencia de DIP no equivale a identidad de origen de cada factura/ERP. No se les asigna una autoridad compartida.

## 3. Regresiones

El fichero `tests/test_price_qtg_his003_synthetic_link.py` verifica:

- QTG `NO_APTO` mantiene `NO_APTO` aunque PRICE/HIS003 produzcan resultados distintos, con autoridad siempre falsa.
- QTG `APTO` en material sintético sigue prohibiendo promoción operacional.
- Compra, versión de parámetros, versión de reglas, `data_snapshot_id` y empresa distintas producen rechazo.
- Un recibo QTG sin clase/tipo o cruzado con otro material no es admisible.
- La ausencia de evidencia económica PRICE o evidencias HIS003 falsificadas no se solventan porque el QTG exista.
- Salida reproducible para iguales fuentes y conservación de entradas.

## 4. Lo que ESTA unidad NO afirma

- **No enlaza el QTG operacional con PRICE/HIS003.** La vía operacional requiere `OperationalAdmissionPreflight`, recibos `OPERATIONAL`, cadena causal O1 y fuentes empresariales admitidas. No se puede simular una firma o una empresa real para obtener esa admisión.
- **No convierte el enlace en un invocador O1 de producción.** El resultado no autoriza comprar o negociar.
- **No aporta un autenticador de empresa ni de documentos externos**: `company_id` y los estados `VALID` declarados siguen dependiendo de una admisión empresarial fiable.
- No altera `company_app.py`, la interfaz, las pruebas históricas ni el cálculo financiero.
- No modifica la taxonomía de procedencias o las restricciones de `REFERENCE_OPERATIONAL_SIMULATION`.

## 5. Pendientes para el cierre integral de fase 1

1. CI verde y auditoría estática de las PR #575–#580 apiladas.
2. Acordar si fase 1 significa **cierre de seguridad sintética del Core** (alcance alcanzable) o **admisión operacional** (bloqueada hasta fuentes/mandatos reales).
3. Para la integración en `main`, verificar el orden base a tope, proteger las regresiones y preservar decisiones documentales cerradas.
4. Mantener explícitamente la frontera operacional `FORBIDDEN` hasta completar el expediente real correspondiente.

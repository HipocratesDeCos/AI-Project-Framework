# Preparación de entrada de compra desde un expediente recibido

En **Carga de archivos → Expedientes recibidos**, elegir una versión guardada y pulsar **Preparar entrada de compra**. Seleccionar artículo/proveedor, introducir referencia, cantidad, precio neto en EUR y fecha, y pulsar **Preparar y comprobar entrada**.

La operación se valida con el modelo vigente `eios.core.models.PurchaseOperation`. Es el primer adaptador entre el expediente recibido y el contrato existente, sin modificar C0/Rules ni declarar construido un paquete DIP completo.

## Contratos revisados

- `eios/core/models.py`: PurchaseOperation y DecisionContext.
- `eios/core/decision_input_package.py`: factoría DIP-AGG-01/v0.1, con contextos, evidencias y Centro de Parámetros explícitos.
- `eios/core/finance_decision_input_package.py`: FIN-DIP-01/v0.1, vinculación del horizonte a P-FIN-001 y del mínimo, si se aporta, a P-FIN-002.
- `eios/core/operational_admission.py`: admisión estructural mediante material enlazado; guardar documentos no equivale a ese proceso y el material sintético no se promueve a operacional.
- `eios/stock/rule_inputs.py`: coberturas/necesidad requieren portadores con procedencia y autoridad; el stock recibido o las ventas históricas no los sustituyen automáticamente.

## Mapeo efectivo

| Campo de PurchaseOperation | Procedencia |
|---|---|
| decision_id / scenario_id | Identificadores técnicos deterministas de la preparación; no ejecutan ni identifican una decisión emitida o un escenario evaluado. |
| article_id | Elección entre fichas únicas de la versión seleccionada. |
| supplier_id | Elección entre proveedores únicos de la misma versión. |
| quantity | Cantidad introducida expresamente. |
| unit_price | Precio neto introducido, respetando la precisión del contrato sin redondearlo para hacerlo válido. |
| currency | EUR explícito, única moneda admitida por el contrato actual. |
| operation_date | Fecha introducida expresamente. |

La unidad y referencia de propuesta son auxiliares externos a PurchaseOperation. La unidad debe coincidir exactamente con la ficha del artículo. Empresa, naturaleza, corte, versión y referencias de origen permanecen vinculados al resultado; no se infieren por descripción ni se convierten monedas o embalajes. Las fichas contradictorias o con IDs incompatibles con el máximo canónico de 64 caracteres no se ofrecen para preparar una operación.

La referencia de compra no impone que el artículo tenga un único proveedor posible: permite elegir otro proveedor documentado en la misma versión y deja sin referencia histórica cuando corresponda. Como límites de interfaz local, cantidad/precio no exceden 1.000.000.000; el contrato exige cantidad positiva y precio no negativo. La validación de la operación no implica que un precio cero sea aprobado por reglas.

## Referencias fechadas

La consulta considera líneas del proveedor y moneda de la operación, con fecha anterior o igual a la menor entre fecha de operación y corte documental. La última fecha debe tener una única línea compatible. No se elige una compra anterior para ocultar una última unidad incompatible o una factura contradictoria; tampoco se suman líneas empatadas. El precio neto efectivo deriva de neto de línea/cantidad. La diferencia y porcentaje son descriptivos, sin umbrales ni reglas PRE. Una referencia de precio cero deja el porcentaje indeterminado.

El inventario debe ser único y compatible. Si su fecha es posterior a la operación, sus valores se retiran del resumen. Si es anterior, se identifica como referencia fechada, sin acreditar stock actual, pedidos pendientes o necesidad de compra. Las reservas ausentes siguen siendo desconocidas.

## Entrada parcial y requisitos pendientes

El resultado mantiene `operation_contract_valid=true`, `preparation_status=PARTIAL_INPUT`, `evaluation_status=NOT_EXECUTED`, `PENDING`, `FORBIDDEN`, `decision_authority=false`. Conserva la naturaleza REAL/SYNTHETIC del expediente sin cambiar etiquetas.

Quedan explícitamente sin construir (`null`) DecisionContext, Evidence, FinanceBasicInput y DecisionInputPackage. Para completarlos se necesita vinculación de versiones/snapshot, evidencias/procedencia aceptadas, tesorería y cuotas/IVA/costes de la operación, resolución de parámetros desde el Centro, contexto de stock/necesidad y el proceso de admisión/ejecución aplicable. No se proporcionan valores por defecto para ocultar esos requisitos. Los avisos de la comprobación guardada siguen identificados por recuento y hash.

Puede descargarse el resultado mediante **Descargar preparación JSON**. Es una preparación parcial con identidad SHA-256 reproducible, no un DIP deserializable ni un resultado QTG/Decisor. La consulta no persiste preparaciones, propuestas o decisiones en SQLite: el JSON se guarda donde indique el navegador. La versión documental ya guardada permanece en SQLite.

Editar campos, cambiar versión o contexto invalida el resultado y descarta respuestas pendientes. La empresa activa en Propuestas no cambia.

## API local y validación

- `POST /api/reception/purchase/options`: `dossier_id`, catálogos coherentes y fuentes de esa versión.
- `POST /api/reception/purchase/prepare`: `dossier_id` y `operation` con los ocho campos explícitos: reference, article_id, supplier_id, unit, quantity, unit_price, currency, operation_date.

Ambos endpoints exigen Host local y token de sesión. Se rechazan campos adicionales en operation, incluidas supuestas evidencias o autoridad suministradas desde el cliente.

Ocho pruebas específicas verifican contrato, coherencia, temporalidad, ausencia de valores futuros, contradicciones, precisión/moneda, conservación de material real, ausencia de escrituras e identidad reproducible. La aceptación HTTP integrada incluye la nueva preparación y mantiene cero propuestas/datasets activos. La prueba de pantalla con jsdom verifica formulario, referencias, JSON, pendientes e invalidación.

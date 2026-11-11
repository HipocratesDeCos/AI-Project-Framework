# Demostración completa de compra · v0.1

## Propósito

Un conjunto ficticio completo permite comprobar el recorrido de compra sin modificar el expediente del usuario. «Completo para simular» no equivale a documentos reales contrastados ni a una justificación autorizada de compra. La entrada utiliza `CompanyDataStore.import_dataset`, activa parámetros mediante sus adaptadores y guarda propuestas mediante `PurchaseDesk.save`; no utiliza fixtures de tests ni cambia los contratos del núcleo.

El origen conserva un soporte JSON con todas las cifras ficticias, el puente entre inventario al corte y stock libre al pedido y los supuestos de planificación. La generación usa una base temporal y publica solo al finalizar en un destino nuevo; rechaza sobrescribir una base existente.

## Datos coherentes del caso

- Empresa y proveedor ficticios de jardinería; artículo JAR-DEMO-001, unidad Unidad.
- Corte: 30/09/2026. Stock físico 100; reservado 10; libre 90.
- Pedido: 04/11/2026. Stock libre 60: 30 unidades adicionales consumidas desde el corte, reservas sin cambio.
- Consumo futuro: 5 unidades/día adicionales a las reservas ya descontadas.
- Recepción de esta compra: 7 días desde pedido, 11/11/2026.
- Otra entrada pendiente: 50 unidades el 18/11/2026; lista completa del período ficticio.
- Cobertura objetivo: 30 días desde recepción. Seguridad: 20. Múltiplo: 10.
- Cantidad calculada para el objetivo: 100. No hay falta antes de recepción.
- Precio histórico neto: 12,50 EUR, IVA 21 %, descuento 0 % documentado en soporte ficticio. Precio de la propuesta base: 14,80 EUR.
- Portes a cargo del proveedor. No hay pagos adicionales de portes.
- Tesorería inicial: 15.000 EUR. Reserva: 3.000 EUR. Horizonte: 90 días desde corte, hasta 29/12/2026.
- Pago ya previsto: 6.000 EUR el 20/11. Cobro ya previsto: 5.000 EUR el 25/11. Ninguno se presenta como acreditado.

## Cinco propuestas guardadas

Cada caso se evalúa por separado contra la misma previsión del libro: las cinco propuestas no se suman entre sí.

| Referencia | Cantidad | Condición | Total EUR | Mínimo de caja EUR | Reserva prevista |
|---|---:|---|---:|---:|---|
| DEMO-BASE | 500 | 14,80 EUR, pago 15/11 | 8.954,00 | 46,00 | No respetada |
| DEMO-CANTIDAD | 100 | 14,80 EUR, pago 15/11 | 1.790,80 | 7.209,20 | Respetada |
| DEMO-COMBINADA | 100 | 12,50 EUR, pago 15/11 | 1.512,50 | 7.487,50 | Respetada |
| DEMO-APLAZADA | 500 | 14,80 EUR, pago 25/11 | 8.954,00 | 5.046,00 | Respetada |
| DEMO-CUOTAS | 500 | 4.477 EUR el 15/11 y 4.477 EUR el 30/11 | 8.954,00 | 4.523,00 | Respetada |

Cambiar cantidad afecta a cobertura y dinero inmovilizado; no es equivalente a mejorar el precio a igual volumen. La mayor cantidad supera el objetivo hipotético. Los aplazamientos y cuotas son propuestas ficticias, no aceptación del proveedor.

## Acceso local (PowerShell)

En el repositorio, después de actualizar `feat/purchase-workspace-redesign`:

```powershell
python -m eios.company_purchase_demo --db .\Data\eios_demo_completa_01.sqlite3
python -m eios.company_app --db .\Data\eios_demo_completa_01.sqlite3 --port 8766
```

Abrir http://localhost:8766, Propuestas de compra, Propuestas guardadas. Pulsar Revisar en DEMO-BASE para ver síntesis, alternativas y fuentes; comparar después DEMO-CANTIDAD, DEMO-COMBINADA, DEMO-APLAZADA y DEMO-CUOTAS. El informe imprimible conserva los resultados. Para reiniciar, ejecutar solo el segundo comando. Si la base ya existe, el generador informa y no la modifica; elegir otro nombre permite una nueva demostración.

## Corrección de mensajes

`quantity_review` mantiene sus carencias documentales y añade `simulation_readiness` tras validar el escenario de stock. Si los supuestos completos corresponden a artículo, unidad, pedido y versión, muestra cinco grupos cubiertos para simulación. Las carencias anteriores quedan bajo «Para pasar de hipótesis a datos contrastados», sin convertirse en documentos verificados ni desaparecer por ocultación. Sin hipótesis completa sigue mostrando los datos faltantes. Cambiar contexto invalida la captura, como antes.

## Validación

Verificación de los cinco totales y saldos, objetivo 100, procedencia sintética, lista documental conservada, alternativa combinada y rechazo de sobrescritura. Recorrido Chromium de la base generada: acceso a las cinco propuestas, lista de simulación completa, distinción documental, combinación, informe y resultado de cuotas.

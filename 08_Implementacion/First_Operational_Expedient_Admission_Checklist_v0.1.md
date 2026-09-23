# EIOS — First Operational Expedited Admission Checklist v0.1

**Baseline:** `main @ 073d6bf774fa03266ca22b7bb20f5790c31be353`  
**Fecha:** 23/09/2026  
**Estado:** CHECKLIST OPERATIVO — DERIVADO DE CONTRATOS VIGENTES

## 1. Objetivo

Preparar el primer expediente real `PROJECTION_ONLY / OPERATIONAL` sin ensayo-error y sin rebajar las salvaguardas de provenance.

Este checklist no concede autoridad, no autentica documentos y no garantiza un resultado QTG favorable.

## 2. Bloque A — Identidad de la operación

Aportar:

- decisión;
- escenario;
- artículo;
- proveedor;
- cantidad;
- precio unitario;
- moneda;
- fecha de operación;
- empresa;
- rules_version;
- parameters_version;
- data_snapshot_id;
- fecha efectiva de parámetros.

Resultado esperado: `PurchaseOperation + DecisionContext + FinanceDecisionInputPackage` coherentes.

## 3. Bloque B — Datos financieros

Aportar:

- snapshot financiero;
- fecha económica;
- moneda;
- tesorería disponible presentada;
- cobros relevantes;
- pagos relevantes;
- flujos incompletos o conflictivos también;
- configuración P-FIN-001;
- P-FIN-002 cuando exista mínimo de tesorería.

No omitir un flujo porque sea incómodo o incierto.

## 4. Bloque C — Pedido, confirmación y cuotas

Conservar bytes reales de los documentos que sustenten:

- operación;
- pedido;
- versión del pedido;
- confirmación;
- calendario de pagos.

Para cada cuota:

- installment_ref;
- secuencia;
- importe;
- moneda;
- vencimiento;
- flow_id PAYMENT asociado;
- documento/página/sección.

No dividir el total para inventar cuotas.

## 5. Bloque D — Criterios QTG

Aportar exactamente las seis funciones autorizadas del manifiesto v0.2, con contenido preservado y SHA-256 coincidente:

1. HORIZON_FLOW_INVENTORY_COMPLETENESS
2. PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT
3. DETERMINE_PROJECTION_RELIABILITY
4. OUT_OF_HORIZON_CONFLICT_PRESERVATION
5. INITIAL_TREASURY_SUFFICIENCY
6. ECONOMIC_FLOW_UNIQUENESS

No sirven solo nombres, enlaces o hashes sin contenido.

## 6. Bloque E — Tesorería

Aportar soporte documental real que permita localizar:

- empresa;
- moneda;
- fecha económica;
- importe utilizable;
- restricciones;
- suficiencia de fuentes.

También:

- record_ref;
- declaration;
- observaciones;
- mandato de revisión;
- soporte de reconocimiento de canal;
- soporte de contraste;
- reviewer_ref;
- verifier_ref;
- fecha con zona;
- revisión personal de las seis condiciones.

`PRESENTED_OPERATIONAL` no autentica el soporte: solo declara su naturaleza.

## 7. Bloque F — Inventario de flujos

Aportar:

- perímetros examinados;
- fuentes por perímetro;
- documentos de inventario;
- cobertura declarada;
- limitaciones;
- candidatos encontrados;
- todos los flujos capturados;
- posibles flujos no capturados;
- clasificación de horizonte;
- soporte de importe/moneda/vencimiento/pertenencia;
- economic_identity_ref cuando exista;
- assessment de duplicación;
- mandato;
- revisión personal de las nueve condiciones;
- hallazgo individual para cada cuota dentro de PURCHASE_PAYMENT_COHERENCE.

No eliminar candidatos, conflictos o duplicidades para obtener un resultado favorable.

## 8. Naturalezas obligatorias

Para entrar legítimamente en QTG OPERATIONAL deben ser operacionales, cuando estén presentes:

- payment_capture;
- required_calendar;
- treasury_support;
- treasury_additional_material;
- treasury_mandate;
- flow_inventory;
- flow_mandate.

No se permite reutilizar material `SYNTHETIC` cambiando la etiqueta.

## 9. Qué comprobará EIOS automáticamente

El preflight comprobará:

- perfil PROJECTION_ONLY;
- envelope construido por los builders cerrados;
- material natures;
- ausencia de material sintético;
- fingerprints y pertenencia ya validados por el envelope;
- pendientes de tesorería;
- pendientes de inventario;
- flujos capturados sin assessment;
- candidatos no emparejados;
- cuotas requeridas no revisadas.

Si la estructura es legítimamente operacional, podrá ejecutar:

```text
produce_projection_quality(OPERATIONAL)
→ ProjectionQualityReceipt
→ consume_projection_quality(OPERATIONAL)
```

## 10. Qué NO comprobará automáticamente

El preflight no certifica:

- autenticidad del documento;
- identidad de la persona;
- mandato real;
- reconocimiento del canal;
- verdad económica;
- completitud empresarial externa;
- ausencia real de otros flujos;
- suficiencia de una revisión humana;
- corrección de la decisión posterior.

## 11. Resultado del preflight

Estados técnicos:

- `STRUCTURALLY_ADMISSIBLE`
- `REJECTED_SYNTHETIC_MATERIAL`
- `REJECTED_NON_OPERATIONAL_NATURE`

`STRUCTURALLY_ADMISSIBLE ≠ APTO`.

El QTG operacional determina después el resultado funcional.

## 12. Orden del primer piloto real

```text
1. Recopilar expediente
2. Construir cadena documental
3. Construir ProjectionMaterialEnvelope
4. Ejecutar preflight
5. Ejecutar QTG OPERATIONAL
6. Consumir receipt OPERATIONAL
7. Materializar ProjectionQualityO1Binding
8. Ejecutar O1 por fachada causal
9. Registrar decisión humana
10. Ejecutar Shadow Mode
11. Auditar el piloto
```

## 13. Regla de stop

Si falta material real necesario, se conserva como pendiente.

No se sustituye por:

- mock;
- inferencia favorable;
- documento redactado para pruebas;
- autoridad inventada;
- relabeling sintético.

# EIOS — PROJECTION_ONLY Operational Material Admission Contract v0.1

**Estado:** CERRADO — EXPEDIENTE OPERACIONAL PENDIENTE

**Baseline:** `main @ 27d09c80565f97dbfba32f7e1a720fa9ce15a32c`

**Ámbito:** condiciones documentales y estructurales para admitir el primer caso `PROJECTION_ONLY / OPERATIONAL` sin inventar fuentes, autoridades o resultados.

## 1. DISEÑAR

### 1.1 Propósito

Definir el expediente mínimo que deberá presentarse para construir legítimamente:

```text
FinanceDecisionInputPackage
→ DocumentaryPaymentCapture + RequiredInstallmentCalendar
→ FinanceQualityPreparation
→ cadena de tesorería
→ cadena de inventario de flujos
→ ProjectionMaterialEnvelope
→ ProjectionQualityReceipt(OPERATIONAL)
→ ProjectionQualityConsumption(OPERATIONAL)
```

Este contrato no solicita todavía datos concretos, no autentica fuentes externas y no eleva una etiqueta a prueba. Su función es impedir que un mock, fixture o documento ficticio sea presentado como material operacional.

### 1.2 Significado de caso operacional positivo

“Positivo” significa **admisible y recomputable como expediente operacional**. No significa `APTO`.

Un expediente válido puede producir `APTO`, `APTO_CON_ADVERTENCIAS` o `NO_APTO`. El resultado debe derivarse del material; nunca será requisito previo ni dato suministrado.

## 2. INVENTARIO DE ADMISIÓN

### 2.1 Identidad y captura financiera

Se deberá presentar:

- `PurchaseOperation` real del caso, con decisión, escenario, artículo, proveedor, cantidad, precio, moneda y fecha;
- `DecisionContext` completo y coherente: decisión, escenario, versiones de reglas/parámetros y snapshot;
- evidencia seleccionada con referencias y estados no promovidos;
- `FinanceBasicInput` del mismo contexto y snapshot;
- snapshot financiero con empresa, fecha económica, moneda y tesorería disponible;
- todos los cobros y pagos potencialmente relevantes, incluidos incompletos, conflictivos o finalmente excluidos;
- horizonte resuelto desde `P-FIN-001` y, cuando proceda, mínimo de tesorería desde `P-FIN-002`;
- resoluciones del Centro válidas para empresa, versión y fecha efectiva;
- identidad de empresa y fecha efectiva coincidente con el snapshot.

La captura no certifica por sí sola completitud ni autenticidad; preserva exactamente lo presentado.

### 2.2 Pedido, confirmación, pagos y cuotas

El expediente deberá contener bytes reales preservables de los documentos que sustenten:

- operación;
- pedido y versión;
- confirmación;
- calendario de pagos;
- asociaciones entre cada cuota declarada y cada flujo `PAYMENT` capturado.

Cada localizador deberá señalar documento, página y sección existentes. El calendario requerido deberá declarar:

- referencia y autoridad de la declaración;
- naturaleza `PRESENTED_OPERATIONAL`;
- total, moneda y todas las cuotas;
- para cada cuota: identidad, secuencia, importe, moneda, vencimiento y localizadores;
- coherencia exacta con operación, pedido, versión y confirmación de la captura.

No se admite deducir cuotas por simple división del total, copiar fechas estimadas ni omitir pagos adicionales no asociados.

### 2.3 Criterios autorizados

Deberán aportarse los contenidos exactos de las seis funciones del manifiesto v0.2:

1. `HORIZON_FLOW_INVENTORY_COMPLETENESS`;
2. `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT`;
3. `DETERMINATE_PROJECTION_RELIABILITY`;
4. `OUT_OF_HORIZON_CONFLICT_PRESERVATION`;
5. `INITIAL_TREASURY_SUFFICIENCY`;
6. `ECONOMIC_FLOW_UNIQUENESS`.

La admisión verificará referencia, versión y SHA-256 contra el manifiesto autorizado. No se admite sustituir contenido por nombre, resumen, enlace no preservado o hash sin bytes.

La enumeración efectiva de `REQUIRED_FUNCTIONS` del código prevalece como control mecánico; este contrato no modifica el manifiesto.

### 2.4 Soporte documental de tesorería

Se requieren documentos reales preservados que permitan localizar y contrastar:

- correspondencia de la fuente;
- corte económico;
- soporte del importe;
- disponibilidad;
- restricciones;
- suficiencia de fuentes.

La declaración deberá identificar empresa documental, moneda, fecha económica, importe disponible y localizadores. Cualquier revisión o presentación deberá conservar revisor y fecha consciente de zona horaria cuando el contrato físico los exija.

Los documentos adicionales son opcionales. Si existen, deberán declararse `PRESENTED_OPERATIONAL`, conservar bytes y mantener referencias no colisionantes. Si no existen, su ausencia no puede ocultar una carencia necesaria: las declaraciones deberán conservar `NOT_ESTABLISHED`, insuficiencia o pendiente según corresponda.

### 2.5 Evaluación contextual de tesorería

Para cada una de las seis condiciones se deberá declarar, sin convertir texto libre en programa:

- aplicabilidad y razón;
- necesidad para una proyección determinada y razón;
- impacto;
- suficiencia del soporte y razón;
- criterio exacto utilizado;
- observaciones y localizadores que sustentan la declaración.

`DECLARED_SUFFICIENT` requiere soporte localizado. La declaración sigue siendo presentada; no equivale a verdad ni sustituye la revisión.

### 2.6 Mandato de tesorería

La comprobación manual deberá preservar separadamente:

- documento de mandato;
- soporte de reconocimiento del canal;
- soporte de contraste;
- referencias de mandato, canal, revisor, verificador y revisión objetivo;
- fecha de verificación con zona horaria;
- base de reconocimiento;
- naturaleza `PRESENTED_OPERATIONAL`;
- observaciones de todas las condiciones exigidas;
- propósito exacto `TREASURY_REVIEW_FOR_DOCUMENTARY_CUTOFF_PILOT`.

Una referencia textual a una persona o canal no demuestra autorización. La admisión conserva lo presentado; la autoridad externa deberá estar previamente reconocida o independientemente soportada según el contrato cerrado.

### 2.7 Revisión personal de tesorería

La revisión deberá:

- corresponder al revisor y referencia objetivo del mandato;
- cubrir las seis condiciones o conservar explícitamente las pendientes;
- mantener `CONFIRMED_BY_REVIEW`, `NOT_CONFIRMED` o `CONFLICT_REPORTED` sin promoción;
- localizar todo hallazgo confirmado/no confirmado en documentos de tesorería preservados;
- conservar fecha, referencia de revisión y, si existe, revisión anterior.

La falta de cobertura necesaria puede producir `NO_APTO`; no invalida por sí sola la naturaleza operacional si el expediente preserva honestamente la incompletitud.

### 2.8 Inventario operacional de flujos

Se deberán presentar:

- perímetros explícitos para todas las fuentes relevantes del horizonte;
- empresa, fecha base, fin de horizonte y moneda coherentes con la preparación;
- documentos reales de inventario;
- declaración de cobertura y limitaciones por perímetro;
- candidatos encontrados, incluidos no capturados;
- evaluación de todos los flujos capturados;
- referencias de identidad económica para detectar duplicaciones;
- localizadores en documentos de inventario o pago;
- presenter y fecha cuando correspondan;
- naturaleza `PRESENTED_OPERATIONAL`.

Para cada flujo deberán preservarse, sin rellenar por conveniencia:

- soporte de importe;
- moneda;
- vencimiento;
- pertenencia económica;
- clasificación respecto del horizonte;
- unicidad/posible duplicación;
- criterio y razón.

Un flujo solo podrá excluirse de atributos y unicidad por `AFTER_HORIZON` demostrado. Fecha desconocida, `NON_FUTURE`, conflicto o ausencia no autorizan exclusión automática.

### 2.9 Mandato y revisión del inventario

El mandato de flujos deberá aportar los tres grupos documentales —mandato, reconocimiento del canal y contraste—, identidades, fecha, naturaleza operacional y propósito exacto `FLOW_INVENTORY_REVIEW_FOR_PROJECTION_ONLY`.

La revisión personal deberá cubrir el inventario completo de condiciones y conservar:

- perímetros, candidatos y flujos afectados;
- localizadores válidos;
- conflictos y limitaciones;
- hallazgo individual para cada cuota requerida dentro de `PURCHASE_PAYMENT_COHERENCE`;
- coherencia del resultado agregado con los resultados de todas las cuotas.

No se permite declarar completitud ignorando candidatos no capturados, flujos pendientes o duplicaciones posibles.

## 3. AUDITAR

### A1 — etiqueta no autenticante

Los builders aceptan `PRESENTED_OPERATIONAL`, pero esa etiqueta solo separa naturaleza presentada de fixture sintética. No autentica contenido, emisor, mandato, canal, revisor ni verificador.

### A2 — bytes y localizadores

Las cadenas conservan bytes y SHA-256, pero una huella solo prueba identidad del contenido recibido. Los localizadores deben referirse a documentos preservados; no demuestran por sí solos que la fuente sea externa o auténtica.

### A3 — declaraciones no son hechos

Tesorería, cobertura, pertenencia y unicidad contienen declaraciones estructuradas. La revisión y el contraste no deben elevarlas automáticamente a hechos ni eliminar conflictos.

### A4 — completitud no equivale a resultado favorable

Un expediente operacional puede ser completo como trazabilidad y concluir que faltan datos necesarios. La admisión no exige `APTO`.

### A5 — horizonte derivado

El horizonte no puede suministrarse como número libre si contradice `P-FIN-001`. Snapshot, empresa, fecha efectiva y versión de parámetros deben permanecer vinculados.

### A6 — pagos adicionales

La coincidencia exacta de las cuotas requeridas no demuestra que no existan otros pagos o cobros relevantes. El inventario ampliado conserva esa frontera.

### A7 — revisión sin mandato

Una revisión personal no es autorizada solo por contener `reviewer_ref`. Debe corresponder al mandato verificado y a su revisión objetivo.

### A8 — caso real no disponible

El repositorio no contiene actualmente un expediente que satisfaga estas condiciones con fuentes operacionales autorizadas. No se puede materializar el caso sustituyéndolo por los contenidos sintéticos de tests.

## 4. DEPURAR

Quedan prohibidos como vías de desbloqueo:

- cambiar `case_kind` o `mandate_kind` de fixtures existentes;
- redactar pedidos, confirmaciones, extractos, mandatos o revisiones ficticios;
- inventar revisor, verificador, autoridad o canal;
- reutilizar hashes sin contenido preservado;
- completar huecos con supuestos favorables;
- eliminar candidatos, flujos o conflictos para obtener `APTO`;
- asumir que `PRESENTED_OPERATIONAL` significa “verificado”;
- ejecutar Finance Basic o el binding causal antes de cerrar la calidad del expediente.

El expediente se admitirá tal como resulte: completo, incompleto, conflictivo o no evaluable. QTG determinará el estado; la admisión solo protege naturaleza, pertenencia y trazabilidad.

## 5. AUDITAR 2

La segunda revisión confirma:

- las siete naturalezas recomputadas por el producer quedan cubiertas: captura, calendario, soporte de tesorería, material adicional opcional, mandato de tesorería, inventario y mandato de flujos;
- las revisiones personales quedan ligadas a sus mandatos y objetivos aunque no formen parte del vector de naturalezas;
- cuotas y flujos conservan soporte individual;
- los flujos fuera de horizonte no bloquean atributos solo cuando su exclusión está demostrada;
- los conflictos permanecen visibles;
- no se exige un resultado QTG previo;
- no se inventa ninguna fuente ni arquitectura de autenticación externa;
- el contrato desbloquea la preparación del expediente, no la integración Vertical.

### Corrección de precisión

`treasury_additional_material` puede ser `null` cuando no se presentan documentos adicionales. Esto no equivale a material sintético ni demuestra suficiencia. Cuando existan documentos adicionales, su naturaleza debe ser explícitamente `PRESENTED_OPERATIONAL`.

## 6. CERRAR

Se aprueba este contrato como checklist vinculante para el primer expediente operacional `PROJECTION_ONLY`.

La implementación del binding causal seguirá bloqueada hasta que el titular presente o autorice material concreto que pueda atravesar este contrato. Recibir documentos no implicará aceptarlos: deberán auditarse contra cada punto y las fronteras cerradas.

## 7. MATERIALIZAR → CI

Esta unidad materializa solo el contrato documental. No crea fixtures, datos, autorizaciones, resultados QTG ni rutas operacionales.

La modificación local ajena de `08_Implementacion/Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` queda excluida.

El cierre integrado exige suite completa, PR de un único archivo, CI exact-head, merge protegido por SHA y CI post-merge. CI verde no acredita la existencia del expediente.

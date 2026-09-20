# EIOS — Post-BL-007 Gate Intake Contract v0.1

**Baseline:** `main @ c95cdfcc9c6b288a39ea260ab1c59bca3d37deb1`

**Estado:** DISEÑADO → AUDITADO → DEPURADO → AUDIT 2 SUPERADA — DOCUMENTAL ONLY

## 1. Propósito

Definir qué material mínimo debe existir para poder reabrir de forma legítima un frente funcional actualmente bloqueado.

Este contrato no resuelve ningún gate. Solo convierte bloqueos abstractos en condiciones de entrada verificables.

No autoriza:

- código funcional nuevo;
- cambios de reglas;
- nuevos parámetros;
- reinterpretaciones de semántica;
- promoción de datos sintéticos a operacionales;
- cierre de un frente por mera presencia de un documento;
- uso de una conversación como sustituto de una fuente autorizada.

## 2. Regla general de admisión

Un frente bloqueado solo podrá pasar de `BLOCKED` a `READY_FOR_DESIGN` cuando exista material que permita contestar afirmativamente, con evidencia verificable, estas cuatro preguntas:

1. **¿Qué autoridad define el significado?**
2. **¿Qué productor físico aporta el dato/evidencia?**
3. **¿Qué identidad/provenance conecta ese material con la operación evaluada?**
4. **¿Qué comportamiento fail-closed aplica cuando falta o contradice la evidencia?**

Si una de las cuatro respuestas depende de inferencia, default, similitud nominal o conveniencia, el gate permanece cerrado.

## 3. HIS-001 — referencia demasiado antigua

### Estado actual

- regla existente: `R-HIS-001`;
- parámetro efectivo demostrado: `P-DAT-002`;
- Price C1 conserva `PriceReference.operation_date`;
- Price C1 consume `TemporalStatus`, pero no lo produce.

### Intake mínimo requerido

Debe existir una fuente autorizada que defina:

- fecha base exacta contra la que se calcula antigüedad;
- unidad temporal y semántica exacta de `P-DAT-002`;
- tratamiento de fechas iguales al límite;
- tratamiento de meses/semanas naturales vs duración fija;
- tratamiento de fecha ausente;
- tratamiento de fecha futura;
- tratamiento de contradicciones entre fuentes;
- identidad de la referencia histórica evaluada;
- productor físico que emite la observación temporal o material equivalente;
- trazabilidad hacia regla/parámetro/fuente.

### Gate de apertura

`HIS001-G01` — semántica temporal cerrada.  
`HIS001-G02` — productor EVIDENCE/DATA identificado.  
`HIS001-G03` — binding provenance-safe hacia la referencia concreta.  
`HIS001-G04` — política fail-closed documentada.

Solo con G01–G04 podrá abrirse diseño técnico de `R-HIS-001`.

## 4. DAT-001 — datos actualizados

### Estado actual

- regla existente: `R-DAT-001`;
- relación `P-DAT-001 → R-DAT-001` documentada;
- no existe timestamp canónico general ni productor provenance-safe de frescura.

### Intake mínimo requerido

Debe definirse:

- qué objeto o dataset está sujeto a frescura;
- cuál es su timestamp canónico;
- quién lo produce;
- cómo se relaciona con `DecisionContext.data_snapshot_id`;
- si la frescura se evalúa por dataset, evidencia, campo o fuente;
- zona horaria/calendario aplicable;
- semántica exacta de `P-DAT-001`;
- tratamiento de timestamps ausentes, futuros o contradictorios;
- evidencia y traza de origen.

### Gate de apertura

`DAT001-G01` — ámbito de frescura cerrado.  
`DAT001-G02` — timestamp canónico identificado.  
`DAT001-G03` — productor provenance-safe identificado.  
`DAT001-G04` — relación con snapshot/decisión demostrada.  
`DAT001-G05` — fail-closed documentado.

## 5. PAG-001 — plazo ofrecido desfavorable

### Estado actual

- carrier factual genérico existente;
- condiciones de pago/cuotas preservables;
- no existe escalar canónico autorizado `offered_payment_term_days`;
- multicuota y `P-PAG-003` siguen abiertos.

### Intake mínimo requerido

Debe definirse:

- evento base desde el que se cuentan días;
- significado canónico de “plazo ofrecido”;
- cómo se representa una operación multicuota;
- si existe agregación autorizada y cuál;
- tratamiento de cuotas parciales;
- tratamiento de fechas ausentes/contradictorias;
- transformación exacta de `P-PAG-003`;
- relación exacta entre facts existentes y `R-PAG-001`;
- provenance de proveedor/operación/documento.

### Gate de apertura

`PAG001-G01` — semántica canónica de plazo.  
`PAG001-G02` — semántica multicuota.  
`PAG001-G03` — transformación `P-PAG-003`.  
`PAG001-G04` — dependency binding EVIDENCE/DATA.  
`PAG001-G05` — productor provenance-safe.

`P-PAG-005` no queda resuelto por estos gates y deberá permanecer fuera de cualquier cálculo económico hasta disponer de autoridad propia.

## 6. QTG OPERATIONAL → O1

### Estado actual

La cadena sintética `PROJECTION_ONLY / SYNTHETIC_TEST → TEST_ONLY` está cerrada. La ruta operacional permanece bloqueada.

### Intake mínimo requerido

Debe existir un expediente operacional concreto que sea:

- real;
- explícitamente autorizado para evaluación;
- trazable a documentos/fuentes originales;
- identificable de forma estable;
- suficientemente completo para el contrato de admisión aplicable;
- no derivado de fixtures sintéticas;
- no promovido mediante cambio de etiquetas.

Además debe quedar documentado:

- alcance de uso;
- clasificación;
- propietario/autorizador;
- límites de tratamiento;
- si los datos pueden persistirse o solo evaluarse en memoria;
- reglas de redacción/anonimización si aplican.

### Gate de apertura

`QTG-O1-G01` — expediente real aportado.  
`QTG-O1-G02` — autorización explícita de uso.  
`QTG-O1-G03` — identidad y provenance verificables.  
`QTG-O1-G04` — completitud/admisión validable.

## 7. MGE / Profitability

### Estado actual

PR draft #73 contiene metodología auditada, pero `MGE-AUTH v0.1` permanece **NO AUTORIZADA**.

### Intake mínimo requerido

Se requiere una aprobación humana explícita que identifique:

- documento/version de política aprobada;
- ámbito empresarial;
- fecha de vigencia;
- responsable/autorizador;
- si la aprobación es metodológica, parametrizable o ejecutable;
- límites y excepciones.

Una instrucción genérica como “continúa”, “prosigue” o “implementa lo pendiente” no satisface este gate.

### Gate de apertura

`MGE-G01` — aprobación explícita de la política.  
`MGE-G02` — versión y alcance identificados.  
`MGE-G03` — parámetros/política ejecutable sin contradicciones pendientes.

## 8. Stage 2 / Viability Frontier

### Estado actual

El core VF permanece cerrado. La publicación de Stage 2 sigue en cuarentena por ausencia de productor provenance-safe de consecuencias H/K/U/S.

### Intake mínimo requerido

Debe existir una fuente físicamente identificada que produzca, con provenance demostrable:

- consecuencias H/K/U/S;
- identidad de operación/escenario;
- versión/metodología;
- evidencia/trazas de soporte;
- semántica de ausencia/indeterminación;
- garantías de no reutilización de resultados desprendidos.

### Gate de apertura

`S2VF-G01` — productor físico autorizado.  
`S2VF-G02` — contrato de identity/provenance.  
`S2VF-G03` — fail-closed para ausencia/contradicción.

## 9. Registro de intake

Toda futura entrada que pretenda abrir un gate debe registrar, como mínimo:

```text
gate_id
source_document
source_version
source_authority
scope
effective_date
producer
identity_binding
provenance_evidence
fail_closed_behavior
known_limitations
review_status
```

La mera presencia de estos campos no prueba validez; deben estar sustentados por fuentes reales y auditables.

## 10. No-alcance

Este contrato no:

- selecciona qué gate debe resolverse primero;
- asigna prioridad empresarial;
- define políticas pendientes;
- convierte un gate en aprobado;
- autoriza nuevos componentes;
- cambia el estado del Vertical MVP;
- sustituye auditorías especializadas.

## 11. Dictamen

**POST-BL-007 GATE INTAKE CONTRACT: CERRADO DOCUMENTALMENTE.**

El proyecto dispone ahora de un criterio explícito para reconocer cuándo un frente bloqueado puede pasar legítimamente a diseño, sin depender de memoria conversacional ni reinterpretaciones.

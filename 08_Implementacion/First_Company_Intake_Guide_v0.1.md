# EIOS — Guía de entrada para la primera empresa · v0.1

**Estado:** guía de preparación. No registra una empresa, no admite un expediente y no habilita una ejecución operacional.

## 1. Qué se prepara

Una empresa que decida probar EIOS presentará una operación de compra concreta y el material que permita examinarla. El primer perfil previsto es `PROJECTION_ONLY`. El sistema utiliza referencias a documentos y objetos de dominio; una referencia sirve para localizar material, **no demuestra que sea auténtico, suficiente o autorizado**.

El manifiesto canónico está en `eios/core/operational_intake.py` (`CANONICAL_INTAKE_ITEMS`). Esta tabla agrupa sus **24 claves exactas** para facilitar la recogida. Los nombres entre código son identificadores del sistema, no títulos que la empresa deba imponer a sus documentos.

| Bloque para la empresa | Claves del manifiesto | Qué conviene localizar |
|---|---|---|
| Operación y contexto | `purchase_operation`, `decision_context` | Compra examinada y contexto al que corresponde. |
| Base financiera | `finance_snapshot`, `finance_cash_flows`, `parameter_p_fin_001` | Situación financiera, flujos y criterio aplicable. |
| Soporte de compra | `operation_support_document`, `order_document`, `order_version`, `confirmation_document`, `required_installment_calendar` | Pedido, versión, confirmación, obligaciones y vencimientos completos. |
| Criterio de proyección | `projection_criteria_content` | Contenido del criterio utilizado para interpretar la proyección. |
| Tesorería y revisión | `treasury_support_documents`, `treasury_declaration`, `treasury_contextual_assessment`, `treasury_mandate_documents`, `treasury_personal_review` | Soportes del saldo y su alcance, declaración, valoración, mandato y acto de revisión identificable. |
| Inventario de flujos y revisión | `flow_inventory_perimeters`, `flow_inventory_documents`, `flow_inventory_candidates`, `captured_flow_assessments`, `flow_inventory_mandate_documents`, `flow_inventory_personal_review` | Perímetro, fuentes, flujos candidatos, valoraciones y soporte de la revisión competente. |
| Según el caso | `parameter_p_fin_002`, `treasury_additional_material` | Material condicional: su ausencia no bloquea el manifiesto por sí sola; el contrato de dominio determina si hace falta. |

## 2. Orden de trabajo

1. **Elegir una compra y un corte documental.** Reunir el material presentado por la empresa, conservando origen, versiones y discrepancias. No reutilizar los expedientes ficticios 001/002 como pruebas empresariales.
2. **Inventariar referencias.** Asociar cada pieza a la clave canónica pertinente. El manifiesto vacío (`empty_operational_expedient_intake_manifest`) muestra lo que falta. `REQUIRED_SET_COMPLETE` solo confirma que cada clave obligatoria tiene al menos una referencia no vacía.
3. **Construir y comprobar el expediente.** Los objetos de dominio, el `ProjectionMaterialEnvelope` y el preflight de admisión examinan estructura y pertenencia conforme a sus contratos. Un manifiesto completo no implica `STRUCTURALLY_ADMISSIBLE`.
4. **Examinar los actos humanos exigidos.** Verificar por separado soporte de mandato, alcance, vigencia y revisión efectiva sobre el material correspondiente; registrar faltantes y contradicciones. Un nombre, una firma aislada o una plantilla cumplimentada no acreditan por sí solos facultad o revisión suficiente.
5. **Ejecutar solo si procede.** Un expediente admitido puede pasar al productor y consumidor QTG operacional y al vínculo QTG↔O1 existente, conforme a sus validadores. `APTO` tampoco autoriza una compra ni concede autoridad decisional.

## 3. Cómo leer el estado

| Resultado visible | Lectura correcta |
|---|---|
| `REQUIRED_SET_INCOMPLETE` | Faltan referencias de bloques obligatorios; completar el inventario antes de construir el expediente. |
| `REQUIRED_SET_COMPLETE` | Están referenciados los bloques obligatorios; todavía se deben examinar contenido, pertenencia, admisión y actos humanos. |
| `STRUCTURALLY_ADMISSIBLE` | El preflight acepta la estructura según su contrato; no autentica por sí solo las fuentes. |
| QTG `APTO` | Resultado funcional de calidad para el consumo autorizado; no es una decisión de compra. |

## 4. Preparar la hoja de referencias

Desde la raíz del repositorio, el comando siguiente crea un JSON nuevo con las 24 claves canónicas y listas vacías. No inventa documentos ni admite un expediente:

```powershell
python -m examples.operational_intake_collection --output referencias-empresa.json
```

Tras incorporar únicamente las referencias que realmente se hayan recibido, se puede comprobar qué bloques faltan:

```powershell
python -m examples.operational_intake_collection --check referencias-empresa.json
```

Cada valor es una lista de referencias de texto, por ejemplo `"order_document": ["ruta-o-identificador-del-pedido"]`. El comando de creación no sobrescribe un archivo existente. La comprobación no lee el contenido de los documentos y su resultado no sustituye la admisión ni una revisión humana.

## 5. Límite actual

Esta guía permite preparar una colaboración futura; **no hay un primer expediente empresarial real aportado** ni un E2E operacional positivo ejecutado. Los paquetes de referencia siguen siendo `SYNTHETIC`, con política `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, efecto `NO_OPERATIONAL_EFFECT` y autoridad decisional `false`.

**Base de lectura:** `08_Implementacion/Operational_Expedient_Intake_Manifest_v0.1.md`, `08_Implementacion/Finance_Pilot_Supervised_Review_Procedure_v0.1.md` y `07_Pruebas/Real_Pilot_Readiness_Reconciliation_2026_09_27.md`. Esta guía explica los contratos vigentes; no los amplía.

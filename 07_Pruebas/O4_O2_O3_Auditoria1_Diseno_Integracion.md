# EIOS — O4 → O2 → O3 · AUDITORÍA 1 DEL DISEÑO DE INTEGRACIÓN

**Estado:** 🔎 AUDITADO — REQUIERE DEPURACIÓN ANTES DE AUDITORÍA 2  
**Diseño auditado:** `O4_O2_O3_Diseno_Integracion_Evaluacion.md`  
**SHA diseño:** `adc0a66c0b3939c46ea236f2392afcbc2a9ad57e`  
**Baseline:** `accbfa6f7e59b5070539d86a6e65f1ba28653e52`

## 1. Resultado

La integración O4 → O2 → O3 está arquitectónicamente justificada y mantiene las autoridades separadas, pero el diseño todavía no define con precisión suficiente el contrato de transporte entre las tres capas.

No se detecta necesidad de introducir una nueva autoridad empresarial. Sí se requieren precisiones antes de Auditoría 2.

## 2. Hallazgos

### H1 — Representación contractual del candidato O4 → O2

**Severidad:** Alta.

El diseño establece que O4 entrega candidatos con cambios canónicos, contexto, padre, política y trazabilidad, pero no define el DTO/estructura exacta que atraviesa la frontera.

Debe quedar explícito que el adaptador transporta únicamente datos ya generados por O4 y no crea una nueva identidad de escenario. O2 debe seguir siendo la autoridad que crea `ScenarioVersion`, `scenario_id` y `fingerprint`.

### H2 — Correspondencia de cardinalidad y errores por candidato

**Severidad:** Alta.

El diseño permite lotes de cero, uno o varios candidatos, pero no fija la semántica del resultado cuando algunos candidatos son aceptados por O2 y otros son rechazados técnicamente.

Debe definirse procesamiento independiente por candidato, preservando correspondencia 1:1 entre cada candidato O4 y su intento de versionado O2. No debe existir reducción silenciosa del lote.

### H3 — Condición exacta de entrada a O3

**Severidad:** Alta.

Debe distinguirse inequívocamente `ScenarioStatus.VALID` de cualquier estado DRAFT/INVALID. Solo `VALID` puede entrar en O3, coherente con el contrato actual de O3.

La integración no debe marcar `EVALUATED` en O2 como paso intermedio: ese estado continúa reservado para una integración futura explícita.

### H4 — Resultados Assessment / Viability Frontier

**Severidad:** Alta.

El diseño afirma que O3 consume resultados ya producidos, pero no define si ambos son obligatorios para todo estado ni cómo se representan ausencias/limitaciones.

La depuración debe conservar el contrato actual: `COMPLETED` requiere Assessment y Viability; resultados parciales/no evaluables deben mantener sus limitaciones sin convertir ausencia en resultado negativo.

### H5 — Trazabilidad sin identidad paralela

**Severidad:** Media.

La cadena candidato → ScenarioVersion → ScenarioEvaluationResult está bien planteada, pero debe especificarse qué referencias se transportan sin crear un nuevo `integration_id`, fingerprint o trace authority.

La integración puede conservar referencias existentes; no debe convertirse en propietario de identidad o trazabilidad.

### H6 — Errores técnicos y estado global del lote

**Severidad:** Media.

Debe definirse que un fallo técnico individual no determina automáticamente el estado de los demás candidatos ni constituye una conclusión empresarial sobre la operación.

La integración debe distinguir resultado por candidato y resumen técnico de lote, sin introducir `best candidate`, ranking o selección implícita.

## 3. Verificaciones superadas

- No se introduce `decision_version`.
- No se introduce autoridad empresarial nueva.
- O4 no ejecuta O2/O3 internamente.
- O2 conserva identidad/versionado de escenario.
- O3 conserva su carácter de consumidor de resultados ya producidos.
- No se autoriza ranking, scoring, selección, recomendación, optimización o negociación.
- No se autoriza persistencia, API ni SQL nuevos.
- La distinción técnico/empresarial queda preservada.

## 4. Depuración obligatoria

Antes de Auditoría 2, el diseño debe incorporar:

1. una representación contractual mínima y explícita del candidato O4;
2. semántica 1:1 de procesamiento y errores por candidato;
3. condición exacta `ScenarioStatus.VALID` para O3;
4. reglas explícitas para Assessment/Viability y estados parciales;
5. trazabilidad mediante referencias existentes, sin identidad paralela;
6. semántica de lote sin ranking, selección ni truncamiento.

**Conclusión:** DISEÑO VÁLIDO EN PRINCIPIO; DEPURACIÓN OBLIGATORIA ANTES DE AUDITORÍA 2. No se autoriza implementación todavía.

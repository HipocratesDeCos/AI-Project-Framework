# EIOS — U1.2 Vertical MVP Read-Only Composition — Audit 1 v0.1

**Baseline:** `main @ 076828839ebe6004a5052ad5e778cb4c1b1dc62a`

**Objeto:** auditar el contrato U1.2 contra U1.1, la integración visual Vertical vigente y las cuarentenas de provenance.

## A1 — Riesgo de reabrir U1.1

El shell U1.1 contiene entrada de operación y contenido estático. Modificarlo directamente mezclaría el cierre histórico U1.1 con una nueva unidad.

**Depuración:** U1.2 se materializa como renderer/superficie independiente. U1.1 permanece sin cambios.

## A2 — Riesgo de saltar Application Boundary

Aceptar `VerticalMVPSupportResult`, modelos de dominio o resultados de capacidad en el renderer permitiría crear una segunda frontera de presentación y podría reintroducir resultados desprendidos.

**Depuración:** la entrada única es el `Mapping` ya producido por `build_vertical_mvp_view_model`.

## A3 — Riesgo de confundir estado técnico con decisión

`COMPLETED`, `FAILED`, `BLOCKED` o el resultado CRC podrían presentarse como aprobación/rechazo empresarial.

**Depuración:** las etiquetas visuales deberán identificar explícitamente estado técnico y soporte CRC. No se usan verbos decisionales.

## A4 — Riesgo de convertir ausencia en resultado favorable

`rules_available=false` o `scenario_support_available=false` podrían aparecer como ausencia de incidencias.

**Depuración:** ausencia se representa como “no disponible / no suministrado”, nunca como éxito.

## A5 — Regla omitida ≠ FALSE

La capa visual ya preserva listas separadas de reglas ejecutadas/omitidas.

**Depuración:** el renderer mantiene esa separación y no sintetiza Assessments.

## A6 — NOT_EVALUABLE

Una presentación simplificada podría convertir `NOT_EVALUABLE` en warning genérico, false o vacío.

**Depuración:** estados/outcomes se muestran literalmente y pueden acompañarse solo de una etiqueta presentacional neutral.

## A7 — Scenario comparison

La comparación descriptiva puede contener diferencias y observaciones, pero la autoridad vigente prohíbe “best scenario”, score o ranking.

**Depuración:** U1.2 solo lista información existente en `scenario_comparison` y no calcula preferencias.

## A8 — QTG en cuarentena

La matriz de regresión vigente prohíbe QTG en la frontera genérica O1/Vertical y resultados QTG desprendidos.

**Depuración:** U1.2 no introduce parámetros, imports ni bloques QTG especializados. Solo renderiza las capacidades que ya existan legítimamente en el view-model Vertical.

## A9 — NI/Ladder provenance

La presencia de invocadores NI/Ladder no demuestra provenance y sus resultados crudos están prohibidos en fronteras públicas.

**Depuración:** el renderer no acepta resultados NI/Ladder directamente ni los interpreta. Solo muestra estado de capacidad ya presente en el payload autorizado.

## A10 — Inyección de contenido

Texto de razones, conflictos, evidence/traces o scenario values puede contener caracteres HTML.

**Depuración:** el renderer debe usar `html.escape` o nodos de texto equivalentes. Ningún valor dinámico se trata como markup.

## A11 — Mutación

Una capa de render no debe alterar arrays ni mappings recibidos.

**Depuración:** ninguna operación in-place; solo lectura/iteración y composición de salida.

## A12 — Duplicación de lógica del view-model

Revalidar o recalcular semántica del dominio en el renderer crearía divergencia.

**Depuración:** solo se valida forma mínima necesaria para fail-closed; no se recalculan estados, comparaciones, reglas o CRC.

## Dictamen

**AUDIT 1: SUPERADA — 0 bloqueadores.**

La unidad es implementable sin datos operacionales y sin nueva autoridad funcional si mantiene estrictamente:

`authorized presentation payload → read-only renderer`.

Siguiente paso: DEPURAR contrato con estas salvaguardas y materializar una implementación pura, sin networking ni motores.


## AUDITAR 2 — implementación materializada

### Delta físico

La rama añade/modifica únicamente:

- `08_Implementacion/U1_2_Vertical_MVP_ReadOnly_Composition_Contract_v0.1.md`;
- este registro de auditoría;
- `eios/frontend/visual/vertical_mvp_renderer.py`;
- export explícito en `eios/frontend/visual/__init__.py`;
- `tests/test_vertical_mvp_readonly_renderer.py`.

No se modifica:

- U1.1 `view_model.py`;
- U1.1 `index.html`;
- `application_boundary.py`;
- O1 / Vertical MVP;
- Rules / CRC;
- Scenario / Twin;
- PRICE / TCO / Finance / QTG;
- NI / Ladder;
- modelos de dominio;
- SQL;
- reglas o parámetros.

### Verificación estática

El renderer:

1. consume solo `Mapping`;
2. no importa ningún módulo `eios.*`;
3. no recibe modelos, invocadores ni callables;
4. no contiene JavaScript;
5. no realiza I/O, red o persistencia;
6. usa `html.escape(..., quote=True)` para valores escalares;
7. serializa estructuras mediante `json.dumps(..., allow_nan=False)` y después las escapa;
8. conserva el orden de listas y registros;
9. distingue explícitamente bloque no suministrado de resultado favorable;
10. etiqueta `execution_status` como estado técnico;
11. etiqueta CRC como soporte y no decisión humana;
12. no calcula score, ranking, recomendación, aprobación ni escenario preferido;
13. no muta el view-model;
14. falla cerrado ante estructura incompleta o contradicción entre availability flags y bloques asociados.

### Cobertura de pruebas materializada

La suite nueva comprueba:

- documento HTML completo y navegable por anclas;
- render literal de `PARTIAL`, `NOT_EVALUABLE` y resultado CRC ya producido;
- ausencia explícita Rules/CRC;
- ausencia explícita Scenario Support;
- separación de reglas ejecutadas/omitidas;
- preservación de orden de capacidades y escenarios;
- escape de `<script>` y markup de imagen/evento;
- determinismo del render;
- no mutación;
- ausencia de superficies decisionales inventadas;
- fail-closed de view-model incompleto/inconsistente;
- ausencia mecánica de imports `eios.*` o motores en el módulo renderer.

### Hallazgo de Audit 2

No se detecta transferencia de autoridad analítica al frontend.

La validación de forma del renderer no recalcula semántica; únicamente exige la estructura que el view-model cerrado ya declara para evitar representación parcial silenciosa.

**AUDITAR 2: SUPERADA — 0 bloqueadores técnicos detectados antes de CI.**

## CERRAR

U1.2 queda **CERRADA TÉCNICAMENTE — CI PENDIENTE**.

La unidad añade una composición visual read-only sobre una frontera de presentación ya autorizada. No habilita ejecución desde navegador ni modifica el cierre U1.1.

## MATERIALIZAR → CI

Materialización completada en la rama `feat/u1-2-vertical-readonly-composition`.

La integración queda condicionada a:

1. CI completa sobre el HEAD exacto;
2. reconciliación de `main`;
3. PR mergeable;
4. merge protegido por SHA;
5. equivalencia del árbol probado con el árbol integrado.

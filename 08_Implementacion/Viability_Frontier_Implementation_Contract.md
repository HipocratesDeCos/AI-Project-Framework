# EIOS — VIABILITY FRONTIER · IMPLEMENTATION CONTRACT

**Versión:** 0.2
**Estado:** CONTRATO DEPURADO — PENDIENTE DE AUDITORÍA 2
**Baseline:** d82cf899ccc0a133e9a6d9a7be3084ca3f5dbc40
**Autoridad documental:** `05_Motor/Viability_Frontier.md` v2.1

## 1. Propósito y autoridad

Materializar técnicamente el contrato documental cerrado sin ampliar su autoridad. El componente no determina por sí mismo qué reglas son aplicables ni qué consecuencias normativas existen.

## 2. Entrada canónica

La entrada técnica estará compuesta por:

- `decision_id` y `scenario_id` del contexto autorizado;
- versiones/reglas/parámetros y `data_snapshot_id` cuando formen parte del contexto disponible;
- colección inmutable de `Assessment` ya producidos;
- una consecuencia de frontera explícitamente autorizada asociada a cada Assessment aplicable;
- referencias de trazabilidad.

La consecuencia autorizada deberá declarar exactamente una función de frontera: `H`, `K`, `U` o `S`, además de su estado de evaluación necesario para aplicar la precedencia. Un Assessment sin consecuencia autorizada es descriptivo y no puede crear frontera por inferencia.

La implementación no derivará `H/K/U/S` desde severidad, criticality, GAP, R0–R3, cantidad de Assessment ni historial.

## 3. Identidad y aislamiento

El resultado conservará `decision_id` y `scenario_id`, junto con el contexto de versión/snapshot que haya sido recibido. Assessment pertenecientes a otro contexto no podrán mezclarse silenciosamente; una incompatibilidad de identidad/contexto produce error técnico de entrada.

El escenario actual no hereda restricciones del escenario precedente por historial.

## 4. Estados y determinación

Estados permitidos: `VIABLE`, `VIABLE_CON_CONDICIONES`, `NOT_VIABLE`, `NOT_EVALUABLE`.

Precedencia única:

1. `H` autorizada + incumplida + suficientemente evaluada → `NOT_VIABLE`.
2. Sin `H` incumplida + `U` material → `NOT_EVALUABLE`.
3. Sin `H`/`U` + `K` incumplida + solucionable → `VIABLE_CON_CONDICIONES`.
4. En otro caso → `VIABLE`.

La implementación no aplicará precedencias adicionales.

## 5. Suficiencia y conflictos

`NOT_VIABLE` solo se emite con consecuencia `H` explícita, aplicable, incumplida y suficientemente evaluada.

Si existe conflicto entre consecuencias que requiera una política no autorizada por la documentación vigente, no se inventará una precedencia. El resultado será `NOT_EVALUABLE` y conservará una limitación identificable como conflicto no resuelto.

Esto no convierte una insuficiencia ordinaria en una conclusión empresarial negativa y no sustituye la autoridad de CRC.

## 6. Orden y determinismo

La colección de Assessment y las referencias se canonicalizarán mediante claves estables derivadas de sus identificadores autorizados. El orden de entrada no podrá cambiar el resultado.

No se deducirá causalidad automática entre Assessment redundantes. Los duplicados semánticos no intensifican el resultado por conteo.

## 7. Inmutabilidad y trazabilidad

La función no mutará Assessment, contexto ni referencias. El resultado mantendrá trazabilidad hacia los Assessment y reglas que sustentan la clasificación.

No se crea un repositorio alternativo de evidencia.

## 8. Monotonicidad y no compensación

Las señales `S` no modifican por sí mismas el resultado. Resultados favorables no compensan una `H` incumplida. Resultados desfavorables múltiples no crean una nueva restricción.

La revelación de una `H` previamente no evaluada puede cambiar el resultado porque activa una restricción normativa preexistente; no constituye inferencia nueva.

## 9. Errores técnicos

Entrada mal formada, consecuencia inexistente o inválida, identidad incompatible o referencias internamente inconsistentes producirán un error técnico explícito y determinista; no se transformarán silenciosamente en `NOT_VIABLE` ni en recomendación empresarial.

## 10. Integración

VF consume resultados ya producidos. No ejecuta reglas, Evidence, Scenario Engine, O1, CRC ni negociación. Tampoco llama internamente a otros motores.

Su resultado queda disponible para las capas posteriores conforme a sus contratos. La integración E2E entre VF y otras capacidades requiere su propio contrato si introduce comportamiento adicional.

## 11. Exclusiones

Fuera de alcance: nuevas reglas, parámetros, umbrales, fórmulas, score, pesos, compensación, ranking, optimización, selección, recomendación, negociación, decisión de compra, persistencia, SQL, API y cualquier autoridad paralela a CRC.

## 12. Criterios de aceptación

1. Determinismo e independencia del orden de entrada.
2. Identidad/contexto preservados y mezclas rechazadas.
3. `H` válida produce `NOT_VIABLE`.
4. `U` material sin `H` incumplida produce `NOT_EVALUABLE`.
5. `K` incumplida y solucionable sin `H/U` produce `VIABLE_CON_CONDICIONES`.
6. Ausencia de consecuencias autorizadas no crea frontera.
7. Severidad/criticality/GAP/R0–R3 no crean `H`.
8. Redundancia no intensifica por conteo.
9. `S` no modifica el resultado.
10. Favorables no compensan `H`.
11. Conflicto no autorizado queda `NOT_EVALUABLE` con causa.
12. Entradas inválidas producen error técnico explícito.
13. Assessment y contexto permanecen inmutables.
14. Trazabilidad preservada.
15. No acceso interno a motores ni ejecución de reglas.
16. No recomendación/decisión empresarial.
17. Escenarios no heredan restricciones por historial.

## 13. Estado

**CONTRATO DEPURADO — LISTO PARA AUDITORÍA 2.**

No se autoriza implementación de código hasta superar Audit 2.

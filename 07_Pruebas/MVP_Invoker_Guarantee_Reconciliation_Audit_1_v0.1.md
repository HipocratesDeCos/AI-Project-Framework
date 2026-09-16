# EIOS — MVP Invoker Guarantee Reconciliation · Audit 1 v0.1

## Estado

**AUDIT 1: SUPERADA — 0 BLOQUEADORES**

Unidad: `MVP-INVOKER-GUARANTEE-RECON-01`

Baseline auditado: `main @ d79e27cad7c557c382d6f86dc5336073db8eede6`

Diseño auditado: `08_Implementacion/MVP_Invoker_Guarantee_Reconciliation_Design_v0.1.md`

## 1. Evidencia de la regresión

Se confirma una cadena causal exacta:

1. PR #117 cerró la cuarentena NI/Ladder y declaró que los invokers explícitos no eran certificados provenance-safe.
2. PR #118 aplicó el mismo principio a Scenario Coordination: `invoker presence alone is not provenance proof`.
3. Antes de la cuarentena QTG, `mvp_execution.py` conservaba esa formulación genérica correcta.
4. El commit `d5c4f5f239e1f1b08a530d69bace279650ae3670`, cuyo objeto era retirar `quality_invoker`, sustituyó lateralmente esa salvaguarda por `explicit provenance-safe invokers` para todas las capacidades restantes.
5. El contrato QTG no autorizaba ampliar la garantía de NI/Ladder, Scenario Coordination o Decision Twin.

**Dictamen:** regresión objetiva y localizada.

## 2. Contraste con E2E

El E2E Execution Boundary acepta un catálogo explícito `capability -> invoker`, valida plan/contexto y ejecuta el callable. El tipo genérico `CapabilityInvoker` no codifica ni demuestra provenance-safe por sí mismo.

Restaurar `invoker presence alone is not provenance proof` alinea el docstring con la capacidad real del boundary.

**Resultado: PASS.**

## 3. PRICE / TCO

PRICE y TCO poseen builders específicos que sí implementan políticas provenance-safe. El texto genérico no debe negar esa propiedad; simplemente no debe atribuirla automáticamente a cualquier callable compatible con `CapabilityInvoker`.

La garantía positiva de PRICE/TCO permanece en sus contratos/builders especializados.

**Resultado: PASS.**

## 4. Scenario Coordination

PR #118 prohíbe afirmar que cualquier invocador Scenario Coordination sea provenance-safe por el mero hecho de ser invocador. La ruta especializada puede reconstruir soporte desde una orquestación congelada, pero la procedencia de esa orquestación pertenece a otra frontera.

La corrección propuesta preserva exactamente esa separación.

**Resultado: PASS.**

## 5. NI / Ladder

El contrato vigente es inequívoco:

- raw results desprendidos: prohibidos en la frontera pública;
- invocadores explícitos: admitidos;
- invocador explícito ≠ certificación provenance-safe;
- productor provenance-safe positivo: no materializado por PR #117.

No se ha encontrado contrato posterior que cambie esa política ni builders `build_provenanced_negotiation*` en el baseline.

**Resultado: PASS.**

## 6. Decision Twin

La firma genérica conserva `decision_twin_invoker`, pero PR #144 puso en cuarentena el wrapper público dependiente de Stage 2/VF.

La frase `must arrive through explicit invokers` describe únicamente la forma aceptada si una capacidad cruza esta frontera; no afirma que exista actualmente un productor público autorizado.

Para evitar reapertura implícita, el docstring corregido no describirá Decision Twin como actualmente disponible ni como provenance-safe.

**Resultado: PASS con precisión de redacción.**

## 7. QTG

La cláusula especial QTG introducida por PR #142 es correcta y debe preservarse:

- QTG sigue en `MVP_CAPABILITY_ORDER`;
- no existe argumento `quality_invoker`;
- reapertura exige productor provenance-safe desde Decision Input Package autorizado.

La corrección no restaurará el callable QTG.

**Resultado: PASS.**

## 8. Superficie afectada

Se ha contrastado:

- `eios/core/mvp_execution.py` — contiene la sobreafirmación;
- `eios/mvp.py` — usa `explicit authorized invokers`, formulación compatible y no requiere cambio;
- contrato E2E — no sobreafirma provenance genérico;
- contrato NI/Ladder — autoridad correctiva;
- contrato Scenario Coordination — autoridad correctiva;
- PR #142 / commit causante — regresión localizada.

No se identifica necesidad de modificar otro archivo funcional actual.

## 9. Riesgos de depuración

La depuración debe fijar una redacción exacta que:

1. diga `explicit invokers`, no `explicit provenance-safe invokers`;
2. conserve la prohibición de detached raw results;
3. restaure literalmente el principio `Invoker presence alone is not provenance proof`;
4. conserve íntegra la cláusula QTG;
5. no enumere builders o estados de disponibilidad susceptibles de quedar obsoletos en el docstring genérico.

## 10. Matriz Audit 1

| Control | Resultado |
|---|---|
| Regresión demostrada | PASS |
| Autoridad previa suficiente | PASS |
| Runtime requiere cambio | NO |
| API requiere cambio | NO |
| PRICE/TCO degradados | NO |
| Scenario / NI / Ladder reconciliados | PASS |
| Decision Twin reabierto | NO |
| QTG reabierto | NO |
| Bloqueadores | **0** |

## 11. Resultado

**AUDIT 1 SUPERADA — 0 BLOQUEADORES.**

Procede **DEPURAR** únicamente la formulación del diseño antes de Audit 2.
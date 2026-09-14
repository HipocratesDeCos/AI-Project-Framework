# EIOS — Scenario Stage 2 VF Provenance Quarantine — Reconciliation

**Baseline histórico afectado:** contratos cerrados de Stage 2 y VF→Scenario Analytics, más wrappers públicos aguas abajo que dependían de esa garantía.  
**Autoridad vigente para la integración pública:** `Scenario_Stage2_VF_Provenance_Quarantine_Contract_v0.1.md`.

## 1. Motivo

La auditoría posterior detectó una contradicción que no estaba identificada al cerrar:

- `Scenario_Stage2_Provenance_Boundary_Contract_v0.1.md` trató un `ViabilityResult` tipado y contextualmente consistente como material suficiente para una frontera pública provenance-safe;
- `Viability_Frontier_Scenario_Analytics_Integration_Contract_v0.1.md` denominó “procedencia validada” a una verificación de identidad/versiones sobre un `ViabilityResult` ya producido;
- el modelo físico de VF define `FrontierAssessment` como representación de una consecuencia **ya autorizada externamente** y no contiene un productor que acredite dicha autorización;
- un caller puede construir directamente `ViabilityResult` y sus IDs/trazas sin que la frontera pueda distinguirlo de un resultado producido por una fuente autorizada;
- `eios.rules.decision_twin_integration` reutilizaba esa frontera Stage 2 y, por ello, heredaba exactamente la misma insuficiencia aunque el comparador Decision Twin core fuese correcto.

## 2. Regla de lectura

Los contratos anteriores se conservan como registro histórico de las fronteras que materializaron y de los problemas que sí resolvieron en su momento.

Quedan, sin embargo, **superseded únicamente en la afirmación de procedencia VF hacia una finalización pública Stage 2 y en cualquier wrapper público que dependa de esa afirmación**.

Siguen vigentes sus conclusiones sobre:

- Stage 2 interno;
- cobertura exacta de escenarios;
- separación entre estado VF y estado O3;
- inmutabilidad;
- ausencia de autoridad decisional;
- validación contextual del bridge VF;
- procedencia C0 `Assessment+Trace`;
- semántica y comparación descriptiva de Decision Twin core.

No sigue vigente la inferencia de que tipo + identidad + versiones de `ViabilityResult` acreditan el productor VF, ni que un wrapper aguas abajo pueda recuperar esa garantía por simple composición.

## 3. Estado operativo resultante

Hasta que exista un productor físico y auditable de consecuencias VF:

- el bridge `eios.core.viability_scenario_integration` es únicamente context-bound transport;
- no existe finalización pública Scenario Stage 2 que pueda proclamarse provenance-safe;
- las APIs públicas que elevaban `ViabilityResult` desprendido a esa condición quedan en cuarentena;
- `eios.rules.decision_twin_integration` queda en cuarentena por dependencia directa de Stage 2;
- Decision Twin core/comparator permanece cerrado y disponible en su frontera propia;
- O4/O2/O3, C0 y VF permanecen cerrados dentro de sus fronteras propias.

## 4. Reapertura

Una futura reapertura no podrá basarse solo en reintroducir los símbolos retirados ni en recalcular VF desde `FrontierAssessment` arbitrario. Deberá demostrar físicamente la fuente/autoridad de las consecuencias de frontera y su vinculación trazable con la ejecución actual.

Los wrappers aguas abajo solo podrán reabrirse después de que la cadena positiva Stage 2 de la que dependen haya recuperado una procedencia demostrable.

Esta reconciliación no crea arquitectura ni autoridad nueva; corrige exclusivamente la interpretación de procedencia entre contratos históricos y el estado físico actual.

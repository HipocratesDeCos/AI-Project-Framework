# EIOS — STK-M10 · Cierre de autoridad metodológica de contradicciones v0.1

**Estado:** CERRADO — MATERIALIZADO — CI LOCAL VALIDADO
**Baseline:** `232218bf49a3641e1f198e1468fc2f61f41added`
**Ámbito:** comparabilidad, detección, preservación, propagación, resolución autorizada y fronteras de autoridad; sin motor cuantitativo

## 1. DISEÑAR

Formalizar qué constituye una contradicción real, qué diferencias son legítimas, cómo se preserva y propaga, cuándo puede resolverse y qué autoridades permanecen separadas.

## 2. AUDITAR

Se contrastó la decisión humana con STK-M01…M09, Evidence Contract, la Capa de Resolución de Conflictos y la Matriz de Autoridad Documental.

Existe autoridad suficiente para cerrar M10 sin crear heurísticas, corregir fuentes silenciosamente, duplicar la CRC ni crear una precedencia documental paralela.

## 3. DEPURAR

- una diferencia no es automáticamente contradicción;
- artículo, variable, unidad, normalización, tiempo, ámbito, versión y contexto deben ser comparables;
- diferencias legítimas permanecen separadas;
- se conservan todas las evidencias y la discrepancia completa;
- el estado no resuelto es `CONFLICTING_DATA / UNRESOLVED_CONTRADICTION`;
- no se selecciona por recencia, magnitud, probabilidad aparente, promedio, score o prioridad arbitraria;
- una resolución exige política de autoridad aplicable;
- la incertidumbre bloquea toda conclusión materialmente dependiente;
- conflictos entre resultados permanecen en CRC y contradicciones documentales en la matriz de autoridad;
- `contradiction ≠ missing_data`;
- la resolución posterior no reescribe la historia;
- no se autoriza ninguna decisión empresarial automática.

## 4. AUDITAR 2

Resultado:

- `6 passed` en las pruebas específicas M10;
- `332 passed` en la suite completa, con todas las advertencias promovidas a error;
- `STK-M01…M10` quedan metodológicamente cerrados;
- la auditoría de entrada a contrato e implementación permanece pendiente;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M10` queda cerrado como autoridad metodológica de contradicciones de datos y evidencias STK.

## 6. MATERIALIZAR

Se actualiza la matriz y se añaden la autoridad M10 y sus pruebas. No se modifican reglas, parámetros, contratos, SQL ni código ejecutable.

## 7. CI

La evidencia de commit, publicación, integración y CI se incorporará sin anticipar resultados todavía no materializados.

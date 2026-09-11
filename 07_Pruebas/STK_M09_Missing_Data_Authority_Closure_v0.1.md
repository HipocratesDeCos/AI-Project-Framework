# EIOS — STK-M09 · Cierre de autoridad metodológica de ausencia de datos v0.1

**Estado:** CERRADO — MATERIALIZADO — CI LOCAL VALIDADO
**Baseline:** `2ce3811f3f8d40295c3043bf5d6ca64536adccd7`
**Ámbito:** estados de ausencia, no sustitución, propagación, trazabilidad, reevaluación y autoridad; sin motor cuantitativo

## 1. DISEÑAR

Formalizar el significado de ausencia, sus estados mínimos, la prohibición de sustitución implícita, la propagación a M01–M08, el registro trazable y la reevaluación.

## 2. AUDITAR

Se contrastó la decisión humana con las autoridades cerradas STK-M01…M08 y con `Criticality` y `Evaluability_Impact` de la matriz de dependencias.

Existe autoridad suficiente para cerrar M09 sin asignar criticidades pendientes, autorizar imputaciones concretas ni convertir incertidumbre en un resultado empresarial.

## 3. DEPURAR

- ausencia no equivale a cero, inexistencia, normalidad ni ausencia de riesgo;
- se distinguen `UNKNOWN`, `NOT_EVIDENCED`, `NOT_APPLICABLE` y `CONFLICTING_DATA`;
- `NOT_APPLICABLE` exige inaplicabilidad demostrada;
- no se autorizan sustituciones implícitas;
- toda imputación futura requiere política específica, autorizada, versionada y trazable;
- la incertidumbre se propaga a toda conclusión dependiente;
- no se inventan criticidades ni tratamientos parciales;
- una reevaluación crea una versión trazable y no reescribe la anterior;
- la alerta de calidad no constituye una decisión automática.

## 4. AUDITAR 2

Resultado:

- `6 passed` en las pruebas específicas M09;
- `326 passed` en la suite completa, con todas las advertencias promovidas a error;
- `STK-M10` permanece pendiente;
- STK continúa no apto para implementación cuantitativa;
- no cambia código ejecutable, SQL, reglas, parámetros ni contratos técnicos.

## 5. CERRAR

`STK-M09` queda cerrado como autoridad metodológica transversal de ausencia e insuficiencia de evidencia.

## 6. MATERIALIZAR

Se actualiza la matriz y se añaden la autoridad M09 y sus pruebas. No se modifican reglas, parámetros, contratos, SQL ni código ejecutable.

## 7. CI

La evidencia de commit, publicación, integración y CI se incorporará sin anticipar resultados todavía no materializados.

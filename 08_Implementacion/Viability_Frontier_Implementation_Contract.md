# EIOS — VIABILITY FRONTIER · IMPLEMENTATION CONTRACT

**Versión:** 0.1
**Estado:** CONTRATO TÉCNICO — PENDIENTE DE AUDITORÍA 2
**Baseline:** d82cf899ccc0a133e9a6d9a7be3084ca3f5dbc40

## 1. Propósito

Materializar técnicamente el contrato documental cerrado de `05_Motor/Viability_Frontier.md` sin ampliar su autoridad.

## 2. Responsabilidad

El componente recibirá `Assessment` ya producidos y determinará únicamente el estado base de viabilidad cuando las consecuencias de frontera estén explícitamente autorizadas.

Estados permitidos:

- `VIABLE`
- `VIABLE_CON_CONDICIONES`
- `NOT_VIABLE`
- `NOT_EVALUABLE`

No genera recomendaciones de compra.

## 3. Entradas

La implementación deberá recibir, como mínimo:

- contexto de operación autorizado;
- colección inmutable de `Assessment`;
- consecuencia de frontera explícitamente autorizada para cada resultado aplicable;
- referencias de trazabilidad.

No descubrirá reglas aplicables ni fabricará consecuencias.

## 4. Determinación

Aplicará exclusivamente esta precedencia:

1. restricción dura autorizada, incumplida y suficientemente evaluada → `NOT_VIABLE`;
2. ausencia de restricción dura incumplida + insuficiencia material → `NOT_EVALUABLE`;
3. condición autorizada incumplida y solucionable → `VIABLE_CON_CONDICIONES`;
4. en ausencia de las anteriores → `VIABLE`.

No habrá voto, suma, promedio, score, peso ni compensación.

## 5. No inferencia

La implementación rechazará cualquier intento de derivar una restricción o consecuencia únicamente desde:

- severidad;
- criticality;
- cantidad de Assessment desfavorables;
- GAP;
- códigos R0–R3;
- historial de escenarios.

## 6. Conflictos

Si la información recibida requiere una política de resolución no autorizada, el resultado será `NOT_EVALUABLE` con limitación técnica/documental explícita; nunca se inventará precedencia.

La resolución normativa posterior corresponde a CRC.

## 7. Monotonicidad y no compensación

La implementación deberá garantizar que señales informativas o resultados redundantes no modifiquen el estado por conteo y que resultados favorables no neutralicen una restricción dura autorizada incumplida.

## 8. Trazabilidad

El resultado conservará referencias a los Assessment y reglas que sustentan la clasificación. No almacenará una segunda evidencia ni alterará los Assessment recibidos.

## 9. Inmutabilidad y determinismo

La función será pura respecto a sus entradas: sin mutación, persistencia, llamadas de red, ejecución de reglas, acceso a motores externos o estado global.

La misma entrada canónica deberá producir el mismo resultado.

## 10. Exclusiones

Fuera de alcance:

- creación/evaluación de reglas;
- cálculo de evidencia;
- creación de escenarios;
- scoring/optimización/ranking;
- negociación;
- recomendación empresarial;
- decisión de compra;
- sustitución de CRC;
- persistencia/SQL/API;
- inferencia de parámetros o umbrales.

## 11. Criterios de aceptación

La futura implementación deberá demostrar al menos:

1. viable cuando no existen restricciones/condiciones activadas;
2. no viable ante una restricción dura autorizada incumplida;
3. no evaluable ante insuficiencia material sin hard constraint incumplida;
4. viable con condiciones ante condición autorizada incumplida y solucionable;
5. severidad sin consecuencia explícita no crea frontera;
6. múltiples resultados desfavorables no crean score ni bloqueo por conteo;
7. resultados favorables no compensan hard constraint;
8. Assessment no son mutados;
9. conflictos no autorizados no generan precedencia inventada;
10. trazabilidad preservada;
11. determinismo;
12. ausencia de acceso a motores/reglas externos;
13. ausencia de recomendación empresarial;
14. separación de CRC;
15. escenario anterior no altera automáticamente el actual.

## 12. Estado

**AUTORIZADO PARA AUDITORÍA 1 DEL CONTRATO; NO AUTORIZADO TODAVÍA PARA IMPLEMENTACIÓN DE CÓDIGO.**

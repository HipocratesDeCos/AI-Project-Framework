# EIOS — O4 · CONTROLLED SCENARIO GENERATION & EXPLORATION

**Estado:** 🟡 DISEÑO — NO IMPLEMENTADO
**Baseline:** `ad7961935cc19ca4ab0a19dbef0ac9d4721c8374`
**Rama de diseño:** `design/o4-controlled-scenario-generation`

---

## 1. Propósito

Definir una capacidad futura de generación y exploración controlada de escenarios que amplíe O2 sin modificar su autoridad ni convertir el Scenario Engine en un motor de optimización o decisión.

O4 deberá producir únicamente candidatos de escenario sujetos a un espacio de hipótesis explícitamente autorizado. La evaluación de esos candidatos permanecerá separada y podrá utilizar O3 cuando exista una integración contractual posterior.

---

## 2. Posición funcional

```text
ESPACIO DE HIPÓTESIS AUTORIZADO
            ↓
           O4
 generación / exploración acotada
            ↓
    ScenarioVersion (O2)
            ↓
      evaluación (O3)
            ↓
 resultados derivados
```

O4 no sustituye O2 ni O3.

---

## 3. Entrada autorizada

O4 solo podrá recibir:

- escenario base o contexto de escenario autorizado;
- variables de escenario explícitamente declaradas;
- dominios o valores permitidos para cada variable;
- límites combinatorios explícitos;
- política de generación aprobada;
- identidad y contexto de decisión compatibles con las autoridades existentes.

La ausencia de una variable en el espacio autorizado implica que O4 no puede generarla por inferencia.

---

## 4. Espacio de escenarios

El espacio de búsqueda debe estar definido externamente al algoritmo mediante una especificación explícita por variable.

Cada variable deberá distinguir, como mínimo:

```text
identidad de variable
       ↓
tipo de valor
       ↓
dominio permitido
       ↓
regla de discretización, si procede
       ↓
límite de cardinalidad
```

O4 no podrá interpretar un parámetro EIOS como variable de escenario sin autorización expresa.

---

## 5. Generación

La generación inicial deberá ser **determinista**.

Misma entrada + misma política + mismo contexto ⇒ mismo conjunto ordenado de candidatos.

Las operaciones permitidas podrán incluir inicialmente:

- enumeración de valores autorizados;
- producto cartesiano explícitamente acotado;
- combinaciones explícitamente autorizadas;
- exploración de escenarios derivados de un escenario padre.

No se autoriza generación probabilística, heurística adaptativa ni optimización en este diseño inicial.

---

## 6. Límites combinatorios

Toda generación deberá estar sometida a límites explícitos antes de producir candidatos.

Como mínimo:

- número máximo de variables;
- cardinalidad máxima por variable;
- número máximo de combinaciones;
- profundidad máxima de derivación;
- número máximo de escenarios emitidos.

Si el espacio solicitado excede un límite, la operación deberá resultar **BLOCKED / NOT_EVALUABLE**, nunca ejecutar una expansión ilimitada.

Los valores concretos de dichos límites quedan pendientes de calibración y aprobación contractual.

---

## 7. Deduplicación y determinismo

Los candidatos deberán canonicalizarse antes de su emisión.

Dos escenarios con idéntica identidad de contexto y conjunto de cambios canónicos no podrán aparecer como candidatos distintos.

El orden de entrada no deberá alterar la identidad determinista del escenario.

La deduplicación no podrá alterar la semántica de los cambios autorizados.

---

## 8. Poda

La poda solo podrá utilizar condiciones declaradas previamente por la política de generación.

O4 no podrá inventar criterios de poda basados en:

- preferencias empresariales;
- ranking;
- utilidad;
- rentabilidad no autorizada;
- predicciones;
- decisión humana implícita.

Una condición de poda deberá ser trazable y determinista.

---

## 9. Relación con O2

O4 genera representaciones candidatas; O2 continúa siendo la autoridad contractual para la representación y versionado del escenario.

```text
O4 genera candidato
        ↓
O2 valida / representa ScenarioVersion
```

O4 no debe crear una segunda identidad de escenario ni un segundo mecanismo de versionado.

---

## 10. Relación con O3

O4 no evaluará reglas ni viabilidad.

La secuencia futura, si se autoriza integración, será:

```text
O4 → O2 → O3
```

O3 continuará consumiendo resultados ya producidos y no recibirá autoridad adicional por la existencia de O4.

---

## 11. Invariantes iniciales

```text
OPERACIÓN REAL ≠ ESCENARIO
PARÁMETRO ≠ VARIABLE DE ESCENARIO
O4 ≠ O2
O4 ≠ O3
O4 ≠ VIABILITY FRONTIER
O4 ≠ DECISION TWIN
O4 ≠ NEGOTIATION
O4 ≠ CRC
O4 ≠ OPTIMIZATION ENGINE
CANDIDATO ≠ ALTERNATIVA
ALTERNATIVA ≠ DECISIÓN
NOT_EVALUABLE ≠ NOT_VIABLE
```

Además:

1. no mutación del escenario padre;
2. no mutación de la operación real;
3. no modificación de reglas;
4. no modificación de parámetros;
5. no creación de dependencias;
6. no invención de evidencia;
7. determinismo;
8. límites finitos obligatorios;
9. trazabilidad de la política utilizada;
10. ausencia de selección empresarial.

---

## 12. Fuera de alcance

Este diseño no autoriza:

- optimización matemática;
- ranking de escenarios;
- selección automática;
- recomendación;
- negociación automática;
- decisión empresarial;
- aprendizaje adaptativo;
- búsqueda ilimitada;
- API;
- persistencia;
- SQL;
- nuevo modelo de datos.

---

## 13. Criterios para avanzar

Antes de cualquier implementación deberán completarse, como mínimo:

1. definición formal de tipos de variables;
2. política de dominios y discretización;
3. límites contractuales definitivos;
4. semántica exacta de BLOCKED / NOT_EVALUABLE;
5. contrato de deduplicación;
6. contrato de poda;
7. trazabilidad de generación;
8. auditoría de autoridad O4 ↔ O2 ↔ O3;
9. pruebas deterministas de frontera;
10. decisión explícita sobre si O4 incluye o excluye combinaciones multidimensionales en MVP.

Solo después podrá iniciarse la secuencia:

**AUDITAR → DEPURAR → AUDITAR 2 → CERRAR → MATERIALIZAR → CI**.

---

## 14. Estado

Este documento constituye exclusivamente el **inicio formal del diseño O4**.

No modifica `main`.

No modifica contratos cerrados.

No modifica `models.py`.

No introduce código ejecutable.

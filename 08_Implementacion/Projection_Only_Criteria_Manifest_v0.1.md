# EIOS — QTG-PROJECTION-CRITERIA-MANIFEST-01 — Manifiesto v0.1

Fecha: 19/09/2026. Baseline remoto: `1ccaf0b8427bdd63d9f61b5db9ab22e2e2bc6193`; PR #196 y CI #903/#904 SUCCESS.
Autoridad: aprobación explícita de los cuatro criterios de `PROJECTION_ONLY`.
Estado: diseño, auditorías e implementación completados; integración condicionada a CI.

## DISEÑAR

Crear un manifiesto inmutable que cierre qué material de criterio puede aceptar el futuro productor `PROJECTION_ONLY`, sin interpretar ni ejecutar texto presentado.

Cada `AuthorizedProjectionCriterion` conserva:

- función cerrada;
- referencia;
- versión;
- SHA-256 exacto del contenido autorizado.

Las cuatro funciones obligatorias son:

1. `HORIZON_FLOW_INVENTORY_COMPLETENESS`: inventariar todos los cobros y pagos potencialmente relevantes del horizonte o declarar incompletitud;
2. `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT`: acreditar importe, moneda, vencimiento y pertenencia económica de cada flujo participante;
3. `DETERMINATE_PROJECTION_RELIABILITY`: bloquear una proyección determinada fiable cuando falte la completitud necesaria;
4. `OUT_OF_HORIZON_CONFLICT_PRESERVATION`: no bloquear por flujos demostrablemente fuera del horizonte, conservando sus conflictos.

`ProjectionCriteriaManifest` añade identidad y versión del manifiesto, autoridad declarada y fecha consciente de zona horaria. `validate_preparation_criteria_against_manifest` exige igualdad exacta entre los pares referencia/versión y sus hashes presentes en `FinanceQualityPreparation` y los autorizados. No consume el contenido, no crea checks y no llama a Finance ni QTG.

Schema: `QTG-PROJECTION-CRITERIA-MANIFEST-01/v0.1`.

## AUDITAR

A1: aceptar solo referencia/versión permitiría sustituir el contenido. Se vincula SHA-256 exacto.

A2: aceptar un subconjunto permitiría omitir una regla aprobada. Se exige cobertura exacta de las cuatro funciones.

A3: aceptar extras ampliaría política sin autorización. La comparación con la preparación es igualdad de mapas, no inclusión parcial.

A4: dos contenidos bajo una función o una identidad repetida harían ambiguo el criterio. Se rechazan funciones e identidades duplicadas.

A5: un hash con forma libre debilitaría el contrato. Solo se admite SHA-256 hexadecimal minúsculo de 64 caracteres.

A6: el manifiesto podría confundirse con ejecución o resultado. Su assurance scope se limita a identidades autorizadas; no contiene contenido, checks, estado ni resultado.

A7: una fecha sin zona o referencias vacías impedirían reproducir la declaración de autoridad. Se rechazan.

A8: un manifiesto estructural no demuestra por sí mismo que una persona tenga competencia real. `authority_ref` conserva la declaración; no sustituye futuras garantías de gobierno ni habilita QTG.

## DEPURAR

A1–A8 incorporados. Se mantiene separada la cadena:

```text
criterio presentado → reference/version/hash → manifiesto autorizado → futura traducción cerrada
```

El paso actual cierra únicamente los tres primeros elementos. La futura traducción a checks sigue prohibida hasta diseñar el productor.

## AUDITAR 2

Pruebas focales: **17 satisfactorias**. Cubren coincidencia exacta, alteración de contenido/referencia/versión, criterio extra o ausente, funciones e identidades duplicadas, autoridad/fecha inválidas, formato de hash, inmutabilidad y rechazo de objetos no construidos.

Suite completa: **1.266 pruebas satisfactorias**, seis avisos preexistentes/no bloqueantes. No se modifica `FinanceQualityPreparation`, las cadenas de tesorería/flujos, Rules, C0, PRICE, Scenario, Decision Twin ni Finance Basic.

PASS técnico: `QTG-PROJECTION-CRITERIA-MANIFEST-01` queda resuelto dentro de este alcance.

## CERRAR → MATERIALIZAR → CI

Material:

- `eios/core/projection_criteria_manifest.py`;
- `tests/test_projection_criteria_manifest.py`;
- este documento.

El cierre integrado exige CI exact-head y post-merge. QTG continúa inhabilitado.

Siguiente unidad legítima: `QTG-PROJECTION-MATERIAL-01`, envelope agregado e inmutable que vincule preparación, manifiesto autorizado, cadena exacta de tesorería y cadena exacta de flujos, recomputando todas sus pertenencias sin producir todavía checks.

# EIOS — QTG-PROJECTION-CRITERIA-MANIFEST-02 — Extensión v0.2

Fecha: 19/09/2026. Baseline remoto: `f4d2d4f51391a4c762547e6c0292509bdd917a7e`; PR #199 y CI #909/#910 SUCCESS.
Autoridad: aprobación explícita del titular de las funciones `INITIAL_TREASURY_SUFFICIENCY`, `ECONOMIC_FLOW_UNIQUENESS` y de la posterior separación entre `SYNTHETIC_TEST` y `OPERATIONAL`.
Estado: diseño, auditorías e implementación completados; integración condicionada a CI.

## DISEÑAR

Extender el catálogo cerrado de `ProjectionCriteriaManifest` de cuatro a seis funciones, sin modificar ni reinterpretar las cuatro existentes:

1. `HORIZON_FLOW_INVENTORY_COMPLETENESS`;
2. `PARTICIPATING_FLOW_ATTRIBUTE_SUPPORT`;
3. `DETERMINATE_PROJECTION_RELIABILITY`;
4. `OUT_OF_HORIZON_CONFLICT_PRESERVATION`;
5. `INITIAL_TREASURY_SUFFICIENCY`;
6. `ECONOMIC_FLOW_UNIQUENESS`.

`INITIAL_TREASURY_SUFFICIENCY` vincula una identidad/version/hash autorizada a la base cerrada `FIN-PILOT-TREASURY-SUFF-01`. No certifica ningún saldo ni ejecuta la cadena de tesorería.

`ECONOMIC_FLOW_UNIQUENESS` vincula una identidad/version/hash autorizada a la exigencia ya cerrada de cómputo económico único. No introduce algoritmo de deduplicación, fusión heurística o prioridad documental.

El schema avanza de `QTG-PROJECTION-CRITERIA-MANIFEST-01/v0.1` a `/v0.2`. La comparación con `FinanceQualityPreparation` continúa exigiendo igualdad exacta del conjunto completo reference/version/hash.

La autorización de los modos se conserva como alcance de la siguiente unidad; este cambio no añade modo de ejecución al manifiesto.

## AUDITAR

A1: reutilizar una función de flujos para tesorería ampliaría su semántica por analogía. Se crea una función separada.

A2: incluir unicidad dentro de los cuatro atributos ocultaría el riesgo de doble cómputo. Se crea una función independiente.

A3: aceptar manifiestos v0.1 en el futuro productor dejaría dos controles sin criterio ejecutable. La cobertura exacta pasa a seis funciones; cuatro ya no bastan.

A4: la mera presencia de las nuevas etiquetas podría interpretarse como criterio material. Se mantienen reference/version/hash obligatorios y coincidencia exacta con el contenido presentado.

A5: la función de unicidad podría usarse para elegir o fusionar flujos. Se limita a autorizar el criterio; el productor solo podrá valorar el material estructurado existente.

A6: la suficiencia de tesorería podría extenderse a margen, liquidez externa o fondo de maniobra. Su alcance permanece exclusivamente en la tesorería inicial de `PROJECTION_ONLY`.

A7: mezclar modo operativo en el manifiesto confundiría criterio y ejecución. Los modos se posponen al contrato productor/recibo.

## DEPURAR

A1–A7 incorporados. La extensión es aditiva en autoridad y estricta en validación: cualquier criterio ausente, adicional, duplicado o alterado sigue rechazado.

No se modifica `FinanceQualityPreparation`, `ProjectionMaterialEnvelope`, las cadenas especializadas, `QualityCheck`, el gate ni Finance Basic.

## AUDITAR 2

Las pruebas focales confirman:

- presencia exacta de las seis funciones;
- schema `/v0.2`;
- rechazo de la antigua cobertura parcial de cuatro/cinco funciones;
- invariantes previas de identidad, hash, autoridad, inmutabilidad y coincidencia con la preparación.

Resultado focal: **30 pruebas satisfactorias** para manifiesto y envelope.

Suite completa: **1.279 pruebas satisfactorias**, siete avisos preexistentes/no bloqueantes.

PASS técnico: las dos funciones nuevas quedan exigidas de forma exacta y no alteran la vinculación del envelope.

## CERRAR → MATERIALIZAR → CI

Material:

- `eios/core/projection_criteria_manifest.py`;
- `tests/test_projection_criteria_manifest.py`;
- este documento.

QTG continúa inhabilitado. El cierre integrado exige CI exact-head y post-merge.

Siguiente unidad legítima: diseñar el contrato `QTG-PROJECTION-PRODUCER-01` y su recibo recomputable con modos cerrados `SYNTHETIC_TEST` y `OPERATIONAL`, sin implementar todavía su ejecución positiva.

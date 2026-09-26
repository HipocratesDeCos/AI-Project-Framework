# EIOS — Auditoría de cierre del paquete de referencia sintética v0.1

**Base comprobada:** `main @ 3d4be6f5530e51792f3c7fda29bc069ceb42e04f`.

## DISEÑAR

Determinar si `Reference Business Case 001` ya ofrece un paquete local completo,
repetible y legible para una demostración de compras de una empresa ficticia.
Esta auditoría no concede admisión operacional ni transforma el caso fijo en
un adaptador de empresas arbitrarias.

## AUDITAR — evidencia ejecutada

Se generó el paquete con las ocho opciones de observación y
`--with-buyer-preview`, y se ejecutó `verify_reference_demo` sobre el
directorio publicado. Resultado: **20 archivos**, dos terminales, ocho pares
de sidecars y dos HTML. La repetición coincide con las huellas terminales:

| Variante | QTG | Huella terminal |
|---|---|---|
| `negative` | `NO_APTO / BAJA` | `6e4493d8780ae5e7df1fcb08e8eaf14f32605cb58893c7e0d8aba2ef5de173f1` |
| `qtg-eligible` | `APTO / ALTA` | `53a9bf49ef0ab6dba6c9c3e1d737e26652dc84fbf13736d0a0f7a31d34e6ba3b` |

Los ocho pares son PRICE, TCO, Supplier Risk/Value, C0/CRC, Decision Twin,
Scenario Coordination, Negotiation Intelligence y Negotiation Ladder. El
visor técnico y la vista sintética para compras se recomponen en la
verificación. La segunda presenta la misma propuesta ficticia, separa QTG de
ejecución técnica y conserva limitaciones y trazas.

## DEPURAR — alcance probado

| Afirmación | Estado |
|---|---|
| E2E del caso de referencia fijo, con ambas variantes | Comprobado por generación y repetición local. |
| Ocho capturas ligadas a sus terminales | Comprobado por el verificador existente. |
| Vista local de lectura para explicar la simulación | Comprobado; no es una UI empresarial operacional. |
| Material `SYNTHETIC`, QTG `SYNTHETIC_TEST_ONLY`, ruta `FORBIDDEN`, efecto `NO_OPERATIONAL_EFFECT`, autoridad decisional `false` | Conservado en ambos terminales. |
| Empresa real, expediente presentado y admisión operacional | No forman parte de este paquete. |
| Adaptación automática del runner a cualquier empresa o sector | No demostrada: el runner acepta solo los dos fixtures cerrados de `Reference Business Case 001`. |

Las huellas vinculan artefactos y permiten detectar cambios frente al
fixture repetido; no autentican hechos externos. `APTO`, `COMPLETED`,
`VIABLE`, `AUTHORIZED` o un CRC `COMPRAR` no otorgan autoridad empresarial.

## AUDITAR 2

`case_provenance.py` clasifica un bundle sintético completo como
`REFERENCE_OPERATIONAL_SIMULATION` y mantiene `FORBIDDEN`. El contrato del
adaptador `ProjectionOnlySyntheticMaterialBundle` ya dispone de una frontera
de material canónico; el runner de ejemplo añade los supuestos particulares
del fixture. La revisión de la interfaz confirma que la página HTML de
compras es una proyección estática de archivos verificados, no una entrada
para ejecutar un caso de cliente.

No se halló una contradicción objetiva que requiera abrir QTG, Operational
Admission, el binding QTG↔O1 ni `run_mvp_execution`.

## CERRAR

Se cierra **la demostración reproducible del caso fijo**. La siguiente unidad
con valor arquitectónico es auditar la parametrización de un *segundo caso
sintético* con otra empresa ficticia: identificar qué material puede cambiar
sin modificar el núcleo, qué productores exigen fixtures concretos y qué
binding impide mezclar empresas o variantes. El diseño debe reutilizar el
cargador, el adaptador y los invocadores existentes, y mantener
`SYNTHETIC / SYNTHETIC_TEST_ONLY / FORBIDDEN / NO_OPERATIONAL_EFFECT / false`.
No se presupone que el runner actual admita ese segundo caso.

## MATERIALIZAR → CI

Este documento registra la auditoría y el límite de cierre. No modifica
runtime, fixtures, contratos ni tests. Su integración requiere CI del PR.

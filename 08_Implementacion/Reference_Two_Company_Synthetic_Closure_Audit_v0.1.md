# EIOS — Cierre de la demostración sintética con dos empresas v0.1

## DISEÑAR → AUDITAR

Se audita la afirmación acotada: dos empresas ficticias distintas pueden
atravesar la misma fachada E2E de referencia y quedar reunidas en una lectura
local verificable. La comparación no mide rendimiento entre empresas ni
constituye una decisión de compra.

La prueba ejecutó `create_comparison_bundle` en un directorio temporal y
`verify_comparison_bundle` tras la publicación. Inventario observado:

| Expediente | Archivos | QTG | Ejecución | Lectura |
|---|---:|---|---|---|
| 001 negativo | Integrado en 20 archivos del caso 001 | `NO_APTO` | `COMPLETED` | Variante de control, fuera de las columnas comparadas. |
| 001 apto | Mismos 20 archivos: dos terminales, ocho pares de capturas y dos HTML | `APTO` | `COMPLETED` | Fiabilidad favorable únicamente en la prueba ficticia. |
| 002 | 10 archivos: terminal, ocho capturas y un HTML | `APTO` | `PARTIALLY_COMPLETED` | Fiabilidad del proveedor no determinable. |
| Comparación | Un HTML de lectura | — | — | Variante apta 001 frente a empresa 002. |

Todos los terminales observados declaran `material_nature=SYNTHETIC`,
`qtg_mode_policy=SYNTHETIC_TEST_ONLY`, `effect_scope=NO_OPERATIONAL_EFFECT`,
`operational_path=FORBIDDEN` y `decision_authority=false`. El estado de
ejecución completo no concede autoridad decisional.

## DEPURAR → AUDITAR 2

La entrada QTG `APTO` aparece tanto en el 001 apto como en el 002. La
diferencia del estado terminal procede de sus materiales de proveedor:
`FAVORABLE` en el ensayo 001 y `NOT_DETERMINABLE` en el 002. Esto demuestra
que la fachada no asigna automáticamente el mismo estado terminal a
dos empresas ni confunde calidad de entrada con fiabilidad de proveedor.

La repetición exacta valida cada expediente y recompone la comparación HTML.
Las pruebas focalizadas rechazan alteraciones del HTML, del expediente 002 y
archivos extra en la raíz del paquete. La prueba de creación también evita
sobrescribir una carpeta existente. La CI de PR cubre la suite general.

**Límite:** ambos casos siguen preparados con fixtures y material de
invocadores propios. Se demuestra reutilización de las capacidades y de la
fachada para dos entradas fijas, no ingestión libre de documentos de una
empresa real, admisión operacional, parametrización general ni recomendación
entre proveedores. La vista comparativa describe resultados entre empresas
ficticias; no atribuye a una el precio o el riesgo de la otra.

## CERRAR → MATERIALIZAR → CI

Se cierra la demostración sintética de dos empresas con paquetes completos,
lectura conjunta y repetición verificable. La próxima frontera arquitectónica
requiere auditar la parametrización de las fuentes sintéticas y sus vínculos
antes de prometer entrada arbitraria. Una tercera fixture solo sería útil si
probase un comportamiento nuevo. No hay documentación empresarial real;
la ruta operacional permanece bloqueada. Este cierre no cambia productores,
reglas, QTG, admisión operacional ni binding QTG↔O1.

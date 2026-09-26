# EIOS — Auditoría de parametrización de fuentes sintéticas v0.1

## DISEÑAR

Determinar qué entrada admite ya un caso sintético adicional y qué datos
siguen declarados en los ejemplos 001 y 002. Esta auditoría no cambia las
reglas, el cargador, la fachada ni la ruta operacional. Se contrastaron los
dos runners, sus preparadores, el cargador y el adaptador existentes.

## AUDITAR — fronteras comprobadas

| Tramo | Parametrización actual | Dato que aún necesita declarar cada caso |
|---|---|---|
| Dataset `PROJECTION_ONLY` | `load_projection_mock_dataset(root)` acepta un directorio explícito con 13 componentes, manifiesto exacto y hashes. | Archivos internamente coherentes de una sola empresa, sus límites y `dataset_id`. |
| Bundle canónico | `build_projection_only_synthetic_material_bundle(dataset)` reutiliza el mismo adaptador. | Compra, contexto y evidencia semántica suficientes dentro del dataset. |
| Procedencia y QTG | La clasificación liga el bundle a un `reference_case_id`; QTG opera en `SYNTHETIC_TEST`. | ID nuevo, política de ejecución y consumo de prueba ligados al bundle. |
| PRICE y TCO | Los invocadores observados y modelos son reutilizables; TCO toma la compra. | Referencias, fechas, evidencias, método y juicio de representatividad de PRICE propios. |
| Riesgo del proveedor | Productor e invocador observados son reutilizables. | `company_scope`, estado y autoridad de evaluación, hechos y referencias propios; el 001 declara `FAVORABLE`, el 002 `NOT_DETERMINABLE`. |
| C0 | Regla R-DAT-003 y binding Assessment↔Trace son compartidos. | Requirement set, evidencia, clasificación, resultado base y trazas coherentes con compra/contexto. |
| Twin y escenarios | Preparación e invocadores son compartidos. | Política, variaciones y C0 de cada escenario hijo; trazas de la misma empresa. |
| NI y Ladder | Invocadores C0-bound son compartidos. | Autoridad y evidencia sintéticas, contenido y binding al C0 de esa ejecución. |
| Capturas y presentación | Validadores ligan las ocho observaciones al terminal; cada paquete se repite exactamente. | Contrato de inventario, identidad y lectura del nuevo caso; no bastaría renombrar el HTML del 001 o 002. |

El ejemplo 001 fija dos rutas de fixture y `COMPANY-MOCK-001`; el módulo de
material 002 fija otra ruta y declara valores adicionales para PRICE,
Supplier Risk/Value, C0, escenarios y negociación. Esos valores no se
derivan por completo de los 13 componentes. Un `--fixture-dir` añadido al
runner 001 o 002 no podría producir honestamente todos los invocadores.

## DEPURAR → AUDITAR 2

Hay comprobaciones positivas de separación: el adaptador rechaza una mezcla
de empresa en el snapshot financiero incluso con hashes actualizados; el
invocador de riesgo 002 rechaza una compra ajena; los sidecars se validan
contra el terminal de su misma ejecución. El paquete comparativo repite por
separado ambos casos. Estas defensas no equivalen a un contrato público para
fuentes auxiliares arbitrarias.

Un futuro perfil parametrizado tendría que declarar **explícitamente**:

1. Identidad única del caso y dataset validado, empresa, compra, contexto y
   referencias cruzadas; ninguna identidad heredada del ejemplo 001.
2. Material y autoridad sintética de cada invocador, incluidos juicios que
   requieren evidencia. La falta de hechos debe conservarse como ausencia
   o indeterminación, sin fabricar un `FAVORABLE` ni un `COMPRAR`.
3. Binding de C0 para raíz e hijos, fechas reproducibles y capturas cerradas
   contra una sola ejecución. QTG `APTO` no demuestra suficiencia C0.
4. Inventario exacto de salida, repetición y presentación de límites. Todo
   perfil seguiría en `SYNTHETIC / SYNTHETIC_TEST_ONLY / FORBIDDEN /
   NO_OPERATIONAL_EFFECT / false`.

No se introduce todavía un esquema de configuración ni una fábrica genérica:
solo hay dos declaraciones completas y difieren precisamente en juicios
semánticos. Generalizarlas sin una tercera necesidad concreta escondería
supuestos bajo campos opcionales o valores por defecto.

## CERRAR → MATERIALIZAR → CI

**Dictamen:** la frontera de dataset y bundle ya es reutilizable. La
parametrización E2E permanece limitada por las fuentes auxiliares y su
autoridad sintética explícita. La próxima implementación debe responder a
un caso adicional con una diferencia metodológica definida, o extraer un
preparador común solo si elimina duplicación demostrada sin relajar bindings.
Hasta entonces, se conservan los dos runners fijos y sus verificadores.
Esta unidad materializa únicamente el mapa auditado y se somete a CI de PR.

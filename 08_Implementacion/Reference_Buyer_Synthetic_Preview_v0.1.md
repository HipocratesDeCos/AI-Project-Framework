# EIOS — Demostración sintética de compras v0.1

## DISEÑAR → AUDITAR

Se materializa una vista de lectura local, separada de `reference-review.html`.
Parte de un directorio producido por `examples.reference_business_case_demo`.
La frontera y el inventario de autoridades están en
`Reference_Buyer_Synthetic_Preview_Boundary_Audit_v0.1.md`.

## DEPURAR → AUDITAR 2

Antes de proyectar datos, se ejecuta `verify_reference_demo`: valida ambas
variantes, ocho pares opcionales de capturas, bindings relacionados, HTML
técnico y repetición del fixture exacto. La vista escapa contenido dinámico,
mantiene un aviso sintético visible y carece de formularios, scripts, enlaces
y acciones. Muestra valores solo cuando están presentes; no calcula reglas,
ranking, precio objetivo ni decisiones de compra. Un paquete incompleto o
alterado impide la exportación.

## CERRAR → MATERIALIZAR

```powershell
cd C:\proyectos\AI-Project-Framework
python -m examples.reference_business_case_buyer_preview --demo-dir reference-demo-full --output reference-demo-full\reference-buyer-preview.html
Invoke-Item .\reference-demo-full\reference-buyer-preview.html
```

El comando no reemplaza un archivo existente. `reference-buyer-preview.html`
es una **demostración ficticia de lectura**, no la interfaz operacional que
usaría una empresa cliente. `APTO`, `COMPLETED`, `AUTHORIZED`, los importes y
el consolidado CRC se explican con sus límites de procedencia. La ruta sigue
`FORBIDDEN`, el efecto `NO_OPERATIONAL_EFFECT` y la autoridad decisional
`false`.

## Paquete integrado

También puede añadirse `--with-buyer-preview` a la generación del paquete
`examples.reference_business_case_demo --output-dir ...` junto a cualquier
combinación de las ocho opciones de observación. El archivo resultante se
incluye en el directorio publicado de forma atómica. Una ejecución posterior
de `--verify-dir` reconstruye la vista desde los artefactos verificados y
rechaza cualquier cambio en el HTML. El comando independiente anterior sirve
para paquetes ya generados sin la vista; en ese caso el mismo verificador la
reconoce a partir de entonces.

## Interpretación económica para compras

La tarjeta PRICE muestra el valor, la moneda, el número de referencias
seleccionadas y el método declarados por el productor. Explica que esa
referencia de transacciones ficticias no constituye precio objetivo, techo
autorizado ni oferta. La tarjeta TCO muestra el valor y los componentes
incluidos. Aunque el productor declare listas vacías de limitaciones o
componentes pendientes, la vista explica que el fixture no ha aportado otros
costes atribuibles: lo no informado no equivale a cero ni a un coste total
empresarial. Se presentan hechos ya capturados, sin recalcular importes.

## Interpretación de proveedor y C0/CRC

La tarjeta de proveedor expone dimensiones de riesgo declaradas por la
evaluación externa sintética, el recuento de fuentes factuales incluidas y si
existe comparación de valor. `RELIABILITY: FAVORABLE` es una declaración del
fixture: el recuento factual cero no permite deducir fiabilidad real ni elegir
proveedor. La tarjeta C0/CRC distingue la base sintética suministrada y el
consolidado obtenido, y mantiene al lado el QTG de cada variante. Una base o
un consolidado `COMPRAR` no es una orden de compra. No está demostrada una
derivación causal QTG → C0; las variantes `NO_APTO` y `APTO` no se tratan como
autorización operacional.

## Contexto de propuesta

La vista presenta una sola ficha de propuesta cuando ambas variantes del
fixture contienen exactamente la misma compra: artículo, proveedor, cantidad,
precio unitario de entrada y fecha ficticia. Rechaza una divergencia en vez de
atribuir silenciosamente una propuesta a ambas variantes. El precio propuesto
no se transforma en precio objetivo, importe total ni recomendación. Los
controles QTG conservan también el estado «no aplica» cuando corresponda.

## CI

`tests/test_reference_business_case_buyer_preview.py` verifica la vista
completa, el determinismo, ausencia de acciones, ausencia de capturas
opcionales y rechazo de paquetes alterados. Ejecutar la suite antes de
integración.

## Contexto descriptivo Decision Twin y Scenario Coordination

**DISEÑAR → AUDITAR:** las dos capturas ya verificadas contienen
representaciones, estados de viabilidad y diferencias, mientras la vista
mostraba solo nombres y cantidades. El contrato de Decision Twin prohíbe
deducir ranking o selección; O2 tampoco selecciona escenarios.

**DEPURAR → AUDITAR 2:** la vista proyecta los estados Stage 2 asociados a
cada representación, las diferencias y atributos faltantes declarados, y el
estado técnico y de viabilidad de cada escenario. La diferencia estructural
de `viability_result` incluye los `scenario_id` distintos; se explica que
no demuestra una diferencia empresarial. Los estados `VIABLE` no son una
evaluación económica real. Las pruebas comprueban estos textos sobre el
paquete completo y conservan la verificación exacta del HTML.

**CERRAR → MATERIALIZAR → CI:** solo cambia la proyección de lectura de
capturas ya validadas; no hay nueva ejecución, autoridad ni ruta operacional.

## Contexto descriptivo Negotiation Intelligence y Ladder

**DISEÑAR → AUDITAR:** las capturas NI contienen objetivo, solicitud inicial,
alternativa de espera, justificaciones y trazas. Ladder contiene pasos,
transiciones y rutas. La vista de compras mostraba solo el objetivo NI y el
número de pasos Ladder, pese a disponer de esos datos verificados.

**DEPURAR → AUDITAR 2:** se proyectan esos contenidos declarados y los tipos
de paso en su orden original, con escape HTML. El texto de negociación sigue
siendo ficticio. `AUTHORIZED` no implica mandato empresarial; la vinculación
a C0 no demuestra derivación causal del texto. La reconstrucción interna NI
de Ladder no prueba identidad con una invocación NI separada. Las pruebas
verifican contenido y límites en ambas variantes del paquete completo.

**CERRAR → MATERIALIZAR → CI:** se conserva la vista estática y sin acciones.
La unidad no cambia los sidecars, la ejecución ni la ruta `FORBIDDEN`.

## Lectura inicial y trazas desplegables

**DISEÑAR → AUDITAR:** el paquete completo ofrece dieciséis huellas de
observación y dos terminales; todas son necesarias para la trazabilidad,
pero su aparición continua dificulta leer primero el contraste QTG. El
material validado contiene ambos estados y permite un resumen sin cálculo.

**DEPURAR → AUDITAR 2:** se antepone una tarjeta por variante con QTG y
ejecución técnica, seguida de la propuesta común y el detalle existente.
Las huellas se conservan en elementos HTML `details` de lectura, cerrados por
defecto; no se eliminan del archivo ni se convierten en enlaces o acciones.
El aviso sintético permanece visible. Las pruebas comprueban el orden, ambas
tarjetas y la presencia de todas las huellas en el paquete completo.

**CERRAR → MATERIALIZAR → CI:** el HTML sigue siendo determinista y se
recompone en `--verify-dir`. No cambia el fixture ni se crea autoridad nueva.

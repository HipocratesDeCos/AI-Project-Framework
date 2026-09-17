# DIP-AGG-01 — Materialización acotada

Baseline: `9160eb976d19c3ccee6d19931321fe835eb466bc` (PR #157).
Contrato: `08_Implementacion/Decision_Input_Package_Aggregation_Contract_v0.1.md`.

## DISEÑAR
Módulo aislado `eios/core/decision_input_package.py`. Constructor con las entradas del contrato y un Centro existente. Sin integración en las fachadas MVP.
El carrier almacena únicamente bytes JSON canónicos inmutables; propiedades devuelven reconstrucciones independientes de los tipos existentes. Su fingerprint identifica contenido, no origen.
El constructor revalida y copia inputs antes de consultar el Centro. Comprueba configuración, alcance y vigencia antes de resolver; conserva ausencias explícitas y propaga errores. No evalúa calidad ni reglas.

## AUDITAR
Tres riesgos de implementación identificados: dataclasses Configuration carecen de validación runtime; Pydantic puede recibir modelos construidos sin validación; frozen superficial deja mutables los objetos anidados.
No basta con reutilizar estos objetos sin revalidación ni copia.

## DEPURAR
Revalidación de contenido Pydantic; comprobación de tipos físicos de Configuration y ResolvedConfiguration; almacenaje inmutable sin referencias a inputs ni al Centro. Serialización cubre todos los campos declarados. Ninguna normalización temporal/económica nueva.

## AUDITAR 2
El plan depurado cubre alcance contextual, IDs duplicados, partición presentes/ausentes, propagación de fallos y reproducibilidad. No introduce un tipo empresarial genérico, política ni autoridad nueva. SUPERADA para el plan acotado.

## CERRAR
Plan de materialización técnica cerrado. Su implementación y CI se comprobarán posteriormente; no se declara provenance end-to-end ni productor QTG.

## MATERIALIZAR / auditoría del delta
Materializado un módulo aislado, su suite de aceptación y este registro. El carrier conserva bytes canónicos inmutables; propiedades y to_payload devuelven reconstrucciones independientes.
Revisión contra el contrato: claves canónicas exactas, todos los campos Configuration/ResolvedConfiguration incluidos, misma semántica temporal del resolver, sin cambio de firmas MVP ni importación desde las fachadas.
No se acepta configuración pre-resuelta ni resultados/callbacks QTG. No se suministra constructor de importación/deserialización externo. Esta restricción no convierte el tipo en certificado de origen ni barrera criptográfica.
Resultado: sin desviaciones identificadas en el alcance seleccionado; sin cambios en código cerrado de otros componentes.

## Verificación y CI
PR #157 integrada en el baseline indicado; CI preintegración #824 y postintegración #825 SUCCESS.
Suite local final: 966 pruebas aprobadas, incluidas 39 pruebas nuevas. Los avisos restantes pertenecen a tests existentes.
Las pruebas nuevas cubren captura y reconstrucción, partition presentes/ausentes, configuraciones de otro ámbito, errores temporales, revalidación de modelos/dataclasses, fallos de repositorio, binding de resolución, sensibilidad del fingerprint y mutaciones durante/después de las lecturas.
CI Python + SQL del nuevo delta pendiente sobre el HEAD exacto de su PR. No se declara cierre integrado hasta verificar CI pre y postmerge.

## Continuidad
QTG mantiene su cuarentena: el agregado de entradas seleccionadas no demuestra un productor de controles autorizados ni su criticidad/aplicabilidad.
Una unidad posterior deberá diseñar ese productor para el alcance realmente representado. Tampoco quedan resueltos autenticidad ERP, lectura multi-parámetro atómica o binding empresarial individual de Evidence.

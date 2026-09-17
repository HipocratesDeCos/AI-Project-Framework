# EIOS — DIP-READINESS-01
Fecha: 17/09/2026
Estado: análisis documental completado; contrato físico DIP aún no cerrado.
Baseline operativo auditado: main @ 584617ee28971020a3e433c22c07b6a50ac5b279.
Alcance: continuidad y requisitos previos al diseño físico del Decision Input Package. No constituye autoridad funcional ni contrato de implementación.

## DISEÑAR
Pregunta: ¿qué unidad precede legítimamente al productor QTG?
Resultado: contrato de agregación del Decision Input Package, conforme a DSS_Functional_Architecture.md §7 y Quality_Trust_Implementation_Contract.md §4.
Entregable de esta unidad: inventario verificable y delimitación del diseño siguiente. No se crea un paquete nominal para fingir procedencia.

## Reconciliación
- PR #115 está merged; merge 2909528a7473e048296632937b6aedb436833763.
- main actual: PR #156; CI postintegración #821 SUCCESS sobre el SHA operativo auditado.
- La comparación GitHub desde el baseline recibido informa ahead_by=298, behind_by=0. La colección de commits del endpoint puede estar truncada; no se presenta como inventario exhaustivo.
- BL-004 conserva su SHA histórico d3c462a2536ee20204b9d5c9dce1024e1ca7d31c; no equivale al HEAD operativo.
- PR #142 retira quality_invoker del Vertical MVP; el dominio QTG permanece cerrado.
- PR #144 pone en cuarentena Stage 2 público y el wrapper Decision Twin dependiente. Se preservan VF y Decision Twin core; no se reabren sus motores.
- Finance horizon provenance y R-HIS-002 PRICE provenance tienen materialización posterior, recogida por Project_Context v2.5.
- PR #73 MGE continúa abierta: una continuación genérica no aprueba su política.

## Inventario físico y límites
| Pieza | Fuente física | Qué demuestra | Qué no demuestra |
|---|---|---|---|
| Propuesta | eios/core/models.py: PurchaseOperation / InputContract | Payload C0 tipado | Datos comerciales y financieros completos de Pantalla 1 |
| Identidad | eios/core/models.py: DecisionContext | Cinco identificadores/versiones de ejecución | Empresa, permisos o procedencia de cada dato |
| Evidencia | eios/core/models.py: Evidence | Referencias y estado contractual | Pertenencia automática a compra, empresa o snapshot |
| Parametrización | eios/parameters/resolution.py: ResolvedConfiguration | Configuración individual, vigencia y versión contextual | Inventario global autorizado ni procedencia acreditada solo por construcción manual |
| Datos empresariales | Modelos especializados de eios/stock/ y eios/finance/ | Contratos propios de dominio | Carrier empresarial agregado universal |
| Evaluación QTG | eios/quality/gate.py | Precedencia normativa sobre QualityCheck suministrados | Productor de controles desde un DIP ni verificación agregada de procedencia |
| Envolvente legacy | eios/core/models.py: PurchaseEvaluation | Transporte Sprint 1 de context/purchase/quality/evidence | DIP actual: usa QualityStatus y EvidenceRef legacy, sin datos empresariales ni configuración agregada |
| Trace C0 | eios/core/models.py y eios/core/c0.py | Trazabilidad de evaluación de reglas | Identidad o fingerprint de un DIP previo a QTG |

## AUDITAR
Fuentes contrastadas: Matriz_Autoridad_Documental.md, Project_Governance.md, Project_Context.md v2.5, BL-004, DSS_Functional_Architecture.md §6–8, contrato QTG v0.4, contrato de cuarentena QTG y modelos físicos anteriores.
Hallazgos:
1. La agregación está autorizada funcionalmente; su ausencia física no prohíbe diseñarla.
2. InputContract es alias de PurchaseOperation; no existe un segundo payload canónico que deba inventarse.
3. Ni data_snapshot_id ni una referencia ni un fingerprint aislado prueban origen.
4. No puede inferirse un productor QTG seguro de PurchaseEvaluation legacy o de un callable genérico.
5. Diseñar un carrier y diseñar los controles aplicables/criticidad son unidades distintas.

## DEPURAR
El diseño siguiente debe delimitar:
- subconjunto explícito de datos empresariales con autoridad especializada y productor demostrable;
- composición y preservación de los contratos existentes, sin redefinirlos;
- vinculación verificable de compra/contexto, empresa cuando corresponda, snapshot, evidencia y configuraciones;
- identidad, versionado y material reproducible del agregado, sin un segundo sistema de Decision Versioning;
- representación de ausencia, incertidumbre y contradicciones;
- validación de procedencia frente a mismatches y mutación/desprendimiento;
- consumidores previstos y pruebas de aceptación del agregado.
Estos puntos son preguntas de contrato pendientes, no nuevas reglas ni soluciones físicas aprobadas.
No se atribuye criticidad universal a un campo ni se inventan política temporal, defaults, scores o criterios económicos.

## AUDITAR 2
Segunda comprobación del resultado depurado:
- el inventario distingue referencias/identidad de procedencia;
- preserva contratos C0, evidencia, parámetros y motores cerrados;
- registra las cuarentenas posteriores al baseline recibido;
- no confunde cierre del diagnóstico con cierre DIP/QTG;
- deja el diseño físico abierto sin convertir falta de detalle en prohibición de diseñar.
Resultado: sin contradicción identificada en este análisis acotado. No es una auditoría exhaustiva de todos los dominios EIOS.

## CERRAR
Se cierra únicamente DIP-READINESS-01 como análisis de continuidad.
Siguiente unidad: propuesta de contrato físico de agregación DIP para un alcance explícito, sometida al ciclo completo antes de implementar.
QTG permanece bloqueado para integración positiva; el contrato DIP aún no se declara cerrado.

## MATERIALIZAR
Un único archivo en 07_Pruebas. Sin modificación de fuentes canónicas, código ejecutable, reglas, parámetros, SQL o APIs.
La integración de este archivo no autoriza por sí sola la implementación del contrato DIP ni el productor QTG.

## CI
CI de referencia: #821 SUCCESS sobre 584617ee28971020a3e433c22c07b6a50ac5b279.
La CI de esta materialización debe verificarse sobre el HEAD exacto de su PR; #821 no valida el nuevo delta.

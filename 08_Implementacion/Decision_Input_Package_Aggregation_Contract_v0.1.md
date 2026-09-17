# EIOS — Decision Input Package — Aggregation Contract v0.1
Unidad: DIP-AGG-01
Fecha: 17/09/2026
Estado: diseño técnico auditado; materialización documental; implementación ejecutable pendiente.
Baseline: main @ 584617ee28971020a3e433c22c07b6a50ac5b279.

## 1. Autoridad y alcance
DSS_Functional_Architecture.md §7 autoriza agregar propuesta, evidencia, datos empresariales y parametrización vigente. Quality_Trust_Implementation_Contract.md §4 consume esa representación; no determina su estructura física.
Este contrato concreta únicamente una primera agregación seleccionada. Respeta Matriz_Autoridad_Documental.md, Project_Governance.md, Evidence_Contract.md, Centro_Parametrizacion.md y contratos especializados.
No redefine datos C0, semántica financiera, parámetros, reglas, Decision Versioning ni QTG.
No representa todos los datos de Pantalla 1 ni el Vertical MVP completo.

## 2. Subconjunto físico
| Componente del agregado | Tipo existente / contenido | Presencia |
|---|---|---|
| Propuesta | PurchaseOperation / InputContract | Obligatoria |
| Contexto | DecisionContext completo | Obligatoria |
| Evidencia presentada | tuple[Evidence, ...] | Explícita; vacía significa no presentada |
| Datos empresariales disponibles | FinancialSnapshot | Opcional; None conserva ausencia |
| Empresa de selección | company_id | Obligatoria, no vacía |
| Instante de resolución | effective_at: datetime | Obligatorio |
| Parámetros solicitados | tuple[str, ...] de IDs explícitos | Obligatoria, puede estar vacía |
| Configuraciones disponibles | tuple[ResolvedConfiguration, ...] | Derivada del Centro |
| Parámetros sin configuración | tuple[str, ...] | Derivada; nunca rellenada con defaults |
| Versión física | schema_version = DIP-AGG-01/v0.1 | Obligatoria |
| Identidad del contenido | fingerprint SHA-256 | Derivada; no acredita origen |

FinancialSnapshot se selecciona por disponer ya de empresa, fecha, snapshot, moneda y referencias explícitas. No se incorpora FinanceBasicResult: un resultado analítico no es dato previo al gate.
No se añade un diccionario empresarial arbitrario ni se convierten coverage_days, score proveedor o datos comerciales en métricas nuevas.
Otros dominios requerirán extensión explícita del contrato con sus propias autoridades.

## 3. Constructor previsto
build_decision_input_package recibe propuesta, contexto, evidencia, snapshot financiero opcional, empresa, instante, IDs seleccionados y ParameterConfigurationCenter.
No acepta configuraciones resueltas suministradas como sustituto de la lectura del Centro; tampoco resultados QTG ni callbacks de controles.
Para cada ID usa get_configuration_at(company_id, parameter_id, effective_at) y resolve_configuration_for_context(...).
Una configuración ausente se registra como ausencia. Un ID desconocido o un fallo del Centro propaga el error; no se interpreta como ausencia.
El Centro conserva sus puertos existentes. Pasar una instancia o un repositorio a esos puertos no acredita por sí solo autenticidad de persistencia ni autorización de lectura. El constructor no implementa autenticación, enumeración empresarial ni descubrimiento global.
No se afirma consistencia transaccional multi-parámetro: el Centro actual resuelve individualmente. Si el uso exige un snapshot atómico de configuración, falta ese contrato/productor y debe bloquearse ese uso.
La versión contextual se conserva como binding existente; no se inventa una versión de repositorio ni se convierte la coincidencia de versión en prueba de lectura histórica.

## 4. Validaciones estructurales
Antes de construir:
1. Revalidar modelos desde su contenido, además de verificar tipos: model_construct/model_copy(update=...) pueden omitir validadores.
2. decision_id y scenario_id de la propuesta deben coincidir con contexto.
3. IDs de evidencia y parámetros solicitados no pueden duplicarse. Los conflictos no se colapsan por último valor.
4. Cada configuración disponible conserva todos sus campos; parameter_id solicitado, empresa, versión contextual y effective_at deben coincidir exactamente con la selección.
5. Resolver/revalidar vigencia con el contrato existente; incompatibilidad temporal produce error técnico.
6. IDs disponibles y ausentes son disjuntos y su unión coincide exactamente con los IDs solicitados.
7. Si hay FinancialSnapshot: empresa = company_scope y data_snapshot_id = contexto.data_snapshot_id.
No se obliga a as_of_date = operation_date ni a as_of_date = effective_at.date(): no existe aquí autoridad para imponer esa ventana. Se conservan las tres fechas. La aplicabilidad temporal posterior queda pendiente de su fuente especializada.
No se impone que toda source_ref financiera sea evidence_id C0: esos espacios de referencia no están declarados equivalentes.
No se asigna origen empresarial a Evidence por mera inclusión en el paquete: Evidence no transporta ese binding.
No se transforman fallos técnicos en NO_APTO, NOT_EVALUABLE o resultado de regla.

## 5. Congelación y reproducibilidad
El paquete conserva un snapshot profundo del contenido capturado; mutar los argumentos originales o copias entregadas a consumidores no altera el material almacenado.
frozen=True superficial no satisface esta garantía: los modelos anidados y contenedores requieren protección efectiva.
La implementación podrá almacenar material canónico inmutable y devolver copias revalidadas. No expondrá referencias mutables internas.
El fingerprint cubre versión física, propuesta, los cinco campos del contexto, toda evidencia, snapshot opcional, selección empresarial/temporal, IDs solicitados, configuraciones completas y ausencias.
Canonización: JSON UTF-8, ensure_ascii=False, claves ordenadas, separadores compactos; Decimal mediante format(value, "f"), fechas/datetimes mediante isoformat; None se conserva. Colecciones conservan orden suministrado y de selección. No hay equivalencia por reordenación implícita.
Sin timestamp de construcción ni UUID aleatorio en el material identificado.
Mismo contenido canónico produce mismo fingerprint; modificar cualquier contenido material debe modificarlo.
Fingerprint significa identidad del contenido capturado; no firma, cadena de custodia ni prueba de origen.
No modifica fingerprints/Trace C0. No crea una versión de decisión: schema_version identifica únicamente la representación técnica.

## 6. Ausencia, evidencia y contradicciones
El paquete conserva Evidence GAP/DEMONSTRATED y referencias sin elevarlas a evidencia válida para una regla.
No ejecuta validate_evidence ni genera EvidenceValidation como juicio agregado.
None, evidencia vacía y parámetros sin configuración permanecen explícitos.
Una contradicción documental o económica se conserva en sus entradas; no se resuelve por prioridad, promedio o score.
IDs duplicados hacen ambigua la representación y se rechazan técnicamente; no se interpretan como resolución de una contradicción de negocio.
El agregado no decide completitud suficiente para continuar: ese juicio corresponde a QTG conforme a controles aplicables autorizados.

## 7. Consumidores y garantías
Primera materialización: módulo separado de agregación y tests del contrato. No cambia run_mvp_execution, run_vertical_mvp_support ni firmas de motores cerrados.
No exporta un quality_invoker ni un QTG_COMPLETED.
Este carrier podrá servir como entrada a un futuro productor QTG, después de diseñar controles observables, aplicabilidad, criticidad y binding verificable a la compra/contexto.
La existencia del carrier no levanta automáticamente la cuarentena QTG.
Stage 2/VF y el wrapper Decision Twin dependiente conservan sus cuarentenas.

## 8. Aceptación ejecutable pendiente
Pruebas exigidas antes de declarar materialización física:
- agregación válida y reconstrucción de contenido;
- mismatches propuesta/contexto y snapshot/empresa/contexto;
- configuraciones de empresa, parámetro, versión, instante o vigencia incorrectos;
- IDs duplicados, partición exacta disponibles/ausentes y parámetro desconocido;
- propagación visible de fallos del Centro;
- revalidación de modelos construidos sin validación;
- conservación de GAP, None, fechas distintas y referencias de espacios diferentes;
- mutación posterior del input o copias sin alterar paquete/fingerprint;
- fingerprint estable y sensible a cada familia material;
- configuración obtenida mediante el Centro, sin passthrough alternativo;
- ninguna ejecución QTG ni cambio de APIs existentes.
Suite completa Python y CI SQL deben pasar sobre el HEAD de implementación.

## 9. Gate
El diseño técnico de agregación puede pasar a una unidad de implementación acotada después de integrar y verificar este contrato.
No se declara DIP end-to-end provenance-safe ni productor QTG materializado.
Si la implementación necesita un nuevo dato, política o productor no descrito, se detiene esa ampliación y vuelve a diseño.

## 10. Depuración incorporada tras Audit 1
A1. Los IDs seleccionados y company_id deben ser strings no vacíos, sin espacios periféricos. No se normaliza casing ni se acepta un ID alterado silenciosamente. La selección vacía queda registrada y no demuestra completitud global.
A2. Configuraciones se serializan por todos los campos de Configuration y por parameters_version/effective_at de ResolvedConfiguration. No se incluyen objetos Centro, puertos, funciones o validadores en el fingerprint.
A3. Payload canónico con claves exactas: schema_version, purchase, context, evidence, financial_snapshot, company_id, effective_at, requested_parameter_ids, configurations, missing_parameter_ids. configurations sigue el orden de requested_parameter_ids filtrado a presentes; missing_parameter_ids sigue el mismo orden filtrado a ausentes.
A4. Monedas, fechas y espacios de referencia distintos se preservan. La agregación no declara comparabilidad, conversión monetaria ni frescura por mera coexistencia.
A5. Snapshot profundo de inputs antes de lecturas externas; revalidación del resultado del Centro antes de congelarlo. Esto evita mutaciones de argumentos durante la construcción, pero no crea atomicidad empresarial/configuración entre fuentes.
A6. Comparaciones de datetime usan la compatibilidad y semántica del contrato de resolución existente; canonización preserva isoformat y su offset sin normalizarlo. Dos representaciones con offset diferente pueden tener fingerprints diferentes aunque representen el mismo instante; el contrato identifica contenido, no equivalencia temporal universal.

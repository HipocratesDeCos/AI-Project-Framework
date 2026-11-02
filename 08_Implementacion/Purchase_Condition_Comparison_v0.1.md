# Comparación explícita de condiciones de compra v0.1

Base revisada: ac6a502ea918855b809a91cd96c0dda09695524e.

## Alcance y almacenamiento

Comparación solicitada por una persona, disponible con o sin déficit, para una propuesta sintética guardada y su mismo contexto documental. Conserva artículo, proveedor, cantidad y moneda. Permite variantes de precio, descuentos y calendario. Reutiliza commercial_terms, payment_plan y purchase_cash_preview sin ampliar sus autoridades. No hay ganadora automática ni nuevas reglas o parámetros empresariales.

La tabla independiente purchase_condition_comparison conserva identificador, dataset, propuesta, fecha y payload. Cada estudio nuevo se inserta; la propuesta y estudios previos no se actualizan. El payload incluye original reconstruido, alternativas completas, parámetros activados, contexto documental, huella financiera, versión de cálculo, responsable y huella del resultado. Las propuestas antiguas no se migran a evidencias nuevas.

POST /api/purchases/comparisons calcula y conserva; POST /api/purchases/comparisons/read recupera históricos y marca desactualización por contexto o activación financiera. La interfaz de revisión de propuestas permite precio, descuento porcentual, vencimiento y calendario completo de cuotas. El backend admite de una a diez alternativas por estudio. La pantalla añade una por estudio.

## Condiciones y evidencia

Cada campo modificado requiere origen DOCUMENTED, HYPOTHETICAL o UNCONFIRMED. DOCUMENTED exige referencia. La aceptación se mantiene separada: PENDING o DECLARED_ACCEPTED; esta última exige origen documental y referencia propia. Todas son declaraciones no verificadas: DECLARED_UNVERIFIED. No existe promoción a aceptación acreditada. La vigencia declarada se registra y se marca caducada respecto al día UTC del cálculo; no acredita disponibilidad comercial. Los campos heredados del original se conservan sin atribuirles evidencia nueva. El origen por campo y estos estados pertenecen al registro local; no sustituyen la taxonomía canónica de NI.

## Comparabilidad y persistencia

Mismo corte, horizonte, fuente financiera y activación para todas las alternativas calculables. Vencimientos fuera del horizonte o condiciones incoherentes quedan pendientes y sin ahorro computado. Los pendientes no se eliminan del informe ni se presentan favorables. No se inventan descuentos ni aceptación; cuotas e IVA se validan con los contratos existentes. Al guardar, BEGIN IMMEDIATE protege la comprobación final del contexto documental y de la activación frente a los utilizados en el cálculo. Una variación intermedia exige recalcular.

Se informa total con IVA y portes declarados, diferencia monetaria respecto al original (no ahorro económico completo), pagos, saldo mínimo, fecha y falta para la reserva. Las compensaciones de cierre diario, incertidumbre de cobros y completitud documental siguen siendo límites del motor existente. Una oferta caducada conserva un cálculo hipotético, no una opción disponible.

## Auditoría de implementación

- La simulación no se limita al déficit; se invoca explícitamente para el original y cada alternativa.
- No se cambia cantidad, proveedor, moneda, reglas, límites ni parámetros desde alternativas.
- Una huella identifica contenido, no veracidad ni aceptación.
- La aceptación acreditada por un proceso documental queda fuera de esta versión: solo declaración pendiente de verificar.
- Se conserva SYNTHETIC, decision_authority=false, operational_path=FORBIDDEN y viability_status=NOT_EVALUATED.
- La revisión es de código y pruebas automatizadas; no certifica operación real ni verificación visual en navegador.

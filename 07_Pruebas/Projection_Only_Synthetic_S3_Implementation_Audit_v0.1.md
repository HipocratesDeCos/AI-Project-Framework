# EIOS — PROJECTION_ONLY Synthetic S3 Implementation Audit v0.1

**Estado:** CERRADO TÉCNICAMENTE — CI PENDIENTE

**Baseline:** `main @ 30a5a7fea3b5786858e378d27a43b2758c460185`

**Unidad:** S3 — captura documental, calendario de cuotas y cobertura estructural.

## DISEÑAR

Se extiende exclusivamente la frontera privada del adaptador sintético. S1–S2 permanecen intactos y reutilizables mediante `_build_synthetic_foundation()`. La nueva etapa `_build_synthetic_stage3()` consume el mismo `ProjectionMockDataset` validado y construye, por las factorías EIOS ya cerradas:

1. `DocumentaryMaterial[]` y `DocumentaryPaymentBinding[]`;
2. `DocumentaryPaymentCapture`;
3. `RequiredInstallmentCalendar`;
4. `RequiredInstallmentCoverage` recomputada.

La etapa no interpreta documentos, no descubre cuotas, no corrige discrepancias y no ejecuta Finance, Quality Gate ni QTG. La salida continúa siendo privada; `__all__` permanece vacío.

## AUDITAR

**A1 — base64 válido pero no canónico.** Una codificación puede ser aceptada por el decodificador y producir los mismos bytes con bits de relleno alternativos. Se exige igualdad exacta `base64.b64encode(decoded) == supplied` además de `validate=True`.

**A2 — doble integridad.** El hash SHA-256 del archivo de componente ya queda protegido por `ProjectionMockDataset`; S3 verifica además que el SHA-256 declarado dentro de cada documento coincide con los bytes base64 decodificados. Ninguna capa sustituye a la otra.

**A3 — duplicación de lógica.** S3 no replica reglas de captura ni cobertura. Los duplicados, referencias, PAYMENT, secuencia, suma, divisa, fechas y pertenencia permanecen bajo `build_documentary_payment_capture()` y `check_required_installment_coverage()`.

**A4 — discrepancia no equivale a error técnico.** Mismatch de importe, referencia o soporte debe materializarse como cobertura estructural negativa, no abortar la traducción. Las pruebas conservan `AMOUNT_MISMATCH` y `reference_mismatches`.

**A5 — responsabilidad implícita.** Se eliminó `external_review_ref` del schema físico S3 porque el contrato del componente no lo autoriza. La factoría recibe `None`; la revisión pertenece a otras cadenas, no a este input.

**A6 — promoción operacional.** Ambos componentes S3 aceptan únicamente `case_kind=SYNTHETIC`. `PRESENTED_OPERATIONAL` se rechaza en schema antes de construir dominio.

**A7 — parcialidad pública.** `_SyntheticStage3` es un agregado interno e inmutable. No se exporta, no crea bundle final y no puede consumirse como resultado QTG.

## DEPURAR

Se mantienen fuera de alcance:

- OCR, parsing semántico o autenticación documental;
- inferencia de referencias, cuotas, importes, fechas o divisas;
- defaults y coerciones;
- revisión humana o designación documental;
- modificación de `DOC-PAY-CAP-01` o `DOC-PAY-COVER-01`;
- ejecución de Finance Basic, Quality Gate, productor/consumidor QTG;
- salida pública parcial.

El schema de `payment_documents` queda limitado a naturaleza sintética, referencias de operación/pedido/confirmación, documentos base64+SHA-256 y bindings. El calendario conserva declaración, autoridad sintética, referencias, total y cuotas con locators.

## AUDITAR 2

El delta contra el baseline modifica únicamente:

- `eios/core/_projection_synthetic_foundation.py`;
- `tests/test_projection_synthetic_foundation.py`;
- este registro de auditoría.

La revisión del delta confirma:

- base64 estándar estricto y representación canónica exacta;
- SHA-256 interno recomputado antes de crear `DocumentaryMaterial`;
- tipos internos `extra=forbid`, `strict=True`, `frozen=True`;
- fechas de cuotas convertidas por parser ISO canónico;
- importes convertidos desde cadenas decimales finitas;
- captura y cobertura construidas únicamente por factorías cerradas;
- conflictos estructurales preservados como material observable;
- S1–S2 sin cambio funcional;
- ausencia de salida pública y de ejecución analítica/QTG.

La verificación ejecutable queda sometida a CI exact-head. No se declara resultado de pruebas antes de que GitHub Actions lo confirme.

## CERRAR → MATERIALIZAR → CI

S3 queda cerrada técnicamente dentro del alcance anterior y materializada en rama aislada. La integración exige:

1. PR contra el baseline exacto;
2. CI completa satisfactoria;
3. comprobación de no avance incompatible de `main`;
4. merge protegido;
5. CI post-merge satisfactoria.

Solo después podrá abrirse S4 — criterios presentados, manifiesto autorizado sintético y `FinanceQualityPreparation`. QTG continúa deshabilitado.

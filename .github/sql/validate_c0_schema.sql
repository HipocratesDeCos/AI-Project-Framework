/*
EIOS — SQL Server C0 schema validation
Scope: structural and invariant validation of 001_C0_Schema.sql
This script runs only against an ephemeral CI database.
*/

SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @failures int = 0;

/* V1 — expected tables */
DECLARE @expected_tables TABLE (table_name sysname PRIMARY KEY);
INSERT INTO @expected_tables (table_name)
VALUES
    (N'c0_input'),
    (N'c0_context'),
    (N'c0_evidence'),
    (N'c0_evidence_validation'),
    (N'c0_rule_contract'),
    (N'c0_assessment'),
    (N'c0_assessment_evidence'),
    (N'c0_trace'),
    (N'c0_trace_evidence');

IF EXISTS
(
    SELECT 1
    FROM @expected_tables e
    WHERE OBJECT_ID(N'eios.' + e.table_name, N'U') IS NULL
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V1: expected C0 table is missing';
END;

IF (SELECT COUNT(*) FROM sys.tables WHERE schema_id = SCHEMA_ID(N'eios')) <> 9
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V1: unexpected table count in schema eios';
END;

/* V2 — expected indexes */
DECLARE @expected_indexes TABLE (index_name sysname, table_name sysname, PRIMARY KEY (index_name, table_name));
INSERT INTO @expected_indexes (index_name, table_name)
VALUES
    (N'IX_c0_input_decision_scenario', N'c0_input'),
    (N'IX_c0_context_decision_scenario_versions', N'c0_context'),
    (N'IX_c0_assessment_rule_status', N'c0_assessment'),
    (N'IX_c0_trace_decision_scenario_created', N'c0_trace');

IF EXISTS
(
    SELECT 1
    FROM @expected_indexes e
    WHERE NOT EXISTS
    (
        SELECT 1
        FROM sys.indexes i
        WHERE i.name = e.index_name
          AND i.object_id = OBJECT_ID(N'eios.' + e.table_name)
    )
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V2: expected index is missing';
END;

/* V3 — expected foreign keys */
DECLARE @expected_fks TABLE (fk_name sysname PRIMARY KEY);
INSERT INTO @expected_fks (fk_name)
VALUES
    (N'FK_c0_evidence_validation_evidence'),
    (N'FK_c0_assessment_evidence_assessment'),
    (N'FK_c0_assessment_evidence_evidence'),
    (N'FK_c0_trace_evidence_trace'),
    (N'FK_c0_trace_evidence_evidence');

IF EXISTS
(
    SELECT 1
    FROM @expected_fks e
    WHERE NOT EXISTS (SELECT 1 FROM sys.foreign_keys fk WHERE fk.name = e.fk_name)
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V3: expected foreign key is missing';
END;

/* V4 — expected CHECK constraints */
DECLARE @expected_checks TABLE (constraint_name sysname PRIMARY KEY);
INSERT INTO @expected_checks (constraint_name)
VALUES
    (N'CK_c0_input_quantity'),
    (N'CK_c0_input_unit_price'),
    (N'CK_c0_input_currency'),
    (N'CK_c0_input_identifiers_nonempty'),
    (N'CK_c0_input_fingerprint'),
    (N'CK_c0_context_nonempty'),
    (N'CK_c0_evidence_state'),
    (N'CK_c0_evidence_nonempty'),
    (N'CK_c0_evidence_demonstration'),
    (N'CK_c0_evidence_validation_status'),
    (N'CK_c0_evidence_validation_nonempty'),
    (N'CK_c0_rule_contract_nonempty'),
    (N'CK_c0_assessment_status'),
    (N'CK_c0_assessment_status_outcome'),
    (N'CK_c0_assessment_nonempty'),
    (N'CK_c0_assessment_evidence_ordinal'),
    (N'CK_c0_assessment_evidence_id_nonempty'),
    (N'CK_c0_trace_status'),
    (N'CK_c0_trace_status_outcome'),
    (N'CK_c0_trace_nonempty'),
    (N'CK_c0_trace_fingerprint'),
    (N'CK_c0_trace_evidence_ordinal'),
    (N'CK_c0_trace_evidence_id_nonempty');

IF EXISTS
(
    SELECT 1
    FROM @expected_checks e
    WHERE NOT EXISTS (SELECT 1 FROM sys.check_constraints c WHERE c.name = e.constraint_name)
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V4: expected CHECK constraint is missing';
END;

/* V5 — valid rows must be accepted */
BEGIN TRY
    BEGIN TRANSACTION;

    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES
        (N'DEC-0001', N'SCN-0001', N'ART-001', N'PROV-001', 100.0000, 12.5000, 'EUR', '2026-08-21', REPLICATE('A', 64));

    INSERT INTO eios.c0_context
        (decision_id, scenario_id, rules_version, parameters_version, data_snapshot_id)
    VALUES
        (N'DEC-0001', N'SCN-0001', N'R-1', N'P-1', N'DS-1');

    INSERT INTO eios.c0_evidence
        (evidence_id, source_type, source_ref, captured_at, state, demonstration_ref)
    VALUES
        (N'E-001', N'ERP', N'purchase-history/001', '2026-08-21', 'DEMONSTRATED', N'ERP:purchase-history/001'),
        (N'E-GAP-001', N'ERP', N'purchase-history/missing', '2026-08-21', 'GAP', NULL);

    INSERT INTO eios.c0_evidence_validation (evidence_id, status, reason)
    VALUES (N'E-001', 'VALID', N'Evidencia demostrada y trazable');

    INSERT INTO eios.c0_rule_contract (rule_id, version, requires_evidence)
    VALUES (N'R-PRICE-001', N'R-1', 1);

    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-PRICE-001', 'EVALUABLE', 1, N'Validación positiva');

    INSERT INTO eios.c0_assessment_evidence (assessment_row_id, evidence_ordinal, evidence_id)
    VALUES (1, 0, N'E-001');

    INSERT INTO eios.c0_trace
        (trace_id, decision_id, scenario_id, rules_version, parameters_version, data_snapshot_id, input_fingerprint, rule_id, assessment_status, assessment_outcome, created_at)
    VALUES
        (N'TRACE-0001', N'DEC-0001', N'SCN-0001', N'R-1', N'P-1', N'DS-1', REPLICATE('A', 64), N'R-PRICE-001', 'EVALUABLE', 1, '2026-08-21T10:00:00+00:00');

    INSERT INTO eios.c0_trace_evidence (trace_id, evidence_ordinal, evidence_id)
    VALUES (N'TRACE-0001', 0, N'E-001');

    ROLLBACK TRANSACTION;
END TRY
BEGIN CATCH
    IF XACT_STATE() <> 0 ROLLBACK TRANSACTION;
    SET @failures += 1;
    PRINT 'FAIL V5: valid C0 rows were rejected';
END CATCH;

/* V6 — invalid states must be rejected */
DECLARE @case_failed bit;

/* Empty contractual identifiers */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'', N'SCN-0001', N'ART-001', N'PROV-001', 1.0000, 1.0000, 'EUR', '2026-08-21', REPLICATE('A', 64));
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.1: empty identifier accepted'; END;

/* Invalid quantity */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'DEC-X', N'SCN-X', N'ART-X', N'PROV-X', 0.0000, 1.0000, 'EUR', '2026-08-21', REPLICATE('B', 64));
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.2: non-positive quantity accepted'; END;

/* Invalid currency */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'DEC-Y', N'SCN-Y', N'ART-Y', N'PROV-Y', 1.0000, 1.0000, 'USD', '2026-08-21', REPLICATE('C', 64));
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.3: non-EUR currency accepted'; END;

/* Invalid fingerprint */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'DEC-Z', N'SCN-Z', N'ART-Z', N'PROV-Z', 1.0000, 1.0000, 'EUR', '2026-08-21', REPLICATE('D', 63) + 'G');
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.4: invalid fingerprint accepted'; END;

/* Demonstrated evidence without reference */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_evidence
        (evidence_id, source_type, source_ref, captured_at, state, demonstration_ref)
    VALUES (N'E-BAD-1', N'ERP', N'ref', '2026-08-21', 'DEMONSTRATED', NULL);
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.5: demonstrated evidence without reference accepted'; END;

/* EVALUABLE without outcome */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-BAD-1', 'EVALUABLE', NULL, N'bad');
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.6: EVALUABLE without outcome accepted'; END;

/* NOT_EVALUABLE with outcome */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-BAD-2', 'NOT_EVALUABLE', 0, N'bad');
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.7: NOT_EVALUABLE with outcome accepted'; END;

/* Negative evidence ordinal */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-BAD-3', 'EVALUABLE', 1, N'bad');
    DECLARE @bad_assessment_id bigint = SCOPE_IDENTITY();
    INSERT INTO eios.c0_assessment_evidence (assessment_row_id, evidence_ordinal, evidence_id)
    VALUES (@bad_assessment_id, -1, N'E-001');
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.8: negative evidence ordinal accepted'; END;

/* FK violation */
SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_evidence_validation (evidence_id, status, reason)
    VALUES (N'E-NOT-FOUND', 'VALID', N'bad');
END TRY
BEGIN CATCH
    SET @case_failed = 1;
END CATCH;
IF @case_failed = 0
BEGIN SET @failures += 1; PRINT 'FAIL V6.9: FK violation accepted'; END;

IF @failures <> 0
BEGIN
    PRINT CONCAT('C0 SQL validation FAILED: ', @failures, ' failure(s).');
    THROW 51000, 'EIOS C0 SQL Server validation failed.', 1;
END;

PRINT 'EIOS C0 SQL Server validation PASSED.';

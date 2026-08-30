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

/* V2 — expected columns, SQL types, lengths, precision/scale and nullability */
DECLARE @expected_columns TABLE
(
    table_name sysname,
    column_name sysname,
    type_name sysname,
    max_length smallint NULL,
    precision tinyint NULL,
    scale tinyint NULL,
    is_nullable bit,
    is_identity bit,
    PRIMARY KEY (table_name, column_name)
);

INSERT INTO @expected_columns
    (table_name, column_name, type_name, max_length, precision, scale, is_nullable, is_identity)
VALUES
    (N'c0_input', N'input_row_id',      N'bigint',          8,   NULL, NULL, 0, 1),
    (N'c0_input', N'decision_id',       N'nvarchar',       128, NULL, NULL, 0, 0),
    (N'c0_input', N'scenario_id',       N'nvarchar',       128, NULL, NULL, 0, 0),
    (N'c0_input', N'article_id',        N'nvarchar',       128, NULL, NULL, 0, 0),
    (N'c0_input', N'supplier_id',       N'nvarchar',       128, NULL, NULL, 0, 0),
    (N'c0_input', N'quantity',          N'decimal',         17,  38,  4, 0, 0),
    (N'c0_input', N'unit_price',        N'decimal',         17,  38,  4, 0, 0),
    (N'c0_input', N'currency',          N'char',              3, NULL, NULL, 0, 0),
    (N'c0_input', N'operation_date',    N'date',              3, NULL, NULL, 0, 0),
    (N'c0_input', N'input_fingerprint', N'char',             64, NULL, NULL, 0, 0),

    (N'c0_context', N'context_row_id',     N'bigint',    8,   NULL, NULL, 0, 1),
    (N'c0_context', N'decision_id',        N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_context', N'scenario_id',        N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_context', N'rules_version',      N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_context', N'parameters_version', N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_context', N'data_snapshot_id',   N'nvarchar', 128, NULL, NULL, 0, 0),

    (N'c0_evidence', N'evidence_id',       N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_evidence', N'source_type',       N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_evidence', N'source_ref',        N'nvarchar', 512, NULL, NULL, 0, 0),
    (N'c0_evidence', N'captured_at',        N'date',       3, NULL, NULL, 0, 0),
    (N'c0_evidence', N'state',              N'varchar',    16, NULL, NULL, 0, 0),
    (N'c0_evidence', N'demonstration_ref',  N'nvarchar', 512, NULL, NULL, 1, 0),

    (N'c0_evidence_validation', N'evidence_id', N'nvarchar', 128, NULL, NULL, 0, 0),
    (N'c0_evidence_validation', N'status',      N'varchar',   8, NULL, NULL, 0, 0),
    (N'c0_evidence_validation', N'reason',      N'nvarchar',512, NULL, NULL, 0, 0),

    (N'c0_rule_contract', N'rule_id',           N'nvarchar',128, NULL, NULL, 0, 0),
    (N'c0_rule_contract', N'version',           N'nvarchar',128, NULL, NULL, 0, 0),
    (N'c0_rule_contract', N'requires_evidence', N'bit',       1, NULL, NULL, 0, 0),

    (N'c0_assessment', N'assessment_row_id', N'bigint',    8, NULL, NULL, 0, 1),
    (N'c0_assessment', N'rule_id',           N'nvarchar',128, NULL, NULL, 0, 0),
    (N'c0_assessment', N'status',            N'varchar',  16, NULL, NULL, 0, 0),
    (N'c0_assessment', N'outcome',            N'bit',       1, NULL, NULL, 1, 0),
    (N'c0_assessment', N'reason',             N'nvarchar',512, NULL, NULL, 0, 0),

    (N'c0_assessment_evidence', N'assessment_row_id', N'bigint',    8, NULL, NULL, 0, 0),
    (N'c0_assessment_evidence', N'evidence_ordinal',  N'int',        4, NULL, NULL, 0, 0),
    (N'c0_assessment_evidence', N'evidence_id',       N'nvarchar',128, NULL, NULL, 0, 0),

    (N'c0_trace', N'trace_id',           N'nvarchar',      256, NULL, NULL, 0, 0),
    (N'c0_trace', N'decision_id',        N'nvarchar',      128, NULL, NULL, 0, 0),
    (N'c0_trace', N'scenario_id',       N'nvarchar',      128, NULL, NULL, 0, 0),
    (N'c0_trace', N'rules_version',     N'nvarchar',      128, NULL, NULL, 0, 0),
    (N'c0_trace', N'parameters_version',N'nvarchar',      128, NULL, NULL, 0, 0),
    (N'c0_trace', N'data_snapshot_id',  N'nvarchar',      128, NULL, NULL, 0, 0),
    (N'c0_trace', N'input_fingerprint', N'char',           64, NULL, NULL, 0, 0),
    (N'c0_trace', N'rule_id',            N'nvarchar',      128, NULL, NULL, 0, 0),
    (N'c0_trace', N'assessment_status',  N'varchar',       16, NULL, NULL, 0, 0),
    (N'c0_trace', N'assessment_outcome', N'bit',             1, NULL, NULL, 1, 0),
    (N'c0_trace', N'created_at',         N'datetimeoffset', 10, NULL, 7, 0, 0),

    (N'c0_trace_evidence', N'trace_id',         N'nvarchar',128, NULL, NULL, 0, 0),
    (N'c0_trace_evidence', N'evidence_ordinal', N'int',       4, NULL, NULL, 0, 0),
    (N'c0_trace_evidence', N'evidence_id',      N'nvarchar',128, NULL, NULL, 0, 0);

IF (SELECT COUNT(*) FROM sys.columns c JOIN sys.tables t ON t.object_id = c.object_id
    WHERE t.schema_id = SCHEMA_ID(N'eios')) <> (SELECT COUNT(*) FROM @expected_columns)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V2: unexpected C0 column count';
END;

IF EXISTS
(
    SELECT 1
    FROM @expected_columns e
    LEFT JOIN sys.tables t
      ON t.schema_id = SCHEMA_ID(N'eios') AND t.name = e.table_name
    LEFT JOIN sys.columns c
      ON c.object_id = t.object_id AND c.name = e.column_name
    LEFT JOIN sys.types ty
      ON ty.user_type_id = c.user_type_id
    WHERE c.column_id IS NULL
       OR ty.name <> e.type_name
       OR c.is_nullable <> e.is_nullable
       OR c.is_identity <> e.is_identity
       OR (e.max_length IS NOT NULL AND c.max_length <> e.max_length)
       OR (e.precision IS NOT NULL AND c.precision <> e.precision)
       OR (e.scale IS NOT NULL AND c.scale <> e.scale)
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V2: column definition differs from C0 SQL contract';
END;

/* V3 — expected indexes */
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
        SELECT 1 FROM sys.indexes i
        WHERE i.name = e.index_name AND i.object_id = OBJECT_ID(N'eios.' + e.table_name)
    )
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V3: expected index is missing';
END;

/* V4 — expected foreign keys */
DECLARE @expected_fks TABLE (fk_name sysname PRIMARY KEY);
INSERT INTO @expected_fks (fk_name)
VALUES
    (N'FK_c0_evidence_validation_evidence'),
    (N'FK_c0_assessment_evidence_assessment'),
    (N'FK_c0_assessment_evidence_evidence'),
    (N'FK_c0_trace_evidence_trace'),
    (N'FK_c0_trace_evidence_evidence');

IF (SELECT COUNT(*) FROM sys.foreign_keys WHERE parent_object_id IN
    (SELECT object_id FROM sys.tables WHERE schema_id = SCHEMA_ID(N'eios'))) <> 5
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V4: unexpected foreign key count';
END;

IF EXISTS
(
    SELECT 1 FROM @expected_fks e
    WHERE NOT EXISTS (SELECT 1 FROM sys.foreign_keys fk WHERE fk.name = e.fk_name)
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V4: expected foreign key is missing';
END;

/* V5 — expected primary/unique constraints */
IF (SELECT COUNT(*) FROM sys.key_constraints kc
    WHERE kc.parent_object_id IN (SELECT object_id FROM sys.tables WHERE schema_id = SCHEMA_ID(N'eios'))
      AND kc.type = 'PK') <> 9
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V5: unexpected primary key count';
END;

IF (SELECT COUNT(*) FROM sys.key_constraints kc
    WHERE kc.parent_object_id IN (SELECT object_id FROM sys.tables WHERE schema_id = SCHEMA_ID(N'eios'))
      AND kc.type = 'UQ') <> 3
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V5: unexpected unique constraint count';
END;

/* V6 — expected CHECK constraints */
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

IF (SELECT COUNT(*) FROM sys.check_constraints cc
    WHERE cc.parent_object_id IN (SELECT object_id FROM sys.tables WHERE schema_id = SCHEMA_ID(N'eios'))) <> 22
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V6: unexpected CHECK constraint count';
END;

IF EXISTS
(
    SELECT 1 FROM @expected_checks e
    WHERE NOT EXISTS (SELECT 1 FROM sys.check_constraints c WHERE c.name = e.constraint_name)
)
BEGIN
    SET @failures += 1;
    PRINT 'FAIL V6: expected CHECK constraint is missing';
END;

/* V7 — valid rows must be accepted */
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
    PRINT 'FAIL V7: valid C0 rows were rejected';
END CATCH;

/* V8 — invalid states must be rejected */
DECLARE @case_failed bit;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'', N'SCN-0001', N'ART-001', N'PROV-001', 1.0000, 1.0000, 'EUR', '2026-08-21', REPLICATE('A', 64));
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.1: empty identifier accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'DEC-X', N'SCN-X', N'ART-X', N'PROV-X', 0.0000, 1.0000, 'EUR', '2026-08-21', REPLICATE('B', 64));
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.2: non-positive quantity accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'DEC-Y', N'SCN-Y', N'ART-Y', N'PROV-Y', 1.0000, 1.0000, 'USD', '2026-08-21', REPLICATE('C', 64));
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.3: non-EUR currency accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_input
        (decision_id, scenario_id, article_id, supplier_id, quantity, unit_price, currency, operation_date, input_fingerprint)
    VALUES (N'DEC-Z', N'SCN-Z', N'ART-Z', N'PROV-Z', 1.0000, 1.0000, 'EUR', '2026-08-21', REPLICATE('D', 63) + 'G');
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.4: invalid fingerprint accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_evidence
        (evidence_id, source_type, source_ref, captured_at, state, demonstration_ref)
    VALUES (N'E-BAD-1', N'ERP', N'ref', '2026-08-21', 'DEMONSTRATED', NULL);
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.5: demonstrated evidence without reference accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-BAD-1', 'EVALUABLE', NULL, N'bad');
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.6: EVALUABLE without outcome accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-BAD-2', 'NOT_EVALUABLE', 0, N'bad');
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.7: NOT_EVALUABLE with outcome accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_assessment (rule_id, status, outcome, reason)
    VALUES (N'R-BAD-3', 'EVALUABLE', 1, N'bad');
    DECLARE @bad_assessment_id bigint = SCOPE_IDENTITY();
    INSERT INTO eios.c0_assessment_evidence (assessment_row_id, evidence_ordinal, evidence_id)
    VALUES (@bad_assessment_id, -1, N'E-001');
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.8: negative evidence ordinal accepted'; END;

SET @case_failed = 0;
BEGIN TRY
    INSERT INTO eios.c0_evidence_validation (evidence_id, status, reason)
    VALUES (N'E-NOT-FOUND', 'VALID', N'bad');
END TRY
BEGIN CATCH SET @case_failed = 1; END CATCH;
IF @case_failed = 0 BEGIN SET @failures += 1; PRINT 'FAIL V8.9: FK violation accepted'; END;

IF @failures <> 0
BEGIN
    PRINT CONCAT('C0 SQL validation FAILED: ', @failures, ' failure(s).');
    THROW 51000, 'EIOS C0 SQL Server validation failed.', 1;
END;

PRINT 'EIOS C0 SQL Server validation PASSED.';

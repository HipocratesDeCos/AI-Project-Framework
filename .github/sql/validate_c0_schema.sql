/*
EIOS — SQL Server C0 schema validation
Scope: structural and invariant validation of 001_C0_Schema.sql
Environment: ephemeral CI database only
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

DECLARE @failures int = 0;

/* V1 — exact table set */
DECLARE @expected_tables TABLE (table_name sysname PRIMARY KEY);
INSERT INTO @expected_tables VALUES
(N'c0_input'),(N'c0_context'),(N'c0_evidence'),(N'c0_evidence_validation'),
(N'c0_rule_contract'),(N'c0_assessment'),(N'c0_assessment_evidence'),
(N'c0_trace'),(N'c0_trace_evidence');

IF EXISTS (SELECT 1 FROM @expected_tables e WHERE OBJECT_ID(N'eios.'+e.table_name,N'U') IS NULL)
BEGIN SET @failures+=1; PRINT 'FAIL V1: expected table missing'; END;
IF EXISTS (SELECT 1 FROM sys.tables t WHERE t.schema_id=SCHEMA_ID(N'eios') AND t.name NOT IN (SELECT table_name FROM @expected_tables))
BEGIN SET @failures+=1; PRINT 'FAIL V1: unexpected table present'; END;

/* V2 — exact columns, SQL type, character length, precision/scale, datetime precision, nullability and identity */
DECLARE @expected_columns TABLE
(
 table_name sysname, column_name sysname, data_type sysname,
 char_length int NULL, numeric_precision int NULL, numeric_scale int NULL,
 datetime_precision int NULL, is_nullable bit, is_identity bit,
 PRIMARY KEY(table_name,column_name)
);
INSERT INTO @expected_columns VALUES
(N'c0_input',N'input_row_id',N'bigint',NULL,19,0,NULL,0,1),
(N'c0_input',N'decision_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_input',N'scenario_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_input',N'article_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_input',N'supplier_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_input',N'quantity',N'decimal',NULL,38,4,NULL,0,0),
(N'c0_input',N'unit_price',N'decimal',NULL,38,4,NULL,0,0),
(N'c0_input',N'currency',N'char',3,NULL,NULL,NULL,0,0),
(N'c0_input',N'operation_date',N'date',NULL,NULL,NULL,NULL,0,0),
(N'c0_input',N'input_fingerprint',N'char',64,NULL,NULL,NULL,0,0),
(N'c0_context',N'context_row_id',N'bigint',NULL,19,0,NULL,0,1),
(N'c0_context',N'decision_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_context',N'scenario_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_context',N'rules_version',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_context',N'parameters_version',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_context',N'data_snapshot_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_evidence',N'evidence_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_evidence',N'source_type',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_evidence',N'source_ref',N'nvarchar',256,NULL,NULL,NULL,0,0),
(N'c0_evidence',N'captured_at',N'date',NULL,NULL,NULL,NULL,0,0),
(N'c0_evidence',N'state',N'varchar',16,NULL,NULL,NULL,0,0),
(N'c0_evidence',N'demonstration_ref',N'nvarchar',256,NULL,NULL,NULL,1,0),
(N'c0_evidence_validation',N'evidence_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_evidence_validation',N'status',N'varchar',8,NULL,NULL,NULL,0,0),
(N'c0_evidence_validation',N'reason',N'nvarchar',256,NULL,NULL,NULL,0,0),
(N'c0_rule_contract',N'rule_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_rule_contract',N'version',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_rule_contract',N'requires_evidence',N'bit',NULL,1,0,NULL,0,0),
(N'c0_assessment',N'assessment_row_id',N'bigint',NULL,19,0,NULL,0,1),
(N'c0_assessment',N'rule_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_assessment',N'status',N'varchar',16,NULL,NULL,NULL,0,0),
(N'c0_assessment',N'outcome',N'bit',NULL,1,0,NULL,1,0),
(N'c0_assessment',N'reason',N'nvarchar',256,NULL,NULL,NULL,0,0),
(N'c0_assessment_evidence',N'assessment_row_id',N'bigint',NULL,19,0,NULL,0,0),
(N'c0_assessment_evidence',N'evidence_ordinal',N'int',NULL,10,0,NULL,0,0),
(N'c0_assessment_evidence',N'evidence_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'trace_id',N'nvarchar',128,NULL,NULL,NULL,0,0),
(N'c0_trace',N'decision_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'scenario_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'rules_version',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'parameters_version',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'data_snapshot_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'input_fingerprint',N'char',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'rule_id',N'nvarchar',64,NULL,NULL,NULL,0,0),
(N'c0_trace',N'assessment_status',N'varchar',16,NULL,NULL,NULL,0,0),
(N'c0_trace',N'assessment_outcome',N'bit',NULL,1,0,NULL,1,0),
(N'c0_trace',N'created_at',N'datetimeoffset',NULL,NULL,NULL,7,0,0),
(N'c0_trace_evidence',N'trace_id',N'nvarchar',128,NULL,NULL,NULL,0,0),
(N'c0_trace_evidence',N'evidence_ordinal',N'int',NULL,10,0,NULL,0,0),
(N'c0_trace_evidence',N'evidence_id',N'nvarchar',64,NULL,NULL,NULL,0,0);

IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='eios') <> (SELECT COUNT(*) FROM @expected_columns)
BEGIN SET @failures+=1; PRINT 'FAIL V2: column count differs'; END;
IF EXISTS (
 SELECT 1 FROM @expected_columns e
 LEFT JOIN INFORMATION_SCHEMA.COLUMNS c ON c.TABLE_SCHEMA='eios' AND c.TABLE_NAME=e.table_name AND c.COLUMN_NAME=e.column_name
 WHERE c.COLUMN_NAME IS NULL
    OR c.DATA_TYPE<>e.data_type
    OR c.IS_NULLABLE <> CASE WHEN e.is_nullable=1 THEN 'YES' ELSE 'NO' END
    OR ISNULL(c.CHARACTER_MAXIMUM_LENGTH,-999)<>ISNULL(e.char_length,-999)
    OR ISNULL(CONVERT(int,c.NUMERIC_PRECISION),-999)<>ISNULL(e.numeric_precision,-999)
    OR ISNULL(CONVERT(int,c.NUMERIC_SCALE),-999)<>ISNULL(e.numeric_scale,-999)
    OR ISNULL(CONVERT(int,c.DATETIME_PRECISION),-999)<>ISNULL(e.datetime_precision,-999)
    OR ISNULL(COLUMNPROPERTY(OBJECT_ID(N'eios.'+e.table_name),e.column_name,'IsIdentity'),0)<>e.is_identity
)
BEGIN SET @failures+=1; PRINT 'FAIL V2: column definition differs from C0 SQL contract'; END;

/* V2 diagnostic — expose the exact mismatched metadata row(s) in CI */
SELECT
    e.table_name,
    e.column_name,
    e.data_type AS expected_data_type,
    c.DATA_TYPE AS actual_data_type,
    e.char_length AS expected_char_length,
    c.CHARACTER_MAXIMUM_LENGTH AS actual_char_length,
    e.numeric_precision AS expected_numeric_precision,
    CONVERT(int,c.NUMERIC_PRECISION) AS actual_numeric_precision,
    e.numeric_scale AS expected_numeric_scale,
    CONVERT(int,c.NUMERIC_SCALE) AS actual_numeric_scale,
    e.datetime_precision AS expected_datetime_precision,
    CONVERT(int,c.DATETIME_PRECISION) AS actual_datetime_precision,
    CASE WHEN e.is_nullable=1 THEN 'YES' ELSE 'NO' END AS expected_nullable,
    c.IS_NULLABLE AS actual_nullable,
    e.is_identity AS expected_identity,
    COLUMNPROPERTY(OBJECT_ID(N'eios.'+e.table_name),e.column_name,'IsIdentity') AS actual_identity
FROM @expected_columns e
LEFT JOIN INFORMATION_SCHEMA.COLUMNS c
  ON c.TABLE_SCHEMA='eios' AND c.TABLE_NAME=e.table_name AND c.COLUMN_NAME=e.column_name
WHERE c.COLUMN_NAME IS NULL
   OR c.DATA_TYPE<>e.data_type
   OR c.IS_NULLABLE <> CASE WHEN e.is_nullable=1 THEN 'YES' ELSE 'NO' END
   OR ISNULL(CONVERT(int,c.CHARACTER_MAXIMUM_LENGTH),-999)<>ISNULL(e.char_length,-999)
   OR ISNULL(CONVERT(int,c.NUMERIC_PRECISION),-999)<>ISNULL(e.numeric_precision,-999)
   OR ISNULL(CONVERT(int,c.NUMERIC_SCALE),-999)<>ISNULL(e.numeric_scale,-999)
   OR ISNULL(CONVERT(int,c.DATETIME_PRECISION),-999)<>ISNULL(e.datetime_precision,-999)
   OR ISNULL(COLUMNPROPERTY(OBJECT_ID(N'eios.'+e.table_name),e.column_name,'IsIdentity'),0)<>e.is_identity;

/* V3 — expected indexes */
DECLARE @expected_indexes TABLE(index_name sysname PRIMARY KEY, table_name sysname);
INSERT INTO @expected_indexes VALUES
(N'IX_c0_input_decision_scenario',N'c0_input'),
(N'IX_c0_context_decision_scenario_versions',N'c0_context'),
(N'IX_c0_assessment_rule_status',N'c0_assessment'),
(N'IX_c0_trace_decision_scenario_created',N'c0_trace');
IF EXISTS (SELECT 1 FROM @expected_indexes e WHERE NOT EXISTS (SELECT 1 FROM sys.indexes i WHERE i.name=e.index_name AND i.object_id=OBJECT_ID(N'eios.'+e.table_name)))
BEGIN SET @failures+=1; PRINT 'FAIL V3: expected index missing'; END;

/* V4 — expected foreign keys */
DECLARE @expected_fks TABLE(fk_name sysname PRIMARY KEY);
INSERT INTO @expected_fks VALUES
(N'FK_c0_evidence_validation_evidence'),(N'FK_c0_assessment_evidence_assessment'),
(N'FK_c0_assessment_evidence_evidence'),(N'FK_c0_trace_evidence_trace'),
(N'FK_c0_trace_evidence_evidence');
IF EXISTS (SELECT 1 FROM @expected_fks e WHERE NOT EXISTS (SELECT 1 FROM sys.foreign_keys f WHERE f.name=e.fk_name))
BEGIN SET @failures+=1; PRINT 'FAIL V4: expected foreign key missing'; END;

/* V5 — PK and UNIQUE constraints */
IF EXISTS (SELECT 1 FROM sys.tables t WHERE t.schema_id=SCHEMA_ID('eios') AND NOT EXISTS (SELECT 1 FROM sys.key_constraints k WHERE k.parent_object_id=t.object_id AND k.type='PK'))
BEGIN SET @failures+=1; PRINT 'FAIL V5: table without PK'; END;
DECLARE @expected_uq TABLE(name sysname PRIMARY KEY);
INSERT INTO @expected_uq VALUES(N'UQ_c0_input_fingerprint'),(N'UQ_c0_assessment_evidence'),(N'UQ_c0_trace_evidence');
IF EXISTS (SELECT 1 FROM @expected_uq e WHERE NOT EXISTS (SELECT 1 FROM sys.key_constraints k WHERE k.name=e.name AND k.type='UQ'))
BEGIN SET @failures+=1; PRINT 'FAIL V5: expected UNIQUE constraint missing'; END;

/* V6 — expected CHECK constraints; extra CHECKs are reported rather than hidden */
DECLARE @expected_checks TABLE(name sysname PRIMARY KEY);
INSERT INTO @expected_checks VALUES
(N'CK_c0_input_quantity'),(N'CK_c0_input_unit_price'),(N'CK_c0_input_currency'),(N'CK_c0_input_identifiers_nonempty'),(N'CK_c0_input_fingerprint'),
(N'CK_c0_context_nonempty'),(N'CK_c0_evidence_state'),(N'CK_c0_evidence_nonempty'),(N'CK_c0_evidence_demonstration'),
(N'CK_c0_evidence_validation_status'),(N'CK_c0_evidence_validation_nonempty'),(N'CK_c0_rule_contract_nonempty'),
(N'CK_c0_assessment_status'),(N'CK_c0_assessment_status_outcome'),(N'CK_c0_assessment_nonempty'),
(N'CK_c0_assessment_evidence_ordinal'),(N'CK_c0_assessment_evidence_id_nonempty'),(N'CK_c0_trace_status'),
(N'CK_c0_trace_status_outcome'),(N'CK_c0_trace_nonempty'),(N'CK_c0_trace_fingerprint'),
(N'CK_c0_trace_evidence_ordinal'),(N'CK_c0_trace_evidence_id_nonempty');
IF EXISTS (SELECT 1 FROM @expected_checks e WHERE NOT EXISTS (SELECT 1 FROM sys.check_constraints c WHERE c.name=e.name))
BEGIN SET @failures+=1; PRINT 'FAIL V6: expected CHECK constraint missing'; END;
IF EXISTS (SELECT 1 FROM sys.check_constraints c WHERE c.parent_object_id IN (SELECT object_id FROM sys.tables WHERE schema_id=SCHEMA_ID('eios')) AND NOT EXISTS (SELECT 1 FROM @expected_checks e WHERE e.name=c.name))
BEGIN SET @failures+=1; PRINT 'FAIL V6: unexpected CHECK constraint present'; END;

/* V7 — valid rows */
BEGIN TRY
 BEGIN TRANSACTION;
 INSERT INTO eios.c0_input(decision_id,scenario_id,article_id,supplier_id,quantity,unit_price,currency,operation_date,input_fingerprint)
 VALUES(N'DEC-0001',N'SCN-0001',N'ART-001',N'PROV-001',100.0000,12.5000,'EUR','2026-08-21',REPLICATE('A',64));
 INSERT INTO eios.c0_context(decision_id,scenario_id,rules_version,parameters_version,data_snapshot_id) VALUES(N'DEC-0001',N'SCN-0001',N'R-1',N'P-1',N'DS-1');
 INSERT INTO eios.c0_evidence(evidence_id,source_type,source_ref,captured_at,state,demonstration_ref) VALUES(N'E-001',N'ERP',N'purchase-history/001','2026-08-21','DEMONSTRATED',N'ERP:purchase-history/001'),(N'E-GAP-001',N'ERP',N'purchase-history/missing','2026-08-21','GAP',NULL);
 INSERT INTO eios.c0_evidence_validation(evidence_id,status,reason) VALUES(N'E-001','VALID',N'Valid');
 INSERT INTO eios.c0_rule_contract(rule_id,version,requires_evidence) VALUES(N'R-001',N'1',1);
 INSERT INTO eios.c0_assessment(rule_id,status,outcome,reason) VALUES(N'R-001',N'EVALUABLE',1,N'Valid');
 INSERT INTO eios.c0_assessment_evidence(assessment_row_id,evidence_ordinal,evidence_id) VALUES(SCOPE_IDENTITY(),0,N'E-001');
 INSERT INTO eios.c0_trace(trace_id,decision_id,scenario_id,rules_version,parameters_version,data_snapshot_id,input_fingerprint,rule_id,assessment_status,assessment_outcome,created_at)
 VALUES(N'T-001',N'DEC-0001',N'SCN-0001',N'R-1',N'P-1',N'DS-1',REPLICATE('B',64),N'R-001',N'EVALUABLE',1,SYSDATETIMEOFFSET());
 COMMIT;
END TRY
BEGIN CATCH
 IF XACT_STATE()<>0 ROLLBACK;
 SET @failures+=1; PRINT 'FAIL V7: valid C0 rows were rejected';
END CATCH;

/* V8 — negative invariant tests */
DECLARE @rejected int=0;
BEGIN TRY INSERT INTO eios.c0_input(decision_id,scenario_id,article_id,supplier_id,quantity,unit_price,currency,operation_date,input_fingerprint) VALUES(N'',N'S',N'A',N'P',1,1,'EUR','2026-08-21',REPLICATE('C',64)); END TRY BEGIN CATCH SET @rejected+=1; END CATCH;
BEGIN TRY INSERT INTO eios.c0_input(decision_id,scenario_id,article_id,supplier_id,quantity,unit_price,currency,operation_date,input_fingerprint) VALUES(N'D',N'S',N'A',N'P',0,1,'EUR','2026-08-21',REPLICATE('C',64)); END TRY BEGIN CATCH SET @rejected+=1; END CATCH;
BEGIN TRY INSERT INTO eios.c0_input(decision_id,scenario_id,article_id,supplier_id,quantity,unit_price,currency,operation_date,input_fingerprint) VALUES(N'D',N'S',N'A',N'P',1,1,'USD','2026-08-21',REPLICATE('C',64)); END TRY BEGIN CATCH SET @rejected+=1; END CATCH;
BEGIN TRY INSERT INTO eios.c0_evidence(evidence_id,source_type,source_ref,captured_at,state,demonstration_ref) VALUES(N'E-BAD',N'ERP',N'X','2026-08-21','DEMONSTRATED',NULL); END TRY BEGIN CATCH SET @rejected+=1; END CATCH;
BEGIN TRY INSERT INTO eios.c0_assessment(rule_id,status,outcome,reason) VALUES(N'R-BAD',N'EVALUABLE',NULL,N'Bad'); END TRY BEGIN CATCH SET @rejected+=1; END CATCH;
BEGIN TRY INSERT INTO eios.c0_assessment(rule_id,status,outcome,reason) VALUES(N'R-BAD2',N'NOT_EVALUABLE',0,N'Bad'); END TRY BEGIN CATCH SET @rejected+=1; END CATCH;
IF @rejected<>6 BEGIN SET @failures+=1; PRINT 'FAIL V8: negative invariant rejection count differs'; END;

IF @failures=0 PRINT 'EIOS C0 SQL validation PASSED';
ELSE
BEGIN PRINT CONCAT('EIOS C0 SQL validation FAILED: ',@failures,' failure(s).'); THROW 51000,'EIOS C0 SQL Server validation failed.',1; END;
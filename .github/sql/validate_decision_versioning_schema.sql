/*
EIOS — SQL Server Decision Versioning schema validation
Scope: structural and invariant validation of 002_Decision_Versioning_Schema.sql
Environment: ephemeral CI database only
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;
DECLARE @failures int = 0;

/* V1 — exact Decision Versioning table */
IF OBJECT_ID(N'eios.decision_state', N'U') IS NULL
BEGIN SET @failures += 1; PRINT 'FAIL V1: eios.decision_state missing'; END
ELSE PRINT 'PASS V1: eios.decision_state exists';

/* V2 — exact columns, SQL type, length, precision, scale, datetime precision, nullability, identity */
DECLARE @expected_columns TABLE
(
    column_name sysname PRIMARY KEY,
    data_type sysname,
    char_length int NULL,
    numeric_precision int NULL,
    numeric_scale int NULL,
    datetime_precision int NULL,
    is_nullable bit,
    is_identity bit
);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'decision_state_record_id',N'bigint',NULL,19,0,NULL,0,1);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'decision_id',N'nvarchar',64,NULL,NULL,NULL,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'scenario_id',N'nvarchar',64,NULL,NULL,NULL,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'data_snapshot_id',N'nvarchar',64,NULL,NULL,NULL,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'rules_version',N'nvarchar',64,NULL,NULL,NULL,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'parameters_version',N'nvarchar',64,NULL,NULL,NULL,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'forecast_version',N'nvarchar',64,NULL,NULL,NULL,1,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'rfp_version',N'nvarchar',64,NULL,NULL,NULL,1,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'eios_version',N'nvarchar',64,NULL,NULL,NULL,1,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'timestamp',N'datetimeoffset',NULL,NULL,NULL,7,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'user_id',N'nvarchar',128,NULL,NULL,NULL,0,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'input_fingerprint',N'char',64,NULL,NULL,NULL,1,0);
INSERT INTO @expected_columns (column_name,data_type,char_length,numeric_precision,numeric_scale,datetime_precision,is_nullable,is_identity) VALUES (N'trace_id',N'nvarchar',128,NULL,NULL,NULL,1,0);

IF (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA=N'eios' AND TABLE_NAME=N'decision_state') <> (SELECT COUNT(*) FROM @expected_columns)
BEGIN SET @failures += 1; PRINT 'FAIL V2: column count differs'; END;
IF EXISTS (
    SELECT 1
    FROM @expected_columns e
    LEFT JOIN INFORMATION_SCHEMA.COLUMNS c
      ON c.TABLE_SCHEMA=N'eios' AND c.TABLE_NAME=N'decision_state' AND c.COLUMN_NAME=e.column_name
    WHERE c.COLUMN_NAME IS NULL
       OR c.DATA_TYPE <> e.data_type
       OR c.IS_NULLABLE <> CASE WHEN e.is_nullable=1 THEN 'YES' ELSE 'NO' END
       OR ISNULL(CONVERT(int,c.CHARACTER_MAXIMUM_LENGTH),-999) <> ISNULL(e.char_length,-999)
       OR ISNULL(CONVERT(int,c.NUMERIC_PRECISION),-999) <> ISNULL(e.numeric_precision,-999)
       OR ISNULL(CONVERT(int,c.NUMERIC_SCALE),-999) <> ISNULL(e.numeric_scale,-999)
       OR ISNULL(CONVERT(int,c.DATETIME_PRECISION),-999) <> ISNULL(e.datetime_precision,-999)
       OR ISNULL(COLUMNPROPERTY(OBJECT_ID(N'eios.decision_state'),e.column_name,'IsIdentity'),0) <> e.is_identity
)
BEGIN SET @failures += 1; PRINT 'FAIL V2: column definition differs'; END
ELSE PRINT 'PASS V2: exact column contract';

/* V3 — expected primary key and no functional UNIQUE constraint */
IF NOT EXISTS (
    SELECT 1 FROM sys.key_constraints
    WHERE parent_object_id=OBJECT_ID(N'eios.decision_state')
      AND type='PK' AND name=N'PK_decision_state'
)
BEGIN SET @failures += 1; PRINT 'FAIL V3: primary key missing'; END
ELSE PRINT 'PASS V3: primary key';

IF EXISTS (
    SELECT 1 FROM sys.key_constraints
    WHERE parent_object_id=OBJECT_ID(N'eios.decision_state')
      AND type='UQ'
)
BEGIN SET @failures += 1; PRINT 'FAIL V3: unexpected UNIQUE constraint'; END;

/* V4 — expected CHECK constraints */
DECLARE @expected_checks TABLE(name sysname PRIMARY KEY);
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_decision_id_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_scenario_id_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_data_snapshot_id_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_rules_version_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_parameters_version_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_user_id_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_timestamp_utc');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_fingerprint_hex');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_forecast_version_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_rfp_version_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_eios_version_nonempty');
INSERT INTO @expected_checks(name) VALUES (N'CK_decision_state_trace_id_nonempty');
IF EXISTS (SELECT 1 FROM @expected_checks e WHERE NOT EXISTS (SELECT 1 FROM sys.check_constraints c WHERE c.parent_object_id=OBJECT_ID(N'eios.decision_state') AND c.name=e.name))
BEGIN SET @failures += 1; PRINT 'FAIL V4: expected CHECK missing'; END
ELSE PRINT 'PASS V4: expected CHECK constraints';
IF EXISTS (SELECT 1 FROM sys.check_constraints c WHERE c.parent_object_id=OBJECT_ID(N'eios.decision_state') AND NOT EXISTS (SELECT 1 FROM @expected_checks e WHERE e.name=c.name))
BEGIN SET @failures += 1; PRINT 'FAIL V4: unexpected CHECK constraint'; END;

/* V5 — no foreign keys to future artifacts */
IF EXISTS (SELECT 1 FROM sys.foreign_keys WHERE parent_object_id=OBJECT_ID(N'eios.decision_state'))
BEGIN SET @failures += 1; PRINT 'FAIL V5: unexpected foreign key'; END
ELSE PRINT 'PASS V5: no premature foreign keys';

/* V6 — role and permissions define append-only writer boundary */
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name=N'eios_decision_state_writer' AND type='R')
BEGIN SET @failures += 1; PRINT 'FAIL V6: writer role missing'; END;

DECLARE @role_id int = (SELECT principal_id FROM sys.database_principals WHERE name=N'eios_decision_state_writer' AND type='R');
IF @role_id IS NOT NULL
BEGIN
    IF NOT EXISTS (SELECT 1 FROM sys.database_permissions WHERE major_id=OBJECT_ID(N'eios.decision_state') AND grantee_principal_id=@role_id AND permission_name=N'SELECT' AND state='G')
    BEGIN SET @failures += 1; PRINT 'FAIL V6: SELECT grant missing'; END;
    IF NOT EXISTS (SELECT 1 FROM sys.database_permissions WHERE major_id=OBJECT_ID(N'eios.decision_state') AND grantee_principal_id=@role_id AND permission_name=N'INSERT' AND state='G')
    BEGIN SET @failures += 1; PRINT 'FAIL V6: INSERT grant missing'; END;
    IF NOT EXISTS (SELECT 1 FROM sys.database_permissions WHERE major_id=OBJECT_ID(N'eios.decision_state') AND grantee_principal_id=@role_id AND permission_name=N'UPDATE' AND state='D')
    BEGIN SET @failures += 1; PRINT 'FAIL V6: UPDATE deny missing'; END;
    IF NOT EXISTS (SELECT 1 FROM sys.database_permissions WHERE major_id=OBJECT_ID(N'eios.decision_state') AND grantee_principal_id=@role_id AND permission_name=N'DELETE' AND state='D')
    BEGIN SET @failures += 1; PRINT 'FAIL V6: DELETE deny missing'; END;
END

/* V7 — valid rows, including NULL optional references */
BEGIN TRY
    BEGIN TRANSACTION;
    INSERT INTO eios.decision_state
    (decision_id,scenario_id,data_snapshot_id,rules_version,parameters_version,forecast_version,rfp_version,eios_version,[timestamp],user_id,input_fingerprint,trace_id)
    VALUES (N'DEC-0001',N'SCN-0001',N'DS-1',N'R-1',N'P-1',NULL,NULL,NULL,'2026-08-21T10:00:00+00:00',N'human:001',REPLICATE('A',64),N'T-001');
    INSERT INTO eios.decision_state
    (decision_id,scenario_id,data_snapshot_id,rules_version,parameters_version,forecast_version,rfp_version,eios_version,[timestamp],user_id,input_fingerprint,trace_id)
    VALUES (N'DEC-0002',N'SCN-0002',N'DS-2',N'R-2',N'P-2',N'F-1',N'RFP-1',N'EIOS-1','2026-08-21T11:00:00+00:00',N'service:erp-sync',NULL,NULL);
    COMMIT;
    PRINT 'PASS V7: valid rows accepted';
END TRY
BEGIN CATCH
    IF XACT_STATE()<>0 ROLLBACK;
    SET @failures += 1;
    PRINT 'FAIL V7: valid rows rejected';
END CATCH;

/* V8 — negative invariant tests */
DECLARE @rejected int = 0;
BEGIN TRY INSERT INTO eios.decision_state(decision_id,scenario_id,data_snapshot_id,rules_version,parameters_version,[timestamp],user_id) VALUES(N'',N'S',N'DS',N'R',N'P','2026-08-21T10:00:00+00:00',N'U'); END TRY BEGIN CATCH SET @rejected += 1; END CATCH;
BEGIN TRY INSERT INTO eios.decision_state(decision_id,scenario_id,data_snapshot_id,rules_version,parameters_version,[timestamp],user_id) VALUES(N'D',N'S',N'DS',N'R',N'P','2026-08-21T10:00:00+02:00',N'U'); END TRY BEGIN CATCH SET @rejected += 1; END CATCH;
BEGIN TRY INSERT INTO eios.decision_state(decision_id,scenario_id,data_snapshot_id,rules_version,parameters_version,[timestamp],user_id,input_fingerprint) VALUES(N'D',N'S',N'DS',N'R',N'P','2026-08-21T10:00:00+00:00',N'U',REPLICATE('G',64)); END TRY BEGIN CATCH SET @rejected += 1; END CATCH;
BEGIN TRY INSERT INTO eios.decision_state(decision_id,scenario_id,data_snapshot_id,rules_version,parameters_version,[timestamp],user_id,forecast_version) VALUES(N'D',N'S',N'DS',N'R',N'P','2026-08-21T10:00:00+00:00',N'U',N''); END TRY BEGIN CATCH SET @rejected += 1; END CATCH;
IF @rejected <> 4 BEGIN SET @failures += 1; PRINT 'FAIL V8: expected negative tests were not all rejected'; END ELSE PRINT 'PASS V8: negative invariants rejected';

/* V9 — no unintended indexes beyond PK */
IF EXISTS (
    SELECT 1 FROM sys.indexes
    WHERE object_id=OBJECT_ID(N'eios.decision_state')
      AND is_primary_key=0
      AND is_unique_constraint=0
)
BEGIN SET @failures += 1; PRINT 'FAIL V9: unexpected non-PK index'; END
ELSE PRINT 'PASS V9: no unjustified secondary indexes';

/* V10 — cleanup and final status */
DELETE FROM eios.decision_state;
IF EXISTS (SELECT 1 FROM eios.decision_state)
BEGIN SET @failures += 1; PRINT 'FAIL V10: cleanup failed'; END
ELSE PRINT 'PASS V10: cleanup completed';

IF @failures > 0
BEGIN
    PRINT 'EIOS Decision Versioning SQL validation FAILED';
    THROW 51001, 'EIOS Decision Versioning SQL validation FAILED', 1;
END;

PRINT 'EIOS Decision Versioning SQL validation PASSED';

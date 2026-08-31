/*
EIOS — Validation of Centro de Parametrización SQL schema
Scope: structural validation only. No business-rule semantics are tested here.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF OBJECT_ID(N'eios.parameter_configuration', N'U') IS NULL
    THROW 51000, 'Missing eios.parameter_configuration', 1;

IF OBJECT_ID(N'eios.parameter_configuration_history', N'U') IS NULL
    THROW 51001, 'Missing eios.parameter_configuration_history', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.key_constraints
    WHERE name = N'PK_parameter_configuration'
      AND parent_object_id = OBJECT_ID(N'eios.parameter_configuration')
)
    THROW 51002, 'Missing configuration primary key', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.key_constraints
    WHERE name = N'PK_parameter_configuration_history'
      AND parent_object_id = OBJECT_ID(N'eios.parameter_configuration_history')
)
    THROW 51003, 'Missing history primary key', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.foreign_keys
    WHERE name = N'FK_parameter_configuration_history_configuration'
      AND parent_object_id = OBJECT_ID(N'eios.parameter_configuration_history')
      AND referenced_object_id = OBJECT_ID(N'eios.parameter_configuration')
)
    THROW 51004, 'Missing history-to-configuration foreign key', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.check_constraints
    WHERE name = N'CK_parameter_configuration_validity'
      AND parent_object_id = OBJECT_ID(N'eios.parameter_configuration')
)
    THROW 51005, 'Missing validity constraint', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_parameter_configuration_lookup'
      AND object_id = OBJECT_ID(N'eios.parameter_configuration')
)
    THROW 51006, 'Missing configuration lookup index', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_parameter_configuration_history_lookup'
      AND object_id = OBJECT_ID(N'eios.parameter_configuration_history')
)
    THROW 51007, 'Missing history lookup index', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.database_principals
    WHERE name = N'eios_parameter_configuration_history_writer'
      AND type = 'R'
)
    THROW 51008, 'Missing history writer role', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.database_permissions p
    JOIN sys.database_principals r ON r.principal_id = p.grantee_principal_id
    WHERE r.name = N'eios_parameter_configuration_history_writer'
      AND p.major_id = OBJECT_ID(N'eios.parameter_configuration_history')
      AND p.permission_name = N'INSERT'
      AND p.state_desc IN (N'GRANT', N'GRANT_WITH_GRANT_OPTION')
)
    THROW 51009, 'History writer INSERT permission missing', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.database_permissions p
    JOIN sys.database_principals r ON r.principal_id = p.grantee_principal_id
    WHERE r.name = N'eios_parameter_configuration_history_writer'
      AND p.major_id = OBJECT_ID(N'eios.parameter_configuration_history')
      AND p.permission_name = N'UPDATE'
      AND p.state_desc = N'DENY'
)
    THROW 51010, 'History writer UPDATE denial missing', 1;

IF NOT EXISTS
(
    SELECT 1
    FROM sys.database_permissions p
    JOIN sys.database_principals r ON r.principal_id = p.grantee_principal_id
    WHERE r.name = N'eios_parameter_configuration_history_writer'
      AND p.major_id = OBJECT_ID(N'eios.parameter_configuration_history')
      AND p.permission_name = N'DELETE'
      AND p.state_desc = N'DENY'
)
    THROW 51011, 'History writer DELETE denial missing', 1;

BEGIN TRANSACTION;

DECLARE @configuration_id bigint;

INSERT INTO eios.parameter_configuration
(
    parameter_id,
    company_id,
    value,
    value_type,
    unit,
    valid_from,
    valid_to,
    created_at,
    updated_at
)
VALUES
(
    N'PRE-001',
    N'CI-COMPANY-001',
    N'100',
    N'decimal',
    N'EUR',
    '2026-01-01T00:00:00+00:00',
    '2027-01-01T00:00:00+00:00',
    '2026-01-01T00:00:00+00:00',
    '2026-01-01T00:00:00+00:00'
);

SET @configuration_id = SCOPE_IDENTITY();

INSERT INTO eios.parameter_configuration_history
(
    configuration_id,
    parameter_id,
    company_id,
    previous_value,
    new_value,
    changed_by,
    changed_at,
    change_reason
)
VALUES
(
    @configuration_id,
    N'PRE-001',
    N'CI-COMPANY-001',
    NULL,
    N'100',
    N'ci-test',
    '2026-01-01T00:00:00+00:00',
    N'initial configuration'
);

IF NOT EXISTS
(
    SELECT 1
    FROM eios.parameter_configuration_history
    WHERE configuration_id = @configuration_id
      AND parameter_id = N'PRE-001'
      AND company_id = N'CI-COMPANY-001'
)
    THROW 51012, 'Valid history insert failed', 1;

IF EXISTS
(
    SELECT 1
    FROM eios.parameter_configuration
    WHERE company_id = N'CI-COMPANY-001'
      AND parameter_id = N'PRE-001'
      AND valid_from <= '2026-06-01T00:00:00+00:00'
      AND (valid_to IS NULL OR valid_to > '2026-06-01T00:00:00+00:00')
)
    PRINT 'Effective-date lookup: PASS';
ELSE
    THROW 51013, 'Effective-date lookup failed', 1;

BEGIN TRY
    INSERT INTO eios.parameter_configuration
    (
        parameter_id, company_id, value, valid_from, valid_to, created_at, updated_at
    )
    VALUES
    (
        N'PRE-INVALID', N'CI-COMPANY-001', N'1',
        '2027-01-01T00:00:00+00:00',
        '2026-01-01T00:00:00+00:00',
        '2026-01-01T00:00:00+00:00',
        '2026-01-01T00:00:00+00:00'
    );
    THROW 51014, 'Invalid validity was accepted', 1;
END TRY
BEGIN CATCH
    IF ERROR_NUMBER() = 51014
        THROW;
    PRINT 'Invalid validity rejection: PASS';
END CATCH;

ROLLBACK TRANSACTION;

PRINT 'Centro de Parametrización SQL schema validation: PASS';

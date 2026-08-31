/*
EIOS — Centro de Parametrización — SQL Server persistence
Migration: 003
Scope: approved parameter configuration contract

This migration persists configuration state and append-only change history.
It does not create functional authority, rule semantics, decision logic,
or a Company master entity.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF SCHEMA_ID(N'eios') IS NULL
    EXEC(N'CREATE SCHEMA eios');
GO

IF OBJECT_ID(N'eios.parameter_configuration', N'U') IS NULL
BEGIN
    CREATE TABLE eios.parameter_configuration
    (
        configuration_id bigint IDENTITY(1,1) NOT NULL,
        parameter_id nvarchar(64) NOT NULL,
        company_id nvarchar(128) NOT NULL,
        value nvarchar(512) NOT NULL,
        value_type nvarchar(64) NULL,
        unit nvarchar(64) NULL,
        valid_from datetimeoffset(7) NOT NULL,
        valid_to datetimeoffset(7) NULL,
        created_at datetimeoffset(7) NOT NULL,
        updated_at datetimeoffset(7) NOT NULL,

        CONSTRAINT PK_parameter_configuration
            PRIMARY KEY CLUSTERED (configuration_id),
        CONSTRAINT CK_parameter_configuration_parameter_nonempty
            CHECK (LEN(LTRIM(RTRIM(parameter_id))) > 0),
        CONSTRAINT CK_parameter_configuration_company_nonempty
            CHECK (LEN(LTRIM(RTRIM(company_id))) > 0),
        CONSTRAINT CK_parameter_configuration_value_nonempty
            CHECK (LEN(LTRIM(RTRIM(value))) > 0),
        CONSTRAINT CK_parameter_configuration_validity
            CHECK (valid_to IS NULL OR valid_from < valid_to),
        CONSTRAINT CK_parameter_configuration_timestamps
            CHECK (created_at <= updated_at),
        CONSTRAINT CK_parameter_configuration_value_type_nonempty
            CHECK (value_type IS NULL OR LEN(LTRIM(RTRIM(value_type))) > 0),
        CONSTRAINT CK_parameter_configuration_unit_nonempty
            CHECK (unit IS NULL OR LEN(LTRIM(RTRIM(unit))) > 0)
    );
END;
GO

IF OBJECT_ID(N'eios.parameter_configuration_history', N'U') IS NULL
BEGIN
    CREATE TABLE eios.parameter_configuration_history
    (
        history_id bigint IDENTITY(1,1) NOT NULL,
        configuration_id bigint NOT NULL,
        parameter_id nvarchar(64) NOT NULL,
        company_id nvarchar(128) NOT NULL,
        previous_value nvarchar(512) NULL,
        new_value nvarchar(512) NOT NULL,
        changed_by nvarchar(128) NOT NULL,
        changed_at datetimeoffset(7) NOT NULL,
        change_reason nvarchar(512) NOT NULL,

        CONSTRAINT PK_parameter_configuration_history
            PRIMARY KEY CLUSTERED (history_id),
        CONSTRAINT FK_parameter_configuration_history_configuration
            FOREIGN KEY (configuration_id)
            REFERENCES eios.parameter_configuration (configuration_id),
        CONSTRAINT CK_parameter_configuration_history_parameter_nonempty
            CHECK (LEN(LTRIM(RTRIM(parameter_id))) > 0),
        CONSTRAINT CK_parameter_configuration_history_company_nonempty
            CHECK (LEN(LTRIM(RTRIM(company_id))) > 0),
        CONSTRAINT CK_parameter_configuration_history_new_value_nonempty
            CHECK (LEN(LTRIM(RTRIM(new_value))) > 0),
        CONSTRAINT CK_parameter_configuration_history_changed_by_nonempty
            CHECK (LEN(LTRIM(RTRIM(changed_by))) > 0),
        CONSTRAINT CK_parameter_configuration_history_reason_nonempty
            CHECK (LEN(LTRIM(RTRIM(change_reason))) > 0)
    );
END;
GO

/*
The history table is append-only for its application writer role.
This is a deployment-level technical control, not a functional authority.
*/
IF NOT EXISTS
(
    SELECT 1
    FROM sys.database_principals
    WHERE name = N'eios_parameter_configuration_history_writer'
      AND type = 'R'
)
    CREATE ROLE eios_parameter_configuration_history_writer;
GO

GRANT SELECT, INSERT
    ON OBJECT::eios.parameter_configuration_history
    TO eios_parameter_configuration_history_writer;
DENY UPDATE, DELETE
    ON OBJECT::eios.parameter_configuration_history
    TO eios_parameter_configuration_history_writer;
GO

/*
Structural index supporting effective-date lookup.
No business rule is encoded here.
*/
IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_parameter_configuration_lookup'
      AND object_id = OBJECT_ID(N'eios.parameter_configuration')
)
BEGIN
    CREATE INDEX IX_parameter_configuration_lookup
        ON eios.parameter_configuration
        (
            company_id,
            parameter_id,
            valid_from,
            valid_to
        );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_parameter_configuration_history_lookup'
      AND object_id = OBJECT_ID(N'eios.parameter_configuration_history')
)
BEGIN
    CREATE INDEX IX_parameter_configuration_history_lookup
        ON eios.parameter_configuration_history
        (
            company_id,
            parameter_id,
            changed_at
        );
END;
GO

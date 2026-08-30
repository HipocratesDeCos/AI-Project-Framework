/*
EIOS — Decision Versioning persistence
Scope: minimal historical state persistence
SGBD: Microsoft SQL Server 2022
No functional authority is created by this DDL.
*/
SET NOCOUNT ON;
SET XACT_ABORT ON;

IF SCHEMA_ID(N'eios') IS NULL
    EXEC(N'CREATE SCHEMA eios');
GO

CREATE TABLE eios.decision_state
(
    decision_state_record_id bigint IDENTITY(1,1) NOT NULL,
    decision_id nvarchar(64) NOT NULL,
    scenario_id nvarchar(64) NOT NULL,
    data_snapshot_id nvarchar(64) NOT NULL,
    rules_version nvarchar(64) NOT NULL,
    parameters_version nvarchar(64) NOT NULL,
    forecast_version nvarchar(64) NULL,
    rfp_version nvarchar(64) NULL,
    eios_version nvarchar(64) NULL,
    [timestamp] datetimeoffset(7) NOT NULL,
    user_id nvarchar(128) NOT NULL,
    input_fingerprint char(64) NULL,
    trace_id nvarchar(128) NULL,

    CONSTRAINT PK_decision_state PRIMARY KEY CLUSTERED (decision_state_record_id),

    CONSTRAINT CK_decision_state_decision_id_nonempty
        CHECK (LEN(LTRIM(RTRIM(decision_id))) > 0),
    CONSTRAINT CK_decision_state_scenario_id_nonempty
        CHECK (LEN(LTRIM(RTRIM(scenario_id))) > 0),
    CONSTRAINT CK_decision_state_data_snapshot_id_nonempty
        CHECK (LEN(LTRIM(RTRIM(data_snapshot_id))) > 0),
    CONSTRAINT CK_decision_state_rules_version_nonempty
        CHECK (LEN(LTRIM(RTRIM(rules_version))) > 0),
    CONSTRAINT CK_decision_state_parameters_version_nonempty
        CHECK (LEN(LTRIM(RTRIM(parameters_version))) > 0),
    CONSTRAINT CK_decision_state_user_id_nonempty
        CHECK (LEN(LTRIM(RTRIM(user_id))) > 0),
    CONSTRAINT CK_decision_state_timestamp_utc
        CHECK (DATEPART(TZOFFSET, [timestamp]) = 0),
    CONSTRAINT CK_decision_state_fingerprint_hex
        CHECK (
            input_fingerprint IS NULL
            OR (
                LEN(input_fingerprint) = 64
                AND input_fingerprint NOT LIKE '%[^0-9A-Fa-f]%'
            )
        ),
    CONSTRAINT CK_decision_state_forecast_version_nonempty
        CHECK (forecast_version IS NULL OR LEN(LTRIM(RTRIM(forecast_version))) > 0),
    CONSTRAINT CK_decision_state_rfp_version_nonempty
        CHECK (rfp_version IS NULL OR LEN(LTRIM(RTRIM(rfp_version))) > 0),
    CONSTRAINT CK_decision_state_eios_version_nonempty
        CHECK (eios_version IS NULL OR LEN(LTRIM(RTRIM(eios_version))) > 0),
    CONSTRAINT CK_decision_state_trace_id_nonempty
        CHECK (trace_id IS NULL OR LEN(LTRIM(RTRIM(trace_id))) > 0)
);
GO

/*
Append-only operational boundary.
The role is a deployment-level technical mechanism, not a functional authority.
The application writer receives SELECT/INSERT only; UPDATE/DELETE are explicitly denied.
*/
IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = N'eios_decision_state_writer' AND type = 'R')
    CREATE ROLE eios_decision_state_writer;
GO

GRANT SELECT, INSERT ON OBJECT::eios.decision_state TO eios_decision_state_writer;
DENY UPDATE, DELETE ON OBJECT::eios.decision_state TO eios_decision_state_writer;
GO

/*
EIOS — SQL Server C0 Persistence Slice
Migration: 001
Scope: C0 contracts already materialized

This script persists existing contracts. It does not create functional semantics.
*/

IF SCHEMA_ID(N'eios') IS NULL
    EXEC(N'CREATE SCHEMA eios');
GO

IF OBJECT_ID(N'eios.c0_input', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_input
    (
        input_row_id       bigint IDENTITY(1,1) NOT NULL,
        decision_id        nvarchar(64) NOT NULL,
        scenario_id        nvarchar(64) NOT NULL,
        article_id         nvarchar(64) NOT NULL,
        supplier_id        nvarchar(64) NOT NULL,
        quantity           decimal(38,4) NOT NULL,
        unit_price         decimal(38,4) NOT NULL,
        currency           char(3) NOT NULL,
        operation_date     date NOT NULL,
        input_fingerprint  char(64) NOT NULL,

        CONSTRAINT PK_c0_input PRIMARY KEY CLUSTERED (input_row_id),
        CONSTRAINT UQ_c0_input_fingerprint UNIQUE (input_fingerprint),
        CONSTRAINT CK_c0_input_quantity CHECK (quantity > 0),
        CONSTRAINT CK_c0_input_unit_price CHECK (unit_price >= 0),
        CONSTRAINT CK_c0_input_currency CHECK (currency = 'EUR'),
        CONSTRAINT CK_c0_input_fingerprint CHECK
            (input_fingerprint NOT LIKE '%[^0-9A-Fa-f]%')
    );
END;
GO

IF OBJECT_ID(N'eios.c0_context', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_context
    (
        context_row_id      bigint IDENTITY(1,1) NOT NULL,
        decision_id         nvarchar(64) NOT NULL,
        scenario_id         nvarchar(64) NOT NULL,
        rules_version       nvarchar(64) NOT NULL,
        parameters_version  nvarchar(64) NOT NULL,
        data_snapshot_id    nvarchar(64) NOT NULL,

        CONSTRAINT PK_c0_context PRIMARY KEY CLUSTERED (context_row_id)
    );
END;
GO

IF OBJECT_ID(N'eios.c0_evidence', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_evidence
    (
        evidence_id         nvarchar(64) NOT NULL,
        source_type         nvarchar(64) NOT NULL,
        source_ref          nvarchar(256) NOT NULL,
        captured_at         date NOT NULL,
        state               varchar(16) NOT NULL,
        demonstration_ref   nvarchar(256) NULL,

        CONSTRAINT PK_c0_evidence PRIMARY KEY CLUSTERED (evidence_id),
        CONSTRAINT CK_c0_evidence_state
            CHECK (state IN ('DEMONSTRATED', 'GAP')),
        CONSTRAINT CK_c0_evidence_demonstration
            CHECK
            (
                (state = 'DEMONSTRATED' AND demonstration_ref IS NOT NULL)
                OR
                (state = 'GAP')
            )
    );
END;
GO

IF OBJECT_ID(N'eios.c0_evidence_validation', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_evidence_validation
    (
        evidence_id  nvarchar(64) NOT NULL,
        status       varchar(8) NOT NULL,
        reason       nvarchar(256) NOT NULL,

        CONSTRAINT PK_c0_evidence_validation PRIMARY KEY CLUSTERED (evidence_id),
        CONSTRAINT FK_c0_evidence_validation_evidence
            FOREIGN KEY (evidence_id)
            REFERENCES eios.c0_evidence (evidence_id),
        CONSTRAINT CK_c0_evidence_validation_status
            CHECK (status IN ('VALID', 'INVALID'))
    );
END;
GO

IF OBJECT_ID(N'eios.c0_rule_contract', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_rule_contract
    (
        rule_id            nvarchar(64) NOT NULL,
        version            nvarchar(64) NOT NULL,
        requires_evidence  bit NOT NULL,

        CONSTRAINT PK_c0_rule_contract PRIMARY KEY CLUSTERED (rule_id, version)
    );
END;
GO

IF OBJECT_ID(N'eios.c0_assessment', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_assessment
    (
        assessment_row_id  bigint IDENTITY(1,1) NOT NULL,
        rule_id            nvarchar(64) NOT NULL,
        status             varchar(16) NOT NULL,
        outcome            bit NULL,
        reason             nvarchar(256) NOT NULL,

        CONSTRAINT PK_c0_assessment PRIMARY KEY CLUSTERED (assessment_row_id),
        CONSTRAINT CK_c0_assessment_status
            CHECK (status IN ('EVALUABLE', 'NOT_EVALUABLE')),
        CONSTRAINT CK_c0_assessment_status_outcome
            CHECK
            (
                (status = 'EVALUABLE' AND outcome IS NOT NULL)
                OR
                (status = 'NOT_EVALUABLE' AND outcome IS NULL)
            )
    );
END;
GO

IF OBJECT_ID(N'eios.c0_assessment_evidence', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_assessment_evidence
    (
        assessment_row_id  bigint NOT NULL,
        evidence_ordinal   int NOT NULL,
        evidence_id        nvarchar(64) NOT NULL,

        CONSTRAINT PK_c0_assessment_evidence
            PRIMARY KEY CLUSTERED (assessment_row_id, evidence_ordinal),
        CONSTRAINT UQ_c0_assessment_evidence
            UNIQUE (assessment_row_id, evidence_id),
        CONSTRAINT FK_c0_assessment_evidence_assessment
            FOREIGN KEY (assessment_row_id)
            REFERENCES eios.c0_assessment (assessment_row_id),
        CONSTRAINT FK_c0_assessment_evidence_evidence
            FOREIGN KEY (evidence_id)
            REFERENCES eios.c0_evidence (evidence_id),
        CONSTRAINT CK_c0_assessment_evidence_ordinal
            CHECK (evidence_ordinal >= 0)
    );
END;
GO

IF OBJECT_ID(N'eios.c0_trace', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_trace
    (
        trace_id             nvarchar(128) NOT NULL,
        decision_id          nvarchar(64) NOT NULL,
        scenario_id          nvarchar(64) NOT NULL,
        rules_version        nvarchar(64) NOT NULL,
        parameters_version   nvarchar(64) NOT NULL,
        data_snapshot_id     nvarchar(64) NOT NULL,
        input_fingerprint    char(64) NOT NULL,
        rule_id              nvarchar(64) NOT NULL,
        assessment_status    varchar(16) NOT NULL,
        assessment_outcome   bit NULL,
        created_at           datetimeoffset(7) NOT NULL,

        CONSTRAINT PK_c0_trace PRIMARY KEY CLUSTERED (trace_id),
        CONSTRAINT CK_c0_trace_status
            CHECK (assessment_status IN ('EVALUABLE', 'NOT_EVALUABLE')),
        CONSTRAINT CK_c0_trace_status_outcome
            CHECK
            (
                (assessment_status = 'EVALUABLE' AND assessment_outcome IS NOT NULL)
                OR
                (assessment_status = 'NOT_EVALUABLE' AND assessment_outcome IS NULL)
            ),
        CONSTRAINT CK_c0_trace_fingerprint
            CHECK (input_fingerprint NOT LIKE '%[^0-9A-Fa-f]%')
    );
END;
GO

IF OBJECT_ID(N'eios.c0_trace_evidence', N'U') IS NULL
BEGIN
    CREATE TABLE eios.c0_trace_evidence
    (
        trace_id          nvarchar(128) NOT NULL,
        evidence_ordinal  int NOT NULL,
        evidence_id       nvarchar(64) NOT NULL,

        CONSTRAINT PK_c0_trace_evidence
            PRIMARY KEY CLUSTERED (trace_id, evidence_ordinal),
        CONSTRAINT UQ_c0_trace_evidence
            UNIQUE (trace_id, evidence_id),
        CONSTRAINT FK_c0_trace_evidence_trace
            FOREIGN KEY (trace_id)
            REFERENCES eios.c0_trace (trace_id),
        CONSTRAINT FK_c0_trace_evidence_evidence
            FOREIGN KEY (evidence_id)
            REFERENCES eios.c0_evidence (evidence_id),
        CONSTRAINT CK_c0_trace_evidence_ordinal
            CHECK (evidence_ordinal >= 0)
    );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_c0_input_decision_scenario'
      AND object_id = OBJECT_ID(N'eios.c0_input')
)
BEGIN
    CREATE INDEX IX_c0_input_decision_scenario
        ON eios.c0_input (decision_id, scenario_id);
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_c0_context_decision_scenario_versions'
      AND object_id = OBJECT_ID(N'eios.c0_context')
)
BEGIN
    CREATE INDEX IX_c0_context_decision_scenario_versions
        ON eios.c0_context
        (
            decision_id,
            scenario_id,
            rules_version,
            parameters_version,
            data_snapshot_id
        );
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_c0_assessment_rule_status'
      AND object_id = OBJECT_ID(N'eios.c0_assessment')
)
BEGIN
    CREATE INDEX IX_c0_assessment_rule_status
        ON eios.c0_assessment (rule_id, status);
END;
GO

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_c0_trace_decision_scenario_created'
      AND object_id = OBJECT_ID(N'eios.c0_trace')
)
BEGIN
    CREATE INDEX IX_c0_trace_decision_scenario_created
        ON eios.c0_trace (decision_id, scenario_id, created_at);
END;
GO

/*
No triggers, procedures, temporal tables, ORM mappings or application
connections are created by this migration.
*/

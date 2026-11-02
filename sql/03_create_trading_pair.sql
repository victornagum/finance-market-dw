
-- =============================================
-- Table: config.TradingPair
-- Purpose: Manage active Binance trading pairs
-- =============================================

IF SCHEMA_ID('config') IS NULL
    EXEC('CREATE SCHEMA config');
GO

IF OBJECT_ID('config.TradingPair', 'U') IS NULL
BEGIN
    CREATE TABLE config.TradingPair
    (
        PairKey INT IDENTITY(1,1) NOT NULL,
        Symbol VARCHAR(20) NOT NULL,
        BaseAsset VARCHAR(10) NOT NULL,
        QuoteAsset VARCHAR(10) NOT NULL,
        IsActive BIT NOT NULL
            CONSTRAINT DF_TradingPair_IsActive DEFAULT (1),
        CreatedAt DATETIME2(0) NOT NULL
            CONSTRAINT DF_TradingPair_CreatedAt DEFAULT (SYSUTCDATETIME()),

        CONSTRAINT PK_TradingPair
            PRIMARY KEY (PairKey),

        CONSTRAINT UQ_TradingPair_Symbol
            UNIQUE (Symbol)
    );
END;
GO


IF OBJECT_ID('dw.FactMarketKline', 'U') IS NULL
BEGIN
    CREATE TABLE dw.FactMarketKline (
        OpenTime DATETIME2(3) NOT NULL,
        CloseTime DATETIME2(3) NOT NULL,

        OpenPrice DECIMAL(19, 8) NOT NULL,
        HighPrice DECIMAL(19, 8) NOT NULL,
        LowPrice DECIMAL(19, 8) NOT NULL,
        ClosePrice DECIMAL(19, 8) NOT NULL,

        Volume DECIMAL(28, 8) NOT NULL,
        QuoteVolume DECIMAL(28, 8) NOT NULL,
        NumberOfTrades BIGINT NOT NULL,
        TakerBuyBaseVolume DECIMAL(28, 8) NOT NULL,
        TakerBuyQuoteVolume DECIMAL(28, 8) NOT NULL,

        CONSTRAINT PK_FactMarketKline
            PRIMARY KEY (OpenTime)
    );
END;
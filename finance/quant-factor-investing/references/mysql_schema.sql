-- AlphaSeeker MySQL Database Schema (localhost:3306/alphaseeker)
-- Last updated: 2026-06-09

-- 股票基础信息
CREATE TABLE IF NOT EXISTS stocks_info (
    stock_code VARCHAR(10) NOT NULL PRIMARY KEY,
    stock_name VARCHAR(50) NOT NULL,
    industry VARCHAR(50) DEFAULT NULL,
    exchange VARCHAR(10) DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 财务指标（多期，按stock_code+report_date去重）
CREATE TABLE IF NOT EXISTS financial_indicators (
    record_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    report_date DATE NOT NULL,
    roe DECIMAL(12,4),
    net_profit_growth DECIMAL(12,4),
    debt_to_equity DECIMAL(12,4),
    gross_margin DECIMAL(12,4),
    pe DECIMAL(12,4),
    pb DECIMAL(12,4),
    market_cap BIGINT,
    eps DECIMAL(10,4),
    bvps DECIMAL(10,4),
    cash_to_income DECIMAL(12,4),
    asset_turnover DECIMAL(12,4),
    dividend_yield DECIMAL(8,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stock_code (stock_code),
    INDEX idx_report_date (report_date),
    FOREIGN KEY (stock_code) REFERENCES stocks_info(stock_code) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 日线行情
CREATE TABLE IF NOT EXISTS stock_prices (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    stock_code VARCHAR(10) NOT NULL,
    trade_date DATE NOT NULL,
    open_price DECIMAL(12,4),
    close_price DECIMAL(12,4),
    high_price DECIMAL(12,4),
    low_price DECIMAL(12,4),
    volume BIGINT,
    market_cap BIGINT,
    pe_ratio DECIMAL(12,4),
    pb_ratio DECIMAL(12,4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stock_code (stock_code),
    INDEX idx_trade_date (trade_date),
    UNIQUE KEY uk_code_date (stock_code, trade_date)
) ENGINE=InnoDB;

-- 行业指标
CREATE TABLE IF NOT EXISTS industry_metrics (
    -- (schema not fully documented yet)
    id INT AUTO_INCREMENT PRIMARY KEY
) ENGINE=InnoDB;

-- 数据量参考 (2026-06-09):
-- stocks_info: 5,666 只
-- financial_indicators: 27,988 条 (含多期报告)
-- stock_prices: 6,487,289 条 (~5,000只 × ~1,300交易日)
-- 2025年报覆盖: 5,548 只
-- 最新价格日期: 2026-06-09

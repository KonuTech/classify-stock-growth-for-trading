# Database Design Comparison: Unified vs Normalized

## Overview
This document compares two database design approaches for the stock data ETL pipeline project.

## Quick Decision Matrix

| Criteria | Unified Approach | Normalized Approach | Winner |
|----------|------------------|-------------------|---------|
| **Query Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Unified |
| **Data Integrity** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Normalized |
| **ETL Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Unified |
| **Future Extensibility** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Normalized |
| **Storage Efficiency** | ⭐⭐⭐ | ⭐⭐⭐⭐ | Normalized |
| **Development Speed** | ⭐⭐⭐⭐⭐ | ⭐⭐ | Unified |
| **Maintenance Cost** | ⭐⭐⭐⭐ | ⭐⭐⭐ | Unified |
| **Type Safety** | ⭐⭐ | ⭐⭐⭐⭐⭐ | Normalized |

## Detailed Comparison

### Performance Analysis

#### Unified Approach
```sql
-- Single table query - very fast
SELECT ticker, close_price, volume 
FROM daily_prices 
WHERE trading_date_local = '2024-01-15'
  AND instrument_type = 'stock';

-- Cross-asset analysis - simple join
SELECT s.close_price / i.close_value as relative_performance
FROM daily_prices s, daily_prices i
WHERE s.ticker = 'XTB' AND i.ticker = 'WIG'
  AND s.trading_date_local = i.trading_date_local;
```

#### Normalized Approach
```sql
-- Requires joins but type-specific optimization
SELECT bi.symbol, sp.close_price, sp.volume
FROM base_instruments bi
JOIN stocks s ON bi.id = s.instrument_id
JOIN stock_prices sp ON s.id = sp.stock_id
WHERE sp.trading_date_local = '2024-01-15';

-- Cross-asset analysis - more complex but clearer intent
SELECT sp.close_price / ip.close_value as relative_performance
FROM base_instruments bi1
JOIN stocks s ON bi1.id = s.instrument_id
JOIN stock_prices sp ON s.id = sp.stock_id,
     base_instruments bi2
JOIN indices i ON bi2.id = i.instrument_id  
JOIN index_prices ip ON i.id = ip.index_id
WHERE bi1.symbol = 'XTB' AND bi2.symbol = 'WIG'
  AND sp.trading_date_local = ip.trading_date_local;
```

### Data Integrity Analysis

#### Unified Approach Issues
```sql
-- Problem: Can't enforce stock-specific constraints
-- This should be invalid for an index but system allows it
INSERT INTO daily_prices (ticker, instrument_type, trading_date_local, volume)
VALUES ('WIG', 'index', '2024-01-15', 0); -- Indices shouldn't have 0 volume

-- Problem: Mixed validation rules
-- PE ratio makes sense for stocks but not indices
ALTER TABLE instruments ADD COLUMN pe_ratio DECIMAL(8,2);
-- Now indices have meaningless PE ratio columns
```

#### Normalized Approach Benefits
```sql
-- Type-specific constraints prevent invalid data
ALTER TABLE stock_prices ADD CONSTRAINT positive_volume 
    CHECK (volume >= 0);

ALTER TABLE index_prices ADD CONSTRAINT meaningful_market_cap
    CHECK (total_market_cap > 0);

-- Impossible to insert invalid combinations
-- This will fail at schema level:
INSERT INTO index_prices (index_id, volume) VALUES (1, 1000);
-- ERROR: column "volume" does not exist
```

### ETL Pipeline Complexity

#### Unified Approach - Simple Pipeline
```python
def process_stooq_data(file_path: str, instrument_type: str):
    """Single pipeline handles all instrument types"""
    df = pd.read_csv(file_path)
    df['instrument_type'] = instrument_type
    
    # One insert statement for all types
    df.to_sql('daily_prices', engine, if_exists='append')
```

#### Normalized Approach - Type-Specific Pipelines
```python
def process_stock_data(file_path: str):
    """Dedicated stock processing"""
    df = pd.read_csv(file_path)
    
    # Insert into base_instruments first
    instrument_id = insert_base_instrument(df.iloc[0])
    
    # Then into stocks table
    stock_id = insert_stock(instrument_id, df.iloc[0])
    
    # Finally into stock_prices
    df['stock_id'] = stock_id
    df.to_sql('stock_prices', engine, if_exists='append')

def process_index_data(file_path: str):
    """Dedicated index processing with different logic"""
    # Similar but different processing...
```

### Future Extensibility Scenarios

#### Adding Options Trading Support

**Unified Approach:**
```sql
-- Adds columns that don't apply to stocks/indices
ALTER TABLE instruments ADD COLUMN strike_price DECIMAL(10,4);
ALTER TABLE instruments ADD COLUMN expiry_date DATE;
ALTER TABLE instruments ADD COLUMN option_type CHAR(1);

-- Most rows will have NULL values for these columns
-- Violates normalization principles
```

**Normalized Approach:**
```sql
-- Clean, separate table for options
CREATE TABLE options (
    id SERIAL PRIMARY KEY,
    instrument_id INTEGER REFERENCES base_instruments(id),
    underlying_stock_id INTEGER REFERENCES stocks(id),
    option_type CHAR(1) CHECK (option_type IN ('C', 'P')),
    strike_price DECIMAL(10,4) NOT NULL,
    expiry_date DATE NOT NULL
);

-- No impact on existing stock/index tables
```

## Recommendations

### Choose Unified Approach If:
- **Primary focus on stocks and indices only**
- **High-frequency analytical queries across asset types**
- **Small development team needing rapid prototyping**
- **Performance is critical, complexity is manageable**
- **Limited timeline for initial delivery**

### Choose Normalized Approach If:
- **Plan to support multiple instrument types (options, futures, bonds)**
- **Data integrity is paramount (financial regulatory requirements)**
- **Long-term maintainability is important**
- **Team has strong database design expertise**
- **System will grow significantly over time**

## Hybrid Recommendation

For your current project scope, consider a **phased approach**:

1. **Phase 1**: Start with unified approach for stocks/indices
2. **Phase 2**: Migrate to normalized when adding new instrument types

### Migration Path
```sql
-- Future migration strategy
CREATE TABLE stocks AS 
SELECT * FROM instruments WHERE instrument_type = 'stock';

CREATE TABLE indices AS 
SELECT * FROM instruments WHERE instrument_type = 'index';

-- Maintain views for backward compatibility
CREATE VIEW unified_instruments AS
SELECT 'stock' as source_table, * FROM stocks
UNION ALL
SELECT 'index' as source_table, * FROM indices;
```

## Conclusion

Both approaches are valid for different scenarios. The unified approach offers immediate productivity gains and simpler operations, while the normalized approach provides better long-term scalability and data integrity. 

**For your current project focusing on Polish stock market data (stocks + indices), the unified approach is recommended** for faster development and simpler operations, with the option to normalize later as requirements expand.
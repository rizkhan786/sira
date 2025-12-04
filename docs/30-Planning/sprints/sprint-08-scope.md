# Sprint 8 Scope: Trading Data Foundation & Backtesting Engine

**Sprint Number:** 8  
**Phase:** Phase 4 (Trading & Financial Markets)  
**Duration:** 2 weeks (14 days)  
**Start Date:** TBD (after Sprint 7)  
**End Date:** TBD  
**Status:** Planning  
**Branch:** sprint-08

---

## Sprint Goal

**Build the foundational infrastructure for SIRA trading signals: CSV data ingestion, technical indicator calculation, time-series storage, and a production-ready backtesting engine with strict no-lookahead bias prevention.**

**Success Criteria:** Successfully ingest gold OHLC data, calculate 15+ technical indicators across 3 timeframes (daily, weekly, 4h), and run first backtest with walk-forward validation.

---

## Sprint Overview

This sprint establishes the **data and testing foundation** for SIRA's trading capabilities. We're building the infrastructure needed to:

1. Ingest historical OHLC data from CSV files
2. Calculate technical indicators without lookahead bias
3. Store data in time-series optimized format
4. Run rigorous backtests with transaction costs
5. Generate performance metrics and equity curves

**What We're Building:**
- Data ingestion pipeline (CSV → database)
- Technical indicator calculator (RSI, MACD, BB, ATR, etc.)
- Backtesting engine with no-lookahead enforcement
- Performance metrics module (Sharpe, drawdown, win rate, etc.)
- Walk-forward testing framework

---

## Sprint Deliverables

### Core Deliverables (3 Total)

#### DEL-045: Trading Data Ingestion Pipeline
**Priority:** Should Have  
**Estimated Effort:** 2 days  
**Dependencies:** None

**Scope:**
- Parse CSV files with OHLC data (Open, High, Low, Close)
- Calculate 15+ technical indicators
- Support 3 timeframes: daily, weekly, 4-hourly
- Store in PostgreSQL with TimescaleDB extension
- Handle missing data and gaps

**CSV Format:**
```csv
date,open,high,low,close
2020-01-02,1520.50,1535.20,1518.00,1532.75
2020-01-03,1532.75,1540.10,1525.30,1538.20
```

**Technical Indicators to Calculate:**
1. **Trend:** SMA (20, 50, 200), EMA (12, 26)
2. **Momentum:** RSI(14), Stochastic(14,3,3), MACD(12,26,9)
3. **Volatility:** Bollinger Bands(20,2), ATR(14)
4. **Price Action:** Higher highs/lows, support/resistance levels

**Acceptance Criteria:**
- AC-131: Ingests CSV OHLC data for gold (XAUUSD.FXCM)
- AC-132: Calculates 15+ technical indicators correctly
- AC-133: Handles daily, weekly, 4-hourly timeframes
- AC-134: Detects and handles missing data, gaps
- AC-135: Stores in PostgreSQL TimescaleDB format

**Tasks:**
1. Create `src/trading/data_ingestion.py` module
2. Implement CSV parser with date validation
3. Build technical indicator library (`indicators.py`)
4. Set up TimescaleDB table schema
5. Create ingestion script: `scripts/ingest_market_data.py`
6. Write unit tests for indicators (ensure no lookahead)
7. Create `data/trading/` directory structure

---

#### DEL-046: Trading Backtesting Engine
**Priority:** Must Have  
**Estimated Effort:** 4 days  
**Dependencies:** DEL-045 (needs data)

**Scope:**
- Historical simulation engine
- **CRITICAL:** Strict no-lookahead enforcement (all features shifted by 1 bar)
- Walk-forward testing (expanding window)
- Transaction cost modeling (0.1% commission + 0.05% slippage)
- Performance metrics calculator
- Equity curve and drawdown visualization

**No-Lookahead Prevention:**
```python
# WRONG: Uses today's close to generate today's signal
signal = strategy(df['close'])

# CORRECT: Uses yesterday's close to generate today's signal  
signal = strategy(df['close'].shift(1))

# All indicators must be shifted
features = {
    'rsi': df['rsi'].shift(1),      # Yesterday's RSI
    'macd': df['macd'].shift(1),    # Yesterday's MACD
    'close': df['close'].shift(1)   # Yesterday's close
}
```

**Walk-Forward Testing:**
```
Phase 1:
  Train: 2000-2010 (10 years) → Learn patterns
  Test:  2011-2012 (2 years)  → Validate

Phase 2:
  Train: 2000-2012 (12 years) → Re-learn with new data
  Test:  2013-2014 (2 years)  → Validate

...continue through 2023
```

**Transaction Costs:**
```python
costs = {
    'commission': 0.001,   # 0.1% per trade
    'slippage': 0.0005     # 0.05% (bid-ask spread)
}
# Total round-trip cost: 0.3%
```

**Performance Metrics:**
1. **Return:** Total return, CAGR
2. **Risk:** Max drawdown, volatility (std dev)
3. **Risk-Adjusted:** Sharpe ratio, Sortino ratio, Calmar ratio
4. **Trade Stats:** Win rate, profit factor, avg win/loss
5. **Consistency:** Monthly win rate, longest drawdown period

**Acceptance Criteria:**
- AC-136: Strict no-lookahead enforcement (all features shifted)
- AC-137: Walk-forward testing with expanding window
- AC-138: Models transaction costs (0.3% round-trip)
- AC-139: Tracks 15+ performance metrics
- AC-140: Generates equity curve, drawdown chart, trade log

**Tasks:**
1. Create `src/trading/backtesting.py` core engine
2. Implement `src/trading/portfolio.py` (position tracking)
3. Build `src/trading/metrics.py` (performance calculations)
4. Write **critical test:** `tests/test_no_lookahead.py`
5. Implement walk-forward testing logic
6. Create equity curve and drawdown plotter
7. Generate trade log CSV export

**Critical Test (test_no_lookahead.py):**
```python
def test_no_lookahead():
    """Ensure indicators don't use future data"""
    data = load_data('2020-01-01', '2020-12-31')
    
    # Calculate indicator on full dataset
    full_rsi = calculate_rsi(data)
    
    # Calculate indicator incrementally (bar by bar)
    incremental_rsi = []
    for i in range(len(data)):
        rsi = calculate_rsi(data[:i+1])
        incremental_rsi.append(rsi[-1])
    
    # If values don't match, indicator is repainting!
    assert np.allclose(full_rsi, incremental_rsi)
```

---

#### DEL-044: Publication-Quality Benchmark Report (Optional)
**Priority:** Could Have  
**Estimated Effort:** 1 day (if time permits)  
**Dependencies:** Sprint 5 results

**Scope:**
- Deferred from Sprint 5 - only do if SIRA shows strong benchmark results
- Full 30-50 page report with visualizations
- Interactive HTML dashboard

**Note:** Focus on core trading deliverables. Only attempt this if Sprint 8 work completes ahead of schedule.

---

## Sprint Metrics

**Total Deliverables:** 3 (2 Must Have, 1 Could Have)  
**Total Acceptance Criteria:** 10 (core trading deliverables)  
**Estimated Effort:** 6-7 days (comfortably fits 14-day sprint)

### Priority Breakdown
- **Must Have:** DEL-046 (Backtesting) - 4 days
- **Should Have:** DEL-045 (Data Ingestion) - 2 days
- **Could Have:** DEL-044 (Benchmark Report) - 1 day (optional)

### Recommended Sprint Timeline

**Week 1: Data Foundation**
- **Day 1-2:** DEL-045 - Data ingestion pipeline
  - Day 1: CSV parser + TimescaleDB setup
  - Day 2: Technical indicators + validation
- **Day 3-4:** Start DEL-046 - Backtesting core engine
  - Day 3: Portfolio tracking + position management
  - Day 4: No-lookahead enforcement + tests
- **Day 5:** DEL-046 continued - Transaction costs
  - Friday: Commission/slippage modeling

**Week 2: Backtesting & Validation**
- **Day 8-9:** DEL-046 continued - Performance metrics
  - Day 8: Metrics calculator (Sharpe, drawdown, etc.)
  - Day 9: Equity curve + visualization
- **Day 10:** DEL-046 - Walk-forward testing
  - Day 10: Walk-forward framework
- **Day 11-12:** Testing & Validation
  - Day 11: Unit tests (especially test_no_lookahead.py)
  - Day 12: Integration testing with real data
- **Day 13:** First backtest run (simple buy-and-hold)
- **Day 14:** Sprint review + documentation

---

## Expected Results

### After Sprint 8, You Will Have:

**1. Data Infrastructure:**
- Gold OHLC data ingested (20 years: 2000-2023)
- 15+ technical indicators calculated
- 3 timeframes stored: daily, weekly, 4-hourly
- PostgreSQL TimescaleDB optimized storage

**2. Backtesting Engine:**
- Production-ready backtesting framework
- No-lookahead bias prevention (tested)
- Transaction cost modeling
- Walk-forward testing capability
- 15+ performance metrics

**3. First Backtest Results:**
- Simple buy-and-hold strategy on gold
- Baseline performance metrics
- Equity curve visualization
- Trade log CSV

**Example Output:**
```
=== Gold Buy-and-Hold Backtest (2000-2023) ===

Returns:
- Total Return: +325.4%
- CAGR: 6.3%

Risk:
- Max Drawdown: -45.2% (2011-2015)
- Volatility: 18.7% annualized

Risk-Adjusted:
- Sharpe Ratio: 0.98
- Sortino Ratio: 1.42
- Calmar Ratio: 0.14

Trade Statistics:
- Buy-and-hold: 1 entry, 1 exit
- Hold period: 23 years
- Transaction costs: 0.3% (negligible)
```

This becomes the **baseline** that SIRA must beat in Sprint 9-10.

---

## Success Criteria

### Sprint 8 Complete When:
1. ✅ Gold CSV data ingested successfully
2. ✅ 15+ technical indicators calculated correctly
3. ✅ Data available in 3 timeframes (daily, weekly, 4h)
4. ✅ Backtesting engine operational
5. ✅ No-lookahead test passes (CRITICAL)
6. ✅ Transaction costs modeled (0.3% round-trip)
7. ✅ Performance metrics calculated (15+ metrics)
8. ✅ Equity curve and drawdown chart generated
9. ✅ First backtest completed (buy-and-hold baseline)
10. ✅ Walk-forward testing framework ready

### Quality Gates
- All unit tests pass (especially `test_no_lookahead.py`)
- Indicators match reference implementations (TA-Lib or pandas-ta)
- Backtesting results are reproducible (same data = same results)
- No data leakage detected (manual code review)
- Performance is acceptable (<1 second per 1000 bars)

---

## Data Requirements

### What You Need to Provide

**File:** `data/trading/XAUUSD_FXCM_daily.csv`
```csv
date,open,high,low,close
2000-01-03,284.50,288.25,282.10,287.30
2000-01-04,287.30,290.50,285.75,288.90
...
2023-12-29,2070.50,2082.30,2065.10,2078.45
```

**Timeframes Needed:**
1. **Daily:** `XAUUSD_FXCM_daily.csv` (~6,000 rows for 23 years)
2. **Weekly:** `XAUUSD_FXCM_weekly.csv` (~1,200 rows)
3. **4-Hourly:** `XAUUSD_FXCM_4h.csv` (~33,000 rows)

**Data Quality Requirements:**
- Date format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
- No missing OHLC values (or clearly marked as NaN)
- Sorted by date (ascending)
- Prices in USD per ounce

---

## Risks & Mitigation

### Risk 1: Lookahead Bias
**Impact:** High (invalidates all backtest results)  
**Mitigation:**
- Mandatory `test_no_lookahead.py` test
- Code review focusing on `.shift(1)` usage
- Manual verification of first 10 trades

### Risk 2: Data Quality Issues
**Impact:** Medium (incorrect indicators)  
**Mitigation:**
- Validate against reference implementations (TA-Lib)
- Compare RSI/MACD values to TradingView
- Spot-check 5 random dates

### Risk 3: Performance Bottleneck
**Impact:** Low (slow backtests)  
**Mitigation:**
- Use vectorized pandas operations
- TimescaleDB for fast time-series queries
- Profile code and optimize if needed

---

## Technical Stack

### New Technologies This Sprint
- **TimescaleDB:** PostgreSQL extension for time-series data
- **pandas-ta or TA-Lib:** Technical indicator libraries

### Installation
```bash
# Install TimescaleDB extension (already have PostgreSQL)
# In PostgreSQL:
CREATE EXTENSION IF NOT EXISTS timescaledb;

# Python packages
pip install pandas-ta  # or ta-lib
pip install matplotlib seaborn  # for visualizations
```

### Database Schema
```sql
CREATE TABLE market_data (
    time TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    PRIMARY KEY (time, instrument, timeframe)
);

SELECT create_hypertable('market_data', 'time');

CREATE TABLE indicators (
    time TIMESTAMPTZ NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    timeframe VARCHAR(10) NOT NULL,
    rsi_14 DECIMAL(5,2),
    macd DECIMAL(10,4),
    macd_signal DECIMAL(10,4),
    bb_upper DECIMAL(10,2),
    bb_middle DECIMAL(10,2),
    bb_lower DECIMAL(10,2),
    atr_14 DECIMAL(10,4),
    PRIMARY KEY (time, instrument, timeframe)
);

SELECT create_hypertable('indicators', 'time');
```

---

## Next Steps After Sprint 8

### Sprint 9: Trading Strategy & Pattern Learning
- DEL-047: SIRA Trading Strategy Reasoning (5 days)
- DEL-048: Trading Pattern Learning System (3 days)

### Sprint 10: Comprehensive Backtesting
- DEL-049: Multi-Instrument Backtest Suite (4 days)

---

## Documentation to Create

1. **Data Ingestion Guide:** How to add new instruments/timeframes
2. **Indicator Reference:** List of all 15+ indicators with formulas
3. **Backtesting User Guide:** How to run a backtest
4. **No-Lookahead Best Practices:** Code patterns to avoid bias
5. **Performance Metrics Glossary:** Explanation of Sharpe, Sortino, etc.

---

## Questions to Address During Sprint

1. Should we add volume data if available?
2. Which indicator library: pandas-ta or TA-Lib?
3. What timezone for timestamps (UTC vs market local)?
4. How to handle holidays/weekends in data?
5. Should we split data into train/test in database or in code?

---

## Sprint Retrospective Topics

- Was 2 days enough for data ingestion?
- Did no-lookahead test catch any bugs?
- Performance acceptable for 20 years of data?
- Any missing indicators we need?
- Ready to move to Sprint 9 (strategy implementation)?

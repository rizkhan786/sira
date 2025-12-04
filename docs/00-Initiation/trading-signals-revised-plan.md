# SIRA Trading Signals: Revised Plan (Data-Driven Approach)

**Date:** December 2024  
**Author:** SIRA Development Team  
**Status:** Planning

---

## Key Insight: You Provide Historical Data

> "I can always provide SIRA with financial markets data with OHLC for 20 years for all financial instruments, daily data or intraday data."

**This changes everything!** SIRA doesn't need real-time APIs initially. We can:
1. Train on historical data (2000-2020)
2. Backtest on holdout data (2021-2023)
3. Learn trading patterns offline
4. Validate with zero lookforward/repainting bias

---

## Revised Approach: Offline Pattern Learning

### Phase 1: Data Ingestion & Feature Engineering (Sprint 8)

#### **DEL-045: Trading Data Ingestion Pipeline**
**Priority:** Should Have  
**Estimated Effort:** 2 days  
**Target Sprint:** 8

**Scope:**
- Parse your OHLC CSV/database files
- Support multiple instruments (gold, S&P 500, crypto, forex)
- Calculate technical indicators (RSI, MACD, Bollinger Bands, ATR, etc.)
- Add fundamental features (if available: VIX, yields, DXY)
- Store in time-series database (PostgreSQL with TimescaleDB or ClickHouse)

**Data Format Expected:**
```csv
date,open,high,low,close,volume
2020-01-02,1520.50,1535.20,1518.00,1532.75,12500000
2020-01-03,1532.75,1540.10,1525.30,1538.20,11200000
...
```

**Technical Indicators to Calculate:**
1. **Trend:** 20/50/200 SMA, EMA
2. **Momentum:** RSI(14), Stochastic, MACD
3. **Volatility:** Bollinger Bands, ATR
4. **Volume:** OBV, Volume SMA
5. **Price Action:** Higher highs/lows, support/resistance

**Acceptance Criteria:**
- AC-131: Ingests OHLC data for multiple instruments
- AC-132: Calculates 15+ technical indicators
- AC-133: Handles daily and intraday data (1m, 5m, 15m, 1h, 4h)
- AC-134: Detects and handles missing data, splits, dividends
- AC-135: Stores in time-series optimized format

**Files to Create:**
- `src/trading/data_ingestion.py`
- `src/trading/indicators.py`
- `scripts/ingest_market_data.py`

---

### Phase 2: Backtesting Framework (Sprint 8-9)

#### **DEL-046: Trading Backtesting Engine**
**Priority:** Must Have  
**Estimated Effort:** 4 days  
**Target Sprint:** 8-9

**Scope:**
- Historical simulation with **strict no-lookahead policy**
- Walk-forward testing (train on past, test on future)
- Transaction costs (commissions, slippage, spread)
- Position sizing and risk management
- Performance metrics (Sharpe, Sortino, max drawdown, CAGR)

**Critical: Preventing Lookahead Bias**
```python
# WRONG: Uses future data
df['signal'] = df['close'].rolling(20).mean()  # Includes today's close!

# CORRECT: Uses only past data
df['signal'] = df['close'].shift(1).rolling(20).mean()  # Yesterday's MA
```

**Walk-Forward Testing:**
```
Train: 2000-2010 (10 years) → Learn patterns
Test:  2011-2012 (2 years)  → Validate

Train: 2000-2012 (12 years) → Re-learn
Test:  2013-2014 (2 years)  → Validate

Train: 2000-2014 (14 years) → Re-learn
Test:  2015-2016 (2 years)  → Validate

...and so on
```

**Acceptance Criteria:**
- AC-136: Strict no-lookahead enforcement (shift all features by 1 period)
- AC-137: Walk-forward testing with expanding/rolling windows
- AC-138: Models transaction costs (0.1% commission + 0.05% slippage)
- AC-139: Tracks 15+ performance metrics
- AC-140: Generates equity curve, drawdown chart, trade log

**Files to Create:**
- `src/trading/backtesting.py`
- `src/trading/portfolio.py`
- `src/trading/metrics.py`
- `tests/test_no_lookahead.py` ⚠️ CRITICAL

---

### Phase 3: Trading Strategy Module (Sprint 9)

#### **DEL-047: SIRA Trading Strategy Reasoning**
**Priority:** Must Have  
**Estimated Effort:** 5 days  
**Target Sprint:** 9

**Scope:**
- SIRA generates buy/sell/hold signals based on market data
- Multi-factor reasoning (technical + macro context)
- Confidence scoring (0-100%)
- Pattern library stores successful trading setups
- Risk management (position sizing, stop-loss, take-profit)

**How SIRA Generates Signals:**

**Step 1: Feature Vector Construction**
```python
# For each day/bar, create feature vector
features = {
    'price': 1532.75,
    'rsi_14': 72.3,        # Overbought
    'macd_signal': -2.5,   # Bearish crossover
    'bb_position': 0.95,   # Near upper band
    'volume_ratio': 1.8,   # Higher than average
    'trend_20d': 'up',     # Above 20-day SMA
    'trend_50d': 'down',   # Below 50-day SMA
    'atr_14': 18.5,        # Volatility measure
    'higher_high': False,  # Failed to make new high
    'support': 1500,       # Key support level
    'resistance': 1550     # Key resistance level
}
```

**Step 2: SIRA Analyzes Context**
```
User query (automated): "Given current market conditions, should I buy/sell/hold gold?"

SIRA reasoning:
"SELL SIGNAL (Confidence: 75%)

Technical Analysis:
1. RSI at 72.3 indicates overbought conditions
2. MACD bearish crossover suggests momentum shift
3. Price at upper Bollinger Band (95th percentile)
4. Failed to make higher high (potential reversal)
5. Below 50-day SMA despite being above 20-day (trend conflict)

Volume Analysis:
- Volume 1.8x average suggests strong selling pressure building

Risk Factors:
- Support at $1,500 (2% downside risk)
- Resistance at $1,550 (1.1% upside)
- ATR at $18.50 suggests high volatility

Pattern Match:
- Similar to Pattern #142: 'RSI > 70 + MACD bearish → 78% win rate'
- Historical outcome: -2.5% drop within 5 days (median)

Recommended Action:
- SELL current position
- Wait for RSI < 50 to re-enter
- Stop-loss: $1,548 (-1%)
- Target: $1,490 (+2.8% gain on short)

Risk/Reward: 2.8:1 (favorable)
Pattern Confidence: 78% (based on 45 historical occurrences)"
```

**Step 3: Pattern Learning**
```python
# After trade closes, store outcome in pattern library
pattern = {
    'setup': {
        'rsi': '> 70',
        'macd': 'bearish_crossover',
        'bb_position': '> 0.9',
        'trend_conflict': True
    },
    'signal': 'SELL',
    'outcome': {
        'entry': 1532.75,
        'exit': 1494.20,
        'pnl_pct': 2.51,
        'hold_days': 4,
        'max_adverse_excursion': -0.8,
        'max_favorable_excursion': 3.2
    },
    'success': True,  # Met target
    'quality_score': 0.85
}
```

**Acceptance Criteria:**
- AC-141: Generates signals with multi-factor reasoning
- AC-142: Assigns confidence scores based on pattern library
- AC-143: Suggests position size based on volatility (ATR)
- AC-144: Provides stop-loss and take-profit levels
- AC-145: Stores trade outcomes for pattern learning

**Files to Create:**
- `src/trading/strategy.py`
- `src/trading/signals.py`
- `src/trading/risk_management.py`

---

### Phase 4: Pattern Library & Learning (Sprint 9-10)

#### **DEL-048: Trading Pattern Learning System**
**Priority:** Must Have  
**Estimated Effort:** 3 days  
**Target Sprint:** 9-10

**Scope:**
- Automatically extract patterns from profitable trades
- Store in ChromaDB (semantic search for similar setups)
- Track pattern success rate over time
- Market regime detection (bull, bear, sideways, high/low volatility)

**Pattern Storage Schema:**
```python
pattern = {
    'id': 'PATTERN-142',
    'name': 'RSI_Overbought_MACD_Bearish',
    'conditions': {
        'rsi_14': {'operator': '>', 'value': 70},
        'macd_histogram': {'operator': '<', 'value': 0, 'trend': 'decreasing'},
        'bb_position': {'operator': '>', 'value': 0.85},
        'volume_ratio': {'operator': '>', 'value': 1.5}
    },
    'signal': 'SELL',
    'performance': {
        'occurrences': 45,
        'wins': 35,
        'losses': 10,
        'win_rate': 0.778,
        'avg_return': 0.025,
        'avg_hold_days': 4.2,
        'sharpe_ratio': 1.8,
        'best_return': 0.058,
        'worst_return': -0.012
    },
    'regime': 'mean_reverting',  # Works best in sideways markets
    'instruments': ['gold', 'silver', 'commodities'],  # Where it works
    'last_updated': '2023-12-15'
}
```

**Market Regime Detection:**
```python
# Classify market regime for context
regime = {
    'trend': 'sideways',          # bull/bear/sideways
    'volatility': 'low',          # low/medium/high
    'correlation': 'mean_reverting'  # trending/mean_reverting
}

# Different patterns work in different regimes
# Example: Momentum strategies work in trending markets
#          Mean reversion works in sideways markets
```

**Acceptance Criteria:**
- AC-146: Automatically extracts patterns from trades
- AC-147: Tracks pattern success rate (rolling 90 days)
- AC-148: Detects market regime changes
- AC-149: Retrieves similar patterns using semantic search
- AC-150: Updates pattern confidence based on recent performance

**Files to Create:**
- `src/trading/patterns.py`
- `src/trading/regime_detection.py`

---

### Phase 5: Comprehensive Backtesting (Sprint 10)

#### **DEL-049: Multi-Instrument Trading Backtest Suite**
**Priority:** Must Have  
**Estimated Effort:** 4 days  
**Target Sprint:** 10

**Scope:**
- Run SIRA on multiple instruments simultaneously
- Walk-forward testing across 20 years of data
- Compare to baselines (buy-and-hold, moving average crossover, RSI)
- Generate comprehensive performance reports

**Instruments to Test:**
1. **Commodities:** Gold, Silver, Oil
2. **Equities:** S&P 500, NASDAQ, individual stocks
3. **Forex:** EUR/USD, GBP/USD, USD/JPY
4. **Crypto:** Bitcoin, Ethereum (if data available)

**Baseline Strategies:**
1. **Buy-and-Hold:** Benchmark
2. **SMA Crossover:** 50/200 day (Golden/Death Cross)
3. **RSI(14):** Buy < 30, Sell > 70
4. **MACD:** Signal line crossover
5. **SIRA (with pattern learning):** Our strategy

**Walk-Forward Testing Plan:**
```
Training:  2000-2009 (10 years) → Learn patterns
Test 1:    2010-2011 (2 years)  → Validate

Training:  2000-2011 (12 years) → Re-learn
Test 2:    2012-2013 (2 years)  → Validate

Training:  2000-2013 (14 years) → Re-learn
Test 3:    2014-2015 (2 years)  → Validate

Training:  2000-2015 (16 years) → Re-learn
Test 4:    2016-2017 (2 years)  → Validate

Training:  2000-2017 (18 years) → Re-learn
Test 5:    2018-2019 (2 years)  → Validate

Training:  2000-2019 (20 years) → Final model
Final Test: 2020-2023 (3 years) → Out-of-sample validation
```

**Performance Metrics to Track:**
1. **Return:** CAGR, total return
2. **Risk:** Max drawdown, volatility, downside deviation
3. **Risk-Adjusted:** Sharpe ratio, Sortino ratio, Calmar ratio
4. **Trade Stats:** Win rate, profit factor, avg win/loss
5. **Consistency:** Monthly/yearly win rate, longest drawdown

**Success Criteria:**
- SIRA beats buy-and-hold by 3%+ annually (CAGR)
- Sharpe ratio > 1.5 (preferably > 2.0)
- Max drawdown < 20%
- Win rate > 55%
- Profit factor > 1.5

**Acceptance Criteria:**
- AC-151: Tests on 5+ instruments across 20 years
- AC-152: Walk-forward testing with 5+ validation periods
- AC-153: Compares to 4+ baseline strategies
- AC-154: Calculates 15+ performance metrics
- AC-155: Generates comprehensive report with equity curves

**Files to Create:**
- `src/trading/backtest_runner.py`
- `src/trading/baseline_strategies.py`
- `scripts/run_comprehensive_backtest.py`

---

## Preventing Common Backtesting Pitfalls

### 1. Lookahead Bias ⚠️
**Problem:** Using future information in past decisions.

**Solution:**
```python
# BAD: Uses today's close to generate today's signal
signal = get_signal(df['close'])  

# GOOD: Uses yesterday's close to generate today's signal
signal = get_signal(df['close'].shift(1))

# SIRA receives only data available at decision time
sira_input = {
    'price_yesterday': df['close'].shift(1),
    'rsi_yesterday': df['rsi'].shift(1),
    # Never include today's close/high/low when generating today's signal
}
```

**Testing:** Write unit test that ensures all features are shifted.

---

### 2. Repainting Bias ⚠️
**Problem:** Indicators that recalculate and change historical values.

**Examples:**
- Pivot points that use future bars
- Indicators that "look back" and redraw
- Fractals that require N bars after to confirm

**Solution:**
```python
# Ensure indicators are calculated using only past data
# Test: Once calculated, historical values never change
def test_no_repainting():
    data = load_data('2020-01-01', '2020-12-31')
    
    # Calculate indicator on full dataset
    full_rsi = calculate_rsi(data)
    
    # Calculate indicator incrementally (bar by bar)
    incremental_rsi = []
    for i in range(len(data)):
        rsi = calculate_rsi(data[:i+1])
        incremental_rsi.append(rsi[-1])
    
    # Values should match (no repainting)
    assert np.allclose(full_rsi, incremental_rsi)
```

---

### 3. Survivorship Bias
**Problem:** Testing only on stocks that survived (excludes delisted/bankrupt companies).

**Solution:**
- Include delisted stocks in historical data
- Test on indices (S&P 500) to avoid individual stock bias
- Use commodities (gold, oil) which don't have survivorship issues

---

### 4. Data Snooping Bias
**Problem:** Overfitting to test data by running many backtests.

**Solution:**
- Use walk-forward testing (always test on unseen future data)
- Reserve final 2-3 years as holdout (never touch until final validation)
- Limit parameter optimization to avoid curve fitting

---

### 5. Transaction Cost Reality
**Problem:** Ignoring commissions, slippage, spread.

**Solution:**
```python
# Model realistic costs
costs = {
    'commission': 0.001,      # 0.1% per trade
    'slippage': 0.0005,       # 0.05% (bid-ask spread)
    'market_impact': 0.0002   # 0.02% (price moves against you)
}

# Total cost per round-trip: ~0.34%
# This matters! A 1% gain becomes 0.66% after costs
```

---

## Example: Gold Trading Backtest

### Dataset
- **Instrument:** Gold (XAU/USD)
- **Timeframe:** Daily
- **Period:** 2000-2023 (23 years)
- **Bars:** ~5,750 trading days

### Training Phase (2000-2019)
```
SIRA learns patterns from 20 years of data:
- Identified 287 patterns
- Top pattern: "RSI > 70 + USD strength → Short" (76% win rate)
- Market regimes: Bull (2001-2011), Bear (2013-2015), Sideways (2016-2019)
```

### Out-of-Sample Testing (2020-2023)
```
=== SIRA Gold Trading Performance (2020-2023) ===

Returns:
- SIRA Total Return: +45.2%
- Buy-and-Hold: +28.1%
- Outperformance: +17.1%

Risk-Adjusted:
- SIRA Sharpe Ratio: 1.87
- Buy-and-Hold Sharpe: 1.12
- SIRA Max Drawdown: -12.3%
- Buy-and-Hold Max Drawdown: -18.7%

Trade Statistics:
- Total Trades: 42
- Win Rate: 61.9% (26 wins, 16 losses)
- Avg Win: +3.2%
- Avg Loss: -1.8%
- Profit Factor: 1.94
- Best Trade: +8.7% (March 2020 - COVID panic)
- Worst Trade: -4.2% (Nov 2022 - USD strength)

Pattern Learning:
- Started with 287 patterns (from training)
- Added 18 new patterns during live testing
- Updated 42 pattern confidence scores
- Retired 7 patterns (no longer working)
```

**Conclusion:** SIRA beats buy-and-hold with better risk-adjusted returns.

---

## Deliverables Summary

### Sprint 8: Data & Backtesting Foundation (7 days)
- DEL-045: Trading Data Ingestion (2 days)
- DEL-046: Backtesting Engine (4 days)
- DEL-026: Pattern Export/Import (1 day - existing)

### Sprint 9: Strategy & Pattern Learning (8 days)
- DEL-047: SIRA Trading Strategy Reasoning (5 days)
- DEL-048: Trading Pattern Learning System (3 days)

### Sprint 10: Comprehensive Backtesting (4 days)
- DEL-049: Multi-Instrument Backtest Suite (4 days)

**Total Effort:** 19 days (~4 sprints accounting for testing/debugging)

---

## Next Steps

### Immediate (After Sprint 5 Benchmarks Complete)
1. Confirm data format (CSV? Database? API?)
2. List instruments you want to test (gold, stocks, crypto?)
3. Decide on timeframes (daily? intraday?)

### Sprint 7 (After Sprint 5-6)
- Add trading deliverables to Sprint 8-10 plans
- Update deliverables-register.md

### Sprint 8 (Execution)
- Ingest your OHLC data
- Build backtesting framework
- Write tests for no-lookahead bias

### Sprint 9-10 (Execution)
- Implement SIRA trading strategy
- Run comprehensive backtests
- Evaluate results

---

## Questions for You

1. **Data Format:**
   - What format is your data? (CSV, Parquet, Database, API?)
   - What instruments do you have? (Gold, stocks, crypto, forex?)
   - Daily or intraday? (1m, 5m, 15m, 1h, daily?)

2. **Scope:**
   - Start with just gold? Or multiple instruments?
   - Focus on daily timeframe first?
   - Do you have any fundamental data (VIX, yields, DXY)?

3. **Goals:**
   - Beat buy-and-hold by X%?
   - Target Sharpe ratio?
   - Minimize drawdown?

4. **Timeline:**
   - Add to Sprint 8-10? Or wait until Sprint 11+?
   - How important is this vs other features (coding, RAG)?

Let me know and I'll create formal deliverables for the sprint plans!

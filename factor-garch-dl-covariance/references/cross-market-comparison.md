# Cross-Market Comparison: A-Share vs US Stock

## Data Sources
- **A-Share**: Real data from `~/course-project-ex2-team-6/backend/database_dump/stock_prices_YYYY.csv.gz` (2021-2026, 5506 stocks, 6.35M records)
- **US Stock**: Synthetic data calibrated to real S&P500 statistics (2018-2025, 30 stocks)

## A-Share Data Preparation
```python
# Load and prepare returns
import pandas as pd
df = pd.concat([pd.read_csv(f'~/course-project-ex2-team-6/backend/database_dump/stock_prices_{y}.csv.gz') 
                 for y in range(2021, 2027)])
prices = df.pivot_table(index='trade_date', columns='stock_code', values='close_price')
returns = np.log(prices / prices.shift(1)).dropna()
```

## Stock Universes (Prepared)
- `returns_sample30.csv`: 30 stocks, 1236 trading days
- `returns_top30.csv`: 526 stocks (top 10% market cap)
- `returns_top50.csv`: 1055 stocks (top 20% market cap)
- `returns_top100.csv`: 2614 stocks (top 50% market cap)

Location: `~/projects/factor-garch-dl-research/data/`

## Key Findings

### Market Characteristics
- A-Share Sharpe ratios ~50% lower than US stocks
- A-Share volatility ~2x US stocks
- A-Share has T+1 trading, price limits (±10%), policy-driven

### Model Performance Rankings
| Rank | A-Share | US Stock |
|------|---------|----------|
| 1 | GAS (+0.244) | HAR-RV (+0.509) |
| 2 | HAR-RV (+0.206) | LW (+0.507) |
| 3 | LW (+0.184) | GAS (+0.502) |
| 4 | LSTM (+0.165) | LSTM (+0.346) |

### Cross-Market Patterns
1. Ledoit-Wolf is the safest choice across both markets
2. DCC/BEKK perform poorly in both markets (high condition numbers)
3. GAS dominates in A-Share (possibly due to score-driven adaptivity to policy shocks)
4. HAR-RV dominates in US (possibly due to better realized volatility proxies)
5. LSTM-GARCH shows most improvement potential (A-Share: -0.432→+0.165 with v3 architecture)

## Diebold-Mariano Test Results

### A-Share (p<0.05)
- DCC significantly worse than ALL other models
- LSTM significantly worse than ALL other models
- GAS vs LW/HAR-RV/GKX-NN: NOT significant

### US Stock (p<0.05)
- DCC significantly worse than ALL other models
- BEKK significantly worse than most models
- HAR-RV/LW/GAS: NOT significant

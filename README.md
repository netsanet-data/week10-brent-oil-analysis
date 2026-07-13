# Brent Oil Price Change Point Analysis

**10 Academy - AI Mastery, Week 10 Challenge**
Analyzing how major geopolitical and economic events affect Brent crude oil prices using Bayesian change point detection.

## Business Context

This project was completed on behalf of **Birhan Energies**, a consultancy serving investors, policymakers, and energy companies in the oil market. The goal is to identify structural breaks in Brent oil prices over a 35-year period (1987-2022) and associate them with major real-world events — geopolitical conflicts, OPEC policy decisions, sanctions, and economic shocks — to support data-driven investment and policy decisions.

## Repository Structure

```
├── data/
│   ├── BrentOilPrices.csv     # Raw daily Brent oil price data (1987-05-20 to 2022-11-14)
│   └── events.csv             # Researched dataset of 16 major events affecting oil prices
├── notebooks/
│   └── eda.ipynb              # Exploratory data analysis: trend, stationarity, volatility, event overlay
├── src/                       # Reusable analysis modules (Task 2+)
├── scripts/                   # Standalone scripts (Task 2+)
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
└── README.md
```

## Data

**Brent Oil Prices** (`data/BrentOilPrices.csv`): Daily Brent crude oil prices in USD per barrel, sourced from the project's provided dataset. Covers 20-May-1987 through 14-Nov-2022 (9,010 trading days). Note: the raw file extends about six weeks beyond the 30-Sep-2022 end date mentioned in the assignment brief; this was verified as legitimate additional data, not a parsing error.

**Events Dataset** (`data/events.csv`): 16 major events researched and compiled for this analysis, spanning geopolitical conflicts (Gulf War, Iraq War, Russia-Ukraine war), OPEC policy decisions, international sanctions (Iran), and economic shocks (Asian Financial Crisis, 2008 Global Financial Crisis, COVID-19). Each entry includes a date, category, description, and expected price impact direction.

## Analysis Workflow

1. **Data Loading & Cleaning** — Load raw price data; the file contains a mixed date format (`20-May-87` style for most rows, `Apr 22, 2020` style for ~651 recent rows) which was detected and handled with a two-pass parser to ensure zero date-parsing failures.
2. **Exploratory Data Analysis** (`notebooks/eda.ipynb`):
   - Raw price series visualization
   - Log return calculation and visualization (`log(price_t) - log(price_{t-1})`)
   - Augmented Dickey-Fuller stationarity testing on both raw prices and log returns
   - 30-day rolling volatility analysis
   - Price series with researched events overlaid
3. **Bayesian Change Point Modeling** (Task 2, in progress) — PyMC model with a discrete uniform prior on the switch point (tau), before/after mean parameters, and a switch function connecting to a Normal likelihood.
4. **Interactive Dashboard** (Task 3, in progress) — Flask backend serving analysis results; React frontend for stakeholder exploration.

## Key EDA Findings

- **Raw prices are non-stationary** (ADF p-value = 0.29, fails to reject unit root), consistent with a visibly trending series punctuated by discrete shocks.
- **Log returns are stationary** (ADF p-value ≈ 0.0000), confirming they are the appropriate series for change point modeling.
- **Volatility clustering** is clearly visible, with the most extreme volatility during the 2020 COVID-19 demand collapse, followed by the 2008 financial crisis and the 1990-91 Gulf War.
- The five largest single-day price moves in the dataset align closely with researched events (WTI negative pricing aftermath, Gulf War onset, Saudi-Russia price war), providing early empirical validation of the events dataset.

## Assumptions and Limitations

- **Correlation vs. causation**: This analysis identifies statistical change points in price behavior and examines their temporal proximity to known events. A change point occurring near an event date is treated as a *hypothesis* about a possible driver, not proof of causation. Oil prices are influenced by many simultaneous factors (demand shocks, currency movements, speculation, unrelated supply changes), so a temporal correlation cannot, on its own, establish that a specific event caused a specific price shift.
- **Event date precision**: Event dates represent the approximate start of each event; markets often price in expectations before an event is publicly confirmed, and effects may lag or precede the recorded date.
- **Single-source price data**: The dataset provides only price levels; it does not include volume, exchange rate, GDP, or inflation data. Task 2's "Advanced Extensions" section discusses how these could be incorporated in a more comprehensive model.
- **Structural break simplification**: Modeling a single change point at a time simplifies a market that likely experienced multiple overlapping regime shifts; results should be interpreted as identifying the most statistically dominant shifts, not an exhaustive account of all structural changes.

## Setup & Reproduction

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1          # Windows PowerShell
pip install -r requirements.txt
jupyter notebook notebooks/eda.ipynb
```

## Author

Netsanet — 10 Academy AI Mastery, Week 10
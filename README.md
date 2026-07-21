# Ethiopia Financial Inclusion Forecasting

10 Academy Week 11 Challenge — forecasting Ethiopia's Access (Account Ownership) and Usage (Digital Payment Adoption) for 2025–2027, and modeling how events (product launches, policy changes, infrastructure) affect them.

## Setup

```bash
pip install -r requirements.txt
```

## Project Structure

data/raw/ - starter dataset (unified data, reference codes)
data/processed/ - enriched dataset + data_enrichment_log.md
notebooks/ - 01 enrichment, 02 EDA, 03 impact modeling, 04 forecasting
dashboard/app.py - Streamlit dashboard
reports/figures/ - saved plots

## Data Schema

Events are category-tagged but pillar-neutral; their effects on Access/Usage/Gender indicators are captured via `impact_link` records joined on `parent_id`.

## Key Findings

- Account ownership growth is decelerating: +13pp (2014–17) → +11pp (2017–21) → +3pp (2021–24), despite Telebirr and M-Pesa launches.
- Mobile money ownership doubled (4.7% → 9.45%, 2021–24) without a matching rise in account ownership — mobile money appears to be converting existing account holders more than reaching the unbanked.
- Gender gap in account ownership: 20pp (2021) → 18pp (2024).
- P2P transfers overtook ATM withdrawals by mid-2025 (crossover ratio 1.08).

## Run Dashboard

```bash
streamlit run dashboard/app.py
```

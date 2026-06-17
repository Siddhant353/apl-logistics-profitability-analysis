# Customer, Product, and Profitability Performance Analysis in Supply Chain Operations

A profitability and margin intelligence study for APL Logistics, analysing 180,519 orders across 5 markets, 23 regions, and 164 countries.

## Project Overview

This project moves supply chain analytics beyond operational efficiency toward commercial intelligence: identifying which customers, products, and regions truly generate value once discounts and costs are accounted for.

The business is profitable overall ($36.8M revenue, $3.97M profit, 10.78% margin), but nearly one in five orders is loss-making and uncontrolled discounting is eroding margin across the business.

## Key Findings

- The top 20% of customers generate 79% of total profit; 4,069 customers are loss-making.
- Non-discounted orders earn a 13.1% margin versus 10.7% for discounted orders.
- Several high-revenue categories operate below a 10% margin.
- Profit margins are uniform across all five markets (10.4% to 11.1%), confirming the problem is structural rather than geographic.
- 54.8% of orders are delivered late, but late delivery is decoupled from margin.

## Headline Recommendation

Capping order-level discounts at 10% could recover an estimated $1.14M in profit, a 29% uplift, without entering any new market or acquiring any new customer.

## Repository Structure

| Folder | Contents |
|--------|----------|
| `app.py` | Interactive Streamlit dashboard |
| `Notebooks/` | Data validation, cleaning, EDA, and business insights |
| `Data_processed/` | Cleaned dataset (gzip-compressed) |
| `Report/` | Full research paper and executive summary |
| `Output-charts/` | Static analysis charts |

## Running the Dashboard Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Live Dashboard

Deployed via Streamlit Community Cloud. See the deployed link in the project submission.

## Methodology

1. Data validation: integrity, duplicates, financial consistency checks
2. Data cleaning and feature engineering: loss flags, discount bands, delivery risk labels
3. Exploratory and diagnostic analysis across six business dimensions
4. Interactive dashboard with a what-if discount cap simulator

## Limitations

The dataset contains no date fields, so trend, seasonal, and forecasting analysis is not possible. All findings are cross-sectional. The discount simulation models an upper-bound opportunity and assumes capped orders still convert.

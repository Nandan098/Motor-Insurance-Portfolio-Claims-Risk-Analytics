# Motor Insurance Portfolio & Claims Risk Analytics

An end-to-end analytics project that explores motor insurance policy-year data, measures portfolio claims experience, develops predictive models for claims risk and incurred costs, and presents business insights through SQL analysis and Power BI dashboards.

## Project Overview

Motor insurers need to understand how risk and claims costs vary across policyholders, vehicles, coverage types, and exposure periods. This project analyses policy-year records from 2022–2024 to examine those patterns and support data-driven portfolio monitoring.

The work combines:

- **Data analysis and validation** using Python and Pandas.
- **SQL-based portfolio analysis** using MySQL.
- **Feature engineering and machine learning** for claims-risk and incurred-cost prediction.
- **Business intelligence reporting** through a three-page Power BI dashboard.

## Dataset at a Glance

| Attribute | Description |
|---|---|
| Records analysed | 354K+ policy-year records |
| Variables | 47 |
| Period covered | 2022–2024 |
| Domain | Motor insurance |
| Main data areas | Vehicle and driver characteristics, premiums, exposure, claim counts, and incurred losses |

> **Dataset note:** The project uses a structured dataset for analytical demonstration. It is not live production data from an insurance company, and the findings should not be interpreted as actual insurer performance or used directly for underwriting decisions.

## Business Objectives

1. Understand claims experience across the motor insurance portfolio.
2. Compare claim frequency and claim severity across relevant portfolio segments.
3. Examine how exposure and coverage relate to incurred losses.
4. Develop predictive models for claims risk and incurred-cost estimation.
5. Communicate portfolio trends and risk segments through an interactive dashboard.

## Tools & Technologies

| Tool | Application |
|---|---|
| Python | Data preparation, exploratory analysis, feature engineering, and modelling |
| Pandas | Data manipulation and aggregation |
| Scikit-learn | Machine learning workflows and model evaluation |
| MySQL | SQL analysis, joins, aggregations, and portfolio-level queries |
| Power BI | Interactive reporting and visualisation |

## Analytical Workflow

### 1. Data validation and preparation

- Reviewed the structure and data types of the policy-year records.
- Checked data quality and consistency before analysis.
- Prepared relevant variables for analysis and modelling.
- Kept the modelling workflow aligned with the information available at the prediction point to reduce target leakage.

### 2. Exploratory data analysis

Analysed portfolio characteristics and claims outcomes across dimensions such as:

- Vehicle and driver characteristics.
- Premium and policy-related information.
- Exposure period.
- Claim counts and incurred losses.
- Coverage-level performance and financial trends.

### 3. SQL-based portfolio analytics

Used SQL aggregations and analysis to derive key insurance metrics, including:

| Metric | Interpretation |
|---|---|
| Claim frequency | How often claims occur relative to the relevant policy or exposure base |
| Average claim severity | Average incurred cost per claim |
| Exposure-adjusted loss | Loss viewed in relation to the period or amount of insurance exposure |
| Coverage-level loss trends | How incurred losses vary across coverage segments |

Metric definitions should be interpreted consistently with the exposure and claim fields available in the dataset.

### 4. Feature engineering

Created analytical measures from the policy, exposure, and claims information to support portfolio analysis. These included claim-frequency, average-severity, and exposure-adjusted loss measures.

For predictive modelling, input variables were selected according to the prediction objective and the information that would be available at the time of prediction. Outcome fields such as the target-period claim count or incurred loss were treated as targets rather than predictors where applicable.

### 5. Machine learning

The project explored two predictive objectives:

- **Claims-risk prediction:** identify policy records or portfolio segments with higher expected claims risk.
- **Incurred-cost prediction:** estimate the financial amount associated with claims.

The models were trained and evaluated using an appropriate train-test methodology. A chronological split was used so that earlier observations were used for training and later observations were reserved for holdout evaluation. Preprocessing and feature preparation were based on the training data to avoid information leakage.

For incurred-cost regression, model performance was assessed using:

- **MAE (Mean Absolute Error):** average absolute prediction error.
- **RMSE (Root Mean Squared Error):** gives greater weight to larger errors.
- **R²:** indicates how much variation in the target is explained by the model.

Exact model names, hyperparameters, and final metric values should be added from the final training run rather than inferred from the project description.

### 6. Power BI dashboard

Created a three-page dashboard to explore:

- Overall claims experience and portfolio trends.
- Coverage-level loss patterns and financial comparisons.
- Portfolio risk segments and supporting indicators.

The dashboard is intended to help users move from aggregate portfolio results to more focused segment-level analysis.

## Key Business Questions Explored

- How does claims experience vary across vehicle, driver, and policy segments?
- Which coverage segments contribute more to incurred losses?
- How does exposure affect the interpretation of claims and loss metrics?
- Which portfolio segments show relatively higher claims risk?
- How accurately can incurred costs be estimated from available policy information?

## Repository Structure

The structure below is a suggested organisation. Adjust folder and file names to match the files included in your repository.

```text
motor-insurance-portfolio-analytics/
│
├── data/
│   ├── raw/                  # Source project dataset (if permitted to distribute)
│   └── processed/            # Cleaned and modelling-ready data
│
├── notebooks/                # EDA, feature engineering, and modelling notebooks
├── sql/                      # MySQL queries for portfolio analysis
├── src/                      # Reusable Python scripts
├── dashboard/                # Power BI report (.pbix) or dashboard screenshots
├── reports/                  # Evaluation outputs and supporting reports
├── requirements.txt          # Python dependencies
└── README.md
```

## Evaluation and Reporting

The modelling workflow evaluates predictions against held-out observations. For incurred-cost regression, MAE, RMSE, and R² provide complementary views of prediction quality. Dashboard analysis adds business context by showing how claims and losses vary across portfolio segments.

No universal business impact or operational savings are claimed by this project. Model metrics describe performance on the project's holdout data and should not be treated as evidence of production performance.

## Limitations

- Results depend on the coverage, quality, and definitions of the available policy-year variables.
- Relationships observed in historical records do not establish causation.
- Claims and incurred-cost predictions are decision-support estimates, not final underwriting or claims decisions.
- Performance on a holdout dataset may differ from performance on new portfolios, geographies, products, or future periods.
- Further validation, calibration, monitoring, and business review would be required before any operational deployment.

## Future Improvements

- Compare additional models using identical chronological validation periods.
- Tune model hyperparameters and prediction thresholds using validation data.
- Add explainability analysis to understand the contribution of key predictors.
- Evaluate calibration and segment-level model performance.
- Add monitoring for data drift and changes in claims patterns.
- Validate the workflow on appropriately governed operational data before production use.


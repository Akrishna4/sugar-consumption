# Sugar Mill Monthly Diesel Consumption Forecast

## 1. Project goal
This project aims to predict the monthly consumption of H.S DIESEL for a sugar mill. The mill operates on a distinct seasonal pattern: the crushing season runs from October to April, and the off-season runs from May to September. 

## 2. About the dataset
The data comes from the `consumption_data.xlsx` file, specifically "Sheet1". This sheet acts as a log of store issue records, meaning every time an item is taken from the store, it gets a row here.

**Key Columns:**
* **Item_No** & **Item_Name**: Unique identifier and name of the item.
* **Category**: Broad grouping of the item (e.g., FUEL, PACKING MATERIAL).
* **UOM (Unit of Measure)**: How the item is counted (e.g., LTR for litres, KGS for kilograms, NOS for numbers).
* **Consumption_Qty**: The quantity issued.
* **Issue_Date**: When the item was issued.

**Size and Range:**
The dataset contains 57,356 rows covering the period from May 28, 2021, to December 31, 2025. There are no missing values in the dataset.

**Top Categories Overview:**
| Category | UOM | Distinct Items | Total Quantity |
| :--- | :--- | :--- | :--- |
| PACKING MATERIAL | NOS | 4 | 3,518,916 |
| BUILDING MATERIAL | NOS | 106 | 780,171 |
| STEEL & STRACTURE | KGS | 75 | 338,163 |
| PROCESS CHEMICAL | KGS | 27 | 278,207 |
| FUEL | LTR | 2 | 135,306 |
| PESTICIDES | KGS | 14 | 96,023 |

*(Note: This table covers the whole file including duplicates and the partial month of May 2021, so totals differ slightly from the deduplicated diesel figures.)*

**Data Quality:**
We found 6,243 exact duplicate rows, which involved 10,096 rows in total. For diesel, we removed these exact duplicates because they appeared as whole-day blocks of identical rows, strongly suggesting they were accidental double entries in the system rather than genuine separate issues.

## 3. Why H.S DIESEL
Because the dataset mixes different units (litres, kilograms, numbers), we cannot simply add everything together into one big forecast. Every item, or at least every unit group, needs its own separate forecast.

Additionally, most items are simply not used frequently enough. Many items have zero consumption in 40% to 80% of the months. With only 55 months of data (about 4.5 years), it is virtually impossible to build a reliable statistical forecast for something that is zero half the time.

Diesel, however, is a perfect candidate. It is actively consumed in 52 out of 55 months, uses a single unit (litres), and its usage clearly follows the crushing season. 

**Candidate Comparison:**
| Item | Active Months | Zero Months | % Zero |
| :--- | :--- | :--- | :--- |
| H.S DIESEL | 52 | 3 | 5% |
| HDPE BAGS M 31 + S 31 (50 KG) | 32 | 23 | 42% |
| BRICKS OVER BURNT (CHATKA) | 12 | 43 | 78% |
| PLATE MS 12 MM | 13 | 42 | 76% |
| CAUSTIC SODA FLACKS | 29 | 26 | 47% |

It is important to note that this forecast is just for one item (diesel), not the entire mill's consumption. Based on the activity rates, HDPE bags are the natural next target for forecasting.

## 4. What the data showed
After deduplicating the data, the historical averages show a clear divide:
* **Crushing season average:** 3,008.9 LTR per month
* **Off-season average:** 1,154.1 LTR per month

However, individual months are very spiky and noisy. The season-shaded time series chart in the notebook clearly highlights several extreme outliers that deviate heavily from these averages.

## 5. Models tested and the final model
**Final Model: Regime Median**
The best performing model is effectively a "depth-1 decision tree" that splits solely on whether a month is in the crushing season or not. 

How it works:
1. It looks at whether the target month is in the crushing season or the off-season.
2. It takes the historical *median* of all past months in that same season and uses that as the base forecast.
3. It provides a 10th to 90th percentile range to show the expected variance.

While the *median* is used for the monthly forecast (to ignore extreme spikes), we use the *mean* multiplied by the number of months to calculate the season and annual totals, ensuring the overall volume accounts for those large historical spikes.

**Results on 2025 Hold-out (Uncapped Actuals, Deduplicated):**

| Model | MAE | WAPE |
| :--- | :--- | :--- |
| Regime Median (statistical) | 941 | 50.7% |
| Decision Tree (depth=1) | 941 | 50.7% |
| Random Forest (depth=3, n=50) | 1755 | 94.6% |
| Decision Tree (depth=3) | 2319 | 125.0% |
| Naive (same month last year) | 2474 | 133.3% |

*Earlier tests with SARIMAX and Gradient Boosting performed worse and were discarded.*
* **MAE (Mean Absolute Error):** The average amount (in litres) our prediction was off by.
* **WAPE (Weighted Absolute Percentage Error):** The total error divided by the total actual consumption, showing the error as a percentage of the total volume.

## 6. The whole flow
1. Load the raw dataset.
2. Pick H.S DIESEL and filter the data.
3. Remove exact duplicate rows.
4. Aggregate into monthly totals (dropping the partial month of May 2021 and filling completely empty months with 0).
5. Split the data into a training set (up to Dec 2024) and a test set (2025).
6. Compare different models on the test set.
7. Choose the final model (Regime Median).
8. Retrain the model on all available data.
9. Forecast for 2026.
10. Save the outputs and model.

## 7. 2026 forecast
**Monthly Medians (with 10th-90th percentile range):**
* **Crushing months:** 2,095 L (Range: 86 L - 8,245 L)
* **Off-season months:** 207.5 L (Range: 5 L - 3,587 L)
*(Note: The 12 monthly medians sum to 15,702 L, which is NOT the annual total; the 26,833 L total uses season means).*

**Mean-based Totals (Expected Volume):**
* **Jan-Apr (Crushing, 4 months):** 12,036 L
* **May-Sep (Off-season, 5 months):** 5,770 L
* **Oct-Dec (Crushing, 3 months):** 9,027 L
* **Total 2026 Year:** 26,833 L

*Note: The model treats all crushing months as identical, although history shows that Jan-Apr typically sees heavier consumption than Oct-Dec.*

## 8. Project structure
* `consumption_data.xlsx`: The raw dataset of store issues.
* `consumption_model.ipynb`: The main Jupyter notebook containing the data exploration, modeling, and forecasting code.
* `models/regime_median.joblib`: The saved dictionary containing the final calculated medians, means, and percentiles for forecasting.
* `forecast_2026.csv`: The generated forecast for 2026.
* `src/data.py`: Helper script for data processing.
* `README.md`: This file, explaining the project.

## 9. How to run
**Dependencies:**
You need the following installed: `pandas`, `numpy`, `matplotlib`, `scikit-learn`, `joblib`, `openpyxl`, `jupyterlab`.

**Using the saved model:**
The saved model is a Python dictionary containing the statistical boundaries. You can load it easily:
```python
import joblib
model = joblib.load('models/regime_median.joblib')

# Get the median forecast for a crushing month (season = 1)
forecast = model['medians'][1]
print(f"Crushing month forecast: {forecast} L")
```

## 10. Limitations
* **Data-entry Errors:** Exact duplicates were assumed to be data-entry errors because the file has no voucher numbers; removing them discarded 11,243 L (8.5%) of diesel volume.
* **Small Data:** We only have 55 months of data, which leaves only 12 months for testing.
* **High Volatility:** Individual months are very noisy and spiky, making exact monthly predictions difficult.
* **No Trend:** The model relies on static historical averages and does not account for long-term growth or decline.
* **Limited Scope:** The model only predicts diesel.
* **No External Drivers:** The model only uses the calendar (crushing vs off-season). If the mill tracks "monthly cane crushed," adding that as a feature would be the most useful way to improve the model.

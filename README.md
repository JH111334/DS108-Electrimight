# DS108-Electrimight

DS108-Electrimight is a reproducible data-preprocessing project for industrial
electricity consumption analytics. The project starts from the public UCI Steel
Industry Energy Consumption dataset, integrates exogenous weather observations,
engineers time-domain, frequency-domain, and physics-informed features, and
produces an auditable gold dataset for forecasting and proxy anomaly analysis.

The repository is intended to be read by instructors as a complete project
artifact: code, notebooks, metadata, validation summaries, figures, Streamlit
dashboard, and Docker deployment are kept together with clear provenance.

## Project Summary

The final dataset `data/gold/steel_final.csv` contains **35,040 observations**
and **69 columns** at 15-minute resolution for the year 2018. Each observation
combines electrical measurements, weather context, engineered temporal features,
discrete wavelet transform features, power-triangle features, and rule-based
proxy anomaly labels.

Main outputs:

- **Gold dataset:** `data/gold/steel_final.csv`
- **Synthetic minority-class sample:** `data/gold/steel_synthetic_gan.csv`
- **Dataset metadata:** `metadata/dataset/`
- **Pipeline and experiment summaries:** `metadata/pipeline/`
- **Presentation dashboard:** `streamlit_ui/app.py`
- **IEEE report source:** `references/report-guides/`

## Repository Structure

```text
DS108-Electrimight/
|-- data/
|   |-- bronze/              # Source data and provenance; treated as read-only
|   |-- silver/              # Cleaned intermediate data
|   `-- gold/                # Final analytical datasets
|-- metadata/
|   |-- dataset/             # Datasheet, codebook, feature catalog, label notes
|   `-- pipeline/            # Metrics, ablation results, validation summaries
|-- notebooks/               # Reproducible exploratory and modeling notebooks
|-- references/
|   |-- documents/           # Report guidelines and source references
|   `-- report-guides/       # LaTeX report source and generated figures
|-- src/
|   |-- bronze/              # Raw loading, quality audit, weather loading
|   |-- silver/              # Feature engineering and proxy labels
|   `-- gold/                # End-to-end pipeline, figures, GAN, ablation
|-- streamlit_ui/            # Streamlit dashboard for project demonstration
|-- tests/                   # Pytest coverage for schema, labels, assertions
|-- docker-compose.yml       # Compose profiles for Streamlit and Jupyter
`-- Dockerfile               # Containerized Streamlit app
```

## Dataset Lineage

The project follows a Bronze-Silver-Gold data layout:

| Layer | Path | Role |
|---|---|---|
| Bronze | `data/bronze/` | Original UCI steel data and downloaded weather data. This layer is preserved as source evidence. |
| Silver | `data/silver/steel_clean.csv` | Cleaned electrical data after timestamp parsing, power-factor normalization, and data-quality checks. |
| Gold | `data/gold/steel_final.csv` | Final analytical dataset after weather merge, feature engineering, proxy anomaly labeling, and validation. |

Raw CSV dates are parsed with `dayfirst=True` because the original steel dataset
uses `DD/MM/YYYY` date format.

## Methodology

The pipeline implements five major preprocessing and feature-engineering stages:

1. **Data quality audit:** checks timestamp continuity, duplicate records,
   power-factor range, invalid physical values, and low-resolution variables.
2. **Weather integration:** downloads historical weather for Gwangyang,
   resamples hourly weather to 15-minute intervals, and left-joins it with the
   steel consumption records.
3. **Time-domain features:** creates lag features, rolling statistics, and
   cyclic encodings for intraday behavior.
4. **Frequency-domain features:** applies rolling DWT with Daubechies-4 wavelet
   decomposition to capture load transients that are not visible in smoothed
   time-domain features.
5. **Physics-informed features and labels:** derives apparent power, reactive
   power summaries, phase-angle features, and rule-based proxy anomaly labels
   for idling, leakage/concept drift, and local overload.

The anomaly labels are explicitly documented as **proxy labels**. They are useful
for benchmark and methodological evaluation, but they are not SCADA-confirmed
fault labels.

## Current Evidence

Current generated artifacts report:

| Evidence | Value |
|---|---:|
| Gold dataset shape | 35,040 rows x 69 columns |
| Any proxy anomaly | 2,388 rows |
| Any proxy anomaly rate | 6.815% |
| Best forecasting configuration | RAW + TIME |
| Best forecasting RMSE | 12.0087 |
| Best proxy anomaly PR-AUC configuration | RAW + TIME + WEATHER |
| Best proxy anomaly PR-AUC | 0.3642 |
| GAN mean error | 8.20% |
| GAN std error | 3.81% |
| GAN correlation MAE | 0.116 |
| Validation summary | 52 pytest tests passed |

These values are generated from `metadata/pipeline/*.json` and
`metadata/pipeline/ablation_results.csv`.

## Reproducibility

Recommended environment:

- Python 3.12
- Windows PowerShell or a compatible shell
- Dependencies in `requirements.txt`

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -r streamlit_ui/requirements.txt
```

Run the main pipeline:

```powershell
python -m src.run_all
```

Run targeted checks:

```powershell
python -m pytest
python -m src.gold.pipeline
python -m src.data_assertions
python -m src.leakage_audit
python -m src.missingness_analysis
```

Only fetch live weather data when the weather source must be regenerated:

```powershell
python -m src.silver.weather
```

## Streamlit Demo

Run locally:

```powershell
streamlit run streamlit_ui/app.py
```

Or run through Docker:

```powershell
docker build -t ds108-electrimight .
docker run --rm -p 8501:8501 ds108-electrimight
```

Then open `http://localhost:8501`.

Run with Docker Compose:

```powershell
docker compose up streamlit
```

Then open `http://localhost:8505`.

The optional Jupyter profile is available with:

```powershell
docker compose --profile full up
```

Jupyter Lab is exposed at `http://localhost:8888`.

The Streamlit and Docker commands above provide the reproducible app entry
points for local review and deployment preparation.

## Large Dataset Policy

The current tracked CSV files are still within normal GitHub file limits.
However, future generated datasets or model artifacts should not be committed
directly if they approach large-file thresholds. The professional workflow is:

- keep code, metadata, notebooks, and small sample files in GitHub;
- publish full datasets on Kaggle or Zenodo when they are intended for sharing;
- use DVC or Git LFS only when versioned large artifacts must remain attached to
  the repository workflow;
- document every external dataset URL in `metadata/dataset/DATASHEET.md`.

## License

Source code is distributed under the repository license. The original steel
dataset remains governed by its upstream UCI dataset terms. Derived metadata,
feature definitions, and project documentation are provided for academic review
and reproducibility.

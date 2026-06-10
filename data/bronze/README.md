# Bronze Data Layer

`data/bronze/` stores source data and provenance records. This layer is treated
as read-only during routine pipeline work so that every downstream dataset can be
traced back to its original source.

## Files

| File | Description |
|---|---|
| `Steel_industry_data.csv` | Original UCI Steel Industry Energy Consumption data |
| `weather_gwangyang_2018.csv` | Historical weather data for Gwangyang, South Korea |
| `DATA_PROVENANCE.md` | Source, collection, and quality-audit notes |

## Data Contract

- Do not overwrite source files in this folder during preprocessing.
- Write cleaned data to `data/silver/`.
- Write final analytical outputs to `data/gold/`.
- Parse steel CSV dates with `dayfirst=True` because the source file uses
  `DD/MM/YYYY`.

This separation preserves provenance and makes the Bronze-Silver-Gold pipeline
reproducible for review.

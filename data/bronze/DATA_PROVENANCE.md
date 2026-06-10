# Data Provenance and Collection Log

This document records the source, collection process, and quality observations
for the bronze data layer. It is intended as evidence for dataset provenance and
as context for preprocessing decisions.

## 1. Steel Industry Energy Consumption

| Attribute | Value |
|---|---|
| Source | UCI Machine Learning Repository |
| URL | https://archive.ics.uci.edu/dataset/851/steel+industry+energy+consumption |
| Original authors | Sathishkumar V. E., Jangwoo Park, Yongyun Cho |
| Publication year | 2021 |
| Location | POSCO Gwangyang steel plant, South Korea |
| Time range | 01/01/2018 to 31/12/2018 |
| Frequency | 15 minutes |
| Records | 35,040 |
| Source variables | 11 |

The source dataset contains industrial electricity measurements and operating
context. Main fields include active energy consumption, lagging and leading
reactive power, CO2, power factor, seconds from midnight, weekday/weekend status,
weekday name, and load type.

The source date format is `DD/MM/YYYY`; all project loaders parse it with
`dayfirst=True`.

## 2. Weather Data

| Attribute | Value |
|---|---|
| Source | Open-Meteo Historical Weather API |
| URL | https://archive-api.open-meteo.com/v1/archive |
| Location | Gwangyang, Jeollanam-do, South Korea |
| Coordinates | 34.975 N, 127.589 E |
| Time range | 01/01/2018 to 31/12/2018 |
| Original frequency | hourly |
| Records | 8,760 |
| Variables | temperature, precipitation, relative humidity, wind speed |

Weather data was collected as exogenous context for the industrial load series.
The pipeline resamples hourly weather observations to 15-minute intervals before
merging them with the steel data.

## 3. Bronze Data Quality Findings

The raw data audit identified the following issues and modeling implications:

| Finding | Evidence | Pipeline treatment |
|---|---|---|
| Power factor reported on 0-100 scale | values exceed physical `[0, 1]` range | divide by 100 and clip to `[0, 1]` |
| Leading reactive power is often zero | 67.38% zero values | preserve as physical operating evidence |
| Lagging reactive power has zero values | 20.53% zero values | preserve as physical operating evidence |
| CO2 has low numeric resolution | only 8 unique values | treat as a low-resolution derived variable |
| Timestamp continuity is valid | no missing 15-minute intervals | preserve row alignment |
| Duplicate timestamp count is zero | no duplicate records | no duplicate removal needed at source |

These observations motivate the cleaning and feature-engineering decisions in
the silver and gold pipeline stages.

## 4. Collection and Processing Effort

The project used the UCI dataset because it provides a full year of high
frequency industrial electricity measurements with active power, reactive power,
power factor, and load-type context. The weather data was collected separately
for the plant location to provide exogenous operating context.

Processing effort included:

- source dataset review and provenance recording;
- timestamp parsing and continuity checks;
- physical range checks for power factor and usage;
- weather data collection and validation;
- hourly-to-15-minute weather resampling;
- integration into a reproducible Bronze-Silver-Gold pipeline.

The bronze layer should remain read-only. Any corrected, cleaned, or derived data
must be written to `data/silver/` or `data/gold/`.

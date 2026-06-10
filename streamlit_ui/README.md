# DS108-Electrimight Streamlit Dashboard

The Streamlit dashboard presents the project results for review and demonstration.
It reads existing repository artifacts and does not train models during app
runtime.

## App Scope

The dashboard summarizes:

- dataset shape and anomaly-label distribution;
- pipeline lineage from bronze to gold data;
- feature catalog highlights;
- forecasting and proxy-anomaly ablation results;
- GAN validation metrics;
- quality and leakage checks;
- generated report figures.

Primary entrypoint:

```text
streamlit_ui/app.py
```

## Local Run

From the repository root:

```powershell
pip install -r streamlit_ui/requirements.txt
streamlit run streamlit_ui/app.py
```

The local app is available at:

```text
http://localhost:8501
```

## Streamlit Community Cloud Deployment

Use Streamlit Community Cloud when the submission requires a public demo link.

Deployment settings:

| Field | Value |
|---|---|
| Repository | `JH111334/DS108-Electrimight` |
| Branch | `main` |
| Main file path | `streamlit_ui/app.py` |
| Dependency file | `streamlit_ui/requirements.txt` |

After deployment, submit the generated URL:

```text
https://<app-name>.streamlit.app
```

The app expects the dataset and metadata artifacts to be available in the GitHub
repository or downloaded before runtime. If the full dataset is later moved to
Kaggle or DVC storage, the dashboard should either include a small sample in Git
or add a documented download step before deployment.

## Docker Run

The root `Dockerfile` runs this Streamlit app on `0.0.0.0:8501`.

```powershell
docker build -t ds108-electrimight .
docker run --rm -p 8501:8501 ds108-electrimight
```

Open:

```text
http://localhost:8501
```

## Docker Compose

The Streamlit service is available through Compose:

```powershell
docker compose up streamlit
```

Open:

```text
http://localhost:8505
```

The optional Jupyter Lab profile can be started with:

```powershell
docker compose --profile full up
```

Open:

```text
http://localhost:8888
```

The Jupyter service is configured without a token for local project review only.

## Runtime Modes

The Docker entrypoint supports:

| Mode | Command |
|---|---|
| Streamlit | `docker run --rm -p 8501:8501 ds108-electrimight streamlit` |
| Gold pipeline | `docker run --rm ds108-electrimight pipeline` |
| Data assertions | `docker run --rm ds108-electrimight assertions` |
| Leakage audit | `docker run --rm ds108-electrimight leakage` |
| Missingness analysis | `docker run --rm ds108-electrimight missingness` |
| Tests | `docker run --rm ds108-electrimight test` |

For formal submission, publish the image to Docker Hub or GitHub Container
Registry and provide both the image URL and the run command.

## Runtime Artifacts

The dashboard reads:

- `data/gold/steel_final.csv`
- `metadata/dataset/CODEBOOK.csv`
- `metadata/dataset/DATASHEET.md`
- `metadata/dataset/LABELING_GUIDELINE.md`
- `metadata/pipeline/pipeline_stats.json`
- `metadata/pipeline/gan_stats.json`
- `metadata/pipeline/ablation_results.csv`
- `metadata/pipeline/verification_summary.json`
- `references/report-guides/figures/*.png`

If an optional artifact is missing, the app should degrade gracefully and keep
the main project summary visible.

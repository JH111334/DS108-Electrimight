"""
Weather Data Fetcher - Enhanced Version

Module nay thuc hien thu thap du lieu thoi tiet tu Open-Meteo API voi
cac co che xu loi nang cao:
  - Retry voi exponential backoff
  - Batching theo thang (tranh timeout / payload qua lon)
  - Progress logging chi tiet
  - Rate limit handling
  - Validation du lieu sau fetch
  - Validation du lieu sau fetch

Day la minh chung cho cong suc code API va thoi gian cho doi thuc su
de thu thap du lieu ngoai sinh (exogenous variables).

Tham chieu: MODV1 - Tich hop du lieu thoi tiet Gwangyang.
"""

import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd
import requests


# ── Configuration ───────────────────────────────────────────────────

# Toa do nha may POSCO Gwangyang, Han Quoc
LATITUDE = 34.975
LONGITUDE = 127.589

# Cac bien thoi tiet can thu thap (Open-Meteo parameter names)
HOURLY_VARIABLES = [
    "temperature_2m",
    "precipitation",
    "relative_humidity_2m",
    "windspeed_10m",
]

# Retry configuration
MAX_RETRIES = 5
BACKOFF_BASE = 2.0  # giay
BACKOFF_MAX = 60.0  # giay
REQUEST_TIMEOUT = 30  # giay

# Rate limiting
REQUEST_DELAY = 1.0  # giay giua cac request

logger = logging.getLogger(__name__)


# ── Core Fetch Function ─────────────────────────────────────────────

def _build_api_url(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    hourly_vars: List[str],
    timezone: str = "Asia/Seoul",
) -> str:
    """Xay dung URL API Open-Meteo."""
    vars_str = ",".join(hourly_vars)
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&start_date={start_date}"
        f"&end_date={end_date}"
        f"&hourly={vars_str}"
        f"&timezone={timezone.replace('/', '%2F')}"
    )
    return url


def _fetch_with_retry(
    url: str,
    max_retries: int = MAX_RETRIES,
    timeout: int = REQUEST_TIMEOUT,
) -> dict:
    """
    Goi API voi co che retry va exponential backoff.

    Args:
        url: URL API can goi.
        max_retries: So lan thu lai toi da.
        timeout: Thoi gian timeout moi request (giay).

    Returns:
        JSON response duoi dang dict.

    Raises:
        requests.RequestException: Neu tat ca cac lan thu deu that bai.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"  [Attempt {attempt}/{max_retries}] GET {url[:80]}...")
            t0 = time.perf_counter()
            response = requests.get(url, timeout=timeout)
            elapsed = time.perf_counter() - t0
            logger.info(f"  -> Response received in {elapsed:.2f}s (status={response.status_code})")

            if response.status_code == 429:
                # Rate limited - doi lau hon
                wait = min(BACKOFF_BASE * (2 ** attempt), BACKOFF_MAX)
                logger.warning(f"  -> Rate limited (429). Waiting {wait:.1f}s before retry...")
                time.sleep(wait)
                continue

            response.raise_for_status()
            data = response.json()

            if "hourly" not in data:
                raise ValueError("Invalid API response: 'hourly' key missing.")

            return data

        except requests.Timeout:
            wait = min(BACKOFF_BASE * (2 ** attempt), BACKOFF_MAX)
            logger.warning(f"  -> Timeout. Waiting {wait:.1f}s before retry...")
            time.sleep(wait)

        except requests.HTTPError as e:
            if attempt == max_retries:
                raise
            wait = min(BACKOFF_BASE * (2 ** attempt), BACKOFF_MAX)
            logger.warning(f"  -> HTTP error {e.response.status_code}. Waiting {wait:.1f}s before retry...")
            time.sleep(wait)

        except Exception as e:
            if attempt == max_retries:
                raise requests.RequestException(f"All {max_retries} attempts failed: {e}")
            wait = min(BACKOFF_BASE * (2 ** attempt), BACKOFF_MAX)
            logger.warning(f"  -> Error: {e}. Waiting {wait:.1f}s before retry...")
            time.sleep(wait)

    raise requests.RequestException(f"Failed to fetch after {max_retries} attempts.")


# ── Batch Fetching ──────────────────────────────────────────────────

def fetch_weather_by_months(
    start_date: str,
    end_date: str,
    latitude: float = LATITUDE,
    longitude: float = LONGITUDE,
    hourly_vars: Optional[List[str]] = None,
) -> List[pd.DataFrame]:
    """
    Thu thap du lieu thoi tiet theo tung thang de tranh payload qua lon.

    Open-Meteo khong gioi han cung ky thoi gian, nhung doi voi du lieu
    1 nam (8760 gio), viec chia nho thanh 12 thang giup:
      - Giam thoi gian cho moi request
      - De dang retry tung thang bi loi
      - Hien thi tien trinh ro rang

    Args:
        start_date: Ngay bat dau (YYYY-MM-DD).
        end_date: Ngay ket thuc (YYYY-MM-DD).
        latitude: Vi do.
        longitude: Kinh do.
        hourly_vars: Danh sach bien thoi tiet.

    Returns:
        List cac DataFrame, moi DataFrame la 1 thang.
    """
    if hourly_vars is None:
        hourly_vars = HOURLY_VARIABLES

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")

    dfs = []
    current = start_dt
    batch_idx = 0
    total_batches = 12  # 1 nam = 12 thang

    logger.info("=" * 60)
    logger.info("WEATHER DATA COLLECTION - BATCH MODE")
    logger.info(f"Location: ({latitude}, {longitude}) - Gwangyang, Korea")
    logger.info(f"Period: {start_date} to {end_date}")
    logger.info(f"Variables: {hourly_vars}")
    logger.info(f"Total batches: {total_batches}")
    logger.info("=" * 60)

    overall_t0 = time.perf_counter()

    while current <= end_dt:
        batch_idx += 1
        # Xac dinh cuoi thang
        if current.month == 12:
            next_month = current.replace(year=current.year + 1, month=1, day=1)
        else:
            next_month = current.replace(month=current.month + 1, day=1)

        batch_start = current.strftime("%Y-%m-%d")
        batch_end = (next_month - timedelta(days=1)).strftime("%Y-%m-%d")

        if datetime.strptime(batch_end, "%Y-%m-%d") > end_dt:
            batch_end = end_date

        logger.info(f"\n[Batch {batch_idx}/{total_batches}] {batch_start} -> {batch_end}")

        url = _build_api_url(
            latitude=latitude,
            longitude=longitude,
            start_date=batch_start,
            end_date=batch_end,
            hourly_vars=hourly_vars,
        )

        try:
            t0 = time.perf_counter()
            data = _fetch_with_retry(url)
            elapsed = time.perf_counter() - t0

            hourly = data["hourly"]
            df = pd.DataFrame(hourly)
            df["time"] = pd.to_datetime(df["time"])

            # Validation
            n_records = len(df)
            n_null = df.isnull().sum().sum()
            logger.info(f"  -> Fetched {n_records} records, {n_null} nulls in {elapsed:.2f}s")

            dfs.append(df)

        except Exception as e:
            logger.error(f"  -> FAILED: {e}")
            raise

        # Rate limiting delay
        time.sleep(REQUEST_DELAY)
        current = next_month

    total_elapsed = time.perf_counter() - overall_t0
    total_records = sum(len(d) for d in dfs)
    logger.info("\n" + "=" * 60)
    logger.info(f"COLLECTION COMPLETE: {total_records} records in {total_elapsed:.1f}s")
    logger.info("=" * 60)

    return dfs


# ── Validation ──────────────────────────────────────────────────────

def validate_weather_data(df: pd.DataFrame, expected_start: str, expected_end: str) -> dict:
    """
    Kiem tra tinh hop le cua du lieu thoi tiet sau khi thu thap.

    Args:
        df: DataFrame thoi tiet.
        expected_start: Ngay bat dau mong doi.
        expected_end: Ngay ket thuc mong doi.

    Returns:
        Dict bao cao validation.
    """
    report = {"passed": True, "checks": []}

    # 1. So dong
    expected_hours = (
        datetime.strptime(expected_end, "%Y-%m-%d")
        - datetime.strptime(expected_start, "%Y-%m-%d")
    ).days * 24 + 24
    n_rows = len(df)
    check1 = n_rows == expected_hours
    report["checks"].append(
        {
            "name": "row_count",
            "expected": expected_hours,
            "actual": n_rows,
            "passed": check1,
        }
    )

    # 2. Khong co null
    n_null = df.isnull().sum().sum()
    check2 = n_null == 0
    report["checks"].append(
        {"name": "no_nulls", "expected": 0, "actual": n_null, "passed": check2}
    )

    # 3. Range nhiet do (Gwangyang, Han Quoc)
    if "temperature_2m" in df.columns:
        t_min = df["temperature_2m"].min()
        t_max = df["temperature_2m"].max()
        check3 = -20 <= t_min and t_max <= 45
        report["checks"].append(
            {
                "name": "temperature_range",
                "expected": "[-20, 45] C",
                "actual": f"[{t_min:.1f}, {t_max:.1f}] C",
                "passed": check3,
            }
        )

    # 4. Range do am
    if "relative_humidity_2m" in df.columns:
        rh_min = df["relative_humidity_2m"].min()
        rh_max = df["relative_humidity_2m"].max()
        check4 = 0 <= rh_min and rh_max <= 100
        report["checks"].append(
            {
                "name": "humidity_range",
                "expected": "[0, 100] %",
                "actual": f"[{rh_min:.1f}, {rh_max:.1f}] %",
                "passed": check4,
            }
        )

    report["passed"] = all(c["passed"] for c in report["checks"])
    return report


# ── Main Export Function ────────────────────────────────────────────

def fetch_weather_to_csv(
    start_date: str,
    end_date: str,
    output_csv: str,
    latitude: float = LATITUDE,
    longitude: float = LONGITUDE,
) -> Tuple[pd.DataFrame, dict]:
    """
    Thu thap du lieu thoi tiet va luu vao CSV.

    Day la ham chinh duoc goi tu command line hoac pipeline.

    Args:
        start_date: Ngay bat dau (YYYY-MM-DD).
        end_date: Ngay ket thuc (YYYY-MM-DD).
        output_csv: Duong dan file CSV dau ra.
        latitude: Vi do.
        longitude: Kinh do.

    Returns:
        Tuple (DataFrame, validation_report).
    """
    output_path = Path(output_csv)

    # Thu thap theo thang
    dfs = fetch_weather_by_months(start_date, end_date, latitude, longitude)

    # Gop lai
    df = pd.concat(dfs, ignore_index=True)
    df = df.sort_values("time").reset_index(drop=True)

    # Validation
    logger.info("\nValidating fetched data...")
    report = validate_weather_data(df, start_date, end_date)

    for check in report["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        logger.info(f"  [{status}] {check['name']}: expected={check['expected']}, actual={check['actual']}")

    if not report["passed"]:
        logger.error("Validation FAILED. Data not saved.")
        raise ValueError("Weather data validation failed.")

    # Luu
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    logger.info(f"\nSaved {len(df)} records to {output_path}")

    return df, report


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    START_DATE = "2018-01-01"
    END_DATE = "2018-12-31"
    OUTPUT_FILE = "data/raw/weather_gwangyang_2018.csv"

    fetch_weather_to_csv(START_DATE, END_DATE, OUTPUT_FILE)

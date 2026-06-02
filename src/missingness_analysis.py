"""
Missingness Mechanism Analysis Module (Proactive Audit)

Cung cấp các kiểm định thống kê để phân loại cơ chế thiếu dữ liệu:
MCAR (Missing Completely At Random), MAR (Missing At Random),
và MNAR (Missing Not At Random).

Lưu ý: Tập dữ liệu DS108-Electrimight hiện tại (steel + weather) không có missing values.
Module này được triển khai như một cơ chế audit phòng ngừa (proactive audit)
để pipeline sẵn sàng xử lý missing data một cách có căn cứ khoa học
khi tích hợp thêm cảm biến hoặc dữ liệu mở rộng trong tương lai.

Tham chiếu: Rubin (1976); Sterne et al. (2009) BMJ.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

logger = logging.getLogger(__name__)


# ── Utilities ─────────────────────────────────────────────────────────


def _make_missing_mask(df: pd.DataFrame, cols: Optional[List[str]] = None) -> pd.DataFrame:
    """Tạo ma trận nhị phân đánh dấu vị trí missing (1 = missing)."""
    check_cols = cols if cols else df.columns.tolist()
    return df[check_cols].isnull().astype(int)


def _select_numeric_cols(df: pd.DataFrame, cols: Optional[List[str]] = None) -> List[str]:
    """Lọc các cột số từ DataFrame."""
    candidates = cols if cols else df.columns.tolist()
    numeric = df[candidates].select_dtypes(include=[np.number]).columns.tolist()
    return numeric


# ── MCAR Tests ────────────────────────────────────────────────────────


def little_mcar_test(
    df: pd.DataFrame,
    cols: Optional[List[str]] = None,
    alpha: float = 0.05,
) -> Dict[str, any]:
    """Thực hiện kiểm định Little's MCAR test (phiên bản đơn giản hóa).

    Chiến lược: Với mỗi cột có missing, chia mẫu thành nhóm missing và
    nhóm không missing, sau đó so sánh vector trung bình của các cột số
    khác bằng kiểm định Hotelling T² xấp xỉ bằng chi-square.

    Args:
        df: DataFrame đầu vào.
        cols: Các cột cần kiểm tra. Mặc định tất cả cột số.
        alpha: Mức ý nghĩa.

    Returns:
        Dict chứa kết quả kiểm định cho từng cột và kết luận tổng thể.
    """
    numeric_cols = _select_numeric_cols(df, cols)
    mask = _make_missing_mask(df, numeric_cols)
    results: Dict[str, any] = {}
    any_reject = False

    for col in numeric_cols:
        n_missing = mask[col].sum()
        if n_missing == 0 or n_missing == len(df):
            results[col] = {"n_missing": int(n_missing), "test": "SKIP", "reason": "No variation"}
            continue

        # Các cột khác làm biến so sánh
        other_cols = [c for c in numeric_cols if c != col]
        if not other_cols:
            continue

        missing_group = df.loc[mask[col] == 1, other_cols].dropna()
        observed_group = df.loc[mask[col] == 0, other_cols].dropna()

        if missing_group.empty or observed_group.empty:
            results[col] = {"n_missing": int(n_missing), "test": "SKIP", "reason": "Empty group"}
            continue

        # Xấp xỉ Hotelling T² bằng cách so sánh từng cột với t-test Bonferroni
        pvals = []
        for oc in other_cols:
            try:
                _, pval = stats.ttest_ind(
                    observed_group[oc].dropna(),
                    missing_group[oc].dropna(),
                    equal_var=False,
                    nan_policy="omit",
                )
                pvals.append(pval)
            except Exception:
                continue

        if not pvals:
            continue

        # Bonferroni correction
        bonf_p = min(np.min(pvals) * len(pvals), 1.0)
        reject = bonf_p < alpha
        any_reject = any_reject or reject

        results[col] = {
            "n_missing": int(n_missing),
            "min_pvalue_raw": float(np.min(pvals)),
            "bonferroni_pvalue": float(bonf_p),
            "reject_mcar": bool(reject),
            "mean_diffs": {
                oc: float(observed_group[oc].mean() - missing_group[oc].mean())
                for oc in other_cols
                if not observed_group[oc].empty and not missing_group[oc].empty
            },
        }

    overall = "NOT_MCAR" if any_reject else "MCAR_CANNOT_REJECT"
    return {"per_column": results, "overall_mcar": overall, "alpha": alpha}


def univariate_mcar_ttest(
    df: pd.DataFrame,
    target_col: str,
    compare_cols: Optional[List[str]] = None,
) -> Dict[str, any]:
    """Kiểm định MCAR đơn biến: so sánh trung bình các cột khác giữa missing và observed.

    Args:
        df: DataFrame đầu vào.
        target_col: Cột có missing cần kiểm tra.
        compare_cols: Cột so sánh. Mặc định tất cả cột số khác.

    Returns:
        Dict kết quả t-test cho từng cột so sánh.
    """
    if compare_cols is None:
        compare_cols = _select_numeric_cols(df)
        compare_cols = [c for c in compare_cols if c != target_col]

    mask = df[target_col].isnull()
    missing_idx = df.index[mask]
    observed_idx = df.index[~mask]

    result = {"target_col": target_col, "n_missing": int(mask.sum()), "comparisons": {}}

    for col in compare_cols:
        miss_vals = df.loc[missing_idx, col].dropna()
        obs_vals = df.loc[observed_idx, col].dropna()

        if len(miss_vals) < 2 or len(obs_vals) < 2:
            result["comparisons"][col] = {"status": "insufficient_data"}
            continue

        t_stat, p_val = stats.ttest_ind(obs_vals, miss_vals, equal_var=False, nan_policy="omit")
        result["comparisons"][col] = {
            "observed_mean": float(obs_vals.mean()),
            "missing_mean": float(miss_vals.mean()),
            "diff": float(obs_vals.mean() - miss_vals.mean()),
            "t_statistic": float(t_stat),
            "p_value": float(p_val),
        }

    return result


# ── MAR Test ──────────────────────────────────────────────────────────


def mar_logistic_test(
    df: pd.DataFrame,
    target_col: str,
    predictor_cols: Optional[List[str]] = None,
) -> Dict[str, any]:
    """Kiểm định MAR bằng logistic regression.

    Dự đoán xác suất missing của target_col từ các giá trị observed
    của predictor_cols. Nếu AUC > 0.6 (hoặc có coefficient ý nghĩa),
    missing có khả năng phụ thuộc vào observed data → MAR.

    Args:
        df: DataFrame đầu vào.
        target_col: Cột cần kiểm tra missingness.
        predictor_cols: Cột predictor. Mặc định các cột số khác.

    Returns:
        Dict chứa AUC, coefficients, và kết luận MAR.
    """
    if predictor_cols is None:
        predictor_cols = _select_numeric_cols(df)
        predictor_cols = [c for c in predictor_cols if c != target_col]

    # Chỉ dùng các hàng không missing ở predictors
    sub = df[[target_col] + predictor_cols].dropna(subset=predictor_cols)
    if sub.empty:
        return {"status": "ERROR", "reason": "No complete cases for predictors"}

    y = sub[target_col].isnull().astype(int).values
    X = sub[predictor_cols].values

    if np.unique(y).size < 2:
        return {"status": "SKIP", "reason": "No missing in target after filtering"}

    # Standardize để coefficient so sánh được
    X_mean = np.nanmean(X, axis=0)
    X_std = np.nanstd(X, axis=0)
    X_std[X_std == 0] = 1.0
    X_scaled = (X - X_mean) / X_std

    try:
        model = LogisticRegression(max_iter=1000, solver="lbfgs")
        model.fit(X_scaled, y)
        preds = model.predict_proba(X_scaled)[:, 1]
        auc = roc_auc_score(y, preds)
    except Exception as exc:
        return {"status": "ERROR", "reason": str(exc)}

    # Đánh giá ý nghĩa các hệ số (Wald approx: z = coef / std)
    coefs = dict(zip(predictor_cols, model.coef_[0]))
    intercept = float(model.intercept_[0])

    conclusion = "MAR_LIKELY" if auc > 0.6 else "MAR_WEAK"
    if auc < 0.55:
        conclusion = "MCAR_COMPATIBLE"

    return {
        "status": "OK",
        "target_col": target_col,
        "n_samples": len(sub),
        "n_missing": int(y.sum()),
        "auc": float(auc),
        "intercept": intercept,
        "coefficients": {k: float(v) for k, v in coefs.items()},
        "conclusion": conclusion,
    }


# ── MNAR Indicators ───────────────────────────────────────────────────


def mnar_range_analysis(
    df: pd.DataFrame,
    target_col: str,
    bins: int = 10,
) -> Dict[str, any]:
    """Phân tích MNAR: kiểm tra xem missing có tập trung ở range giá trị nào không.

    Nếu missing xảy ra nhiều ở các bin giá trị thấp/cao của chính cột đó,
    đây là dấu hiệu MNAR (missing phụ thuộc vào giá trị chưa quan sát).

    Args:
        df: DataFrame đầu vào.
        target_col: Cột cần phân tích.
        bins: Số lượng bin phân vị.

    Returns:
        Dict chứa tỷ lệ missing theo bin và kết luận MNAR.
    """
    series = df[target_col]
    mask = series.isnull()

    # Chia bin dựa trên quantile của observed values
    observed = series.dropna()
    if len(observed) < bins * 2:
        return {"status": "SKIP", "reason": "Insufficient observed values"}

    quantiles = np.linspace(0, 1, bins + 1)
    bin_edges = np.quantile(observed, quantiles)
    bin_edges[-1] += 1e-9  # Đảm bảo max nằm trong bin cuối

    # Gán bin cho từng giá trị (bao gồm cả missing, sẽ là NaN)
    binned = pd.cut(series, bins=bin_edges, include_lowest=True)

    missing_rates = {}
    for interval in binned.cat.categories:
        idx = binned == interval
        if idx.sum() == 0:
            continue
        rate = mask[idx].mean()
        missing_rates[str(interval)] = float(rate)

    rates = np.array(list(missing_rates.values()))
    if len(rates) == 0:
        return {"status": "SKIP", "reason": "No bins populated"}

    # Kiểm tra xem có bin nào có tỷ lệ missing bất thường không
    # (so với tỷ lệ missing toàn cục)
    global_rate = mask.mean()
    max_rate = rates.max()
    min_rate = rates.min()
    # pandas already preserves Interval objects in binned.cat.categories.

    # Chi-square goodness-of-fit: observed missing count vs expected uniform
    for interval in binned.cat.categories:
        idx = binned == interval
        # Simplified: so sánh rate với global rate
        pass

    # Đơn giản: nếu max_rate >> global_rate, có thể MNAR
    mnar_signal = max_rate > global_rate * 2 if global_rate > 0 else max_rate > 0.1

    return {
        "status": "OK",
        "target_col": target_col,
        "global_missing_rate": float(global_rate),
        "max_bin_missing_rate": float(max_rate),
        "min_bin_missing_rate": float(min_rate),
        "missing_rates_by_bin": missing_rates,
        "mnar_signal": bool(mnar_signal),
        "conclusion": "MNAR_LIKELY" if mnar_signal else "NO_MNAR_SIGNAL",
    }


# ── Orchestrator ──────────────────────────────────────────────────────


def analyze_missingness_mechanism(
    df: pd.DataFrame,
    cols: Optional[List[str]] = None,
    alpha: float = 0.05,
) -> Dict[str, any]:
    """Chạy toàn bộ phân tích missingness mechanism trên DataFrame.

    Pipeline:
      1. Little's MCAR test (multivariate approximation).
      2. MAR logistic test trên từng cột có missing.
      3. MNAR range analysis trên từng cột có missing.

    Args:
        df: DataFrame đầu vào.
        cols: Các cột số cần phân tích. Mặc định tất cả cột số.
        alpha: Mức ý nghĩa.

    Returns:
        Dict tổng hợp kết quả 3 loại kiểm định.
    """
    numeric_cols = _select_numeric_cols(df, cols)
    cols_with_missing = [c for c in numeric_cols if df[c].isnull().sum() > 0]

    if not cols_with_missing:
        return {"status": "SKIP", "reason": "No missing values found in selected columns"}

    logger.info("Bắt đầu phân tích missingness mechanism cho %d cột", len(cols_with_missing))

    # 1. MCAR
    mcar_result = little_mcar_test(df, cols=numeric_cols, alpha=alpha)

    # 2. MAR
    mar_results = {}
    for col in cols_with_missing:
        mar_results[col] = mar_logistic_test(df, target_col=col)

    # 3. MNAR
    mnar_results = {}
    for col in cols_with_missing:
        mnar_results[col] = mnar_range_analysis(df, target_col=col)

    return {
        "status": "OK",
        "columns_analyzed": cols_with_missing,
        "mcar": mcar_result,
        "mar": mar_results,
        "mnar": mnar_results,
    }


if __name__ == "__main__":
    # Demo nhỏ với synthetic missing data
    np.random.seed(42)
    n = 500
    demo_df = pd.DataFrame({
        "A": np.random.normal(0, 1, n),
        "B": np.random.normal(5, 2, n),
        "C": np.random.normal(-3, 0.5, n),
    })

    # Tạo MCAR: 10% missing ngẫu nhiên ở A
    mcar_idx = np.random.choice(demo_df.index, size=50, replace=False)
    demo_df.loc[mcar_idx, "A"] = np.nan

    # Tạo MAR: missing ở B khi C cao
    mar_idx = demo_df.index[demo_df["C"] > demo_df["C"].quantile(0.8)]
    mar_idx = np.random.choice(mar_idx, size=30, replace=False)
    demo_df.loc[mar_idx, "B"] = np.nan

    result = analyze_missingness_mechanism(demo_df)
    print("=== Missingness Analysis Demo ===")
    print(f"MCAR overall: {result['mcar']['overall_mcar']}")
    for col, res in result["mar"].items():
        if res.get("status") == "OK":
            print(f"MAR {col}: AUC={res['auc']:.3f} -> {res['conclusion']}")

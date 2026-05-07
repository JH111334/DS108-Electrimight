"""
Data Quality Audit Module

Module nay thuc hien kiem tra sau (deep audit) tren du lieu tho de phat hien
cac van de an, khong thay ro bang mat thuong. Day la buoc bat buoc truoc khi
tien hanh bat ky buoc lam sach nao, nham the hien cong suc phan tich va
nhieu "khoang trong" can xu ly trong du lieu.

Cac loai van de duoc kiem tra:
  1. Van de vat ly (Physical Constraints): PF > 1, PF < 0, P < 0, Q < 0...
  2. Van de nhat quan thoi gian (Temporal Consistency): gap, overlap, duplicate time
  3. Van de nhat quan categorical (Categorical Consistency): Ngay-S-Tuan khong khop
  4. Van de do luong (Measurement Artifacts): Gia tri co dinh, do phan giai thap
  5. Van de tinh toan (Derived Column Issues): Cong thuc khong nhat quan

Tham chieu: "Huong dan do an tien xu ly du lieu" - muc II (Data Quality Assessment).
"""

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


# ── Physical Constraint Rules ───────────────────────────────────────

PHYSICAL_RULES = {
    "power_factor_range": {
        "description": "Power Factor phai nam trong [0, 1] (dang he so, khong phai %)",
        "cols": ["Lagging_Current_Power_Factor", "Leading_Current_Power_Factor"],
        "check": lambda s: (s < 0) | (s > 1),
        "severity": "CRITICAL",
    },
    "usage_non_negative": {
        "description": "Cong suat tac dung P (Usage_kWh) khong the am",
        "cols": ["Usage_kWh"],
        "check": lambda s: s < 0,
        "severity": "CRITICAL",
    },
    "reactive_power_sign": {
        "description": "Cong suat phan khang co the am nhung khong nen bang 0 lien tuc",
        "cols": ["Lagging_Current_Reactive.Power_kVarh", "Leading_Current_Reactive_Power_kVarh"],
        "check": lambda s: s == 0,
        "severity": "WARNING",
    },
    "co2_non_negative": {
        "description": "CO2 khong the am",
        "cols": ["CO2(tCO2)"],
        "check": lambda s: s < 0,
        "severity": "CRITICAL",
    },
}


# ── Audit Functions ─────────────────────────────────────────────────

def audit_physical_constraints(df: pd.DataFrame) -> Dict:
    """
    Kiem tra cac rang buoc vat ly cua du lieu dien nang.

    Phat hien PF > 1, P < 0, Q = 0 bat thuong, v.v.
    Day la loi nghiem trong nhat vi vi pham dinh luat vat ly.

    Args:
        df: DataFrame tho.

    Returns:
        Dict chua danh sach vi pham va ty le.
    """
    violations = []
    for rule_name, rule in PHYSICAL_RULES.items():
        for col in rule["cols"]:
            if col not in df.columns:
                continue
            mask = rule["check"](df[col])
            n_viol = int(mask.sum())
            if n_viol > 0:
                violations.append(
                    {
                        "rule": rule_name,
                        "column": col,
                        "severity": rule["severity"],
                        "description": rule["description"],
                        "count": n_viol,
                        "percentage": round(n_viol / len(df) * 100, 4),
                        "sample_indices": df[mask].index[:5].tolist(),
                    }
                )
    return {"n_rules_checked": len(PHYSICAL_RULES), "violations": violations}


def audit_temporal_consistency(df: pd.DataFrame, date_col: str = "date") -> Dict:
    """
    Kiem tra tinh nhat quan thoi gian cua chuoi du lieu.

    Cac van de phat hien:
      - Thieu moc thoi gian (gaps)
      - Trung lap thoi gian (duplicates)
      - Khoang thoi gian khong deu (irregular frequency)

    Args:
        df: DataFrame tho (da sort theo thoi gian).
        date_col: Ten cot thoi gian.

    Returns:
        Dict bao cao temporal audit.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True)
    df = df.sort_values(date_col).reset_index(drop=True)

    diffs = df[date_col].diff().dropna()
    expected = pd.Timedelta("15 minutes")

    gaps = diffs[diffs > expected]
    overlaps = diffs[diffs < expected]
    duplicates = df[date_col].duplicated().sum()

    # Phan tich cau truc gap (neu co)
    gap_details = []
    if len(gaps) > 0:
        for idx, gap in gaps.items():
            gap_details.append(
                {
                    "index": int(idx),
                    "after_timestamp": str(df[date_col].iloc[idx]),
                    "gap_duration_minutes": int(gap.total_seconds() / 60),
                    "expected_records_missing": int(gap / expected) - 1,
                }
            )

    return {
        "total_records": len(df),
        "time_span": str(df[date_col].iloc[-1] - df[date_col].iloc[0]),
        "expected_frequency": "15min",
        "expected_records": int((df[date_col].iloc[-1] - df[date_col].iloc[0]) / expected) + 1,
        "actual_records": len(df),
        "missing_records_estimate": int(
            ((df[date_col].iloc[-1] - df[date_col].iloc[0]) / expected) + 1 - len(df)
        ),
        "duplicate_timestamps": int(duplicates),
        "gaps_found": len(gaps),
        "gap_details": gap_details[:10],  # Chi liet ke 10 gap dau
        "overlaps_found": len(overlaps),
        "irregular_intervals": int((diffs != expected).sum()),
    }


def audit_categorical_consistency(df: pd.DataFrame, date_col: str = "date") -> Dict:
    """
    Kiem tra nhat quan giua cac bien phan loai thoi gian.

    Vi du: Neu 'date' la Thu Hai thi 'Day_of_week' phai la 'Monday'.
           Neu 'date' la Thu Bay/Chu Nhat thi 'WeekStatus' phai la 'Weekend'.

    Args:
        df: DataFrame tho.
        date_col: Ten cot thoi gian.

    Returns:
        Dict bao cao categorical consistency.
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], dayfirst=True)

    issues = []

    # 1. Day_of_week consistency
    if "Day_of_week" in df.columns:
        expected_dow = df[date_col].dt.day_name()
        mismatch_dow = df["Day_of_week"] != expected_dow
        n_mismatch = int(mismatch_dow.sum())
        if n_mismatch > 0:
            issues.append(
                {
                    "check": "day_of_week_match",
                    "description": "Day_of_week khong khop voi timestamp",
                    "count": n_mismatch,
                    "percentage": round(n_mismatch / len(df) * 100, 4),
                    "examples": df[mismatch_dow][[date_col, "Day_of_week"]].head(3).to_dict("records"),
                }
            )

    # 2. WeekStatus consistency
    if "WeekStatus" in df.columns:
        expected_ws = df[date_col].dt.dayofweek.apply(
            lambda x: "Weekend" if x >= 5 else "Weekday"
        )
        mismatch_ws = df["WeekStatus"] != expected_ws
        n_mismatch = int(mismatch_ws.sum())
        if n_mismatch > 0:
            issues.append(
                {
                    "check": "weekend_status_match",
                    "description": "WeekStatus khong khop voi dayofweek",
                    "count": n_mismatch,
                    "percentage": round(n_mismatch / len(df) * 100, 4),
                    "examples": df[mismatch_ws][[date_col, "WeekStatus", "Day_of_week"]].head(3).to_dict("records"),
                }
            )

    # 3. NSM consistency (Number of Seconds from Midnight)
    if "NSM" in df.columns:
        expected_nsm = (
            df[date_col].dt.hour * 3600
            + df[date_col].dt.minute * 60
            + df[date_col].dt.second
        )
        mismatch_nsm = df["NSM"] != expected_nsm
        n_mismatch = int(mismatch_nsm.sum())
        if n_mismatch > 0:
            issues.append(
                {
                    "check": "nsm_match",
                    "description": "NSM khong khop voi thoi gian trong ngay",
                    "count": n_mismatch,
                    "percentage": round(n_mismatch / len(df) * 100, 4),
                    "examples": df[mismatch_nsm][[date_col, "NSM"]].head(3).to_dict("records"),
                }
            )

    return {"n_checks": 3, "issues_found": len(issues), "issues": issues}


def audit_measurement_artifacts(df: pd.DataFrame) -> Dict:
    """
    Kiem tra cac hien tuong do luong (measurement artifacts).

    Cac van de:
      - Gia tri co dinh (constant values) - co the do cam bi treo
      - Do phan giai thap (low resolution) - chi co vai gia tri unique
      - Outliers cuc doan (extreme outliers)
      - Zero values bat thuong

    Args:
        df: DataFrame tho.

    Returns:
        Dict bao cao measurement artifacts.
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    artifacts = []

    for col in numeric_cols:
        series = df[col]
        n_unique = series.nunique()
        n_zero = int((series == 0).sum())
        zero_pct = round(n_zero / len(df) * 100, 4)

        # Constant values check
        if n_unique == 1:
            artifacts.append(
                {
                    "column": col,
                    "type": "constant_value",
                    "description": f"Cot chi co 1 gia tri duy nhat: {series.iloc[0]}",
                    "severity": "CRITICAL",
                }
            )
            continue

        # Low resolution check (< 1% unique values)
        resolution_pct = n_unique / len(df) * 100
        if resolution_pct < 1.0:
            artifacts.append(
                {
                    "column": col,
                    "type": "low_resolution",
                    "description": f"Do phan giai thap: chi {n_unique} gia tri unique ({resolution_pct:.4f}%)",
                    "severity": "WARNING",
                    "unique_values": n_unique,
                }
            )

        # Zero values check
        if n_zero > 0 and col not in ["Leading_Current_Reactive_Power_kVarh"]:
            artifacts.append(
                {
                    "column": col,
                    "type": "zero_values",
                    "description": f"Co {n_zero} gia tri bang 0 ({zero_pct}%)",
                    "severity": "INFO" if zero_pct < 1 else "WARNING",
                    "count": n_zero,
                    "percentage": zero_pct,
                }
            )

        # Extreme outliers (beyond 5 sigma)
        mean, std = series.mean(), series.std()
        if std > 0:
            outliers = np.abs(series - mean) > 5 * std
            n_outliers = int(outliers.sum())
            if n_outliers > 0:
                artifacts.append(
                    {
                        "column": col,
                        "type": "extreme_outliers",
                        "description": f"{n_outliers} outliers vuot qua 5-sigma",
                        "severity": "WARNING",
                        "count": n_outliers,
                        "percentage": round(n_outliers / len(df) * 100, 4),
                    }
                )

    return {"n_numeric_columns_checked": len(numeric_cols), "artifacts": artifacts}


def audit_derived_columns(df: pd.DataFrame) -> Dict:
    """
    Kiem tra tinh nhat quan cua cac cot tinh toan.

    Vi du:
      - CO2(tCO2) thuong tinh tu Usage_kWh * emission_factor
      - Apparent Power S = sqrt(P^2 + Q^2)
      - Power Factor = P / S

    Args:
        df: DataFrame tho.

    Returns:
        Dict bao cao derived column audit.
    """
    findings = []

    # 1. Kiem tra PF theo dinh nghia: PF = P / S
    # Neu du lieu da co P, Q, PF thi PF * S ~ P
    if all(c in df.columns for c in ["Usage_kWh", "Lagging_Current_Reactive.Power_kVarh", "Lagging_Current_Power_Factor"]):
        P = df["Usage_kWh"]
        Q = df["Lagging_Current_Reactive.Power_kVarh"]
        S_calc = np.sqrt(P**2 + Q**2)
        PF_reported = df["Lagging_Current_Power_Factor"]

        # Neu PF duoc bao cao dang % (0-100), chuyen ve he so
        if PF_reported.max() > 1:
            PF_reported_coef = PF_reported / 100.0
            findings.append(
                {
                    "check": "power_factor_unit",
                    "description": "Lagging_Current_Power_Factor duoc bao cao dang % (0-100), can chia 100 de ve he so (0-1)",
                    "severity": "CRITICAL",
                    "max_reported": float(PF_reported.max()),
                    "suggested_fix": "df['Lagging_Current_Power_Factor'] = df['Lagging_Current_Power_Factor'] / 100.0",
                }
            )
        else:
            PF_reported_coef = PF_reported

        # Kiem tra nhat quan: P ~ PF * S
        # (cho phep sai so do lam tron)
        tolerance = 0.05 * S_calc
        consistent = np.abs(P - PF_reported_coef * S_calc) < tolerance
        n_inconsistent = int((~consistent).sum())
        if n_inconsistent > 0:
            findings.append(
                {
                    "check": "power_factor_consistency",
                    "description": f"{n_inconsistent} diem PF khong nhat quan voi P va Q",
                    "severity": "WARNING",
                    "inconsistent_count": n_inconsistent,
                    "percentage": round(n_inconsistent / len(df) * 100, 4),
                }
            )

    # 2. Kiem tra Leading PF unit
    if "Leading_Current_Power_Factor" in df.columns:
        if df["Leading_Current_Power_Factor"].max() > 1:
            findings.append(
                {
                    "check": "leading_power_factor_unit",
                    "description": "Leading_Current_Power_Factor duoc bao cao dang % (0-100), can chia 100",
                    "severity": "CRITICAL",
                    "max_reported": float(df["Leading_Current_Power_Factor"].max()),
                    "suggested_fix": "df['Leading_Current_Power_Factor'] = df['Leading_Current_Power_Factor'] / 100.0",
                }
            )

    # 3. Kiem tra CO2 tinh toan
    if "CO2(tCO2)" in df.columns and "Usage_kWh" in df.columns:
        # Neu Usage_kWh = 0 thi CO2 phai = 0
        zero_usage = df["Usage_kWh"] == 0
        nonzero_co2_at_zero_usage = df.loc[zero_usage, "CO2(tCO2)"] != 0
        if nonzero_co2_at_zero_usage.any():
            findings.append(
                {
                    "check": "co2_zero_usage_consistency",
                    "description": f"Co {int(nonzero_co2_at_zero_usage.sum())} diem co Usage_kWh=0 nhung CO2!=0",
                    "severity": "CRITICAL",
                }
            )

    return {"n_checks": 3, "findings": findings}


# ── Orchestrator ────────────────────────────────────────────────────

def run_full_audit(df: pd.DataFrame, date_col: str = "date") -> Dict:
    """
    Chay toan bo qua trinh audit du lieu.

    Args:
        df: DataFrame tho.
        date_col: Ten cot thoi gian.

    Returns:
        Dict tong hop ket qua audit.
    """
    return {
        "physical_constraints": audit_physical_constraints(df),
        "temporal_consistency": audit_temporal_consistency(df, date_col),
        "categorical_consistency": audit_categorical_consistency(df, date_col),
        "measurement_artifacts": audit_measurement_artifacts(df),
        "derived_columns": audit_derived_columns(df),
    }


def print_audit_report(report: Dict) -> None:
    """
    In bao cao audit ra console duoi dang de doc.

    Args:
        report: Ket qua tu run_full_audit().
    """
    print("=" * 70)
    print("DATA QUALITY AUDIT REPORT")
    print("=" * 70)

    # Physical Constraints
    phys = report["physical_constraints"]
    print(f"\n[1] PHYSICAL CONSTRAINTS - {phys['n_rules_checked']} rules checked")
    if phys["violations"]:
        print(f"    !!! FOUND {len(phys['violations'])} VIOLATIONS !!!")
        for v in phys["violations"]:
            print(f"    [{v['severity']}] {v['rule']} | Col: {v['column']}")
            print(f"        -> {v['description']}")
            print(f"        -> {v['count']} records ({v['percentage']}%)")
    else:
        print("    All physical constraints satisfied.")

    # Temporal
    temp = report["temporal_consistency"]
    print(f"\n[2] TEMPORAL CONSISTENCY")
    print(f"    Records: {temp['actual_records']} / Expected: {temp['expected_records']}")
    print(f"    Missing estimate: {temp['missing_records_estimate']}")
    print(f"    Duplicates: {temp['duplicate_timestamps']}")
    print(f"    Gaps: {temp['gaps_found']} | Overlaps: {temp['overlaps_found']} | Irregular: {temp['irregular_intervals']}")
    if temp["gap_details"]:
        print("    Gap examples:")
        for g in temp["gap_details"][:3]:
            print(f"      - At {g['after_timestamp']}: missing {g['expected_records_missing']} records")

    # Categorical
    cat = report["categorical_consistency"]
    print(f"\n[3] CATEGORICAL CONSISTENCY - {cat['n_checks']} checks")
    if cat["issues_found"]:
        print(f"    !!! FOUND {cat['issues_found']} ISSUES !!!")
        for issue in cat["issues"]:
            print(f"    -> {issue['check']}: {issue['count']} mismatches ({issue['percentage']}%)")
    else:
        print("    All categorical variables consistent with timestamps.")

    # Measurement
    meas = report["measurement_artifacts"]
    print(f"\n[4] MEASUREMENT ARTIFACTS - {meas['n_numeric_columns_checked']} columns checked")
    if meas["artifacts"]:
        critical = [a for a in meas["artifacts"] if a["severity"] == "CRITICAL"]
        warnings = [a for a in meas["artifacts"] if a["severity"] == "WARNING"]
        print(f"    Critical: {len(critical)} | Warnings: {len(warnings)}")
        for a in meas["artifacts"][:5]:
            print(f"    [{a['severity']}] {a['column']}: {a['description']}")
    else:
        print("    No measurement artifacts detected.")

    # Derived
    der = report["derived_columns"]
    print(f"\n[5] DERIVED COLUMNS - {der['n_checks']} checks")
    if der["findings"]:
        print(f"    !!! FOUND {len(der['findings'])} ISSUES !!!")
        for f in der["findings"]:
            print(f"    [{f['severity']}] {f['check']}: {f['description']}")
            if "suggested_fix" in f:
                print(f"        Suggested fix: {f['suggested_fix']}")
    else:
        print("    All derived columns consistent.")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    from src.data_loader import load_steel_data
    from src.utils import RAW_CSV

    df = load_steel_data(RAW_CSV)
    report = run_full_audit(df)
    print_audit_report(report)

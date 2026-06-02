"""Validate FC-GAN augmentation without overwriting the final gold dataset."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from src.gold.gan_augmentation import generate_synthetic_samples, train_gan
from src.utils import GOLD_DIR


def _to_builtin(value: Any) -> Any:
    """Convert numpy scalars to JSON-serializable Python values."""
    if isinstance(value, np.generic):
        return value.item()
    return value


def validate_gan(
    input_path: Path,
    synthetic_path: Path,
    stats_path: Path,
    epochs: int = 2000,
    n_synthetic: int = 500,
    latent_dim: int = 100,
    seed: int = 42,
) -> dict[str, Any]:
    """Train GAN on proxy anomaly rows and write validation artifacts."""
    import tensorflow as tf

    np.random.seed(seed)
    tf.random.set_seed(seed)

    df = pd.read_csv(input_path)
    if "anomaly_any" not in df.columns:
        raise ValueError("Input dataset must contain anomaly_any")
    if "Usage_kWh" not in df.columns:
        raise ValueError("Input dataset must contain Usage_kWh")

    minority_df = df[df["anomaly_any"].astype(bool)].copy()
    numeric_cols = minority_df.select_dtypes(include=[np.number]).columns.tolist()
    data = minority_df[numeric_cols].dropna()
    if data.empty:
        raise ValueError("No numeric proxy anomaly rows available for GAN training")

    scaler = MinMaxScaler(feature_range=(-1, 1))
    data_scaled = scaler.fit_transform(data.values)

    generator, _ = train_gan(
        data_scaled,
        latent_dim=latent_dim,
        epochs=epochs,
        batch_size=min(64, len(data_scaled)),
        sample_interval=max(1, epochs // 10),
    )

    synthetic_scaled = generate_synthetic_samples(
        generator,
        n_samples=n_synthetic,
        latent_dim=latent_dim,
    )
    synthetic = scaler.inverse_transform(synthetic_scaled)
    synthetic_df = pd.DataFrame(synthetic, columns=numeric_cols)

    synthetic_path.parent.mkdir(parents=True, exist_ok=True)
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    synthetic_df.to_csv(synthetic_path, index=False, encoding="utf-8")

    real_usage = data["Usage_kWh"]
    syn_usage = synthetic_df["Usage_kWh"]
    real_corr = data.corr(numeric_only=True)
    syn_corr = synthetic_df.corr(numeric_only=True)
    corr_delta = (real_corr - syn_corr).abs().to_numpy()

    stats = {
        "input_path": str(input_path),
        "synthetic_path": str(synthetic_path),
        "seed": seed,
        "epochs": epochs,
        "latent_dim": latent_dim,
        "minority_samples": int(len(minority_df)),
        "training_samples_after_dropna": int(len(data)),
        "n_features": int(len(numeric_cols)),
        "n_synthetic": int(n_synthetic),
        "real_mean_usage": float(real_usage.mean()),
        "syn_mean_usage": float(syn_usage.mean()),
        "real_std_usage": float(real_usage.std()),
        "syn_std_usage": float(syn_usage.std()),
        "mean_error_pct": float(
            abs(syn_usage.mean() - real_usage.mean()) / abs(real_usage.mean()) * 100
        ),
        "std_error_pct": float(
            abs(syn_usage.std() - real_usage.std()) / abs(real_usage.std()) * 100
        ),
        "correlation_mae": float(np.nanmean(corr_delta)),
        "correlation_max_abs_error": float(np.nanmax(corr_delta)),
    }
    stats = {key: _to_builtin(value) for key, value in stats.items()}
    stats_path.write_text(
        json.dumps(stats, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate FC-GAN augmentation")
    parser.add_argument("--input", type=Path, default=GOLD_DIR / "steel_final.csv")
    parser.add_argument(
        "--synthetic",
        type=Path,
        default=GOLD_DIR / "steel_synthetic_gan.csv",
    )
    parser.add_argument("--stats", type=Path, default=Path("metadata/pipeline/gan_stats.json"))
    parser.add_argument("--epochs", type=int, default=2000)
    parser.add_argument("--n-synthetic", type=int, default=500)
    parser.add_argument("--latent-dim", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    stats = validate_gan(
        input_path=args.input,
        synthetic_path=args.synthetic,
        stats_path=args.stats,
        epochs=args.epochs,
        n_synthetic=args.n_synthetic,
        latent_dim=args.latent_dim,
        seed=args.seed,
    )
    print(json.dumps(stats, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

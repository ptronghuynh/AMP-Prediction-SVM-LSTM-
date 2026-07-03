"""Confidence-interval utilities used by the reproducibility package."""

from __future__ import annotations

import argparse
import math

Z_95 = 1.959963984540054


def wilson_ci(successes: int, total: int, z: float = Z_95) -> tuple[float, float]:
    """Return the Wilson score interval for a binomial proportion."""
    if total <= 0:
        raise ValueError("total must be positive")
    phat = successes / total
    denom = 1.0 + z * z / total
    center = (phat + z * z / (2.0 * total)) / denom
    margin = z * math.sqrt((phat * (1.0 - phat) + z * z / (4.0 * total)) / total) / denom
    return max(0.0, center - margin), min(1.0, center + margin)


def hanley_mcneil_auc_ci(
    auc: float,
    n_positive: int,
    n_negative: int,
    z: float = Z_95,
) -> tuple[float, float]:
    """Return the large-sample Hanley-McNeil AUC confidence interval."""
    if not 0.0 <= auc <= 1.0:
        raise ValueError("auc must be between 0 and 1")
    if n_positive <= 0 or n_negative <= 0:
        raise ValueError("n_positive and n_negative must be positive")
    q1 = auc / (2.0 - auc)
    q2 = 2.0 * auc * auc / (1.0 + auc)
    variance = (
        auc * (1.0 - auc)
        + (n_positive - 1) * (q1 - auc * auc)
        + (n_negative - 1) * (q2 - auc * auc)
    ) / (n_positive * n_negative)
    se = math.sqrt(max(variance, 0.0))
    return max(0.0, auc - z * se), min(1.0, auc + z * se)


def _fmt(value: float) -> str:
    return f"{value:.4f}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute Wilson and Hanley-McNeil confidence intervals.")
    parser.add_argument("--successes", type=int, help="Number of correct predictions for Wilson CI.")
    parser.add_argument("--total", type=int, help="Total number of predictions for Wilson CI.")
    parser.add_argument("--auc", type=float, help="AUC-ROC value for Hanley-McNeil CI.")
    parser.add_argument("--n-positive", type=int, help="Number of positive-class records for AUC CI.")
    parser.add_argument("--n-negative", type=int, help="Number of negative-class records for AUC CI.")
    args = parser.parse_args()

    if args.successes is not None or args.total is not None:
        if args.successes is None or args.total is None:
            raise SystemExit("--successes and --total must be provided together")
        low, high = wilson_ci(args.successes, args.total)
        print(f"wilson_95_ci,{_fmt(low)},{_fmt(high)}")

    if args.auc is not None or args.n_positive is not None or args.n_negative is not None:
        if args.auc is None or args.n_positive is None or args.n_negative is None:
            raise SystemExit("--auc, --n-positive, and --n-negative must be provided together")
        low, high = hanley_mcneil_auc_ci(args.auc, args.n_positive, args.n_negative)
        print(f"auc_95_ci,{_fmt(low)},{_fmt(high)}")

    if args.successes is None and args.auc is None:
        examples = [
            ("SVM-combined accuracy", *wilson_ci(5820, 6000)),
            ("LSTM-combined accuracy", *wilson_ci(5730, 6000)),
            ("AMPDiscover AUC", *hanley_mcneil_auc_ci(0.9202, 500, 500)),
        ]
        for name, low, high in examples:
            print(f"{name},{_fmt(low)},{_fmt(high)}")


if __name__ == "__main__":
    main()

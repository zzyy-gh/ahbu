"""
Spec: 20-plan/affective-state/pilots-README.md#P-6

P-6 — Feature stability module unit test (shared substrate smoke test).

Tests the cross_dataset_correlation function on synthetic data where the
ground-truth reproducibility is known. Inline implementation — the
promotable version moves to 30-implement/shared/eval/feature_stability.py
once a 2nd consumer exists (per promotion rule in 30-implement/README.md).

Synthetic test cases:
  Case 1 — ALL features reproducible: 3 datasets, 5 features each, every
           feature has rho=0.5 with target across datasets, same sign.
           Expected: N_reproducible = 5, all consistent.
  Case 2 — NO features reproducible: 3 datasets, 5 features, every
           feature uncorrelated with target.
           Expected: N_reproducible ~ 0 (modulo random noise).
  Case 3 — SIGN-INCONSISTENT: 3 datasets, 5 features. Feature 0 has
           rho=+0.5 in dataset 1 and 2 but rho=-0.5 in dataset 3.
           Expected: feature 0 NOT counted as reproducible (sign mismatch).

Success criterion: all 3 cases pass.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def cross_dataset_correlation(feature_df_list, target_col, alpha=0.05):
    """Inline implementation. Promotable interface per approach.md.

    For each feature in each dataset, compute Spearman rho with target;
    apply BH-FDR within each dataset; a feature is "reproducible" if
    significant in ALL datasets AND sign consistent.

    Returns DataFrame: feature, n_significant, n_consistent_sign,
                       reproducible (bool), per-dataset rho columns.
    """
    import numpy as np
    import pandas as pd
    from scipy.stats import spearmanr
    from statsmodels.stats.multitest import fdrcorrection

    feature_cols = [c for c in feature_df_list[0].columns if c != target_col]
    rows = []

    per_dataset_results = []
    for df in feature_df_list:
        rhos = {}
        ps = {}
        for f in feature_cols:
            r, p = spearmanr(df[f], df[target_col])
            rhos[f] = r
            ps[f] = p
        sig_arr, _ = fdrcorrection([ps[f] for f in feature_cols], alpha=alpha)
        per_dataset_results.append(
            {f: {"rho": rhos[f], "p": ps[f], "sig": sig_arr[i]} for i, f in enumerate(feature_cols)}
        )

    for f in feature_cols:
        rhos_f = [r[f]["rho"] for r in per_dataset_results]
        sigs_f = [r[f]["sig"] for r in per_dataset_results]
        n_sig = sum(sigs_f)
        n_consistent_sign = (
            1 if all(rhos_f[i] > 0 for i in range(len(rhos_f)))
            or all(rhos_f[i] < 0 for i in range(len(rhos_f)))
            else 0
        )
        reproducible = (n_sig == len(feature_df_list)) and bool(n_consistent_sign)
        row = {
            "feature": f,
            "n_significant": int(n_sig),
            "sign_consistent": bool(n_consistent_sign),
            "reproducible": reproducible,
        }
        for i, r in enumerate(rhos_f):
            row[f"rho_dataset_{i}"] = round(float(r), 4)
        rows.append(row)

    return pd.DataFrame(rows)


def make_dataset(n_subjects, n_features, target_rho, seed, sign_per_feature=None):
    import numpy as np
    import pandas as pd

    rng = np.random.default_rng(seed)
    n = n_subjects * 30
    target = rng.normal(0, 1, n)
    cols = {"target": target}
    for j in range(n_features):
        sign = 1 if sign_per_feature is None else sign_per_feature[j]
        rho = sign * target_rho
        if rho == 0:
            cols[f"f{j}"] = rng.normal(0, 1, n)
        else:
            noise = rng.normal(0, np.sqrt(1 - rho**2), n)
            cols[f"f{j}"] = rho * target + noise
    return pd.DataFrame(cols)


def probe() -> dict:
    cases = []

    df_list = [make_dataset(50, 5, 0.5, seed=s) for s in (1, 2, 3)]
    res1 = cross_dataset_correlation(df_list, target_col="target")
    n_repro_1 = int(res1["reproducible"].sum())
    cases.append(
        {
            "case": "all reproducible (rho=0.5, n=1500/dataset, 5 features)",
            "n_reproducible": n_repro_1,
            "expected_min": 5,
            "ok": n_repro_1 == 5,
        }
    )

    df_list = [make_dataset(50, 5, 0.0, seed=s) for s in (10, 20, 30)]
    res2 = cross_dataset_correlation(df_list, target_col="target")
    n_repro_2 = int(res2["reproducible"].sum())
    cases.append(
        {
            "case": "no reproducible (rho=0.0)",
            "n_reproducible": n_repro_2,
            "expected_max": 0,
            "ok": n_repro_2 == 0,
        }
    )

    signs_dataset3 = [-1, 1, 1, 1, 1]
    df_list = [
        make_dataset(50, 5, 0.5, seed=100),
        make_dataset(50, 5, 0.5, seed=200),
        make_dataset(50, 5, 0.5, seed=300, sign_per_feature=signs_dataset3),
    ]
    res3 = cross_dataset_correlation(df_list, target_col="target")
    feature_0_repro = bool(res3.loc[res3["feature"] == "f0", "reproducible"].iloc[0])
    n_repro_3 = int(res3["reproducible"].sum())
    cases.append(
        {
            "case": "sign-inconsistent (f0 +/+/- across datasets)",
            "feature_0_reproducible": feature_0_repro,
            "n_reproducible": n_repro_3,
            "expected_f0_reproducible": False,
            "expected_n": 4,
            "ok": (not feature_0_repro) and n_repro_3 == 4,
        }
    )

    return {
        "status": "pass" if all(c["ok"] for c in cases) else "fail",
        "n_cases_passed": sum(1 for c in cases if c["ok"]),
        "n_cases_total": len(cases),
        "cases": cases,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-6 feature_stability unit test")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe()
    result["pilot"] = "P-6"
    result["spec"] = "20-plan/affective-state/pilots-README.md#P-6"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p6_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

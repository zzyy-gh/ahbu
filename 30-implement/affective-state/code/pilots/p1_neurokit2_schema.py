"""
Spec: 20-plan/affective-state/pilots-README.md#P-1

P-1 — NeuroKit2 feature schema smoke test.

Lock the feature list at the pinned NeuroKit2 version. Writes
runs/feature_schema_v1.yaml with the exact column names produced by
`nk.hrv_time`, `nk.hrv_frequency`, `nk.hrv_nonlinear`, and `nk.eda_features`
on a synthetic signal. This count IS N_features for the binomial test
(per M-1 fix; the original arXiv:2508.10561 figure of 164 is a comparison
target, not a hard requirement).

Also: per m-1 fix, manually note whether arXiv:2508.10561 includes
cardiac (HRV) features. This script can't verify the paper; user marks
the result field.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def probe() -> dict:
    try:
        import neurokit2 as nk
        import numpy as np
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    fs = 250
    seconds = 60
    rng = np.random.default_rng(42)
    ecg = nk.ecg_simulate(duration=seconds, sampling_rate=fs, noise=0.05, random_state=42)
    eda = np.cumsum(rng.normal(0, 0.01, size=fs * seconds)) + 5.0  # synthetic EDA-like

    schema = {"nk_version": nk.__version__, "feature_groups": {}}
    n_features = 0

    try:
        ecg_signals, info = nk.ecg_process(ecg, sampling_rate=fs)
        rpeaks = info["ECG_R_Peaks"]
        for fn_name in ["hrv_time", "hrv_frequency", "hrv_nonlinear"]:
            fn = getattr(nk, fn_name)
            df = fn(rpeaks, sampling_rate=fs)
            cols = list(df.columns)
            schema["feature_groups"][fn_name] = cols
            n_features += len(cols)
    except Exception as e:  # noqa: BLE001
        schema["ecg_error"] = str(e)

    try:
        eda_clean = nk.eda_clean(eda, sampling_rate=fs)
        try:
            phasic = nk.eda_phasic(eda_clean, sampling_rate=fs, method="cvxeda")
            schema["eda_method"] = "cvxeda"
        except Exception as e:  # noqa: BLE001
            phasic = nk.eda_phasic(eda_clean, sampling_rate=fs, method="highpass")
            schema["eda_method"] = "highpass"
            schema["cvxeda_error"] = str(e)
        eda_signals, info = nk.eda_process(eda, sampling_rate=fs)
        eda_features = nk.eda_intervalrelated(eda_signals)
        cols = list(eda_features.columns)
        schema["feature_groups"]["eda_features"] = cols
        n_features += len(cols)
    except Exception as e:  # noqa: BLE001
        schema["eda_error"] = str(e)

    schema["n_features"] = n_features
    schema["n_features_arxiv_2508_10561_target"] = 164
    schema["arxiv_2508_10561_includes_hrv_FILL_MANUALLY"] = "[unverified — fetch the paper Methods to confirm; per m-1 fix in methodology-critic]"

    out_dir = Path(__file__).resolve().parents[2] / "runs"
    out_dir.mkdir(parents=True, exist_ok=True)
    yaml_path = out_dir / "feature_schema_v1.yaml"
    try:
        import yaml
        yaml_path.write_text(yaml.safe_dump(schema, sort_keys=False))
    except ImportError:
        yaml_path.with_suffix(".json").write_text(json.dumps(schema, indent=2))

    return {
        "status": "pass" if n_features > 0 else "fail",
        "n_features": n_features,
        "schema_path": str(yaml_path),
        "groups": {k: len(v) if isinstance(v, list) else v for k, v in schema["feature_groups"].items()},
        "eda_method_used": schema.get("eda_method"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-1 NeuroKit2 feature schema smoke test")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe()
    result["pilot"] = "P-1"
    result["spec"] = "20-plan/affective-state/pilots-README.md#P-1"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p1_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

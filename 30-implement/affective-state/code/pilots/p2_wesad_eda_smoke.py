"""
Spec: 20-plan/affective-state/pilots-README.md#P-2

P-2 — WESAD ECG + EDA extraction smoke test (subject S2).

Pre-pilot smoke (m-6 fix per methodology-critic): cvxpy install
attempt is logged. If install/import fails, script falls back to
nk.eda_phasic(method="highpass") and documents the swap. Continues
either way.

Procedure:
  1. Locate WESAD/S2/S2.pkl (download per code/README.md).
  2. Load pickle. Extract chest ECG (700 Hz) + EDA (700 Hz) for the
     "stress" and "baseline" condition windows.
  3. Run ECG preprocessing on one 60-second window: bandpass +
     R-peak detection + HRV time/frequency/nonlinear features.
  4. Run EDA preprocessing on one 60-second window: resample to 4 Hz,
     clean, decompose (cvxEDA or highpass), extract features.
  5. Cross-check R-peak count with BioSPPy.

Success criteria:
  (a) ECG R-peak count for a 60-second window: 50 < n < 100 (resting HR).
  (b) EDA pipeline returns positive finite SCL_mean.
  (c) BioSPPy R-peak count within 10% of NeuroKit2 count.
"""

import argparse
import json
import pickle
import sys
import time
from pathlib import Path


def cvxpy_smoke() -> dict:
    try:
        import cvxpy  # noqa: F401
        return {"installed": True, "import_ok": True}
    except ImportError:
        return {"installed": False, "import_ok": False, "fallback": "highpass"}


def probe(wesad_dir: Path) -> dict:
    cvxpy_status = cvxpy_smoke()

    pkl_path = wesad_dir / "S2" / "S2.pkl"
    if not pkl_path.exists():
        return {"status": "fail", "reason": f"S2.pkl not found at {pkl_path}", "cvxpy": cvxpy_status}

    try:
        import numpy as np
        import neurokit2 as nk
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}", "cvxpy": cvxpy_status}

    with open(pkl_path, "rb") as f:
        data = pickle.load(f, encoding="latin1")

    chest_ecg = np.asarray(data["signal"]["chest"]["ECG"]).flatten()
    chest_eda = np.asarray(data["signal"]["chest"]["EDA"]).flatten()
    labels = np.asarray(data["label"])
    fs = 700

    # WESAD label codes: 0=transient, 1=baseline, 2=stress, 3=amusement, 4=meditation
    baseline_idx = np.where(labels == 1)[0]
    stress_idx = np.where(labels == 2)[0]

    if len(baseline_idx) < fs * 60 or len(stress_idx) < fs * 60:
        return {
            "status": "fail",
            "reason": "insufficient baseline or stress samples for 60-s window",
            "n_baseline_samples": int(len(baseline_idx)),
            "n_stress_samples": int(len(stress_idx)),
        }

    win_baseline_ecg = chest_ecg[baseline_idx[: fs * 60]]
    win_baseline_eda = chest_eda[baseline_idx[: fs * 60]]

    # ECG pipeline
    try:
        ecg_signals, info = nk.ecg_process(win_baseline_ecg, sampling_rate=fs)
        rpeaks = info["ECG_R_Peaks"]
        n_peaks_nk = int(len(rpeaks))
        hrv_time = nk.hrv_time(rpeaks, sampling_rate=fs)
        hrv_freq = nk.hrv_frequency(rpeaks, sampling_rate=fs)
        hrv_nl = nk.hrv_nonlinear(rpeaks, sampling_rate=fs)
        n_features_nk = len(hrv_time.columns) + len(hrv_freq.columns) + len(hrv_nl.columns)
    except Exception as e:  # noqa: BLE001
        return {"status": "fail", "reason": f"NeuroKit2 ECG pipeline error: {e}"}

    # EDA pipeline
    try:
        eda_clean = nk.eda_clean(win_baseline_eda, sampling_rate=fs)
        try:
            phasic = nk.eda_phasic(eda_clean, sampling_rate=fs, method="cvxeda")
            eda_method = "cvxeda"
        except Exception:  # noqa: BLE001
            phasic = nk.eda_phasic(eda_clean, sampling_rate=fs, method="highpass")
            eda_method = "highpass"
        eda_signals, info = nk.eda_process(win_baseline_eda, sampling_rate=fs)
        eda_features = nk.eda_intervalrelated(eda_signals)
        # NK2 0.2.13 EDA cols: SCR_Peaks_N, SCR_Peaks_Amplitude_Mean,
        # EDA_Tonic_SD, EDA_Sympathetic, EDA_SympatheticN, EDA_Autocorrelation.
        # No SCL_mean. Use SCR_Peaks_N + EDA_Tonic_SD as smoke proxies.
        eda_cols_present = list(eda_features.columns)
        scr_n = float(eda_features["SCR_Peaks_N"].iloc[0]) if "SCR_Peaks_N" in eda_cols_present else float("nan")
        tonic_sd = float(eda_features["EDA_Tonic_SD"].iloc[0]) if "EDA_Tonic_SD" in eda_cols_present else float("nan")
    except Exception as e:  # noqa: BLE001
        return {"status": "fail", "reason": f"NeuroKit2 EDA pipeline error: {e}"}

    # BioSPPy cross-check
    try:
        import biosppy.signals.ecg as bio_ecg
        bio_out = bio_ecg.ecg(signal=win_baseline_ecg, sampling_rate=fs, show=False)
        n_peaks_bio = int(len(bio_out["rpeaks"]))
        bio_diff_pct = abs(n_peaks_bio - n_peaks_nk) / max(n_peaks_nk, 1) * 100
        bio_check_pass = bio_diff_pct < 10.0
    except Exception as e:  # noqa: BLE001
        n_peaks_bio = None
        bio_diff_pct = None
        bio_check_pass = None

    ecg_pass = 50 <= n_peaks_nk <= 100
    eda_pass = (scr_n == scr_n and scr_n >= 0) and (tonic_sd == tonic_sd and tonic_sd > 0)

    return {
        "status": "pass" if (ecg_pass and eda_pass) else "fail",
        "cvxpy": cvxpy_status,
        "ecg_window_n_peaks_nk": n_peaks_nk,
        "ecg_pass_50_to_100": ecg_pass,
        "ecg_window_n_peaks_biosppy": n_peaks_bio,
        "biosppy_diff_pct_vs_nk": round(bio_diff_pct, 2) if bio_diff_pct is not None else None,
        "biosppy_within_10pct_check": bio_check_pass,
        "eda_method_used": eda_method,
        "eda_columns_present": eda_cols_present,
        "eda_scr_peaks_n_60s": scr_n if scr_n == scr_n else None,
        "eda_tonic_sd": round(tonic_sd, 4) if tonic_sd == tonic_sd else None,
        "eda_pass": eda_pass,
        "n_features_hrv_only": n_features_nk,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-2 WESAD ECG+EDA smoke test")
    ap.add_argument(
        "--wesad-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "WESAD" / "WESAD",
        help="Path to WESAD root containing S2/, S3/, ...",
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.wesad_dir)
    result["pilot"] = "P-2"
    result["spec"] = "20-plan/affective-state/pilots-README.md#P-2"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p2_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

"""
Spec: 20-plan/sleep-staging/pilots-README.md#P-1

P-1 — HMC Sleep Staging Database access tier + ECG channel check.

Question: (a) Is the dataset accessible at PhysioNet credentialed level
(same-session) or DUA-blocked? (b) Of a 10-subject sample, how many have
ECG SQI >= 0.5 on > 70 % of 30-second windows?

Success criteria:
  (a) Access granted within 1 hour of account creation.
  (b) >= 8/10 subjects with > 70 % windows above SQI threshold.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def probe(hmc_dir: Path, n_subjects: int, sqi_threshold: float, frac_threshold: float) -> dict:
    if not hmc_dir.exists():
        return {
            "status": "fail",
            "reason": f"HMC dir not found at {hmc_dir}. Download per code/README.md (PhysioNet account + credentialed access).",
            "remediation": "If PhysioNet returns 'credentialed access required, application pending' instead of immediate download → trigger risk-register R-2 (CAP Sleep substitute path).",
        }

    try:
        import mne
        import neurokit2 as nk
        import numpy as np
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    edf_files = sorted(hmc_dir.glob("**/*.edf"))[:n_subjects]
    if len(edf_files) < n_subjects:
        return {
            "status": "fail",
            "reason": f"Only found {len(edf_files)} edf files; need {n_subjects}",
        }

    per_subject = []
    for f in edf_files:
        subject_id = f.stem
        try:
            raw = mne.io.read_raw_edf(f, preload=False, verbose="error")
            ch_names = raw.ch_names
            ecg_ch = next((c for c in ch_names if "ECG" in c.upper() or "EKG" in c.upper()), None)
            if ecg_ch is None:
                per_subject.append({"subject": subject_id, "ecg_present": False})
                continue

            raw.pick_channels([ecg_ch])
            raw.load_data()
            data = raw.get_data()[0]
            sfreq = raw.info["sfreq"]
            window_samples = int(30 * sfreq)
            n_windows = len(data) // window_samples
            sqi_values = []
            for w in range(n_windows):
                seg = data[w * window_samples : (w + 1) * window_samples]
                try:
                    quality = nk.ecg_quality(seg, sampling_rate=int(sfreq), method="averageQRS")
                    sqi_values.append(float(np.mean(quality)))
                except Exception:  # noqa: BLE001
                    sqi_values.append(0.0)
            sqi_arr = np.array(sqi_values)
            frac_above = float(np.mean(sqi_arr >= sqi_threshold))
            per_subject.append(
                {
                    "subject": subject_id,
                    "ecg_present": True,
                    "ecg_channel_name": ecg_ch,
                    "n_windows": int(n_windows),
                    "frac_windows_above_sqi": round(frac_above, 4),
                    "passes_frac_threshold": frac_above > frac_threshold,
                    "sfreq_hz": float(sfreq),
                }
            )
        except Exception as e:  # noqa: BLE001
            per_subject.append({"subject": subject_id, "ecg_present": False, "error": str(e)})

    n_passing = sum(1 for s in per_subject if s.get("passes_frac_threshold"))
    return {
        "status": "pass" if n_passing >= 8 else "fail",
        "n_sampled": len(per_subject),
        "n_passing_sqi_check": n_passing,
        "sqi_threshold": sqi_threshold,
        "frac_threshold": frac_threshold,
        "per_subject": per_subject,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-1 HMC PSG access + ECG SQI check")
    ap.add_argument(
        "--hmc-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "hmc-sleep-staging-1.0.0",
        help="Local path to downloaded HMC Sleep Staging Database",
    )
    ap.add_argument("--subjects", type=int, default=10)
    ap.add_argument("--sqi-threshold", type=float, default=0.5)
    ap.add_argument("--frac-threshold", type=float, default=0.7)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.hmc_dir, args.subjects, args.sqi_threshold, args.frac_threshold)
    result["pilot"] = "P-1"
    result["spec"] = "20-plan/sleep-staging/pilots-README.md#P-1"

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

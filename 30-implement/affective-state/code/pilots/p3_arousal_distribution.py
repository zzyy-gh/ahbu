"""
Spec: 20-plan/affective-state/pilots-README.md#P-3

P-3 — Arousal label distribution check (WESAD; DEAP only if accessible).

WESAD criteria:
  >= 10 stress windows and >= 10 baseline windows per subject (60s @ 700 Hz).
DEAP criteria:
  per-subject arousal std > 1.0 for at least 25 of 32 subjects.
Median-split criterion:
  tie rate < 10 % per subject.
"""

import argparse
import json
import pickle
import sys
import time
from pathlib import Path


def probe_wesad(wesad_dir: Path, fs: int, window_sec: int) -> dict:
    try:
        import numpy as np
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    if not wesad_dir.exists():
        return {"status": "fail", "reason": f"WESAD dir not found at {wesad_dir}"}

    subjects = sorted([d.name for d in wesad_dir.iterdir() if d.is_dir() and d.name.startswith("S")])
    win_samples = fs * window_sec

    per_subject = []
    for subj in subjects:
        pkl_path = wesad_dir / subj / f"{subj}.pkl"
        if not pkl_path.exists():
            per_subject.append({"subject": subj, "ok": False, "reason": "missing pkl"})
            continue
        with open(pkl_path, "rb") as f:
            data = pickle.load(f, encoding="latin1")
        labels = np.asarray(data["label"])
        baseline_idx = np.where(labels == 1)[0]
        stress_idx = np.where(labels == 2)[0]
        n_baseline_win = len(baseline_idx) // win_samples
        n_stress_win = len(stress_idx) // win_samples
        per_subject.append(
            {
                "subject": subj,
                "n_baseline_windows": int(n_baseline_win),
                "n_stress_windows": int(n_stress_win),
                "ok": (n_baseline_win >= 10) and (n_stress_win >= 10),
            }
        )

    n_passing = sum(1 for s in per_subject if s.get("ok"))
    return {
        "n_subjects": len(per_subject),
        "n_passing_window_threshold": n_passing,
        "per_subject": per_subject,
        "all_subjects_pass": n_passing == len(per_subject),
    }


def probe_deap(deap_dir: Path) -> dict:
    if not deap_dir.exists():
        return {"status": "skipped", "reason": f"DEAP dir not found at {deap_dir} (likely not yet authorized)"}

    try:
        import numpy as np
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    pkl_files = sorted(deap_dir.glob("*.dat"))
    if not pkl_files:
        return {"status": "fail", "reason": f"no .dat files in {deap_dir}"}

    per_subject = []
    for f in pkl_files[:32]:
        try:
            with open(f, "rb") as fh:
                data = pickle.load(fh, encoding="latin1")
            arousal = np.asarray(data["labels"])[:, 1]
            median = float(np.median(arousal))
            tie_count = int(np.sum(arousal == median))
            per_subject.append(
                {
                    "subject": f.stem,
                    "n_clips": int(len(arousal)),
                    "arousal_mean": round(float(arousal.mean()), 3),
                    "arousal_std": round(float(arousal.std()), 3),
                    "median": median,
                    "tie_count": tie_count,
                    "tie_rate": round(tie_count / len(arousal), 4),
                    "high_fraction": round(float((arousal > median).mean()), 3),
                }
            )
        except Exception as e:  # noqa: BLE001
            per_subject.append({"subject": f.stem, "error": str(e)})

    n_high_std = sum(1 for s in per_subject if s.get("arousal_std", 0) > 1.0)
    n_low_tie = sum(1 for s in per_subject if s.get("tie_rate", 1.0) < 0.10)
    return {
        "n_subjects": len(per_subject),
        "n_with_arousal_std_above_1": n_high_std,
        "n_with_tie_rate_below_10pct": n_low_tie,
        "per_subject": per_subject,
    }


def probe(wesad_dir: Path, deap_dir: Path) -> dict:
    wesad = probe_wesad(wesad_dir, fs=700, window_sec=60)
    deap = probe_deap(deap_dir)

    wesad_pass = wesad.get("all_subjects_pass", False)
    deap_pass = (
        deap.get("status") == "skipped"
        or deap.get("n_with_arousal_std_above_1", 0) >= 25
    )
    return {
        "status": "pass" if (wesad_pass and deap_pass) else "fail",
        "wesad": wesad,
        "deap": deap,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-3 arousal label distribution")
    ap.add_argument(
        "--wesad-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "WESAD" / "WESAD",
    )
    ap.add_argument(
        "--deap-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "DEAP" / "data_preprocessed_python",
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.wesad_dir, args.deap_dir)
    result["pilot"] = "P-3"
    result["spec"] = "20-plan/affective-state/pilots-README.md#P-3"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p3_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

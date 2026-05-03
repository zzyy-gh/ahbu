"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-1

P-1 — CinC 2017 download + class count verification.

CRITICAL gating pilot. Verifies:
  (a) PhysioNet/CinC 2017 v1.0.0 is downloadable + loadable
      under its ODC-BY licence.
  (b) Total record count == 8,528 (per CinC 2017 spec).
  (c) AF (`A`) record count >= 700 (expected ~771; >= 700 leaves
      comfortable margin for the 20 % test stratum to clear ~140 AF
      records, well above the protocol-lock §3 expected ~154 AF
      positive).
  (d) 10 sample WFDB records load without error at 300 Hz, single lead.

If (b) or (c) fails, R-1 triggers — methodology must redesign or
retire-cancel.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path


def probe(cinc_dir: Path, target_total: int, min_af_count: int, n_sample_reads: int) -> dict:
    if not cinc_dir.exists():
        return {
            "status": "fail",
            "reason": f"CinC 2017 dir not found at {cinc_dir}. Download per code/README.md.",
        }

    license_path = cinc_dir / "LICENSE.txt"
    license_present = license_path.exists()
    license_text = license_path.read_text(errors="ignore")[:500] if license_present else None
    odcby = license_present and "ODC-BY" in license_text.upper()

    reference_csv = None
    for cand in ("REFERENCE-v3.csv", "REFERENCE.csv", "training2017/REFERENCE-v3.csv", "training2017/REFERENCE.csv"):
        p = cinc_dir / cand
        if p.exists():
            reference_csv = p
            break
    if reference_csv is None:
        return {
            "status": "fail",
            "reason": f"REFERENCE(-v3).csv not found anywhere under {cinc_dir}",
        }

    try:
        import pandas as pd
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    df = pd.read_csv(reference_csv, header=None, names=["record_id", "label"])
    n_total = len(df)
    counts = Counter(df["label"].tolist())
    n_af = int(counts.get("A", 0))
    n_normal = int(counts.get("N", 0))
    n_other = int(counts.get("O", 0))
    n_noisy = int(counts.get("~", 0))

    waveform_dir = reference_csv.parent
    sample_reads: list[dict] = []
    parse_errors = 0
    try:
        import wfdb
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    for record_id in df["record_id"].head(n_sample_reads).tolist():
        rec_path = waveform_dir / record_id
        try:
            r = wfdb.rdrecord(str(rec_path))
            sample_reads.append(
                {
                    "record_id": record_id,
                    "fs_hz": float(r.fs),
                    "n_sig": int(r.n_sig),
                    "sig_len": int(r.sig_len),
                    "ok": True,
                }
            )
        except Exception as e:  # noqa: BLE001
            sample_reads.append({"record_id": record_id, "ok": False, "error": str(e)})
            parse_errors += 1

    fs_ok = all(s.get("fs_hz") == 300.0 for s in sample_reads if s.get("ok"))
    nsig_ok = all(s.get("n_sig") == 1 for s in sample_reads if s.get("ok"))

    total_ok = n_total == target_total
    af_ok = n_af >= min_af_count
    sample_ok = parse_errors == 0 and fs_ok and nsig_ok

    status = "pass" if (total_ok and af_ok and sample_ok and odcby) else "fail"

    return {
        "status": status,
        "cinc_dir": str(cinc_dir),
        "license_present": license_present,
        "license_odcby_confirmed": odcby,
        "reference_csv": str(reference_csv.relative_to(cinc_dir)) if reference_csv else None,
        "n_total": n_total,
        "n_total_target": target_total,
        "n_total_ok": total_ok,
        "per_class": {"N": n_normal, "A": n_af, "O": n_other, "~": n_noisy},
        "n_af": n_af,
        "n_af_min": min_af_count,
        "af_ok": af_ok,
        "n_sample_reads": n_sample_reads,
        "sample_read_results": sample_reads,
        "parse_errors": parse_errors,
        "fs_300hz_uniform": fs_ok,
        "single_lead_uniform": nsig_ok,
        "sample_read_ok": sample_ok,
        "first_ten_record_ids": df["record_id"].head(10).tolist(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-1 CinC 2017 download + class count verification")
    ap.add_argument(
        "--cinc-dir",
        type=Path,
        default=Path.home() / "physionet_data" / "challenge-2017-1.0.0",
        help="Local path to downloaded CinC 2017 v1.0.0 (PhysioNet content dir)",
    )
    ap.add_argument("--target-total", type=int, default=8528)
    ap.add_argument("--min-af-count", type=int, default=700)
    ap.add_argument("--n-sample-reads", type=int, default=10)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.cinc_dir, args.target_total, args.min_af_count, args.n_sample_reads)
    result["pilot"] = "P-1"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-1"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p1_cinc2017_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

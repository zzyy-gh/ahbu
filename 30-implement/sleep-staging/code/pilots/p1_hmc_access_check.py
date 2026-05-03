"""
Spec: 20-plan/sleep-staging/pilots-README.md#P-1

P-1 — HMC Sleep Staging Database access tier + ECG channel check
       + AHI metadata audit (per critic-v2 M-2).

Question: (a) Is the dataset accessible at PhysioNet credentialed level
(same-session) or DUA-blocked? (b) Of a 10-subject sample, how many have
ECG SQI >= 0.5 on > 70 % of 30-second windows? (c) Is AHI metadata
present per subject (and if not, are sex + age available as the §3
fallback stratification variables)?

Success criteria:
  (a) Access granted within 1 hour of account creation.
  (b) >= 8/10 subjects with > 70 % windows above SQI threshold.
  (c) Metadata audit (NON-BLOCKING per critic-v2 M-2): record AHI
      presence and, if present, AHI distribution across the sample.
      Sex and age fields recorded for the §3 fallback stratification
      path. The audit informs the §3 conditional but does not gate
      P-1 PASS — pass/fail logic remains driven by (a) + (b) only.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path


_AHI_KEYS = (
    "ahi",
    "apnea_hypopnea_index",
    "apnea-hypopnea index",
    "respiratory event index",
    "rei",
    "rdi",  # respiratory disturbance index — accept as AHI-equivalent surrogate
)
_SEX_KEYS = ("sex", "gender")
_AGE_KEYS = ("age", "age_at_recording", "age_yr")


def _parse_float(value: str) -> float | None:
    """Extract the first float from a string; return None if no number found."""
    if value is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if m is None:
        return None
    try:
        return float(m.group(0))
    except (TypeError, ValueError):
        return None


def _audit_metadata_for_edf(edf_path: Path, raw) -> dict:
    """Look for AHI / sex / age in EDF header + accompanying metadata files.

    Strategy:
      1. Inspect the MNE Raw header (subject_info, recording, meas_date).
      2. Scan for sibling files matching the subject ID stem (e.g. *.txt,
         *.tsv, *.csv, *.xml, *_metadata.*). Parse key=value-style entries
         and CSV/TSV rows for the AHI / sex / age keys.

    Records every probed location so the audit JSON can show why a value
    was or was not found. Returns dict with keys: ahi, sex, age,
    sources_probed, hits.
    """
    result: dict = {
        "ahi": None,
        "sex": None,
        "age": None,
        "sources_probed": [],
        "hits": [],
    }

    # --- 1. EDF header via MNE -------------------------------------------------
    result["sources_probed"].append(f"mne_header:{edf_path.name}")
    try:
        info = raw.info
        subject_info = dict(info.get("subject_info") or {}) if info else {}
        if subject_info:
            # MNE subject_info keys: 'his_id','last_name','first_name','birthday','sex','hand'
            sex_code = subject_info.get("sex")
            if sex_code is not None:
                # MNE encodes: 0=unknown, 1=male, 2=female
                if sex_code == 1:
                    result["sex"] = "M"
                elif sex_code == 2:
                    result["sex"] = "F"
                if result["sex"] is not None:
                    result["hits"].append({"field": "sex", "source": "mne_header"})
            birthday = subject_info.get("birthday")
            meas_date = info.get("meas_date")
            if birthday and meas_date:
                try:
                    age_yr = (meas_date.year - birthday[0]) - (
                        (meas_date.month, meas_date.day) < (birthday[1], birthday[2])
                    )
                    result["age"] = float(age_yr)
                    result["hits"].append({"field": "age", "source": "mne_header"})
                except Exception:  # noqa: BLE001
                    pass
    except Exception as e:  # noqa: BLE001
        result["sources_probed"].append(f"mne_header_error:{e}")

    # --- 2. sibling metadata files --------------------------------------------
    stem = edf_path.stem
    sibling_patterns = (
        f"{stem}.txt",
        f"{stem}.tsv",
        f"{stem}.csv",
        f"{stem}.xml",
        f"{stem}.json",
        f"{stem}_metadata.*",
        f"{stem}-metadata.*",
        # dataset-level summary files
        "subject-info.csv",
        "subjects.csv",
        "subject_info.tsv",
        "metadata.csv",
        "RECORDS",
    )
    candidate_files: list[Path] = []
    parent = edf_path.parent
    for pat in sibling_patterns:
        candidate_files.extend(parent.glob(pat))
        # also look one level up (dataset root) for summary files
        candidate_files.extend(parent.parent.glob(pat))

    seen_paths: set[Path] = set()
    for f in candidate_files:
        if f in seen_paths or not f.is_file():
            continue
        seen_paths.add(f)
        result["sources_probed"].append(f"file:{f.name}")
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except Exception as e:  # noqa: BLE001
            result["sources_probed"].append(f"read_error:{f.name}:{e}")
            continue
        text_lower = text.lower()

        # CSV/TSV row search — try to find a row keyed by the subject stem
        for line in text.splitlines():
            if stem.lower() in line.lower():
                # split on common delimiters
                for delim in (",", "\t", ";", "|"):
                    if delim in line:
                        parts = [p.strip() for p in line.split(delim)]
                        # heuristic: scan for AHI-shaped numbers
                        # (we cannot infer column meaning without a header,
                        # so rely on key=value scanning below as primary path)
                        _ = parts
                        break

        # key=value / "key: value" scanning
        for key_set, out_field, parser in (
            (_AHI_KEYS, "ahi", _parse_float),
            (_AGE_KEYS, "age", _parse_float),
            (_SEX_KEYS, "sex", lambda v: v.strip()[:1].upper() if v and v.strip() else None),
        ):
            if result[out_field] is not None:
                continue
            for key in key_set:
                # match "key : value" or "key = value" or "key,value" with the key as a word
                pat = re.compile(
                    rf"\b{re.escape(key)}\b[\s]*[:=,\t]\s*([^\r\n,;|]+)",
                    re.IGNORECASE,
                )
                m = pat.search(text_lower)
                if m is None:
                    continue
                # re-extract from original-cased text at the same span for sex
                raw_match = pat.search(text)
                value_str = raw_match.group(1).strip() if raw_match else m.group(1).strip()
                parsed = parser(value_str)
                if parsed is not None and parsed != "":
                    if out_field == "sex" and parsed not in ("M", "F"):
                        # accept "Male"/"Female" too
                        if value_str.lower().startswith("m"):
                            parsed = "M"
                        elif value_str.lower().startswith("f"):
                            parsed = "F"
                        else:
                            continue
                    result[out_field] = parsed
                    result["hits"].append(
                        {"field": out_field, "source": f.name, "key_matched": key}
                    )
                    break

    return result


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
    metadata_audit_per_subject = []
    for f in edf_files:
        subject_id = f.stem
        ahi_val = None
        sex_val = None
        age_val = None
        audit_record: dict = {
            "subject": subject_id,
            "edf_path": str(f),
            "ahi": None,
            "sex": None,
            "age": None,
            "sources_probed": [],
            "hits": [],
        }
        try:
            raw = mne.io.read_raw_edf(f, preload=False, verbose="error")
            # Metadata audit (per critic-v2 M-2). Non-blocking: failures
            # here are recorded but do not change pass/fail.
            try:
                audit = _audit_metadata_for_edf(f, raw)
                ahi_val = audit["ahi"]
                sex_val = audit["sex"]
                age_val = audit["age"]
                audit_record.update(
                    {
                        "ahi": ahi_val,
                        "sex": sex_val,
                        "age": age_val,
                        "sources_probed": audit["sources_probed"],
                        "hits": audit["hits"],
                    }
                )
            except Exception as e:  # noqa: BLE001
                audit_record["audit_error"] = str(e)
            metadata_audit_per_subject.append(audit_record)

            ch_names = raw.ch_names
            ecg_ch = next((c for c in ch_names if "ECG" in c.upper() or "EKG" in c.upper()), None)
            if ecg_ch is None:
                per_subject.append(
                    {
                        "subject": subject_id,
                        "ecg_present": False,
                        "ahi": ahi_val,
                        "sex": sex_val,
                        "age": age_val,
                    }
                )
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
                    "ahi": ahi_val,
                    "sex": sex_val,
                    "age": age_val,
                }
            )
        except Exception as e:  # noqa: BLE001
            per_subject.append(
                {
                    "subject": subject_id,
                    "ecg_present": False,
                    "error": str(e),
                    "ahi": ahi_val,
                    "sex": sex_val,
                    "age": age_val,
                }
            )
            if not any(r["subject"] == subject_id for r in metadata_audit_per_subject):
                metadata_audit_per_subject.append(audit_record)

    n_passing = sum(1 for s in per_subject if s.get("passes_frac_threshold"))

    # --- AHI metadata audit summary (per critic-v2 M-2; non-blocking) -----
    ahi_values = [s["ahi"] for s in per_subject if s.get("ahi") is not None]
    sex_present = sum(1 for s in per_subject if s.get("sex") in ("M", "F"))
    age_present = sum(1 for s in per_subject if s.get("age") is not None)

    def _band(ahi: float) -> str:
        if ahi < 5:
            return "none"
        if ahi < 15:
            return "mild"
        if ahi < 30:
            return "moderate"
        return "severe"

    ahi_distribution: dict[str, int] = {"none": 0, "mild": 0, "moderate": 0, "severe": 0}
    for v in ahi_values:
        ahi_distribution[_band(v)] += 1

    return {
        "status": "pass" if n_passing >= 8 else "fail",
        "n_sampled": len(per_subject),
        "n_passing_sqi_check": n_passing,
        "sqi_threshold": sqi_threshold,
        "frac_threshold": frac_threshold,
        "per_subject": per_subject,
        # AHI metadata audit (added 2026-05-03, critic-v2 M-2).
        # Non-blocking: gating remains the SQI criterion above.
        "ahi_metadata_present_count": len(ahi_values),
        "sex_metadata_present_count": sex_present,
        "age_metadata_present_count": age_present,
        "ahi_distribution": ahi_distribution if ahi_values else None,
        "metadata_audit_note": (
            "AHI presence informs protocol-lock.md §3 conditional "
            "(AHI vs sex+age-decade stratification). Fields recorded "
            "for the §3 fallback path. Audit is non-blocking."
        ),
        "metadata_audit_per_subject": metadata_audit_per_subject,
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

    runs_dir = Path(__file__).resolve().parents[2] / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out or (runs_dir / f"pilot_p1_hmc_access_{int(time.time())}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    # Per critic-v2 M-2: standalone metadata-audit artifact (in addition
    # to the embedded audit in the main result JSON above).
    audit_path = runs_dir / "hmc_metadata_audit.json"
    audit_payload = {
        "pilot": "P-1",
        "spec": "20-plan/sleep-staging/pilots-README.md#P-1",
        "note": (
            "AHI / sex / age metadata audit. Informs protocol-lock.md §3 "
            "stratification conditional. Non-blocking."
        ),
        "n_sampled": result.get("n_sampled"),
        "ahi_metadata_present_count": result.get("ahi_metadata_present_count"),
        "sex_metadata_present_count": result.get("sex_metadata_present_count"),
        "age_metadata_present_count": result.get("age_metadata_present_count"),
        "ahi_distribution": result.get("ahi_distribution"),
        "per_subject": result.get("metadata_audit_per_subject", []),
    }
    audit_path.write_text(json.dumps(audit_payload, indent=2))

    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    print(f"Wrote {audit_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

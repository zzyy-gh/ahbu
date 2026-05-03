"""Helper: download first 10 subjects of HMC PSG (CC-BY 4.0).

Not part of pilot spec — just a fetcher for P-1 setup.

Skip rule: file already complete (size matches server Content-Length)
=> skip. File missing OR partial (size < server Content-Length) =>
re-download. This handles the case where a previous run died mid-EDF.
"""
import sys
import time
from pathlib import Path
import urllib.request

BASE = "https://physionet.org/files/hmc-sleep-staging/1.0.0/"
TARGET = Path.home() / "physionet_data" / "hmc-sleep-staging-1.0.0"


def remote_size(url: str) -> int | None:
    """HEAD request returning Content-Length, or None on failure."""
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=30) as r:
            cl = r.headers.get("Content-Length")
            return int(cl) if cl else None
    except Exception as e:  # noqa: BLE001
        print(f"  HEAD failed for {url}: {e}")
        return None


def fetch(rel_url: str, dest: Path) -> None:
    url = BASE + rel_url
    expected = remote_size(url)
    if dest.exists():
        local = dest.stat().st_size
        if expected is not None and local == expected:
            print(f"skip (complete): {dest.name} ({local/1e6:.1f} MB)")
            return
        if expected is not None and local < expected:
            print(
                f"  re-download (partial {local/1e6:.1f} MB / {expected/1e6:.1f} MB): {dest.name}"
            )
            # urlretrieve overwrites dest atomically; no unlink needed
        elif expected is None and local > 0:
            print(f"skip (HEAD unknown, exists non-empty): {dest.name} ({local/1e6:.1f} MB)")
            return
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"GET {rel_url}")
    t0 = time.time()
    urllib.request.urlretrieve(url, dest)
    sz = dest.stat().st_size
    print(f"  -> {dest} ({sz/1e6:.1f} MB in {time.time()-t0:.1f}s)")


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    # dataset-level metadata
    fetch("RECORDS", TARGET / "RECORDS")
    fetch("subjects_info_aggregated.txt", TARGET / "subjects_info_aggregated.txt")
    fetch("LICENSE.txt", TARGET / "LICENSE.txt")
    fetch("HMCdatabase_quickcheck.xml", TARGET / "HMCdatabase_quickcheck.xml")
    # per-subject EDFs (PSG only — sleepscoring not needed for P-1 ECG SQI check)
    for i in range(1, n + 1):
        sid = f"SN{i:03d}"
        fetch(f"recordings/{sid}.edf", TARGET / "recordings" / f"{sid}.edf")
    print("done")
    return 0


if __name__ == "__main__":
    sys.exit(main())

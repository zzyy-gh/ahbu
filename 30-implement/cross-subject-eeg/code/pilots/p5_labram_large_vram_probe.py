"""
Spec: 20-plan/cross-subject-eeg/pilots-README.md#P-5
P-5 — LaBraM-Large VRAM probe (optional).

Question: does LaBraM-Large fit on GTX 1650 at float16?

Spec: 20-plan/cross-subject-eeg/pilots-README.md §P-5.

Success criterion: peak VRAM <= 3.5 GB at float16.
Skip if Large checkpoint not available.
"""

import argparse
import json
import sys
import time
from pathlib import Path

import torch


def probe(checkpoint_path: Path, n_channels: int, n_samples: int) -> dict:
    if not checkpoint_path.exists():
        return {
            "status": "skipped",
            "reason": f"LaBraM-Large checkpoint not at {checkpoint_path} — pilot is optional.",
        }
    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "CUDA not available"}

    try:
        from labram import LaBraMLarge  # type: ignore
    except ImportError:
        return {
            "status": "skipped",
            "reason": "labram.LaBraMLarge not importable — pilot is optional.",
        }

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    device = torch.device("cuda")

    state = torch.load(checkpoint_path, map_location=device)
    model = LaBraMLarge()
    model.load_state_dict(state, strict=False)
    model.to(device=device, dtype=torch.float16)
    model.eval()

    x = torch.randn(1, n_channels, n_samples, device=device, dtype=torch.float16)
    with torch.no_grad():
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        out = model(x)
        torch.cuda.synchronize()
        t_forward = time.perf_counter() - t0

    peak_gb = torch.cuda.max_memory_allocated() / 1e9
    threshold_gb = 3.5
    return {
        "status": "pass" if peak_gb <= threshold_gb else "fail",
        "device": torch.cuda.get_device_name(),
        "dtype": "float16",
        "peak_vram_gb": round(peak_gb, 3),
        "threshold_gb": threshold_gb,
        "forward_time_s": round(t_forward, 4),
        "output_shape": list(out.shape) if hasattr(out, "shape") else None,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-5 LaBraM-Large VRAM probe")
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--channels", type=int, default=22)
    ap.add_argument("--samples", type=int, default=200)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.checkpoint, args.channels, args.samples)
    result["pilot"] = "P-5"
    result["spec"] = "20-plan/cross-subject-eeg/pilots-README.md#P-5"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p5_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") in ("pass", "skipped") else 1


if __name__ == "__main__":
    sys.exit(main())

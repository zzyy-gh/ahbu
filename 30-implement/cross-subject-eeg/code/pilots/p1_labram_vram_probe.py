"""
P-1 — LaBraM-Base VRAM probe.

Question: how much VRAM does a single LaBraM-Base forward pass consume on
GTX 1650 at batch=1?

Spec: 20-plan/cross-subject-eeg/pilots-README.md §P-1.

Success criterion (per pilots-README + risk-register R-3):
  peak_vram <= 3 GB at float32  OR  peak_vram <= 2.5 GB at float16
"""

import argparse
import json
import sys
import time
from pathlib import Path

import torch


def probe(checkpoint_path: Path, dtype: str, n_channels: int, n_samples: int) -> dict:
    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "CUDA not available", "device": "cpu"}

    if not checkpoint_path.exists():
        return {
            "status": "fail",
            "reason": f"Checkpoint not found at {checkpoint_path}. See code/README.md for download steps.",
        }

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    torch_dtype = {"float32": torch.float32, "float16": torch.float16}[dtype]
    device = torch.device("cuda")

    state = torch.load(checkpoint_path, map_location=device)
    state_keys = list(state.keys())[:5] if isinstance(state, dict) else []

    try:
        from labram import LaBraMBase  # type: ignore
    except ImportError:
        return {
            "status": "fail",
            "reason": "labram package not importable. Clone https://github.com/935963004/LaBraM into external/LaBraM and add it to PYTHONPATH.",
            "checkpoint_keys_sample": state_keys,
        }

    model = LaBraMBase()
    model.load_state_dict(state, strict=False)
    model.to(device=device, dtype=torch_dtype)
    model.eval()

    x = torch.randn(1, n_channels, n_samples, device=device, dtype=torch_dtype)

    with torch.no_grad():
        torch.cuda.synchronize()
        t0 = time.perf_counter()
        out = model(x)
        torch.cuda.synchronize()
        t_forward = time.perf_counter() - t0

    peak_gb = torch.cuda.max_memory_allocated() / 1e9
    out_shape = tuple(out.shape) if hasattr(out, "shape") else None

    threshold_gb = 3.0 if dtype == "float32" else 2.5
    passed = peak_gb <= threshold_gb

    return {
        "status": "pass" if passed else "fail",
        "device": torch.cuda.get_device_name(),
        "dtype": dtype,
        "input_shape": [1, n_channels, n_samples],
        "output_shape": list(out_shape) if out_shape else None,
        "peak_vram_gb": round(peak_gb, 3),
        "threshold_gb": threshold_gb,
        "forward_time_s": round(t_forward, 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-1 LaBraM-Base VRAM probe")
    ap.add_argument("--checkpoint", type=Path, required=True, help="Path to LaBraM-Base .pth")
    ap.add_argument("--dtype", choices=["float32", "float16"], default="float32")
    ap.add_argument("--channels", type=int, default=22, help="Channel count (BNCI2014_001 = 22)")
    ap.add_argument("--samples", type=int, default=200, help="Sample count per epoch (1s @ 200Hz)")
    ap.add_argument("--out", type=Path, default=None, help="Output JSON path")
    args = ap.parse_args()

    result = probe(args.checkpoint, args.dtype, args.channels, args.samples)
    result["pilot"] = "P-1"
    result["spec"] = "20-plan/cross-subject-eeg/pilots-README.md#P-1"

    out_path = args.out or (
        Path(__file__).resolve().parents[2]
        / "runs"
        / f"pilot_p1_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))

    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

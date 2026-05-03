"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-3

P-3 — xresnet1d50 VRAM probe at CinC 2017 input shape.

CRITICAL gating pilot per critic-v2 M-1 fix in approach.md.
Re-probes xresnet1d50 at the actual CinC 2017 headline input shape
(batch=8, seq_len=9000, 1 channel) — the prior P-3 in
cross-subject-eeg ran at (batch=32, seq_len=1000) with 0.62 GB peak,
which is not directly applicable to the 9× longer sequence here.

Success criterion (per protocol-lock §4 kill threshold):
  - Peak VRAM <= 3.0 GB at float32, batch=8 OR <= 2.5 GB at float16,
    batch=8.
  - Above 3.2 GB at both float32 AND float16 → triggers protocol-lock
    R-2 model-substitution path (xresnet1d50 → xresnet1d18).
  - Loss(end) < loss(start) on a 500-record sanity training run
    (skipped if --vram-only is set; training is dev-data dependent).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from pathlib import Path


def build_xresnet1d50(in_channels: int = 1, n_out: int = 4):
    """Construct xresnet1d50 single-lead head from fastai's XResNet primitive.

    fastai 2.x exposes 2D xresnet50 directly but not a top-level
    xresnet1d50. Per the prior PTB-XL pilot pattern (deleted in
    commit 5db216f), the 1D variant is constructed from XResNet +
    ResBlock with ndim=1 + ResNet-50 layer pattern [3,4,6,3] +
    expansion=4 + kernel size 5.
    """
    from fastai.vision.models.xresnet import XResNet, ResBlock

    model = XResNet(
        ResBlock,
        expansion=4,
        layers=[3, 4, 6, 3],
        c_in=in_channels,
        n_out=n_out,
        ndim=1,
        ks=5,
    )
    return model


def probe_at(model, batch: int, seq_len: int, in_channels: int, mixed_precision: bool, device: str) -> dict:
    import torch
    from torch import nn

    model = model.to(device)
    model.train()
    opt = torch.optim.SGD(model.parameters(), lr=0.01)
    loss_fn = nn.CrossEntropyLoss()

    torch.cuda.reset_peak_memory_stats(device)

    x = torch.randn(batch, in_channels, seq_len, device=device)
    y = torch.randint(0, 4, (batch,), device=device)

    started = time.perf_counter()
    try:
        if mixed_precision:
            scaler = torch.amp.GradScaler("cuda")
            with torch.amp.autocast("cuda"):
                logits = model(x)
                loss = loss_fn(logits, y)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
        else:
            logits = model(x)
            loss = loss_fn(logits, y)
            loss.backward()
            opt.step()
        opt.zero_grad()
        torch.cuda.synchronize(device)
        elapsed = time.perf_counter() - started
        peak = float(torch.cuda.max_memory_allocated(device) / 1e9)
        return {
            "ok": True,
            "batch": batch,
            "seq_len": seq_len,
            "in_channels": in_channels,
            "mixed_precision": mixed_precision,
            "peak_vram_gb": round(peak, 3),
            "step_time_s": round(elapsed, 4),
            "loss": round(float(loss.item()), 4),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "ok": False,
            "batch": batch,
            "seq_len": seq_len,
            "mixed_precision": mixed_precision,
            "error": str(e),
            "traceback": traceback.format_exc(),
        }


def probe(batch_primary: int, seq_len: int, in_channels: int, n_classes: int) -> dict:
    try:
        import torch
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    if not torch.cuda.is_available():
        return {
            "status": "fail",
            "reason": "torch.cuda.is_available() is False — no GPU detected. P-3 requires GTX 1650 (or equivalent) for the VRAM probe.",
        }

    device = "cuda:0"
    device_name = torch.cuda.get_device_name(device)
    total_vram_gb = float(torch.cuda.get_device_properties(device).total_memory / 1e9)

    try:
        model = build_xresnet1d50(in_channels=in_channels, n_out=n_classes)
    except Exception as e:  # noqa: BLE001
        return {"status": "fail", "reason": f"could not build xresnet1d50: {e}", "traceback": traceback.format_exc()}

    n_params_m = round(sum(p.numel() for p in model.parameters()) / 1e6, 2)

    results = []
    for batch in (batch_primary, 16):
        for mixed in (False, True):
            r = probe_at(model, batch, seq_len, in_channels, mixed, device)
            results.append(r)
            try:
                import torch
                torch.cuda.empty_cache()
            except Exception:  # noqa: BLE001
                pass

    primary_fp32 = next((r for r in results if r["batch"] == batch_primary and not r["mixed_precision"]), None)
    primary_fp16 = next((r for r in results if r["batch"] == batch_primary and r["mixed_precision"]), None)

    fp32_pass = primary_fp32 is not None and primary_fp32.get("ok") and primary_fp32.get("peak_vram_gb", 99) <= 3.0
    fp16_pass = primary_fp16 is not None and primary_fp16.get("ok") and primary_fp16.get("peak_vram_gb", 99) <= 2.5
    fp32_kill = primary_fp32 is not None and primary_fp32.get("ok") and primary_fp32.get("peak_vram_gb", 99) > 3.2
    fp16_kill = primary_fp16 is not None and primary_fp16.get("ok") and primary_fp16.get("peak_vram_gb", 99) > 3.2

    status = "pass" if (fp32_pass or fp16_pass) else ("kill_substitute_to_xresnet1d18" if (fp32_kill and fp16_kill) else "fail")

    return {
        "status": status,
        "device": device_name,
        "total_vram_gb": round(total_vram_gb, 2),
        "n_params_M": n_params_m,
        "input_shape": [batch_primary, in_channels, seq_len],
        "fp32_threshold_gb": 3.0,
        "fp16_threshold_gb": 2.5,
        "kill_threshold_gb": 3.2,
        "fp32_pass": fp32_pass,
        "fp16_pass": fp16_pass,
        "fp32_kill": fp32_kill,
        "fp16_kill": fp16_kill,
        "per_run": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-3 xresnet1d50 VRAM probe at CinC 2017 input shape")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--seq-len", type=int, default=9000)
    ap.add_argument("--in-channels", type=int, default=1)
    ap.add_argument("--n-classes", type=int, default=4)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.batch, args.seq_len, args.in_channels, args.n_classes)
    result["pilot"] = "P-3"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-3"

    out_path = args.out or (
        Path(__file__).resolve().parents[2] / "runs" / f"pilot_p3_xresnet_vram_{int(time.time())}.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

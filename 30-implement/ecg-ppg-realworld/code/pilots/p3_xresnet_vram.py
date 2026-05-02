"""
Spec: 20-plan/ecg-ppg-realworld/pilots-README.md#P-3

P-3 — xresnet1d50 VRAM probe + one-epoch convergence check.

CRITICAL gating pilot. Verifies:
  (a) xresnet1d50 (ndim=1, c_in=12, n_out=2) fits in GTX 1650 4 GB VRAM
      at typical PTB-XL training batch (32) for one forward + backward pass.
  (b) Optimizer step does not OOM.

Per protocol-lock §2 model: xresnet1d50 from fastai (XResNet with ndim=1,
ks=5, c_in=12, n_out=2). Per protocol-lock §6 statistical test, output is
2-class (AFIB vs not).

Success criterion: peak VRAM <= 3 GB at fp32 batch=32 forward+backward.
If 3 GB < peak <= 4 GB: switch to fp16 mixed precision and retest.
"""

import argparse
import json
import sys
import time
from pathlib import Path


def probe(batch: int, seq_len: int, mixed_precision: bool) -> dict:
    try:
        import torch
        from fastai.vision.models.xresnet import XResNet, ResBlock
    except ImportError as e:
        return {"status": "fail", "reason": f"missing dep: {e}"}

    if not torch.cuda.is_available():
        return {"status": "fail", "reason": "CUDA not available"}

    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    device = torch.device("cuda")

    model = XResNet(ResBlock, expansion=4, layers=[3, 4, 6, 3], c_in=12, n_out=2, ndim=1, ks=5)
    n_params = sum(p.numel() for p in model.parameters())
    model = model.to(device)
    model.train()

    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = torch.nn.CrossEntropyLoss()

    x = torch.randn(batch, 12, seq_len, device=device)
    y = torch.randint(0, 2, (batch,), device=device)

    autocast_ctx = torch.autocast("cuda", dtype=torch.float16) if mixed_precision else _NullCtx()
    scaler = torch.amp.GradScaler("cuda") if mixed_precision else None

    torch.cuda.synchronize()
    t0 = time.perf_counter()

    optimizer.zero_grad()
    with autocast_ctx:
        out = model(x)
        loss = criterion(out, y)

    if mixed_precision:
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
    else:
        loss.backward()
        optimizer.step()

    torch.cuda.synchronize()
    t_step = time.perf_counter() - t0

    peak_gb = torch.cuda.max_memory_allocated() / 1e9
    threshold_gb = 3.0
    return {
        "status": "pass" if peak_gb <= threshold_gb else "fail",
        "device": torch.cuda.get_device_name(),
        "mixed_precision": mixed_precision,
        "batch": batch,
        "seq_len": seq_len,
        "n_params_M": round(n_params / 1e6, 2),
        "peak_vram_gb": round(peak_gb, 3),
        "threshold_gb": threshold_gb,
        "step_time_s": round(t_step, 4),
        "loss_at_step_0": round(float(loss.detach().cpu()), 4),
    }


class _NullCtx:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="P-3 xresnet1d50 VRAM probe")
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--seq-len", type=int, default=1000, help="PTB-XL @ 100 Hz, 10 sec = 1000")
    ap.add_argument("--mixed-precision", action="store_true")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    result = probe(args.batch, args.seq_len, args.mixed_precision)
    result["pilot"] = "P-3"
    result["spec"] = "20-plan/ecg-ppg-realworld/pilots-README.md#P-3"

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

"""
Spec: 20-plan/sleep-staging/pilots-README.md#P-3

P-3 — U-Sleep frozen-inference VRAM probe.

Question: Does U-Sleep frozen inference fit inside the GTX 1650 4 GB VRAM
envelope at batch=32 on a single-channel 35-second window (U-Sleep's
standard input shape)? Single-channel mode matches HMC PSG and MESA per
protocol-lock.md §3 / approach.md.

Success criteria:
  (a) Peak VRAM <= 3 GB at batch=32. (Gating per critic-v2 C-1 and
      protocol-lock.md §6 pre-run checklists.)

Non-gating throughput probes:
  - batch=8 and batch=64 peak-VRAM measurements for batch-size planning.

Notes:
  - Loss-decrease check from the original generic VRAM-probe template is
    N/A here (frozen inference, no training).
  - Synthetic single-channel input is acceptable for the VRAM portion
    (per task spec). Sanity-check macro-F1 on Sleep-EDF is the separate
    P-3 success criterion (c) and is not part of this script.
  - U-Sleep checkpoint: pulled from the official `u-sleep` PyPI package
    if installed, else from the published checkpoint distributed with
    https://github.com/perslev/U-Time. If the checkpoint is not already
    downloaded, the pilot returns status="fail" with a clear remediation
    path — we do NOT fabricate a result.
  - If torch + cuda is unavailable, status="fail" with reason
    "cuda not available — env not yet set up".
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path


# U-Sleep window parameters (per protocol-lock §3, single-channel mode).
USLEEP_WINDOW_SECONDS = 35
USLEEP_SAMPLE_RATE_HZ = 128  # U-Sleep's standard internal sample rate
USLEEP_INPUT_CHANNELS = 1


def _try_import_torch():
    try:
        import torch  # noqa: F401
        return True, None
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def _load_usleep_model():
    """Try to load a pretrained U-Sleep model.

    Order:
      1. `usleep_api` / `u_sleep` PyPI package (perslev's official wrapper).
      2. `utime` package (U-Time repo, pip-installable from GitHub).
      3. Fail with remediation pointing at the checkpoint URL.

    Returns (model, source_str) on success, or (None, reason_str) on fail.
    """
    # 1. Official PyPI wrapper
    try:
        import u_sleep  # type: ignore[import-not-found]

        if hasattr(u_sleep, "load_model"):
            return u_sleep.load_model(), "u_sleep.load_model()"
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        return None, f"u_sleep package present but load_model failed: {e}"

    # 2. U-Time fallback
    try:
        from utime.bin import predict as _predict  # type: ignore[import-not-found]

        # U-Time historically loads via a project YAML; we cannot synthesize
        # one inside a pilot script without copying the upstream resources.
        # Surface this as a checkpoint-acquisition step required from lead.
        _ = _predict
        return None, (
            "utime package present but checkpoint resolution requires a "
            "project YAML from https://github.com/perslev/U-Time — download "
            "the published U-Sleep checkpoint and pass via --checkpoint."
        )
    except ImportError:
        pass
    except Exception as e:  # noqa: BLE001
        return None, f"utime package present but predict module failed: {e}"

    return None, (
        "Neither `u_sleep` nor `utime` is importable. Install via "
        "`pip install u-sleep` (preferred) or clone the U-Time repo and "
        "pip-install it; then re-run. Checkpoint URL: "
        "https://github.com/perslev/U-Sleep (see also "
        "https://github.com/perslev/U-Time)."
    )


def _peak_vram_for_batch(model, batch_size: int, mixed_precision: bool, device) -> dict:
    """Measure peak GPU VRAM for a single forward pass at the given batch size.

    Synthesizes a single-channel input of shape (B, 1, T) where T is
    USLEEP_WINDOW_SECONDS * USLEEP_SAMPLE_RATE_HZ. Many U-Sleep
    implementations expect (B, T, C) or (B, C, T); we try both.
    """
    import torch

    n_samples = USLEEP_WINDOW_SECONDS * USLEEP_SAMPLE_RATE_HZ
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats(device)

    x_bct = torch.randn(batch_size, USLEEP_INPUT_CHANNELS, n_samples, device=device)
    x_btc = x_bct.transpose(1, 2).contiguous()

    forward_kwargs = {}
    autocast_ctx = (
        torch.autocast(device_type="cuda", dtype=torch.float16)
        if mixed_precision
        else torch.autocast(device_type="cuda", enabled=False)
    )

    err: str | None = None
    used_layout: str | None = None
    with torch.inference_mode():
        with autocast_ctx:
            for layout, x in (("BCT", x_bct), ("BTC", x_btc)):
                try:
                    _ = model(x, **forward_kwargs)
                    used_layout = layout
                    err = None
                    break
                except Exception as e:  # noqa: BLE001
                    err = f"{layout}: {e}"
                    continue

    peak_bytes = torch.cuda.max_memory_allocated(device)
    return {
        "batch_size": batch_size,
        "peak_vram_gb": round(peak_bytes / (1024**3), 4),
        "input_layout_used": used_layout,
        "forward_error": err,
    }


def probe(
    batch_sizes: tuple[int, ...],
    mixed_precision: bool,
    checkpoint_path: Path | None,
    vram_threshold_gb: float,
) -> dict:
    ok, err = _try_import_torch()
    if not ok:
        return {
            "status": "fail",
            "reason": f"torch not importable: {err}",
            "remediation": (
                "Install torch per requirements.txt (torch>=2.4,<3) "
                "with CUDA support matching the local driver."
            ),
        }

    import torch

    if not torch.cuda.is_available():
        return {
            "status": "fail",
            "reason": "cuda not available — env not yet set up",
            "remediation": (
                "Install a CUDA-enabled PyTorch wheel matching the GTX 1650 "
                "driver (CUDA 12.x) and verify torch.cuda.is_available() "
                "returns True before re-running."
            ),
        }

    device = torch.device("cuda:0")
    device_name = torch.cuda.get_device_name(device)
    total_vram_gb = round(torch.cuda.get_device_properties(device).total_memory / (1024**3), 2)

    # Load model. Honour --checkpoint if provided.
    model = None
    source = None
    if checkpoint_path is not None:
        if not checkpoint_path.exists():
            return {
                "status": "fail",
                "reason": f"checkpoint path does not exist: {checkpoint_path}",
                "remediation": (
                    "Download the U-Sleep checkpoint from "
                    "https://github.com/perslev/U-Sleep (or the U-Time repo "
                    "https://github.com/perslev/U-Time) and pass --checkpoint."
                ),
            }
        try:
            obj = torch.load(checkpoint_path, map_location=device)
            if hasattr(obj, "to"):
                model = obj.to(device).eval()
                source = f"torch.load({checkpoint_path.name})"
            else:
                # checkpoint is a state-dict; we cannot instantiate the model
                # architecture without the upstream package.
                return {
                    "status": "fail",
                    "reason": (
                        "checkpoint is a state-dict — needs U-Sleep architecture "
                        "to instantiate. Install `u_sleep` or `utime` and re-run."
                    ),
                    "remediation": (
                        "pip install u-sleep (preferred) or clone "
                        "https://github.com/perslev/U-Time and install it, "
                        "then re-run with --checkpoint."
                    ),
                }
        except Exception as e:  # noqa: BLE001
            return {
                "status": "fail",
                "reason": f"failed to load checkpoint: {e}",
            }
    else:
        model, source = _load_usleep_model()
        if model is None:
            return {
                "status": "fail",
                "reason": source,
                "remediation": (
                    "Install the U-Sleep package and ensure its bundled "
                    "checkpoint is downloaded. Alternatively pass an explicit "
                    "--checkpoint pointing at a torch.save'd model object."
                ),
            }
        try:
            model = model.to(device).eval()
            for p in model.parameters():
                p.requires_grad_(False)
        except Exception as e:  # noqa: BLE001
            return {"status": "fail", "reason": f"model.to(cuda) failed: {e}"}

    # Parameter count
    try:
        n_params = sum(p.numel() for p in model.parameters())
        n_params_M = round(n_params / 1e6, 3)
    except Exception:  # noqa: BLE001
        n_params_M = None

    # VRAM probes
    measurements = []
    threshold_passed_at_32 = False
    for bs in batch_sizes:
        m = _peak_vram_for_batch(model, bs, mixed_precision, device)
        measurements.append(m)
        if bs == 32 and m["forward_error"] is None and m["peak_vram_gb"] <= vram_threshold_gb:
            threshold_passed_at_32 = True

    # Pass/fail driven solely by the batch=32 result. batch=8 / batch=64 are
    # non-gating throughput-planning probes per spec.
    bs32 = next((m for m in measurements if m["batch_size"] == 32), None)
    if bs32 is None:
        status = "fail"
        reason = "batch=32 measurement missing"
    elif bs32.get("forward_error"):
        status = "fail"
        reason = f"batch=32 forward failed: {bs32['forward_error']}"
    elif not threshold_passed_at_32:
        status = "fail"
        reason = (
            f"batch=32 peak_vram_gb={bs32['peak_vram_gb']} > "
            f"threshold {vram_threshold_gb} GB. Consider reducing batch "
            "size; if still >3 GB at batch=1, move to Kaggle T4 (R-5)."
        )
    else:
        status = "pass"
        reason = None

    return {
        "status": status,
        "reason": reason,
        "device_name": device_name,
        "total_vram_gb": total_vram_gb,
        "vram_threshold_gb": vram_threshold_gb,
        "mixed_precision": mixed_precision,
        "n_params_M": n_params_M,
        "model_source": source,
        "input_window_seconds": USLEEP_WINDOW_SECONDS,
        "input_sample_rate_hz": USLEEP_SAMPLE_RATE_HZ,
        "input_channels": USLEEP_INPUT_CHANNELS,
        "loss_decrease_check": "N/A (frozen inference; no training)",
        "measurements": measurements,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="P-3 U-Sleep VRAM probe")
    ap.add_argument(
        "--batch-sizes",
        type=str,
        default="8,32,64",
        help="Comma-separated batch sizes. batch=32 is the gating probe; others non-gating.",
    )
    ap.add_argument(
        "--mixed-precision",
        action="store_true",
        help="Use torch.autocast(fp16). Default off; U-Sleep is small enough that fp32 typically fits.",
    )
    ap.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help=(
            "Optional explicit path to a torch.save'd U-Sleep model object. "
            "If absent, falls back to importing the `u_sleep` / `utime` package."
        ),
    )
    ap.add_argument(
        "--vram-threshold-gb",
        type=float,
        default=3.0,
        help="Peak VRAM threshold at batch=32 (gating).",
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    batch_sizes = tuple(int(x) for x in args.batch_sizes.split(",") if x.strip())

    result = probe(
        batch_sizes=batch_sizes,
        mixed_precision=args.mixed_precision,
        checkpoint_path=args.checkpoint,
        vram_threshold_gb=args.vram_threshold_gb,
    )
    result["pilot"] = "P-3"
    result["spec"] = "20-plan/sleep-staging/pilots-README.md#P-3"

    runs_dir = Path(__file__).resolve().parents[2] / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out_path = args.out or (runs_dir / f"pilot_p3_usleep_vram_{int(time.time())}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"\nWrote {out_path}")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())

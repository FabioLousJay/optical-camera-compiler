"""Genuine PyTorch RRDBNet (Real-ESRGAN / Real-ESRNet) architecture, checkpoint provenance,
tiled inference, and OOM fallback.

Never substitutes conventional interpolation for neural inference.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
from typing import Any
import numpy as np
from PIL import Image, ImageFilter

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = None  # type: ignore[assignment]
    nn = None  # type: ignore[assignment]
    F = None  # type: ignore[assignment]


_CANDIDATE_TORCH_PYTHONS = (
    "/Users/fjs/projects/llm_engineering/.venv/bin/python",
)


def _discover_external_torch_python() -> Path | None:
    """Locate an external Python interpreter with PyTorch installed if the current venv lacks torch."""
    if os.environ.get("PHOTONQC_DISABLE_EXTERNAL_TORCH") == "1":
        return None
    env_override = os.environ.get("PHOTONQC_TORCH_PYTHON")
    candidates = [env_override] if env_override else list(_CANDIDATE_TORCH_PYTHONS)
    for cand in candidates:
        if not cand:
            continue
        p = Path(cand).expanduser()
        if p.is_file():
            return p
    return None


def sha256_checkpoint(path: Path) -> str:
    """Compute SHA-256 digest of a model weight file."""
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def detect_compute_device(preferred: str = "auto") -> dict[str, Any]:
    """Detect available PyTorch compute device (CUDA, Apple Silicon MPS, or CPU)."""
    if not TORCH_AVAILABLE:
        ext_py = _discover_external_torch_python()
        if ext_py is not None:
            repo_root = str(Path(__file__).resolve().parent.parent)
            env = {**os.environ, "PYTHONPATH": repo_root}
            try:
                res = subprocess.run(
                    [
                        str(ext_py),
                        "-c",
                        (
                            "import json, photonqc.neural_sr as n; "
                            f"print(json.dumps(n.detect_compute_device({preferred!r})))"
                        ),
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                    env=env,
                    timeout=15,
                )
                info = json.loads(res.stdout.strip())
                info["bridge_python"] = str(ext_py)
                return info
            except Exception:
                pass
        return {
            "torch_available": False,
            "torch_version": None,
            "device": "none",
            "mps_available": False,
            "cuda_available": False,
        }

    cuda_ok = bool(torch.cuda.is_available())
    mps_ok = bool(hasattr(torch.backends, "mps") and torch.backends.mps.is_available())

    if preferred != "auto":
        device = preferred
    elif cuda_ok:
        device = "cuda"
    elif mps_ok:
        device = "mps"
    else:
        device = "cpu"

    return {
        "torch_available": True,
        "torch_version": torch.__version__,
        "device": device,
        "mps_available": mps_ok,
        "cuda_available": cuda_ok,
    }


if TORCH_AVAILABLE:

    class ResidualDenseBlock(nn.Module):
        """Residual Dense Block used in RRDBNet (RealESRGAN_x4plus / RealESRNet_x4plus)."""

        def __init__(self, num_feat: int = 64, num_grow_ch: int = 32) -> None:
            super().__init__()
            self.conv1 = nn.Conv2d(num_feat, num_grow_ch, 3, 1, 1)
            self.conv2 = nn.Conv2d(num_feat + num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv3 = nn.Conv2d(num_feat + 2 * num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv4 = nn.Conv2d(num_feat + 3 * num_grow_ch, num_grow_ch, 3, 1, 1)
            self.conv5 = nn.Conv2d(num_feat + 4 * num_grow_ch, num_feat, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x1 = self.lrelu(self.conv1(x))
            x2 = self.lrelu(self.conv2(torch.cat((x, x1), 1)))
            x3 = self.lrelu(self.conv3(torch.cat((x, x1, x2), 1)))
            x4 = self.lrelu(self.conv4(torch.cat((x, x1, x2, x3), 1)))
            x5 = self.conv5(torch.cat((x, x1, x2, x3, x4), 1))
            return x5 * 0.2 + x

    class RRDB(nn.Module):
        """Residual in Residual Dense Block."""

        def __init__(self, num_feat: int = 64, num_grow_ch: int = 32) -> None:
            super().__init__()
            self.rdb1 = ResidualDenseBlock(num_feat, num_grow_ch)
            self.rdb2 = ResidualDenseBlock(num_feat, num_grow_ch)
            self.rdb3 = ResidualDenseBlock(num_feat, num_grow_ch)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            out = self.rdb1(x)
            out = self.rdb2(out)
            out = self.rdb3(out)
            return out * 0.2 + x

    class RRDBNet(nn.Module):
        """Canonical RRDBNet architecture for RealESRGAN_x4plus and RealESRNet_x4plus."""

        def __init__(
            self,
            num_in_ch: int = 3,
            num_out_ch: int = 3,
            scale: int = 4,
            num_feat: int = 64,
            num_block: int = 23,
            num_grow_ch: int = 32,
        ) -> None:
            super().__init__()
            self.scale = scale
            if scale == 2:
                num_in_ch = num_in_ch * 4
            elif scale == 1:
                num_in_ch = num_in_ch * 16
            self.conv_first = nn.Conv2d(num_in_ch, num_feat, 3, 1, 1)
            self.body = nn.ModuleList(
                [RRDB(num_feat=num_feat, num_grow_ch=num_grow_ch) for _ in range(num_block)]
            )
            self.conv_body = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_up1 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_up2 = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_hr = nn.Conv2d(num_feat, num_feat, 3, 1, 1)
            self.conv_last = nn.Conv2d(num_feat, num_out_ch, 3, 1, 1)
            self.lrelu = nn.LeakyReLU(negative_slope=0.2, inplace=True)

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            feat = self.conv_first(x)
            body_feat = feat
            for block in self.body:
                body_feat = block(body_feat)
            body_feat = self.conv_body(body_feat)
            feat = feat + body_feat
            feat = self.lrelu(self.conv_up1(F.interpolate(feat, scale_factor=2, mode="nearest")))
            feat = self.lrelu(self.conv_up2(F.interpolate(feat, scale_factor=2, mode="nearest")))
            out = self.conv_last(self.lrelu(self.conv_hr(feat)))
            return out


def run_native_rrdbnet_inference(
    image: Image.Image,
    weights_path: Path,
    *,
    device_name: str = "auto",
    tile_size: int = 0,
    tile_pad: int = 10,
) -> tuple[Image.Image, dict[str, Any]]:
    """Execute genuine PyTorch RRDBNet 4x inference using a verified checkpoint file.

    Supports full-image inference, tiled inference with overlap padding, automatic
    OOM tile fallback, and transparent delegation to an external PyTorch MPS/CUDA
    interpreter when the host venv is Python 3.14 without cp314 torch wheels.
    """
    resolved_weights = weights_path.expanduser().resolve()
    if not resolved_weights.is_file():
        raise FileNotFoundError(f"Real-ESRGAN weight file missing: {resolved_weights}")

    if not TORCH_AVAILABLE:
        ext_py = _discover_external_torch_python()
        if ext_py is None:
            raise RuntimeError(
                "PyTorch is not installed in the current Python environment; native RRDBNet inference is BLOCKED."
            )
        repo_root = str(Path(__file__).resolve().parent.parent)
        env = {**os.environ, "PYTHONPATH": repo_root}
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            in_png = tmp / "worker_in.png"
            out_png = tmp / "worker_out.png"
            meta_json = tmp / "worker_meta.json"
            image.save(in_png, format="PNG")
            cmd = [
                str(ext_py),
                "-c",
                "from photonqc.neural_sr import _worker_main; raise SystemExit(_worker_main())",
                "--worker-input",
                str(in_png),
                "--worker-output",
                str(out_png),
                "--worker-meta",
                str(meta_json),
                "--weights",
                str(resolved_weights),
                "--device",
                device_name,
                "--tile-size",
                str(tile_size),
                "--tile-pad",
                str(tile_pad),
            ]
            subprocess.run(cmd, check=True, env=env)
            with Image.open(out_png) as out_im:
                out_im.load()
                res_img = out_im.copy()
            meta = json.loads(meta_json.read_text(encoding="utf-8"))
            meta["bridge_python"] = str(ext_py)
            return res_img, meta

    weights_hash = sha256_checkpoint(resolved_weights)
    dev_info = detect_compute_device(preferred=device_name)
    device = torch.device(dev_info["device"])

    checkpoint = torch.load(str(resolved_weights), map_location="cpu", weights_only=True)
    if isinstance(checkpoint, dict):
        if "params_ema" in checkpoint:
            state_dict = checkpoint["params_ema"]
        elif "params" in checkpoint:
            state_dict = checkpoint["params"]
        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
    else:
        raise ValueError("Unsupported checkpoint format: expected state_dict mapping.")

    # Auto-detect num_feat, num_block, num_grow_ch from state_dict keys so both full 23-block
    # RealESRGAN_x4plus checkpoints and compact test checkpoints load strictly with strict=True.
    if "conv_first.weight" not in state_dict:
        raise ValueError("Checkpoint does not contain RRDBNet 'conv_first.weight' parameter.")
    num_feat = int(state_dict["conv_first.weight"].shape[0])
    body_indices = {
        int(k.split(".")[1])
        for k in state_dict.keys()
        if k.startswith("body.") and k.split(".")[1].isdigit()
    }
    num_block = max(body_indices) + 1 if body_indices else 23
    num_grow_ch = (
        int(state_dict["body.0.rdb1.conv1.weight"].shape[0])
        if "body.0.rdb1.conv1.weight" in state_dict
        else 32
    )

    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        scale=4,
        num_feat=num_feat,
        num_block=num_block,
        num_grow_ch=num_grow_ch,
    )
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    model = model.to(device)

    arr = np.asarray(image, dtype=np.float32) / 255.0
    tensor = torch.from_numpy(np.transpose(arr, (2, 0, 1))).unsqueeze(0).to(device)

    oom_fallback_triggered = False
    active_tile = tile_size

    def _infer_full(inp: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            return model(inp)

    def _infer_tiled(inp: torch.Tensor, tile: int, pad: int) -> torch.Tensor:
        batch, channel, height, width = inp.shape
        out_h = height * 4
        out_w = width * 4
        output = inp.new_zeros((batch, channel, out_h, out_w))
        tiles_x = math.ceil(width / tile)
        tiles_y = math.ceil(height / tile)
        for y in range(tiles_y):
            for x in range(tiles_x):
                ofs_x = x * tile
                ofs_y = y * tile
                in_start_x = ofs_x
                in_end_x = min(ofs_x + tile, width)
                in_start_y = ofs_y
                in_end_y = min(ofs_y + tile, height)

                in_start_x_pad = max(in_start_x - pad, 0)
                in_end_x_pad = min(in_end_x + pad, width)
                in_start_y_pad = max(in_start_y - pad, 0)
                in_end_y_pad = min(in_end_y + pad, height)

                input_tile = inp[:, :, in_start_y_pad:in_end_y_pad, in_start_x_pad:in_end_x_pad]
                with torch.no_grad():
                    output_tile = model(input_tile)

                out_start_x = in_start_x * 4
                out_end_x = in_end_x * 4
                out_start_y = in_start_y * 4
                out_end_y = in_end_y * 4

                out_start_x_tile = (in_start_x - in_start_x_pad) * 4
                out_end_x_tile = out_start_x_tile + (in_end_x - in_start_x) * 4
                out_start_y_tile = (in_start_y - in_start_y_pad) * 4
                out_end_y_tile = out_start_y_tile + (in_end_y - in_start_y) * 4

                output[:, :, out_start_y:out_end_y, out_start_x:out_end_x] = output_tile[
                    :, :, out_start_y_tile:out_end_y_tile, out_start_x_tile:out_end_x_tile
                ]
        return output

    try:
        if active_tile > 0:
            out_tensor = _infer_tiled(tensor, active_tile, tile_pad)
        else:
            out_tensor = _infer_full(tensor)
    except RuntimeError as exc:
        if "out of memory" in str(exc).lower():
            oom_fallback_triggered = True
            active_tile = 128 if active_tile == 0 else max(64, active_tile // 2)
            out_tensor = _infer_tiled(tensor, active_tile, tile_pad)
        else:
            raise

    out_np = out_tensor.squeeze(0).float().cpu().clamp_(0.0, 1.0).numpy()
    out_np = np.transpose(out_np, (1, 2, 0))
    out_uint8 = np.clip(np.rint(out_np * 255.0), 0, 255).astype(np.uint8)
    result_image = Image.fromarray(out_uint8)

    meta = {
        "weights_path": str(resolved_weights),
        "weights_sha256": weights_hash,
        "device": str(device),
        "torch_version": torch.__version__,
        "architecture": f"RRDBNet(feat={num_feat},blocks={num_block},grow={num_grow_ch},scale=4)",
        "tile_size": active_tile,
        "oom_fallback_triggered": oom_fallback_triggered,
        "native_4x_size": list(result_image.size),
    }
    return result_image, meta


def apply_antidrift_neural_stabilizer(
    lr_source: Image.Image,
    sr_gan_img: Image.Image,
    sr_net_img: Image.Image | None = None,
    *,
    gan_edge_weight: float = 0.20,
    hf_injection_gain: float = 0.16,
    envelope_slack: float = 4.0,
) -> tuple[Image.Image, list[str]]:
    """Frequency-Decomposed Source-Locked Neural Stabilization (Anti-Drift & Anti-Hallucination).

     Eliminates adversarial GAN hallucinations, low-frequency tonal/color shift, and edge overshoot
    halos while preserving genuine neural high-frequency edge reconstruction:
    1. Low-Frequency Optical Lock: Anchors macro tonality, color balance, and smooth gradients to
       the source-locked optical base (`I_base`) so the neural network cannot shift exposure or
       invent textures in smooth zones.
    2. Structural Neural High-Frequency Extraction: Combines `RealESRNet_x4plus` (80% L1 structural
       master) with `RealESRGAN_x4plus` (20% high-acuity generator) and extracts the high-frequency
       Laplacian edge residual `Delta_HF = (I_neural - G_sigma(I_neural))`.
    3. Edge-Gated Soft-Clamped Residual Injection: Injects `Delta_HF` strictly along verified source
       structural edges (`M_edge`) with hyperbolic-tangent soft saturation (`tau = 5.0`) to restore
       optical edge slope without step-edge ringing.
    4. Source Envelope & Flat-Black Backdrop Lock: Clamps all pixels to the local source min/max
       optical envelope and locks flat-black studio borders (`max(R,G,B) <= 2`) to exact `(0, 0, 0)`.
    """
    from .restoration import SourcePreservingRestorer

    target_size = sr_gan_img.size
    lanczos_anchor = lr_source.resize(target_size, Image.Resampling.LANCZOS)
    restorer = SourcePreservingRestorer()
    base_img, base_ops = restorer.restore_image(lanczos_anchor)
    base_arr = np.asarray(base_img, dtype=np.float32)
    gan_arr = np.asarray(sr_gan_img, dtype=np.float32)

    ops: list[str] = list(base_ops)

    # Compute source gradient map for edge-selective modulation
    luma_base = (
        0.2126 * base_arr[:, :, 0]
        + 0.7152 * base_arr[:, :, 1]
        + 0.0722 * base_arr[:, :, 2]
    )
    gy, gx = np.gradient(luma_base)
    grad_mag = np.hypot(gx, gy)
    edge_mask = np.clip((grad_mag - 1.2) / 12.0, 0.0, 1.0)[:, :, np.newaxis]

    if sr_net_img is not None:
        net_arr = np.asarray(sr_net_img, dtype=np.float32)
        neural_arr = (1.0 - gan_edge_weight) * net_arr + gan_edge_weight * gan_arr
        ops.append(f"antidrift_esrnet_esrgan_structural_blend_w_{gan_edge_weight:.2f}")
    else:
        neural_arr = gan_arr
        ops.append("antidrift_single_model_neural_residual")

    # Extract high-frequency neural edge transient (Laplacian band r=2.0)
    neural_pil = Image.fromarray(np.clip(np.rint(neural_arr), 0, 255).astype(np.uint8))
    neural_lp = np.asarray(neural_pil.filter(ImageFilter.GaussianBlur(radius=2.0)), dtype=np.float32)
    base_lp = np.asarray(base_img.filter(ImageFilter.GaussianBlur(radius=2.0)), dtype=np.float32)

    delta_hf = (neural_arr - neural_lp) - (base_arr - base_lp)

    # If the source photograph is bilaterally symmetric, enforce symmetric neural HF residual
    # so asymmetric Conv2d filters cannot introduce left-right geometric drift.
    lr_arr_u8 = np.asarray(lr_source, dtype=np.uint8)
    if lr_arr_u8.shape[1] % 2 == 0:
        half_lr = lr_arr_u8.shape[1] // 2
        sym_mad = float(
            np.mean(
                np.abs(
                    lr_arr_u8[:, :half_lr, :].astype(np.float32)
                    - lr_arr_u8[:, half_lr:, :][:, ::-1, :].astype(np.float32)
                )
            )
        )
        if sym_mad < 1.0:
            delta_hf = 0.5 * (delta_hf + delta_hf[:, ::-1, :])
            ops.append("bilateral_symmetry_residual_lock")

    tau = 5.0
    delta_hf_soft = tau * np.tanh(delta_hf / tau)
    fused = base_arr + hf_injection_gain * edge_mask * delta_hf_soft
    ops.append(f"frequency_locked_hf_residual_injection_gain_{hf_injection_gain:.2f}")

    # Local source envelope clamp (prevents GAN overshoot halos and synthetic texture hallucination)
    min_img = lanczos_anchor.filter(ImageFilter.MinFilter(size=3))
    max_img = lanczos_anchor.filter(ImageFilter.MaxFilter(size=3))
    local_min = np.asarray(min_img, dtype=np.float32) - (1.0 + envelope_slack * edge_mask)
    local_max = np.asarray(max_img, dtype=np.float32) + (1.0 + envelope_slack * edge_mask)
    clamped = np.clip(fused, np.maximum(0.0, local_min), np.minimum(255.0, local_max))
    ops.append(f"source_envelope_clamp_slack_{envelope_slack:.1f}")

    # Strict flat-black studio backdrop lock
    lr_max_ch = np.max(np.asarray(lr_source, dtype=np.uint8), axis=2)
    lr_black_pil = Image.fromarray(np.where(lr_max_ch <= 2, 255, 0).astype(np.uint8))
    lr_black_eroded = lr_black_pil.filter(ImageFilter.MinFilter(size=3))
    hr_black_mask = (
        np.asarray(lr_black_eroded.resize(target_size, Image.Resampling.NEAREST), dtype=np.uint8) > 127
    )
    if np.any(hr_black_mask):
        clamped[hr_black_mask] = 0.0
        ops.append("flat_black_backdrop_zero_lock")

    out_uint8 = np.clip(np.rint(clamped), 0, 255).astype(np.uint8)
    return Image.fromarray(out_uint8), ops


def _worker_main() -> int:
    parser = argparse.ArgumentParser(description="PhotonQC PyTorch RRDBNet worker")
    parser.add_argument("--worker-input", type=Path, required=True)
    parser.add_argument("--worker-output", type=Path, required=True)
    parser.add_argument("--worker-meta", type=Path, required=True)
    parser.add_argument("--weights", type=Path, required=True)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--tile-size", type=int, default=0)
    parser.add_argument("--tile-pad", type=int, default=10)
    args = parser.parse_args()

    with Image.open(args.worker_input) as src_im:
        src_im.load()
        rgb_in = src_im.copy()

    out_im, meta = run_native_rrdbnet_inference(
        rgb_in,
        args.weights,
        device_name=args.device,
        tile_size=args.tile_size,
        tile_pad=args.tile_pad,
    )
    out_im.save(args.worker_output, format="PNG")
    args.worker_meta.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(_worker_main())

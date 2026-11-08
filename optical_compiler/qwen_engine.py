"""Local Apple Silicon Metal runner bridge for Qwen-Image-2.1 / Qwen-Image-2.1-Turbo (Unsloth GGUF via stable-diffusion.cpp)."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import subprocess
import time
from typing import Any

from PIL import Image

from .adapters.qwen_image import QWEN_ASPECT_RESOLUTIONS

DEFAULT_QWEN_ENGINE_ROOT = Path("/Users/fjs/.gemini/antigravity/scratch/qwen-image-2.1-engine")


def _engine_root() -> Path:
    override = os.environ.get("QWEN_IMAGE_ENGINE_ROOT")
    if override:
        return Path(override).expanduser().resolve()
    return DEFAULT_QWEN_ENGINE_ROOT


def get_qwen_engine_status() -> dict[str, Any]:
    """Inspect local Apple Silicon Metal `sd-cli` binary and Unsloth Qwen-Image-2.1 GGUF weights."""
    root = _engine_root()
    sd_cli = root / "bin" / "sd-cli"
    models_dir = root / "models"

    denoiser_turbo_q8 = models_dir / "qwen-image-2.1-turbo-Q8_0.gguf"
    denoiser_std_q8 = models_dir / "qwen-image-2.1-Q8_0.gguf"
    denoiser_q4 = models_dir / "qwen-image-2.1-Q4_K_M.gguf"
    llm_encoder = models_dir / "Qwen3-VL-8B-Instruct-UD-Q4_K_XL.gguf"
    vae_model = models_dir / "qwen_image_2.1_vae_bf16.safetensors"

    active_denoiser: Path | None = None
    for cand in (denoiser_turbo_q8, denoiser_std_q8, denoiser_q4):
        if cand.is_file() and cand.stat().st_size > 100 * 1024 * 1024:
            active_denoiser = cand
            break

    def _file_info(p: Path) -> dict[str, Any]:
        exists = p.is_file()
        size_bytes = p.stat().st_size if exists else 0
        return {
            "path": str(p),
            "exists": exists,
            "size_gb": round(size_bytes / (1024**3), 2),
        }

    sd_cli_ok = sd_cli.is_file() and os.access(sd_cli, os.X_OK)
    llm_ok = llm_encoder.is_file() and llm_encoder.stat().st_size > 1_000_000_000
    vae_ok = vae_model.is_file() and vae_model.stat().st_size > 100_000_000
    ready = bool(sd_cli_ok and active_denoiser is not None and llm_ok and vae_ok)

    return {
        "ready": ready,
        "engine_root": str(root),
        "sd_cli": {
            "path": str(sd_cli),
            "installed": sd_cli_ok,
            "metal_backend": "MTL0 (Apple Silicon Metal / Unified Memory)",
        },
        "models": {
            "active_denoiser": str(active_denoiser) if active_denoiser else None,
            "is_turbo": bool(active_denoiser and "turbo" in active_denoiser.name.lower()),
            "denoiser_turbo_q8": _file_info(denoiser_turbo_q8),
            "llm_encoder": _file_info(llm_encoder),
            "vae": _file_info(vae_model),
        },
    }


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run_qwen_image_local(
    prompt: str,
    output_path: str | Path,
    *,
    negative_prompt: str = "",
    aspect_ratio: str = "1:1",
    width: int | None = None,
    height: int | None = None,
    steps: int | None = None,
    cfg_scale: float | None = None,
    seed: int = 42,
    ref_image_path: str | Path | None = None,
    apply_lightroom_pyramid: bool = False,
    pyramid_scale: int = 1,
) -> dict[str, Any]:
    """Execute local Qwen-Image-2.1 / Turbo generation on Apple Silicon Metal via `sd-cli`."""
    status = get_qwen_engine_status()
    if not status["ready"]:
        raise RuntimeError(
            "Local Qwen-Image-2.1 Metal engine is not ready or weights are still downloading. "
            f"Status: {status}"
        )

    sd_cli = Path(status["sd_cli"]["path"])
    denoiser = Path(status["models"]["active_denoiser"])
    llm = Path(status["models"]["llm_encoder"]["path"])
    vae = Path(status["models"]["vae"]["path"])
    is_turbo = bool(status["models"]["is_turbo"])

    default_w, default_h = QWEN_ASPECT_RESOLUTIONS.get(aspect_ratio, (1024, 1024))
    w_px = int(width or default_w)
    h_px = int(height or default_h)
    # Ensure multiples of 16 for DiT patchify
    w_px = max(256, (w_px // 16) * 16)
    h_px = max(256, (h_px // 16) * 16)

    eff_steps = int(steps if steps is not None else (8 if is_turbo else 20))
    eff_cfg = float(cfg_scale if cfg_scale is not None else (1.0 if is_turbo else 6.0))

    out_p = Path(output_path).expanduser().resolve()
    out_p.parent.mkdir(parents=True, exist_ok=True)

    cmd: list[str] = [
        str(sd_cli),
        "--diffusion-model",
        str(denoiser),
        "--vae",
        str(vae),
        "--llm",
        str(llm),
        "-p",
        prompt,
        "--steps",
        str(eff_steps),
        "--cfg-scale",
        str(eff_cfg),
        "--sampling-method",
        "euler",
        "-W",
        str(w_px),
        "-H",
        str(h_px),
        "--seed",
        str(seed),
        "--diffusion-fa",
        "--vae-tiling",
        "-o",
        str(out_p),
    ]

    if is_turbo:
        cmd.extend(
            [
                "--sigmas",
                "1.0,0.978453,0.95418,0.926626,0.89508,0.845148,0.704534,0.414568,0.0",
            ]
        )
    elif negative_prompt:
        cmd.extend(["-n", negative_prompt])

    if ref_image_path:
        ref_p = Path(ref_image_path).expanduser().resolve()
        if not ref_p.is_file():
            raise FileNotFoundError(f"Reference image not found: {ref_p}")
        cmd.extend(["-r", str(ref_p)])

    t0 = time.monotonic()
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False,
        timeout=600,
    )
    elapsed_s = round(time.monotonic() - t0, 2)

    if proc.returncode != 0 or not out_p.is_file():
        stderr_tail = (proc.stderr or proc.stdout or "")[-1200:]
        raise RuntimeError(f"sd-cli failed (exit {proc.returncode}): {stderr_tail}")

    # Automatically remove periodic wan_vae stride-2/4 transposed-conv carrier spikes in Luminance (Y)
    from photonqc.pyramids import LaplacianPyramidConfig, degrid_vae_rgb_image, frequency_separate_portrait_lighting

    with Image.open(out_p) as gen_im:
        gen_im.load()
        rgb_gen = gen_im.convert("RGB")
    rgb_clean, vae_spikes_clamped = degrid_vae_rgb_image(rgb_gen)

    pyramid_meta: dict[str, Any] | None = None
    if apply_lightroom_pyramid:
        pyr_cfg = LaplacianPyramidConfig(
            levels=5,
            scale_factor=max(1, int(pyramid_scale)),
            use_neural_sr=False,
        )
        refined_img, pyramid_meta = frequency_separate_portrait_lighting(rgb_clean, config=pyr_cfg)
        refined_img.save(out_p, format="PNG")
    elif vae_spikes_clamped > 0:
        rgb_clean.save(out_p, format="PNG")

    with Image.open(out_p) as final_im:
        final_dims = list(final_im.size)

    return {
        "method": "qwen_image_2_1_local_metal_gguf",
        "denoiser": denoiser.name,
        "llm_encoder": llm.name,
        "vae": vae.name,
        "is_turbo": is_turbo,
        "steps": eff_steps,
        "cfg_scale": eff_cfg,
        "seed": seed,
        "native_dimensions": [w_px, h_px],
        "output_dimensions": final_dims,
        "elapsed_seconds": elapsed_s,
        "vae_carrier_spikes_clamped": vae_spikes_clamped,
        "lightroom_pyramid_applied": bool(apply_lightroom_pyramid),
        "pyramid_telemetry": pyramid_meta,
        "output_path": str(out_p),
        "output_sha256": _sha256_file(out_p),
    }

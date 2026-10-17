"""Explicit reference resize and genuine Real-ESRGAN super-resolution adapters.

Preserves 100% compatibility with the Section 6 seed `render()` contract while providing
rich provenance tracking (`BackendProvenance` and `render_with_provenance()`).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from typing import Any
from PIL import Image

from .licensing import verify_model_license
from .neural_sr import (
    apply_antidrift_neural_stabilizer,
    run_native_rrdbnet_inference,
    sha256_checkpoint,
)
from .sizing import apply_crop_or_pad


@dataclass
class BackendProvenance:
    """Machine-verifiable provenance record for the image scaling/super-resolution stage."""

    backend: str
    backend_label: str
    is_neural_ai: bool
    model_name: str | None = None
    weights_path: str | None = None
    weights_sha256: str | None = None
    repo_revision: str | None = None
    device: str = "cpu"
    runtime_info: dict[str, Any] = field(default_factory=dict)
    source_size: tuple[int, int] = (0, 0)
    native_model_size: tuple[int, int] = (0, 0)
    final_size: tuple[int, int] = (0, 0)
    post_model_lanczos_resized: bool = False
    transforms: list[str] = field(default_factory=list)
    execution_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _git_revision(repo: Path | None) -> str | None:
    if repo is None or not repo.exists():
        return None
    try:
        res = subprocess.run(
            ["git", "-C", str(repo.resolve()), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        return res.stdout.strip() or None
    except Exception:
        return None


def render_with_provenance(
    input_path: Path,
    size: tuple[int, int],
    backend: str,
    repo: Path | None = None,
    weights: Path | None = None,
    *,
    model_name: str = "RealESRGAN_x4plus",
    crop_policy: str = "reject",
    tile_size: int = 0,
    tile_pad: int = 10,
    allow_non_commercial: bool = False,
) -> tuple[Image.Image, BackendProvenance]:
    """Execute reference Lanczos resize or verified Real-ESRGAN neural inference with full provenance."""
    t0 = time.perf_counter()
    with Image.open(input_path) as source:
        if source.mode != "RGB":
            raise ValueError("MVP supports RGB sources only; do not silently convert color spaces or drop alpha")
        original = source.copy()

    src_size = original.size
    transforms: list[str] = []

    if crop_policy != "reject":
        original, crop_transform = apply_crop_or_pad(original, size, policy=crop_policy)
        if crop_transform != "aspect_ratio_matched":
            transforms.append(crop_transform)

    if backend == "lanczos":
        resized = original.resize(size, Image.Resampling.LANCZOS)
        transforms.append(f"lanczos_resize_{original.width}x{original.height}_to_{size[0]}x{size[1]}")
        elapsed = round(time.perf_counter() - t0, 4)
        prov = BackendProvenance(
            backend="lanczos",
            backend_label="lanczos_reference_not_ai",
            is_neural_ai=False,
            model_name=None,
            weights_path=None,
            weights_sha256=None,
            repo_revision=None,
            device="cpu",
            runtime_info={"resampler": "PIL.Image.Resampling.LANCZOS"},
            source_size=src_size,
            native_model_size=size,
            final_size=size,
            post_model_lanczos_resized=False,
            transforms=transforms,
            execution_seconds=elapsed,
        )
        return resized, prov

    if backend not in ("realesrgan", "realesrgan_native", "realesrgan_antidrift"):
        raise ValueError("Unknown backend")

    # Enforce license governance gate before running any model
    license_spec = verify_model_license(model_name, allow_non_commercial=allow_non_commercial)

    if backend == "realesrgan":
        if repo is None or weights is None:
            raise ValueError("Real-ESRGAN requires --realesrgan-repo and --weights")
        script = repo.resolve() / "inference_realesrgan.py"
        if not script.is_file() or not weights.resolve().is_file():
            raise FileNotFoundError("Real-ESRGAN script or weight file missing")
        if size[0] > original.width * 4 or size[1] > original.height * 4:
            raise ValueError("Requested size exceeds the 4x model output; no fake additional AI pixels")

        weights_hash = sha256_checkpoint(weights.resolve())
        revision = _git_revision(repo.resolve())

        with tempfile.TemporaryDirectory() as temp:
            tmp = Path(temp)
            # If explicit crop/pad changed original dimensions, write prepared input to temp
            infer_input = input_path.resolve()
            if original.size != src_size:
                infer_input = tmp / f"{input_path.stem}_prepared.png"
                original.save(infer_input, format="PNG")

            command = [
                sys.executable,
                str(script),
                "-i",
                str(infer_input),
                "-o",
                str(tmp),
                "-n",
                license_spec.name,
                "--model_path",
                str(weights.resolve()),
                "--outscale",
                "4",
                "--suffix",
                "sr",
                "--ext",
                "png",
                "--fp32",
            ]
            if tile_size > 0:
                command.extend(["--tile", str(tile_size), "--tile_pad", str(tile_pad)])
            subprocess.run(command, cwd=str(repo.resolve()), check=True)
            path = tmp / f"{infer_input.stem}_sr.png"
            if not path.is_file():
                raise RuntimeError(f"Real-ESRGAN output was not found at {path}")
            with Image.open(path) as produced:
                if produced.mode != "RGB":
                    raise ValueError("Real-ESRGAN result not RGB; inspect pipeline")
                image = produced.copy()

        native = image.size
        transforms.append(f"neural_x4_{license_spec.name}_{original.width}x{original.height}_to_{native[0]}x{native[1]}")
        post_lanczos = native != size
        if post_lanczos:
            image = image.resize(size, Image.Resampling.LANCZOS)
            transforms.append(f"final_lanczos_{native[0]}x{native[1]}_to_{size[0]}x{size[1]}")

        label = f"real_esrgan_x4plus_fp32_native_{native[0]}x{native[1]}_final_lanczos_{post_lanczos}"
        elapsed = round(time.perf_counter() - t0, 4)
        prov = BackendProvenance(
            backend="realesrgan",
            backend_label=label,
            is_neural_ai=True,
            model_name=license_spec.name,
            weights_path=str(weights.resolve()),
            weights_sha256=weights_hash,
            repo_revision=revision,
            device="subprocess",
            runtime_info={"license": license_spec.spdx_license, "tile_size": tile_size},
            source_size=src_size,
            native_model_size=native,
            final_size=size,
            post_model_lanczos_resized=post_lanczos,
            transforms=transforms,
            execution_seconds=elapsed,
        )
        return image, prov

    # backend in ("realesrgan_native", "realesrgan_antidrift"): Direct PyTorch RRDBNet execution
    if weights is None:
        raise ValueError("Real-ESRGAN native PyTorch backend requires --weights")
    resolved_weights = weights.resolve()
    if not resolved_weights.is_file():
        raise FileNotFoundError("Real-ESRGAN weight file missing")
    if size[0] > original.width * 4 or size[1] > original.height * 4:
        raise ValueError("Requested size exceeds the 4x model output; no fake additional AI pixels")

    image, meta = run_native_rrdbnet_inference(
        original,
        resolved_weights,
        tile_size=tile_size,
        tile_pad=tile_pad,
    )
    native = image.size
    transforms.append(f"neural_x4_native_rrdbnet_{original.width}x{original.height}_to_{native[0]}x{native[1]}")

    if backend == "realesrgan_antidrift":
        # Check if companion RealESRNet_x4plus.pth exists in the same directory for L1 structural anchor
        companion_net = resolved_weights.parent / "RealESRNet_x4plus.pth"
        sr_net_img: Image.Image | None = None
        if companion_net.is_file() and companion_net != resolved_weights:
            sr_net_img, net_meta = run_native_rrdbnet_inference(
                original,
                companion_net,
                tile_size=tile_size,
                tile_pad=tile_pad,
            )
            meta["structural_anchor_weights"] = str(companion_net)
            meta["structural_anchor_sha256"] = net_meta["weights_sha256"]
        elif resolved_weights.name == "RealESRNet_x4plus.pth":
            sr_net_img = image
        image, stab_ops = apply_antidrift_neural_stabilizer(
            lr_source=original,
            sr_gan_img=image,
            sr_net_img=sr_net_img,
        )
        transforms.extend(stab_ops)

    post_lanczos = native != size
    if post_lanczos:
        image = image.resize(size, Image.Resampling.LANCZOS)
        transforms.append(f"final_lanczos_{native[0]}x{native[1]}_to_{size[0]}x{size[1]}")

    if backend == "realesrgan_antidrift":
        label = f"real_esrgan_antidrift_fp32_native_{native[0]}x{native[1]}_final_lanczos_{post_lanczos}"
    else:
        label = f"real_esrgan_x4plus_fp32_native_{native[0]}x{native[1]}_final_lanczos_{post_lanczos}"
    elapsed = round(time.perf_counter() - t0, 4)
    prov = BackendProvenance(
        backend=backend,
        backend_label=label,
        is_neural_ai=True,
        model_name=license_spec.name,
        weights_path=str(resolved_weights),
        weights_sha256=meta["weights_sha256"],
        repo_revision=_git_revision(repo) if repo else None,
        device=meta["device"],
        runtime_info=meta,
        source_size=src_size,
        native_model_size=native,
        final_size=size,
        post_model_lanczos_resized=post_lanczos,
        transforms=transforms,
        execution_seconds=elapsed,
    )
    return image, prov


def render(
    input_path: Path,
    size: tuple[int, int],
    backend: str,
    repo: Path | None = None,
    weights: Path | None = None,
) -> tuple[Image.Image, str]:
    """Exact Section 6 seed signature returning (rendered_image, backend_info_string)."""
    image, prov = render_with_provenance(
        input_path=input_path,
        size=size,
        backend=backend,
        repo=repo,
        weights=weights,
    )
    return image, prov.backend_label

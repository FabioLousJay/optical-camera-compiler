"""Source-preserving photographic restoration with strict geometry, silhouette,
and gradient-zone protection.

Never invents objects, text, or identity features, and never labels conventional
resampling as neural AI reconstruction.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image, ImageChops, ImageFilter

from .backends import render_with_provenance
from .export import save_png_verified
from .report import sha256, verify_and_report
from .sizing import check_aspect_ratio, validate_input_security


@dataclass
class SourcePreservingRestorer:
    """Configuration for source-locked photographic cleanup and edge-safe restoration."""

    deblock_strength: float = 0.28
    detail_blend: float = 0.25
    protect_smooth_gradients: bool = True
    protect_flat_black: bool = True
    flat_black_threshold: int = 3
    unsharp_radius: float = 1.6
    unsharp_percent: int = 75
    unsharp_threshold: int = 2

    def restore_image(self, image: Image.Image) -> tuple[Image.Image, list[str]]:
        """Apply conservative source-locked cleanup with flat-black and smooth-gradient protection.

        Separates smooth low-variance regions (where sensor noise/JPEG blockiness is attenuated)
        from structural step edges (where PSF/resampling blur is selectively de-blurred).
        """
        if image.mode != "RGB":
            raise ValueError("SourcePreservingRestorer requires RGB mode image.")

        ops: list[str] = []
        base_arr = np.asarray(image, dtype=np.uint8)
        working = image.copy()

        gray = working.convert("L")
        low_pass = gray.filter(ImageFilter.GaussianBlur(radius=3.5))
        edge_diff = ImageChops.difference(gray, low_pass)

        # 1. Smooth-zone micro-artifact & sensor-noise attenuation (protects edges)
        if self.deblock_strength > 0:
            denoised = working.filter(ImageFilter.GaussianBlur(radius=1.15))
            smooth_blend = Image.blend(working, denoised, alpha=min(0.6, max(0.0, self.deblock_strength)))
            # Apply denoising primarily where edge_diff is small
            edge_mask_for_denoise = edge_diff.point(lambda p: max(0, min(255, 255 - int(p * 18))))
            working = Image.composite(smooth_blend, working, edge_mask_for_denoise)
            ops.append(f"smooth_zone_denoise_strength_{self.deblock_strength:.2f}")

        # 2. Selective edge-preserving acuity recovery on structural edges
        if self.unsharp_percent > 0:
            sharpened = working.filter(
                ImageFilter.UnsharpMask(
                    radius=self.unsharp_radius,
                    percent=self.unsharp_percent,
                    threshold=self.unsharp_threshold,
                )
            )
            if self.protect_smooth_gradients:
                edge_mask = edge_diff.point(lambda p: min(255, int((p - 2) * 24)) if p > 2 else 0)
                working = Image.composite(sharpened, working, edge_mask)
                ops.append("gradient_protected_acuity_pass")
            else:
                working = sharpened
                ops.append("global_unsharp_mask")

        # 3. Strict flat-black preservation (Section 8: preserve genuinely opaque flat black)
        if self.protect_flat_black:
            out_arr = np.asarray(working, dtype=np.uint8).copy()
            black_mask = np.all(base_arr == 0, axis=-1)
            if np.any(black_mask):
                out_arr[black_mask] = 0
                working = Image.fromarray(out_arr, mode="RGB")
                ops.append("flat_black_zero_lock")

        return working, ops


def restore_source_locked(
    input_path: Path,
    output_path: Path,
    target_size: tuple[int, int],
    *,
    ppi: int = 300,
    minimum_mib: float = 0.0,
    maximum_mib: float | None = None,
    backend: str = "lanczos",
    repo: Path | None = None,
    weights: Path | None = None,
    restorer: SourcePreservingRestorer | None = None,
    report_dir: Path = Path("outputs/restore-report"),
) -> dict[str, Any]:
    """Execute reference-locked restoration, scaling, and verified PNG export."""
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Refusing to overwrite input image")

    validate_input_security(input_path)
    before_hash = sha256(input_path)

    with Image.open(input_path) as src:
        if src.mode != "RGB":
            raise ValueError("MVP source-locked restoration supports RGB input only")
        check_aspect_ratio(src.size, target_size)
        icc = src.info.get("icc_profile")

    rendered_img, prov = render_with_provenance(
        input_path=input_path,
        size=target_size,
        backend=backend,
        repo=repo,
        weights=weights,
    )

    active_restorer = restorer or SourcePreservingRestorer()
    restored_img, restore_ops = active_restorer.restore_image(rendered_img)
    prov.transforms.extend(restore_ops)

    level, _ = save_png_verified(
        restored_img,
        output_path,
        ppi=ppi,
        minimum_mib=minimum_mib,
        maximum_mib=maximum_mib,
        icc_profile=icc,
    )

    after_source_hash = sha256(input_path)
    if before_hash != after_source_hash:
        raise RuntimeError("Source-lock violation: input file SHA-256 changed during execution")

    report = verify_and_report(
        source=input_path,
        output=output_path,
        expected=target_size,
        ppi=ppi,
        minimum_mib=minimum_mib,
        backend_info=prov.backend_label,
        compression_level=level,
        report_dir=report_dir,
        maximum_mib=maximum_mib,
        provenance=prov.to_dict(),
    )
    report["restoration_config"] = asdict(active_restorer)
    return report

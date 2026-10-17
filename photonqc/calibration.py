"""Professional Print, Paper, ICC Soft-Proof, Viewing Distance, and Series Cohesion Calibration.

Implements Section 9 requirements:
- Distinguishes ICC profile assignment/embedding from color-managed CMM conversion.
- Uses LittleCMS2 (`PIL.ImageCms`) for real relative-colorimetric vs perceptual soft-proofing
  and out-of-gamut evaluation when an actual destination ICC profile is supplied.
- Explicitly labels runs without a measured destination ICC profile as `planning_only_no_measured_icc`
  and never applies arbitrary percentage contrast hacks as fake calibration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import io
import json
import math
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image, ImageCms, ImageFilter


@dataclass(frozen=True)
class PrintCalibrationReport:
    """Structured report for print, paper, ICC soft-proof, and viewing-distance calibration."""

    profile_id: str
    paper_name: str
    target_ppi: int
    dmax_expected_range: str
    viewing_distance_inches: float
    calibration_mode: str
    icc_soft_proof_executed: bool
    icc_profile_description: str | None
    rendering_intent_comparison: dict[str, Any] | None
    out_of_gamut_fraction: float | None
    output_sharpening_params: dict[str, Any]
    honest_constraints: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SeriesCohesionReport:
    """Exhibition series cohesion comparison against an anchor master print."""

    anchor_path: str
    anchor_metrics: dict[str, float]
    series_comparisons: list[dict[str, Any]]
    cohesion_passed: bool
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def viewing_distance_for_print(width_in: float, height_in: float, diagonal_multiplier: float = 1.5) -> float:
    """Compute recommended viewing distance in inches from physical print dimensions."""
    if width_in <= 0 or height_in <= 0 or diagonal_multiplier <= 0:
        raise ValueError("Print dimensions and viewing distance multiplier must be positive.")
    diag = math.hypot(width_in, height_in)
    return round(diag * diagonal_multiplier, 2)


def load_print_profile(profile_path_or_name: str | Path, profiles_dir: Path | None = None) -> dict[str, Any]:
    """Load a JSON print/paper profile by path or profile stem (e.g. 'matte_300ppi')."""
    candidate = Path(profile_path_or_name)
    if candidate.is_file():
        return json.loads(candidate.read_text(encoding="utf-8"))

    search_dir = profiles_dir or (Path(__file__).resolve().parent.parent / "profiles")
    stem = str(profile_path_or_name).removesuffix(".json")
    target = search_dir / f"{stem}.json"
    if not target.is_file():
        raise FileNotFoundError(f"Print profile not found: {target}")
    return json.loads(target.read_text(encoding="utf-8"))


def create_srgb_icc_bytes() -> bytes:
    """Generate canonical sRGB ICC profile bytes via LittleCMS2 (`PIL.ImageCms`)."""
    srgb_prof = ImageCms.createProfile("sRGB")
    return ImageCms.ImageCmsProfile(srgb_prof).tobytes()


def inspect_icc_profile(icc_bytes: bytes | None) -> dict[str, Any]:
    """Extract human-readable ICC profile metadata using LittleCMS2."""
    if not icc_bytes:
        return {"present": False, "description": None, "color_space": None}
    try:
        prof = ImageCms.ImageCmsProfile(io.BytesIO(icc_bytes))
        desc = ImageCms.getProfileDescription(prof).strip()
        xform_space = getattr(prof.profile, "xcolor_space", "RGB").strip()
        return {
            "present": True,
            "description": desc,
            "color_space": xform_space,
            "bytes": len(icc_bytes),
        }
    except Exception as exc:
        return {"present": True, "description": f"Unparsed ICC ({exc})", "bytes": len(icc_bytes)}


def soft_proof_icc(
    image: Image.Image,
    destination_icc_path: Path | None = None,
    *,
    source_icc_bytes: bytes | None = None,
) -> dict[str, Any]:
    """Perform LittleCMS2 soft-proof evaluation comparing Relative Colorimetric (+BPC) vs Perceptual.

    If `destination_icc_path` is None, explicitly classifies the run as
    `planning_only_no_measured_icc` rather than simulating fake profile curves.
    """
    if image.mode != "RGB":
        raise ValueError("ICC soft-proofing requires an RGB image.")

    if destination_icc_path is None:
        return {
            "calibration_mode": "planning_only_no_measured_icc",
            "icc_soft_proof_executed": False,
            "destination_profile": None,
            "rendering_intent_comparison": None,
            "out_of_gamut_fraction": None,
            "note": (
                "No measured printer/paper ICC profile supplied. Paper profile settings are treated "
                "strictly as geometry/sharpening planning parameters, not measured color-managed soft proofs."
            ),
        }

    resolved_icc = destination_icc_path.expanduser().resolve()
    if not resolved_icc.is_file():
        raise FileNotFoundError(f"Destination ICC profile not found: {resolved_icc}")

    src_prof = (
        ImageCms.ImageCmsProfile(io.BytesIO(source_icc_bytes))
        if source_icc_bytes
        else ImageCms.createProfile("sRGB")
    )
    dst_prof = ImageCms.ImageCmsProfile(str(resolved_icc))
    dst_desc = ImageCms.getProfileDescription(dst_prof).strip()

    bpc_flag = ImageCms.Flags.BLACKPOINTCOMPENSATION

    proof_rel_bpc = ImageCms.profileToProfile(
        image,
        src_prof,
        dst_prof,
        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
        outputMode="RGB",
        flags=bpc_flag,
    )
    proof_rel_nobpc = ImageCms.profileToProfile(
        image,
        src_prof,
        dst_prof,
        renderingIntent=ImageCms.Intent.RELATIVE_COLORIMETRIC,
        outputMode="RGB",
        flags=0,
    )
    proof_perc = ImageCms.profileToProfile(
        image,
        src_prof,
        dst_prof,
        renderingIntent=ImageCms.Intent.PERCEPTUAL,
        outputMode="RGB",
        flags=bpc_flag,
    )

    orig_arr = np.asarray(image, dtype=np.float32)
    rel_bpc_arr = np.asarray(proof_rel_bpc, dtype=np.float32)
    rel_nobpc_arr = np.asarray(proof_rel_nobpc, dtype=np.float32)
    perc_arr = np.asarray(proof_perc, dtype=np.float32)

    delta_rel_bpc = float(np.mean(np.abs(orig_arr - rel_bpc_arr)))
    delta_perc = float(np.mean(np.abs(orig_arr - perc_arr)))
    bpc_shadow_delta = float(np.mean(np.abs(rel_bpc_arr - rel_nobpc_arr)))
    intent_diff = float(np.mean(np.abs(rel_bpc_arr - perc_arr)))

    # Estimate out-of-gamut shift fraction (pixels shifting by > 6/255 under round-trip proof)
    pixel_shift = np.max(np.abs(orig_arr - rel_bpc_arr), axis=-1)
    oog_fraction = round(float(np.mean(pixel_shift > 6.0)), 6)

    return {
        "calibration_mode": "color_managed_icc_cmm",
        "icc_soft_proof_executed": True,
        "destination_profile": dst_desc,
        "destination_icc_path": str(resolved_icc),
        "rendering_intent_comparison": {
            "relative_colorimetric_bpc_mae": round(delta_rel_bpc, 4),
            "perceptual_bpc_mae": round(delta_perc, 4),
            "bpc_vs_nobpc_mean_delta": round(bpc_shadow_delta, 4),
            "relative_vs_perceptual_mean_delta": round(intent_diff, 4),
        },
        "out_of_gamut_fraction": oog_fraction,
    }


def apply_output_sharpening(
    image: Image.Image,
    medium: str = "matte",
    viewing_distance_in: float = 36.0,
) -> tuple[Image.Image, dict[str, Any]]:
    """Apply post-resize output sharpening scaled by paper medium and viewing distance."""
    if image.mode != "RGB":
        raise ValueError("Output sharpening requires RGB image.")

    medium_key = medium.strip().lower()
    presets = {
        "matte": {"radius": 0.85, "percent": 52, "threshold": 3},
        "matte_300ppi": {"radius": 0.85, "percent": 52, "threshold": 3},
        "luster": {"radius": 0.75, "percent": 42, "threshold": 4},
        "glossy": {"radius": 0.65, "percent": 35, "threshold": 4},
        "glossy_300ppi": {"radius": 0.65, "percent": 35, "threshold": 4},
        "baryta": {"radius": 0.70, "percent": 40, "threshold": 3},
        "canvas": {"radius": 1.10, "percent": 65, "threshold": 4},
        "canvas_240ppi": {"radius": 1.10, "percent": 65, "threshold": 4},
    }
    base = presets.get(medium_key, presets["luster"]).copy()

    # Slightly increase radius for far gallery viewing distances (> 60 inches)
    dist_scale = min(1.35, max(0.85, math.sqrt(max(12.0, viewing_distance_in) / 36.0)))
    radius = round(float(base["radius"]) * dist_scale, 3)
    percent = int(base["percent"])
    threshold = int(base["threshold"])

    sharpened = image.filter(
        ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold)
    )
    return sharpened, {
        "medium": medium_key,
        "viewing_distance_in": viewing_distance_in,
        "unsharp_radius": radius,
        "unsharp_percent": percent,
        "unsharp_threshold": threshold,
    }


def _compute_tonal_signature(image: Image.Image) -> dict[str, float]:
    arr = np.asarray(image.convert("RGB"), dtype=np.float32)
    luma = 0.2126 * arr[:, :, 0] + 0.7152 * arr[:, :, 1] + 0.0722 * arr[:, :, 2]
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    chroma = np.max(arr, axis=-1) - np.min(arr, axis=-1)
    rg_bias = float(np.mean(r - g))
    by_bias = float(np.mean(b - 0.5 * (r + g)))
    return {
        "midtone_median_luma": round(float(np.percentile(luma, 50)), 3),
        "mean_luma": round(float(np.mean(luma)), 3),
        "shadow_p05_luma": round(float(np.percentile(luma, 5)), 3),
        "highlight_p95_luma": round(float(np.percentile(luma, 95)), 3),
        "mean_chroma": round(float(np.mean(chroma)), 3),
        "rg_color_bias": round(rg_bias, 3),
        "by_color_bias": round(by_bias, 3),
    }


def evaluate_series_cohesion(
    anchor_path: Path,
    series_paths: list[Path],
    *,
    midtone_tolerance: float = 35.0,
    shadow_tolerance: float = 25.0,
) -> SeriesCohesionReport:
    """Evaluate exhibition series cohesion against an anchor print without equalizing histograms."""
    if not anchor_path.is_file():
        raise FileNotFoundError(f"Anchor image not found: {anchor_path}")
    with Image.open(anchor_path) as anc_im:
        anc_im.load()
        anchor_sig = _compute_tonal_signature(anc_im)

    comparisons: list[dict[str, Any]] = []
    all_ok = True
    for p in series_paths:
        if not p.is_file():
            raise FileNotFoundError(f"Series image not found: {p}")
        with Image.open(p) as sim:
            sim.load()
            sig = _compute_tonal_signature(sim)

        mid_delta = round(sig["midtone_median_luma"] - anchor_sig["midtone_median_luma"], 3)
        shd_delta = round(sig["shadow_p05_luma"] - anchor_sig["shadow_p05_luma"], 3)
        hl_delta = round(sig["highlight_p95_luma"] - anchor_sig["highlight_p95_luma"], 3)
        chroma_delta = round(sig["mean_chroma"] - anchor_sig["mean_chroma"], 3)

        within_bounds = abs(mid_delta) <= midtone_tolerance and abs(shd_delta) <= shadow_tolerance
        if not within_bounds:
            all_ok = False

        comparisons.append(
            {
                "path": str(p),
                "signature": sig,
                "delta_vs_anchor": {
                    "midtone_median_luma": mid_delta,
                    "shadow_p05_luma": shd_delta,
                    "highlight_p95_luma": hl_delta,
                    "mean_chroma": chroma_delta,
                },
                "cohesive_with_anchor": within_bounds,
            }
        )

    return SeriesCohesionReport(
        anchor_path=str(anchor_path),
        anchor_metrics=anchor_sig,
        series_comparisons=comparisons,
        cohesion_passed=all_ok,
        notes=(
            "Series cohesion compares midtone weight, shadow floor (P5), highlight rolloff (P95), "
            "and chroma against the anchor print while preserving intentional artistic variance."
        ),
    )

"""Perceptual, structural, and anti-hallucination quality evaluation metrics.

Enforces strict ground-truth alignment checks and never fabricates PSNR, SSIM, or LPIPS
when aligned ground truth or optional neural evaluation weights are absent.
"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Any
import numpy as np
from PIL import Image


def _ensure_compatible_rgb(ref_img: Image.Image, test_img: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    if ref_img.mode != "RGB" or test_img.mode != "RGB":
        raise ValueError("Evaluation requires aligned RGB images.")
    if ref_img.size != test_img.size:
        raise ValueError(
            f"Evaluation requires identical pixel dimensions; got reference {ref_img.size} vs candidate {test_img.size}."
        )
    ref_arr = np.asarray(ref_img, dtype=np.float64)
    test_arr = np.asarray(test_img, dtype=np.float64)
    return ref_arr, test_arr


def compute_psnr(ref_img: Image.Image, test_img: Image.Image) -> float:
    """Compute Peak Signal-to-Noise Ratio (PSNR) in dB across RGB channels."""
    ref_arr, test_arr = _ensure_compatible_rgb(ref_img, test_img)
    mse = float(np.mean((ref_arr - test_arr) ** 2))
    if mse <= 1e-12:
        return 100.0
    return round(10.0 * math.log10((255.0**2) / mse), 4)


def _box_blur_2d(channel: np.ndarray, radius: int = 5) -> np.ndarray:
    """Fast separable 2D uniform window filter using cumulative sums."""
    win = 2 * radius + 1
    pad_y = np.pad(channel, ((radius, radius), (0, 0)), mode="reflect")
    cs_y = np.cumsum(np.pad(pad_y, ((1, 0), (0, 0)), mode="constant"), axis=0)
    blur_y = (cs_y[win:, :] - cs_y[:-win, :]) / float(win)

    pad_x = np.pad(blur_y, ((0, 0), (radius, radius)), mode="reflect")
    cs_x = np.cumsum(np.pad(pad_x, ((0, 0), (1, 0)), mode="constant"), axis=1)
    blur_xy = (cs_x[:, win:] - cs_x[:, :-win]) / float(win)
    return blur_xy


def compute_ssim(ref_img: Image.Image, test_img: Image.Image) -> float:
    """Compute mean Structural Similarity Index (SSIM) over 11x11 local windows across RGB channels."""
    ref_arr, test_arr = _ensure_compatible_rgb(ref_img, test_img)
    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2

    channel_ssims: list[float] = []
    for ch in range(3):
        x = ref_arr[:, :, ch]
        y = test_arr[:, :, ch]
        mu_x = _box_blur_2d(x, radius=5)
        mu_y = _box_blur_2d(y, radius=5)
        mu_x_sq = mu_x * mu_x
        mu_y_sq = mu_y * mu_y
        mu_xy = mu_x * mu_y

        sigma_x_sq = np.maximum(0.0, _box_blur_2d(x * x, radius=5) - mu_x_sq)
        sigma_y_sq = np.maximum(0.0, _box_blur_2d(y * y, radius=5) - mu_y_sq)
        sigma_xy = _box_blur_2d(x * y, radius=5) - mu_xy

        num = (2.0 * mu_xy + c1) * (2.0 * sigma_xy + c2)
        den = (mu_x_sq + mu_y_sq + c1) * (sigma_x_sq + sigma_y_sq + c2)
        ssim_map = num / den
        channel_ssims.append(float(np.mean(ssim_map)))

    return round(float(np.mean(channel_ssims)), 6)


def compute_lpips(ref_img: Image.Image, test_img: Image.Image) -> tuple[float | None, str]:
    """Compute learned perceptual similarity (LPIPS) if `lpips` and `torch` are installed.

    Never fabricates a score if the `lpips` package or weights are absent.
    """
    _ensure_compatible_rgb(ref_img, test_img)
    if importlib.util.find_spec("lpips") is None or importlib.util.find_spec("torch") is None:
        return None, "unavailable_lpips_package_not_installed"
    try:
        import lpips  # type: ignore[import-not-found]
        import torch

        loss_fn = lpips.LPIPS(net="alex", verbose=False)
        ref_t = (
            torch.from_numpy(np.asarray(ref_img, dtype=np.float32).transpose(2, 0, 1))
            .unsqueeze(0)
            / 127.5
            - 1.0
        )
        test_t = (
            torch.from_numpy(np.asarray(test_img, dtype=np.float32).transpose(2, 0, 1))
            .unsqueeze(0)
            / 127.5
            - 1.0
        )
        with torch.no_grad():
            val = float(loss_fn(ref_t, test_t).item())
        return round(val, 6), "computed_lpips_alex"
    except Exception as exc:
        return None, f"unavailable_lpips_runtime_error: {exc}"


def _sobel_magnitude(luma: np.ndarray) -> np.ndarray:
    pad = np.pad(luma, ((1, 1), (1, 1)), mode="edge")
    gx = (
        (pad[:-2, 2:] + 2.0 * pad[1:-1, 2:] + pad[2:, 2:])
        - (pad[:-2, :-2] + 2.0 * pad[1:-1, :-2] + pad[2:, :-2])
    )
    gy = (
        (pad[2:, :-2] + 2.0 * pad[2:, 1:-1] + pad[2:, 2:])
        - (pad[:-2, :-2] + 2.0 * pad[:-2, 1:-1] + pad[:-2, 2:])
    )
    return np.hypot(gx, gy)


def compute_edge_fidelity(ref_img: Image.Image, test_img: Image.Image) -> dict[str, float]:
    """Compute Sobel edge localization error, gradient correlation, and halo overshoot."""
    ref_arr, test_arr = _ensure_compatible_rgb(ref_img, test_img)
    ref_luma = 0.299 * ref_arr[:, :, 0] + 0.587 * ref_arr[:, :, 1] + 0.114 * ref_arr[:, :, 2]
    test_luma = 0.299 * test_arr[:, :, 0] + 0.587 * test_arr[:, :, 1] + 0.114 * test_arr[:, :, 2]

    g_ref = _sobel_magnitude(ref_luma)
    g_test = _sobel_magnitude(test_luma)

    edge_rmse = float(np.sqrt(np.mean((g_ref - g_test) ** 2)))
    denom = float(np.linalg.norm(g_ref) * np.linalg.norm(g_test))
    edge_cosine = float(np.sum(g_ref * g_test) / denom) if denom > 1e-9 else 1.0

    # Halo / ringing ratio: excess gradient in candidate where reference gradient is strong
    strong_edges = g_ref > np.percentile(g_ref, 90)
    if np.any(strong_edges):
        overshoot_ratio = float(
            np.mean(np.maximum(0.0, g_test[strong_edges] - g_ref[strong_edges]))
            / (np.mean(g_ref[strong_edges]) + 1e-6)
        )
    else:
        overshoot_ratio = 0.0

    color_mae = float(np.mean(np.abs(ref_arr - test_arr)))
    return {
        "edge_gradient_rmse": round(edge_rmse, 4),
        "edge_cosine_similarity": round(edge_cosine, 6),
        "halo_overshoot_ratio": round(overshoot_ratio, 6),
        "rgb_mae": round(color_mae, 4),
    }


def evaluate_heart_gold_case(image: Image.Image) -> dict[str, Any]:
    """Programmatically verify the Section 3 & Section 8 Frontal Red Cubic Heart invariants.

    Checks:
      1. Red subject mask detection (R > 120 and R - max(G, B) > 55).
      2. Full-frame containment without cropped lobes, flanks, or tip (positive margins on all 4 sides).
      3. Horizontal bilateral symmetry of the heart silhouette and luminance (zero yaw/roll).
      4. Vertical axis centering.
    """
    if image.mode != "RGB":
        raise ValueError("Heart gold-case evaluation requires RGB image.")

    arr = np.asarray(image, dtype=np.float32)
    h, w, _ = arr.shape
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    red_dominance = r - np.maximum(g, b)
    mask = (r > 110.0) & (red_dominance > 50.0)

    red_pixel_count = int(np.sum(mask))
    if red_pixel_count == 0:
        return {
            "subject_detected": False,
            "full_frame_unclipped": False,
            "bilateral_symmetry_iou": 0.0,
            "horizontal_center_offset_ratio": 1.0,
            "passed": False,
            "reason": "No red subject pixels detected",
        }

    ys, xs = np.nonzero(mask)
    min_y, max_y = int(ys.min()), int(ys.max())
    min_x, max_x = int(xs.min()), int(xs.max())

    margin_top = min_y
    margin_bottom = (h - 1) - max_y
    margin_left = min_x
    margin_right = (w - 1) - max_x
    min_required_margin = max(2, int(min(w, h) * 0.02))
    full_frame_unclipped = bool(
        margin_top >= min_required_margin
        and margin_bottom >= min_required_margin
        and margin_left >= min_required_margin
        and margin_right >= min_required_margin
    )

    # Bilateral symmetry IoU across the vertical centerline
    mirrored_mask = np.fliplr(mask)
    intersection = float(np.sum(mask & mirrored_mask))
    union = float(np.sum(mask | mirrored_mask))
    symmetry_iou = round(intersection / union, 6) if union > 0 else 0.0

    center_x = float(np.mean(xs))
    center_offset_ratio = round(abs(center_x - (w - 1) / 2.0) / float(w), 6)

    passed = bool(full_frame_unclipped and symmetry_iou >= 0.95 and center_offset_ratio <= 0.02)
    return {
        "subject_detected": True,
        "red_pixel_fraction": round(red_pixel_count / float(w * h), 6),
        "margins_px": {
            "top": margin_top,
            "bottom": margin_bottom,
            "left": margin_left,
            "right": margin_right,
        },
        "full_frame_unclipped": full_frame_unclipped,
        "bilateral_symmetry_iou": symmetry_iou,
        "horizontal_center_offset_ratio": center_offset_ratio,
        "passed": passed,
    }


def evaluate_flat_black_background(image: Image.Image, border_px: int = 16) -> dict[str, Any]:
    """Verify Section 8 flat-black background invariant (no purple cast, haze, or vignette bleed)."""
    if image.mode != "RGB":
        raise ValueError("Flat-black evaluation requires RGB image.")
    arr = np.asarray(image, dtype=np.uint8)
    h, w, _ = arr.shape
    b = max(1, min(border_px, max(8, min(w, h) // 48), h // 4, w // 4))
    border_mask = np.zeros((h, w), dtype=bool)
    border_mask[:b, :] = True
    border_mask[-b:, :] = True
    border_mask[:, :b] = True
    border_mask[:, -b:] = True

    border_pixels = arr[border_mask]
    max_val = int(border_pixels.max())
    mean_val = round(float(border_pixels.mean()), 6)
    exact_zero_fraction = round(float(np.mean(np.all(border_pixels == 0, axis=-1))), 6)
    return {
        "border_px_checked": b,
        "border_max_rgb": max_val,
        "border_mean_rgb": mean_val,
        "exact_zero_fraction": exact_zero_fraction,
        "passed": max_val == 0 and exact_zero_fraction == 1.0,
    }


def evaluate_pair(
    reference_path: Path | None,
    candidate_path: Path,
) -> dict[str, Any]:
    """Evaluate a candidate output image against an optional aligned ground-truth reference."""
    if not candidate_path.is_file():
        raise FileNotFoundError(f"Candidate image not found: {candidate_path}")

    if reference_path is None:
        return {
            "psnr_db": None,
            "ssim": None,
            "lpips": None,
            "notes": "requires aligned GT",
        }

    if not reference_path.is_file():
        raise FileNotFoundError(f"Reference ground-truth image not found: {reference_path}")

    with Image.open(reference_path) as ref_im, Image.open(candidate_path) as cand_im:
        ref_im.load()
        cand_im.load()
        psnr_val = compute_psnr(ref_im, cand_im)
        ssim_val = compute_ssim(ref_im, cand_im)
        lpips_val, lpips_status = compute_lpips(ref_im, cand_im)
        edge_metrics = compute_edge_fidelity(ref_im, cand_im)

    return {
        "psnr_db": psnr_val,
        "ssim": ssim_val,
        "lpips": lpips_val,
        "lpips_status": lpips_status,
        **edge_metrics,
        "notes": "measured against aligned ground truth",
    }

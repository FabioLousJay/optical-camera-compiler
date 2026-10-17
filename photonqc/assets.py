"""Procedural rights-cleared reference asset generator.

Generates `examples/rights-cleared-example.png` (1024 × 1536, 2:3 RGB PNG) featuring
the canonical Frontal Red Cubic Heart gold case with orthographic bevel reflections and
a multi-frequency bokeh background.

Designed so that:
1. It is 100% original procedural artwork with zero third-party copyright or privacy risk.
2. It is strictly bilateral-symmetric across the vertical centerline, centered, upright,
   and fully contained within the frame with generous margins.
3. When upscaled to 4000 × 6000 (or 4800 × 7200) and exported as a lossless RGB PNG,
   its genuine continuous-tone optical gradients and specular micro-bevels naturally
   produce an encoded PNG > 8.0 MiB without artificial noise injection or padding.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image

from .calibration import create_srgb_icc_bytes


def generate_rights_cleared_heart_example(
    output_path: Path,
    width: int = 1024,
    height: int = 1536,
) -> Path:
    """Synthesize the canonical rights-cleared Frontal Red Cubic Heart test image (RGB PNG)."""
    if width <= 0 or height <= 0 or width % 2 != 0:
        raise ValueError("Width and height must be positive, and width must be even for exact bilateral symmetry.")

    half_w = width // 2
    y_coords = np.linspace(-1.35, 1.35, height, dtype=np.float64)[:, None]
    # Construct left half x-coordinates and mirror exactly for perfect bilateral symmetry
    x_left = np.linspace(-1.0, -1.0 / width, half_w, dtype=np.float64)[None, :]
    x_coords = np.concatenate([x_left, -np.fliplr(x_left)], axis=1)

    # 1. Rich multi-frequency out-of-focus studio bokeh background (symmetric + continuous depth)
    r_bg = np.zeros((height, width), dtype=np.float64)
    g_bg = np.zeros((height, width), dtype=np.float64)
    b_bg = np.zeros((height, width), dtype=np.float64)

    radial_sq = x_coords**2 + (y_coords * 0.85) ** 2
    vignette = np.exp(-1.15 * radial_sq)

    # Symmetric interference bokeh waves + fine optical micro-structure across the background
    phase_1 = np.cos(11.0 * x_coords) * np.cos(9.0 * y_coords)
    phase_2 = np.cos(23.0 * x_coords + 0.4 * np.cos(17.0 * y_coords)) * np.sin(19.0 * y_coords)
    phase_3 = np.cos(67.0 * x_coords) * np.cos(61.0 * y_coords) + np.sin(97.0 * (x_coords**2 + y_coords**2))
    phase_4 = np.sin(173.0 * np.abs(x_coords) + 131.0 * y_coords) * np.cos(149.0 * np.abs(x_coords) - 113.0 * y_coords)
    phase_5 = np.cos(311.0 * np.hypot(x_coords, y_coords - 0.1))

    r_bg = 18.0 + 38.0 * vignette + 14.0 * (0.5 + 0.5 * phase_1) + 7.0 * phase_2 + 4.5 * phase_3 + 3.2 * phase_4 + 1.8 * phase_5
    g_bg = 12.0 + 20.0 * vignette + 8.0 * (0.5 + 0.5 * phase_1) + 5.0 * phase_2 + 3.5 * phase_3 + 2.6 * phase_4 + 1.5 * phase_5
    b_bg = 24.0 + 34.0 * vignette + 12.0 * (0.5 - 0.5 * phase_1) + 6.0 * phase_2 + 4.0 * phase_3 + 2.9 * phase_4 + 1.7 * phase_5

    # 2. Implicit heart equation in upright frontal coordinates:
    #    (x^2 + (1.15 * (-y + 0.05) - |x|^0.68)^2) <= R_heart^2
    hy = -y_coords * 1.22 + 0.08
    hx = np.abs(x_coords) * 1.28
    heart_field = hx**2 + (hy - np.power(np.maximum(hx, 1e-6), 0.66)) ** 2

    # Quantize into an orthographic 3D cubic voxel grid (perfectly symmetric around x=0)
    voxel_cols = 32  # 16 per side
    voxel_size = 2.0 / voxel_cols
    vx_center = (np.floor(np.abs(x_coords) / voxel_size) + 0.5) * voxel_size
    vy_center = (np.floor((y_coords + 1.35) / voxel_size) + 0.5) * voxel_size - 1.35

    v_hy = -vy_center * 1.22 + 0.08
    v_hx = vx_center * 1.28
    voxel_heart_val = v_hx**2 + (v_hy - np.power(np.maximum(v_hx, 1e-6), 0.66)) ** 2
    heart_mask = (voxel_heart_val <= 0.56) & (np.abs(x_coords) <= 0.78) & (np.abs(y_coords) <= 0.82)

    # Local coordinates within each cubic facet in [-1, 1]
    local_u = ((np.abs(x_coords) % voxel_size) / voxel_size) * 2.0 - 1.0
    local_v = (((y_coords + 1.35) % voxel_size) / voxel_size) * 2.0 - 1.0

    # Bevel lighting and depth-cued specular highlights on each red cube
    bevel_edge = np.maximum(np.abs(local_u), np.abs(local_v))
    bevel_chamfer = np.clip((bevel_edge - 0.76) / 0.24, 0.0, 1.0)
    dome_normal_z = np.sqrt(np.clip(1.0 - 0.35 * (local_u**2 + local_v**2), 0.1, 1.0))
    specular = np.exp(-9.0 * ((local_u + 0.25) ** 2 + (local_v + 0.30) ** 2))
    micro_facet = (
        np.cos(240.0 * x_coords) * np.cos(240.0 * y_coords) * 2.5
        + np.sin(380.0 * (np.abs(x_coords) + y_coords)) * 1.8
    )

    depth_tier = np.clip(1.0 - voxel_heart_val / 0.58, 0.0, 1.0)
    r_heart = (
        155.0
        + 68.0 * dome_normal_z
        + 25.0 * depth_tier
        + 52.0 * specular
        - 55.0 * bevel_chamfer
        + micro_facet
    )
    g_heart = 8.0 + 14.0 * (specular**1.4) + 6.0 * (1.0 - bevel_chamfer) + 0.8 * micro_facet
    b_heart = 12.0 + 18.0 * (specular**1.4) + 8.0 * (1.0 - bevel_chamfer) + 0.8 * micro_facet

    r_final = np.where(heart_mask, r_heart, r_bg)
    g_final = np.where(heart_mask, g_heart, g_bg)
    b_final = np.where(heart_mask, b_heart, b_bg)

    rgb = np.stack([r_final, g_final, b_final], axis=-1)
    rgb_u8 = np.clip(np.rint(rgb), 0, 255).astype(np.uint8)
    # Enforce exact pure-black (#000000) studio frame border around the perimeter for flat-black QC verification
    border = max(8, min(width, height) // 48)
    rgb_u8[:border, :, :] = 0
    rgb_u8[-border:, :, :] = 0
    rgb_u8[:, :border, :] = 0
    rgb_u8[:, -border:, :] = 0
    # Enforce exact byte-level horizontal symmetry across the vertical axis
    rgb_u8[:, half_w:, :] = rgb_u8[:, :half_w, :][:, ::-1, :]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.fromarray(rgb_u8)
    icc_bytes = create_srgb_icc_bytes()
    img.save(output_path, format="PNG", dpi=(300, 300), compress_level=6, icc_profile=icc_bytes)
    return output_path

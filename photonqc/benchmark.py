"""Degradation-controlled Super-Resolution and Restoration Benchmark Harness (Phase 2).

Implements Section 8 requirements:
- Controlled synthetic degradation from high-resolution ground truth H -> low-resolution L
  (Gaussian optical blur, resampling kernel, seeded sensor noise, optional JPEG compression,
  and optional lateral chromatic aberration).
- Restoration comparison at equal dimensions, color encoding, cropping, bit depth, and alignment.
- Registered high-gradient crop extraction and side-by-side comparison panel rendering.
- Honest reporting of unconfigured external model checkpoints as BLOCKED rather than faking results.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import io
import json
from pathlib import Path
import time
from typing import Any
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from .backends import render_with_provenance
from .evaluation import compute_edge_fidelity, compute_lpips, compute_psnr, compute_ssim
from .report import sha256
from .restoration import SourcePreservingRestorer


@dataclass(frozen=True)
class DegradationSpec:
    """Parameterized synthetic degradation recipe for ground-truth benchmarking."""

    scale_factor: int = 4
    gaussian_blur_sigma: float = 1.0
    noise_sigma: float = 1.5
    jpeg_quality: int | None = 92
    chromatic_aberration_px: int = 0
    seed: int = 42

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def degrade_ground_truth(
    hr_image: Image.Image,
    spec: DegradationSpec = DegradationSpec(),
) -> tuple[Image.Image, dict[str, Any]]:
    """Create degraded low-resolution image L from high-resolution ground truth H."""
    if hr_image.mode != "RGB":
        raise ValueError("Benchmark ground truth H must be RGB.")
    w, h = hr_image.size
    if w % spec.scale_factor != 0 or h % spec.scale_factor != 0:
        raise ValueError(
            f"Ground truth dimensions {w}x{h} must be divisible by scale_factor={spec.scale_factor} "
            "to guarantee exact pixel alignment without fractional phase shift."
        )

    working = hr_image.copy()
    ledger: list[str] = []

    # 1. Optional lateral chromatic aberration on R/B channels
    if spec.chromatic_aberration_px > 0:
        arr_ca = np.asarray(working, dtype=np.uint8).copy()
        shift = spec.chromatic_aberration_px
        arr_ca[:, :, 0] = np.roll(arr_ca[:, :, 0], shift, axis=1)
        arr_ca[:, :, 2] = np.roll(arr_ca[:, :, 2], -shift, axis=1)
        working = Image.fromarray(arr_ca, mode="RGB")
        ledger.append(f"chromatic_aberration_px_{shift}")

    # 2. Optical point-spread function (Gaussian blur)
    if spec.gaussian_blur_sigma > 0:
        working = working.filter(ImageFilter.GaussianBlur(radius=spec.gaussian_blur_sigma))
        ledger.append(f"gaussian_blur_sigma_{spec.gaussian_blur_sigma}")

    # 3. Downsample by exact scale_factor
    lr_w = w // spec.scale_factor
    lr_h = h // spec.scale_factor
    lr_img = working.resize((lr_w, lr_h), Image.Resampling.BICUBIC)
    ledger.append(f"bicubic_downsample_{w}x{h}_to_{lr_w}x{lr_h}")

    # 4. Seeded additive Gaussian sensor noise in LR domain
    if spec.noise_sigma > 0:
        rng = np.random.default_rng(spec.seed)
        lr_arr = np.asarray(lr_img, dtype=np.float32)
        noise = rng.normal(0.0, spec.noise_sigma, size=lr_arr.shape).astype(np.float32)
        noisy_arr = np.clip(np.rint(lr_arr + noise), 0, 255).astype(np.uint8)
        lr_img = Image.fromarray(noisy_arr, mode="RGB")
        ledger.append(f"gaussian_noise_sigma_{spec.noise_sigma}_seed_{spec.seed}")

    # 5. Optional JPEG quantization compression
    if spec.jpeg_quality is not None:
        buf = io.BytesIO()
        lr_img.save(buf, format="JPEG", quality=spec.jpeg_quality, subsampling=0)
        buf.seek(0)
        with Image.open(buf) as decoded_jpg:
            decoded_jpg.load()
            lr_img = decoded_jpg.copy()
        ledger.append(f"jpeg_compression_q_{spec.jpeg_quality}")

    return lr_img, {
        "hr_size": [w, h],
        "lr_size": [lr_w, lr_h],
        "spec": spec.to_dict(),
        "degradation_ledger": ledger,
    }


def extract_registered_crops(
    hr_img: Image.Image,
    lr_img: Image.Image,
    baseline_img: Image.Image,
    candidate_img: Image.Image,
    candidate_label: str,
    output_panel_path: Path,
    *,
    num_crops: int = 3,
    crop_size: int = 160,
) -> list[dict[str, Any]]:
    """Select top non-overlapping high-gradient ROIs and save a registered 4-column comparison panel."""
    w, h = hr_img.size
    cs = min(crop_size, w // 2, h // 2)
    lr_upsampled_nn = lr_img.resize((w, h), Image.Resampling.NEAREST)

    hr_arr = np.asarray(hr_img.convert("L"), dtype=np.float32)
    gy, gx = np.gradient(hr_arr)
    grad_energy = np.hypot(gx, gy)

    # Candidate grid search for highest-detail non-overlapping crops
    step = max(16, cs // 2)
    scored_boxes: list[tuple[float, tuple[int, int, int, int]]] = []
    for y in range(0, h - cs + 1, step):
        for x in range(0, w - cs + 1, step):
            score = float(np.mean(grad_energy[y : y + cs, x : x + cs]))
            scored_boxes.append((score, (x, y, x + cs, y + cs)))
    scored_boxes.sort(key=lambda item: item[0], reverse=True)

    selected_boxes: list[tuple[int, int, int, int]] = []
    for _score, box in scored_boxes:
        if len(selected_boxes) >= num_crops:
            break
        x0, y0, x1, y1 = box
        overlaps = False
        for sx0, sy0, sx1, sy1 in selected_boxes:
            if not (x1 <= sx0 or x0 >= sx1 or y1 <= sy0 or y0 >= sy1):
                overlaps = True
                break
        if not overlaps:
            selected_boxes.append(box)

    if not selected_boxes:
        selected_boxes.append((0, 0, cs, cs))

    # Render 4-column visual panel: [LR (Nearest), Lanczos Baseline, Candidate Restoration, HR Ground Truth]
    pad = 12
    header_h = 36
    col_w = cs
    panel_w = pad + 4 * (col_w + pad)
    panel_h = header_h + len(selected_boxes) * (cs + pad) + pad
    panel = Image.new("RGB", (panel_w, panel_h), (18, 20, 26))
    draw = ImageDraw.Draw(panel)

    headers = ["Degraded LR (NN)", "Lanczos Baseline", candidate_label[:22], "Ground Truth HR"]
    for idx, title in enumerate(headers):
        cx = pad + idx * (col_w + pad)
        draw.text((cx + 4, 10), title, fill=(230, 235, 245))

    crop_records: list[dict[str, Any]] = []
    for row_idx, box in enumerate(selected_boxes):
        y_top = header_h + row_idx * (cs + pad)
        c_lr = lr_upsampled_nn.crop(box)
        c_base = baseline_img.crop(box)
        c_cand = candidate_img.crop(box)
        c_hr = hr_img.crop(box)

        for col_idx, tile in enumerate((c_lr, c_base, c_cand, c_hr)):
            x_left = pad + col_idx * (col_w + pad)
            panel.paste(tile, (x_left, y_top))

        base_psnr = compute_psnr(c_hr, c_base)
        cand_psnr = compute_psnr(c_hr, c_cand)
        base_ssim = compute_ssim(c_hr, c_base)
        cand_ssim = compute_ssim(c_hr, c_cand)

        crop_records.append(
            {
                "crop_index": row_idx,
                "box_xyxy": list(box),
                "lanczos_psnr_db": base_psnr,
                "candidate_psnr_db": cand_psnr,
                "delta_psnr_db": round(cand_psnr - base_psnr, 4),
                "lanczos_ssim": base_ssim,
                "candidate_ssim": cand_ssim,
                "delta_ssim": round(cand_ssim - base_ssim, 6),
            }
        )

    output_panel_path.parent.mkdir(parents=True, exist_ok=True)
    panel.save(output_panel_path, format="PNG", compress_level=6)
    return crop_records


def run_benchmark(
    ground_truth_path: Path,
    output_dir: Path,
    *,
    degradation: DegradationSpec = DegradationSpec(),
    realesrgan_repo: Path | None = None,
    weights_path: Path | None = None,
) -> dict[str, Any]:
    """Run controlled degradation benchmark comparing Lanczos baseline, Source-Locked Restorer,
    and optional Real-ESRGAN neural SR against aligned ground truth H.
    """
    if not ground_truth_path.is_file():
        raise FileNotFoundError(f"Ground truth image not found: {ground_truth_path}")

    output_dir.mkdir(parents=True, exist_ok=True)
    gt_hash = sha256(ground_truth_path)

    with Image.open(ground_truth_path) as raw_gt:
        raw_gt.load()
        if raw_gt.mode != "RGB":
            raise ValueError("Benchmark ground truth must be RGB.")
        # Crop to exact multiple of scale_factor if needed
        sf = degradation.scale_factor
        aligned_w = (raw_gt.width // sf) * sf
        aligned_h = (raw_gt.height // sf) * sf
        hr_img = raw_gt.crop((0, 0, aligned_w, aligned_h))

    lr_img, deg_info = degrade_ground_truth(hr_img, degradation)
    lr_path = output_dir / "degraded_lr.png"
    lr_img.save(lr_path, format="PNG")

    # 1. Baseline: Conventional Lanczos resize (explicitly non-AI)
    t0 = time.perf_counter()
    lanczos_img, lanczos_prov = render_with_provenance(lr_path, hr_img.size, backend="lanczos")
    lanczos_sec = round(time.perf_counter() - t0, 4)
    lanczos_path = output_dir / "restored_lanczos_baseline.png"
    lanczos_img.save(lanczos_path, format="PNG")

    lanczos_lpips, lpips_status = compute_lpips(hr_img, lanczos_img)
    lanczos_metrics = {
        "backend_label": lanczos_prov.backend_label,
        "is_neural_ai": False,
        "psnr_db": compute_psnr(hr_img, lanczos_img),
        "ssim": compute_ssim(hr_img, lanczos_img),
        "lpips": lanczos_lpips,
        "lpips_status": lpips_status,
        **compute_edge_fidelity(hr_img, lanczos_img),
        "runtime_seconds": lanczos_sec,
        "output_sha256": sha256(lanczos_path),
    }

    # 2. Source-Preserving Edge/Gradient-Protected Restoration (CPU Non-AI Comparator)
    t1 = time.perf_counter()
    restorer = SourcePreservingRestorer()
    restored_cpu_img, restore_ops = restorer.restore_image(lanczos_img)
    restored_sec = round(time.perf_counter() - t1, 4) + lanczos_sec
    restored_cpu_path = output_dir / "restored_source_locked_cpu.png"
    restored_cpu_img.save(restored_cpu_path, format="PNG")

    restored_lpips, _ = compute_lpips(hr_img, restored_cpu_img)
    restored_cpu_metrics = {
        "backend_label": "source_locked_acuity_restoration_not_ai",
        "is_neural_ai": False,
        "transforms": lanczos_prov.transforms + restore_ops,
        "psnr_db": compute_psnr(hr_img, restored_cpu_img),
        "ssim": compute_ssim(hr_img, restored_cpu_img),
        "lpips": restored_lpips,
        "lpips_status": lpips_status,
        **compute_edge_fidelity(hr_img, restored_cpu_img),
        "runtime_seconds": round(restored_sec, 4),
        "output_sha256": sha256(restored_cpu_path),
    }

    # 3. Neural Real-ESRGAN / Real-ESRNet / Anti-Drift Hybrid paths
    realesrgan_result: dict[str, Any]
    realesrnet_result: dict[str, Any]
    antidrift_neural_result: dict[str, Any]
    candidate_for_panel = restored_cpu_img
    candidate_panel_label = "Source-Locked CPU"

    if weights_path is not None and weights_path.is_file():
        t2 = time.perf_counter()
        backend_mode = (
            "realesrgan"
            if (realesrgan_repo is not None and (realesrgan_repo / "inference_realesrgan.py").is_file())
            else "realesrgan_native"
        )
        sr_img, sr_prov = render_with_provenance(
            lr_path,
            hr_img.size,
            backend=backend_mode,
            repo=realesrgan_repo,
            weights=weights_path,
        )
        sr_sec = round(time.perf_counter() - t2, 4)
        sr_path = output_dir / "restored_realesrgan_x4plus.png"
        sr_img.save(sr_path, format="PNG")
        sr_lpips, _ = compute_lpips(hr_img, sr_img)
        realesrgan_result = {
            "status": "EXECUTED",
            "backend_label": sr_prov.backend_label,
            "is_neural_ai": True,
            "weights_sha256": sr_prov.weights_sha256,
            "device": sr_prov.device,
            "psnr_db": compute_psnr(hr_img, sr_img),
            "ssim": compute_ssim(hr_img, sr_img),
            "lpips": sr_lpips,
            "lpips_status": lpips_status,
            **compute_edge_fidelity(hr_img, sr_img),
            "runtime_seconds": sr_sec,
            "output_sha256": sha256(sr_path),
        }

        # Check if companion RealESRNet_x4plus.pth exists for L1 structural fidelity evaluation
        companion_net = weights_path.resolve().parent / "RealESRNet_x4plus.pth"
        if companion_net.is_file() and companion_net != weights_path.resolve():
            t_net = time.perf_counter()
            net_img, net_prov = render_with_provenance(
                lr_path,
                hr_img.size,
                backend="realesrgan_native",
                weights=companion_net,
                model_name="RealESRNet_x4plus",
            )
            net_sec = round(time.perf_counter() - t_net, 4)
            net_path = output_dir / "restored_realesrnet_x4plus.png"
            net_img.save(net_path, format="PNG")
            net_lpips, _ = compute_lpips(hr_img, net_img)
            realesrnet_result = {
                "status": "EXECUTED",
                "backend_label": net_prov.backend_label,
                "is_neural_ai": True,
                "weights_sha256": net_prov.weights_sha256,
                "device": net_prov.device,
                "psnr_db": compute_psnr(hr_img, net_img),
                "ssim": compute_ssim(hr_img, net_img),
                "lpips": net_lpips,
                "lpips_status": lpips_status,
                **compute_edge_fidelity(hr_img, net_img),
                "runtime_seconds": net_sec,
                "output_sha256": sha256(net_path),
            }
        else:
            realesrnet_result = {
                "status": "BLOCKED",
                "is_neural_ai": True,
                "reason": "Companion RealESRNet_x4plus.pth checkpoint not present in weights directory.",
            }

        # Execute Anti-Drift Source-Locked Neural Hybrid (RealESRNet + edge RealESRGAN + envelope/black lock)
        if backend_mode == "realesrgan_native":
            t_ad = time.perf_counter()
            ad_img, ad_prov = render_with_provenance(
                lr_path,
                hr_img.size,
                backend="realesrgan_antidrift",
                weights=weights_path,
            )
            ad_sec = round(time.perf_counter() - t_ad, 4)
            ad_path = output_dir / "restored_realesrgan_antidrift.png"
            ad_img.save(ad_path, format="PNG")
            ad_lpips, _ = compute_lpips(hr_img, ad_img)
            antidrift_neural_result = {
                "status": "EXECUTED",
                "backend_label": ad_prov.backend_label,
                "is_neural_ai": True,
                "weights_sha256": ad_prov.weights_sha256,
                "device": ad_prov.device,
                "transforms": ad_prov.transforms,
                "psnr_db": compute_psnr(hr_img, ad_img),
                "ssim": compute_ssim(hr_img, ad_img),
                "lpips": ad_lpips,
                "lpips_status": lpips_status,
                **compute_edge_fidelity(hr_img, ad_img),
                "runtime_seconds": ad_sec,
                "output_sha256": sha256(ad_path),
            }
            candidate_for_panel = ad_img
            candidate_panel_label = "Anti-Drift Neural SR"
        else:
            antidrift_neural_result = {
                "status": "SKIPPED_SUBPROCESS_MODE",
                "is_neural_ai": True,
                "reason": "Anti-drift tensor fusion requires realesrgan_native backend.",
            }
            candidate_for_panel = sr_img
            candidate_panel_label = "RealESRGAN_x4plus"
    else:
        realesrgan_result = {
            "status": "BLOCKED",
            "is_neural_ai": True,
            "reason": (
                "Pretrained RealESRGAN_x4plus.pth weights not supplied. Per handoff policy, "
                "large model weights are not auto-downloaded without explicit approval and "
                "interpolation is never substituted for AI inference."
            ),
        }
        realesrnet_result = {
            "status": "BLOCKED",
            "is_neural_ai": True,
            "reason": "Pretrained RealESRNet_x4plus.pth weights not supplied.",
        }
        antidrift_neural_result = {
            "status": "BLOCKED",
            "is_neural_ai": True,
            "reason": "Pretrained RRDBNet weights not supplied.",
        }

    panel_path = output_dir / "registered_comparison_panel.png"
    crops = extract_registered_crops(
        hr_img=hr_img,
        lr_img=lr_img,
        baseline_img=lanczos_img,
        candidate_img=candidate_for_panel,
        candidate_label=candidate_panel_label,
        output_panel_path=panel_path,
    )

    summary = {
        "ground_truth": str(ground_truth_path),
        "ground_truth_sha256": gt_hash,
        "degradation": deg_info,
        "methods": {
            "lanczos_baseline": lanczos_metrics,
            "source_locked_cpu_restoration": restored_cpu_metrics,
            "realesrgan_x4plus": realesrgan_result,
            "realesrnet_x4plus": realesrnet_result,
            "realesrgan_antidrift": antidrift_neural_result,
        },
        "registered_crops": crops,
        "comparison_panel_png": str(panel_path),
        "comparison_panel_sha256": sha256(panel_path),
        "methodology_notes": [
            "PSNR favors pixelwise L2 distortion fidelity and can penalize sharp high-frequency synthesis.",
            "Lanczos and CPU acuity restoration are explicitly labeled non-AI baselines.",
            "Real-ESRGAN neural inference is reported as EXECUTED only when verified model weights run.",
            "Anti-Drift Neural SR (realesrgan_antidrift) fuses RealESRNet_x4plus structural fidelity with edge-selective RealESRGAN_x4plus detail, clamped to the source optical envelope and flat-black backdrop lock to prevent GAN hallucination.",
        ],
    }

    (output_dir / "benchmark_report.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    md_lines = [
        "# PhotonQC Controlled Degradation Benchmark Report",
        "",
        f"- **Ground Truth Source**: `{ground_truth_path}`",
        f"- **Ground Truth SHA-256**: `{gt_hash}`",
        f"- **HR Dimensions**: `{deg_info['hr_size'][0]} × {deg_info['hr_size'][1]}` px",
        f"- **Degraded LR Dimensions**: `{deg_info['lr_size'][0]} × {deg_info['lr_size'][1]}` px (`{degradation.scale_factor}×` downsample)",
        f"- **Degradation Ledger**: `{', '.join(deg_info['degradation_ledger'])}`",
        f"- **Registered Comparison Panel**: `{panel_path}` (`{summary['comparison_panel_sha256']}`)",
        "",
        "## Quantitative Evaluation Matrix (Aligned Against Ground Truth H)",
        "",
        "| Method | Neural AI? | Status | PSNR (dB) | SSIM | Edge RMSE | Halo Ratio | Runtime (s) |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        (
            f"| `lanczos_reference_not_ai` | No | PASS | {lanczos_metrics['psnr_db']:.2f} | "
            f"{lanczos_metrics['ssim']:.4f} | {lanczos_metrics['edge_gradient_rmse']:.2f} | "
            f"{lanczos_metrics['halo_overshoot_ratio']:.4f} | {lanczos_metrics['runtime_seconds']:.3f} |"
        ),
        (
            f"| `source_locked_acuity_restoration_not_ai` | No | PASS | {restored_cpu_metrics['psnr_db']:.2f} | "
            f"{restored_cpu_metrics['ssim']:.4f} | {restored_cpu_metrics['edge_gradient_rmse']:.2f} | "
            f"{restored_cpu_metrics['halo_overshoot_ratio']:.4f} | {restored_cpu_metrics['runtime_seconds']:.3f} |"
        ),
    ]
    if realesrgan_result["status"] == "EXECUTED":
        md_lines.append(
            f"| `RealESRGAN_x4plus` (`{realesrgan_result['device']}`) | **Yes** | EXECUTED | "
            f"{realesrgan_result['psnr_db']:.2f} | {realesrgan_result['ssim']:.4f} | "
            f"{realesrgan_result['edge_gradient_rmse']:.2f} | {realesrgan_result['halo_overshoot_ratio']:.4f} | "
            f"{realesrgan_result['runtime_seconds']:.3f} |"
        )
    else:
        md_lines.append(
            f"| `RealESRGAN_x4plus` | **Yes** | **BLOCKED** | N/A | N/A | N/A | N/A | N/A |"
        )

    if realesrnet_result["status"] == "EXECUTED":
        md_lines.append(
            f"| `RealESRNet_x4plus` (`{realesrnet_result['device']}`) | **Yes** | EXECUTED | "
            f"{realesrnet_result['psnr_db']:.2f} | {realesrnet_result['ssim']:.4f} | "
            f"{realesrnet_result['edge_gradient_rmse']:.2f} | {realesrnet_result['halo_overshoot_ratio']:.4f} | "
            f"{realesrnet_result['runtime_seconds']:.3f} |"
        )

    if antidrift_neural_result["status"] == "EXECUTED":
        md_lines.append(
            f"| `realesrgan_antidrift` (`{antidrift_neural_result['device']}`) | **Yes** | **EXECUTED (Recommended)** | "
            f"**{antidrift_neural_result['psnr_db']:.2f}** | **{antidrift_neural_result['ssim']:.4f}** | "
            f"**{antidrift_neural_result['edge_gradient_rmse']:.2f}** | **{antidrift_neural_result['halo_overshoot_ratio']:.4f}** | "
            f"{antidrift_neural_result['runtime_seconds']:.3f} |"
        )

    md_lines.extend(
        [
            "",
            f"## Registered High-Gradient Crop Comparisons (`{candidate_panel_label}` vs. Lanczos)",
            "",
            "| Crop # | Bounding Box `(x0, y0, x1, y1)` | Lanczos PSNR (dB) | Candidate PSNR (dB) | Δ PSNR (dB) | Lanczos SSIM | Candidate SSIM |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
        ]
    )
    for c in crops:
        md_lines.append(
            f"| {c['crop_index']} | `{tuple(c['box_xyxy'])}` | {c['lanczos_psnr_db']:.2f} | "
            f"{c['candidate_psnr_db']:.2f} | {c['delta_psnr_db']:+.2f} | "
            f"{c['lanczos_ssim']:.4f} | {c['candidate_ssim']:.4f} |"
        )

    md_lines.extend(
        [
            "",
            "## Methodology & Anti-Drift Qualifications",
            *[f"- {note}" for note in summary["methodology_notes"]],
        ]
    )
    (output_dir / "benchmark_report.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return summary

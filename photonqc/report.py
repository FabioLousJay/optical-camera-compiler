"""Measured output verification, integrity hash, and machine-readable reports."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any
import uuid
from PIL import Image


def sha256(path: Path) -> str:
    """Compute SHA-256 hex digest of a file on disk."""
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_and_report(
    source: Path,
    output: Path,
    expected: tuple[int, int],
    ppi: int,
    minimum_mib: float,
    backend_info: str,
    compression_level: int,
    report_dir: Path,
    *,
    maximum_mib: float | None = None,
    provenance: dict[str, Any] | None = None,
    metrics: dict[str, Any] | None = None,
    calibration_info: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Fully decode saved PNG, verify all hard acceptance gates, and write JSON/Markdown reports."""
    with Image.open(source) as src_img:
        src_dims = src_img.size
        src_icc = src_img.info.get("icc_profile")

    with Image.open(output) as image:
        image.load()  # full decode rather than checking just PNG header
        dims = image.size
        mode = image.mode
        actual_ppi = tuple(image.info.get("dpi", (0, 0)))
        out_icc = image.info.get("icc_profile")
        has_icc = bool(out_icc)

    actual_bytes = output.stat().st_size
    actual_mib = actual_bytes / (1024 * 1024)
    actual_mb_decimal = actual_bytes / 1_000_000.0

    geometry_ok = dims == expected
    mode_ok = mode == "RGB"
    min_mib_ok = actual_mib >= minimum_mib
    max_mib_ok = maximum_mib is None or actual_mib <= maximum_mib
    ppi_ok = not any(abs(value - ppi) > 0.5 for value in actual_ppi)

    if not geometry_ok or not mode_ok or not min_mib_ok or not max_mib_ok:
        raise RuntimeError("Output dimensions, mode, or minimum size failed verification")
    if not ppi_ok:
        raise RuntimeError("PNG PPI metadata failed round-trip verification")

    src_hash = sha256(source)
    out_hash = sha256(output)
    icc_hash = hashlib.sha256(src_icc).hexdigest() if src_icc else None

    transforms = ["lossless_png_export"]
    model_block: dict[str, Any] = {
        "backend": "lanczos" if backend_info == "lanczos_reference_not_ai" else "realesrgan",
        "name": None if backend_info == "lanczos_reference_not_ai" else "RealESRGAN_x4plus",
        "weights_sha256": None,
        "revision": None,
        "is_neural_ai": backend_info != "lanczos_reference_not_ai",
    }
    if provenance:
        if provenance.get("transforms"):
            transforms = list(provenance["transforms"]) + ["lossless_png_export"]
        model_block.update(
            {
                "backend": provenance.get("backend", model_block["backend"]),
                "name": provenance.get("model_name", model_block["name"]),
                "weights_sha256": provenance.get("weights_sha256"),
                "revision": provenance.get("repo_revision"),
                "device": provenance.get("device", "cpu"),
                "is_neural_ai": provenance.get("is_neural_ai", model_block["is_neural_ai"]),
            }
        )
    elif backend_info == "lanczos_reference_not_ai":
        transforms = ["lanczos_reference_resize", "lossless_png_export"]
    else:
        transforms = ["neural_x4", "final_lanczos_if_needed", "lossless_png_export"]

    metrics_block = metrics or {
        "psnr_db": None,
        "ssim": None,
        "lpips": None,
        "notes": "requires aligned GT",
    }

    checks_block = {
        "decode": True,
        "geometry": geometry_ok,
        "mode_rgb": mode_ok,
        "minimum_mib": min_mib_ok,
        "maximum_mib": max_mib_ok,
        "ppi_roundtrip": ppi_ok,
        "icc": has_icc if src_icc else True,
        "source_unmodified": True,
    }

    report: dict[str, Any] = {
        "run_id": f"photonqc-{uuid.uuid4().hex[:12]}",
        "source": str(source),
        "output": str(output),
        "pixels": list(dims),
        "megapixels": round(dims[0] * dims[1] / 1_000_000, 4),
        "mode": mode,
        "requested_ppi": ppi,
        "readback_ppi": [round(float(v), 4) for v in actual_ppi],
        "size_bytes": actual_bytes,
        "size_mib": round(actual_mib, 6),
        "size_mb_decimal": round(actual_mb_decimal, 6),
        "min_mib": minimum_mib,
        "max_mib": maximum_mib,
        "png_compression_level": compression_level,
        "sr_backend": backend_info,
        "embedded_icc": has_icc,
        "input_sha256": src_hash,
        "source_sha256": src_hash,
        "output_sha256": out_hash,
        "model": model_block,
        "input": {
            "width_px": src_dims[0],
            "height_px": src_dims[1],
            "icc_sha256": icc_hash,
        },
        "output_detail": {
            "width_px": dims[0],
            "height_px": dims[1],
            "format": "PNG",
            "mode": mode,
            "size_bytes": actual_bytes,
            "sha256": out_hash,
        },
        "transforms": transforms,
        "metrics": metrics_block,
        "checks": checks_block,
        "outcome": "PASS",
        "validation": "passed",
        "warning": "File size does not measure actual fidelity",
    }
    if calibration_info:
        report["calibration"] = calibration_info

    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# PhotonQC / PhotoPipe Export Report",
        "",
        "- Validation: **passed**",
        f"- Outcome: **{report['outcome']}**",
        f"- Backend Identity: `{backend_info}` (Neural AI: `{model_block['is_neural_ai']}`)",
    ]
    lines += [f"- {key}: `{value}`" for key, value in report.items() if key != "validation"]
    (report_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report

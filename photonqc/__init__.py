"""PhotonQC (PhotoPipe Lab): Constraint-validated AI photography, super-resolution,
perceptual evaluation, and print-aware export engineering platform.
"""

from __future__ import annotations

__version__ = "1.0.0"

from .backends import BackendProvenance, render, render_with_provenance
from .calibration import (
    PrintCalibrationReport,
    SeriesCohesionReport,
    apply_output_sharpening,
    evaluate_series_cohesion,
    load_print_profile,
    soft_proof_icc,
)
from .evaluation import (
    compute_edge_fidelity,
    compute_lpips,
    compute_psnr,
    compute_ssim,
    evaluate_flat_black_background,
    evaluate_heart_gold_case,
    evaluate_pair,
)
from .export import MIB, save_png_verified
from .licensing import MODEL_GOVERNANCE_REGISTRY, ModelLicenseSpec, verify_model_license
from .report import sha256, verify_and_report
from .restoration import SourcePreservingRestorer, restore_source_locked
from .sizing import (
    MAX_INPUT_PIXELS,
    PixelSpec,
    PrintSpec,
    apply_crop_or_pad,
    check_aspect_ratio,
    inches_to_pixels,
    resolve_target_dimensions,
    validate_input_security,
)

__all__ = [
    "__version__",
    "MIB",
    "MAX_INPUT_PIXELS",
    "PrintSpec",
    "PixelSpec",
    "inches_to_pixels",
    "resolve_target_dimensions",
    "check_aspect_ratio",
    "apply_crop_or_pad",
    "validate_input_security",
    "ModelLicenseSpec",
    "MODEL_GOVERNANCE_REGISTRY",
    "verify_model_license",
    "BackendProvenance",
    "render",
    "render_with_provenance",
    "save_png_verified",
    "sha256",
    "verify_and_report",
    "SourcePreservingRestorer",
    "restore_source_locked",
    "compute_psnr",
    "compute_ssim",
    "compute_lpips",
    "compute_edge_fidelity",
    "evaluate_heart_gold_case",
    "evaluate_flat_black_background",
    "evaluate_pair",
    "PrintCalibrationReport",
    "SeriesCohesionReport",
    "load_print_profile",
    "soft_proof_icc",
    "apply_output_sharpening",
    "evaluate_series_cohesion",
]

"""Optical Camera Compiler: Hardware-level optical simulation for zero-artifact photorealism."""

from __future__ import annotations

from pathlib import Path as _Path
import site as _site
import sys as _sys

if _sys.prefix == _sys.base_prefix:
    _venv_sp = (
        _Path(__file__).resolve().parent.parent
        / ".venv"
        / "lib"
        / f"python{_sys.version_info.major}.{_sys.version_info.minor}"
        / "site-packages"
    )
    if _venv_sp.is_dir() and str(_venv_sp) not in _sys.path:
        _site.addsitedir(str(_venv_sp))

from .compiler import OpticalCompiler, compile_ab_harness, compile_abc_harness, compile_scene, recommend_rigs
from .intelligence import (
    PromptIntelligenceEngine,
    QualityGateResult,
    RigRecommendation,
    SceneIntent,
)
from .models import (
    UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE,
    CameraProfile,
    CaptureMode,
    CompiledPayload,
    ContentType,
    HighResPNGOutputLockSpec,
    LightingEnvironmentSpec,
    LightingPreset,
    LightingSetup,
    MicroPhysics,
    NegativeShield,
    ReconstructionLock4XSpec,
    ReferenceImageInput,
    ReferenceMode,
    RendererScorecard,
    SceneInput,
    SensorOptics,
    SeriesCohesionSpec,
    StressProbe,
    SuperResolutionBackend,
    SkinLightingModifier,
    TargetEngine,
    UniversalDepixelateV2Spec,
    format_universal_medium_format_override,
)
from .pfep import (
    PROMPT_TEMPLATES,
    RUN_LOG_TEMPLATE,
    init_pfep_project,
)
from .presets import CAMERA_PRESETS, LENS_CATALOG
from .profiles import apply_overrides, auto_select_profile, load_profile
from .restoration import (
    EXPORT_PROFILES,
    PNGUpscaleReport,
    PrintSpec,
    ReconstructionReport,
    RestorationConfig,
    RunReport,
    add_micro_noise,
    calculate_exact_ratio_102mp_dimensions,
    execute_4x_full_color_png_upscale,
    execute_4x_reconstruction_lock,
    export_closed_loop,
    inches_to_pixels,
    restore_and_upscale_102mp,
    scale_multiplier_for_size,
    sha256_file,
    viewing_distance_inches,
)

# Unified PhotonQC AI Photography Engineering Platform re-exports
from photonqc import (
    MODEL_GOVERNANCE_REGISTRY,
    BackendProvenance,
    ModelLicenseSpec,
    PixelSpec,
    PrintCalibrationReport,
    SeriesCohesionReport,
    SourcePreservingRestorer,
    apply_crop_or_pad,
    apply_output_sharpening,
    compute_edge_fidelity,
    compute_lpips,
    compute_psnr,
    compute_ssim,
    evaluate_flat_black_background,
    evaluate_heart_gold_case,
    evaluate_pair,
    evaluate_series_cohesion,
    load_print_profile,
    render_with_provenance,
    restore_source_locked,
    save_png_verified,
    soft_proof_icc,
    validate_input_security,
    verify_and_report,
    verify_model_license,
)
from photonqc.benchmark import DegradationSpec, run_benchmark
from photonqc.neural_sr import detect_compute_device

__version__ = "3.9.4"

__all__ = [
    "OpticalCompiler",
    "compile_scene",
    "compile_ab_harness",
    "compile_abc_harness",
    "recommend_rigs",
    "PromptIntelligenceEngine",
    "QualityGateResult",
    "RigRecommendation",
    "SceneIntent",
    "UNIVERSAL_MEDIUM_FORMAT_PORTRAIT_OVERRIDE",
    "format_universal_medium_format_override",
    "UniversalDepixelateV2Spec",
    "SceneInput",
    "CameraProfile",
    "SensorOptics",
    "LightingSetup",
    "MicroPhysics",
    "NegativeShield",
    "SkinLightingModifier",
    "CAMERA_PRESETS",
    "LENS_CATALOG",
    "CompiledPayload",
    "ContentType",
    "ReferenceMode",
    "ReferenceImageInput",
    "TargetEngine",
    "CaptureMode",
    "LightingPreset",
    "StressProbe",
    "RendererScorecard",
    "LightingEnvironmentSpec",
    "SeriesCohesionSpec",
    "PrintSpec",
    "EXPORT_PROFILES",
    "auto_select_profile",
    "load_profile",
    "apply_overrides",
    "restore_and_upscale_102mp",
    "calculate_exact_ratio_102mp_dimensions",
    "RestorationConfig",
    "inches_to_pixels",
    "scale_multiplier_for_size",
    "viewing_distance_inches",
    "add_micro_noise",
    "sha256_file",
    "export_closed_loop",
    "RunReport",
    "ReconstructionLock4XSpec",
    "SuperResolutionBackend",
    "ReconstructionReport",
    "execute_4x_reconstruction_lock",
    "HighResPNGOutputLockSpec",
    "PNGUpscaleReport",
    "execute_4x_full_color_png_upscale",
    "init_pfep_project",
    "PROMPT_TEMPLATES",
    "RUN_LOG_TEMPLATE",
    # PhotonQC Platform
    "BackendProvenance",
    "render_with_provenance",
    "SourcePreservingRestorer",
    "restore_source_locked",
    "PrintCalibrationReport",
    "SeriesCohesionReport",
    "load_print_profile",
    "soft_proof_icc",
    "apply_output_sharpening",
    "evaluate_series_cohesion",
    "compute_psnr",
    "compute_ssim",
    "compute_lpips",
    "compute_edge_fidelity",
    "evaluate_pair",
    "evaluate_heart_gold_case",
    "evaluate_flat_black_background",
    "MODEL_GOVERNANCE_REGISTRY",
    "ModelLicenseSpec",
    "verify_model_license",
    "PixelSpec",
    "apply_crop_or_pad",
    "validate_input_security",
    "save_png_verified",
    "verify_and_report",
    "DegradationSpec",
    "run_benchmark",
    "detect_compute_device",
]

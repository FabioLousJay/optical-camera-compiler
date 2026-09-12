"""Optical Camera Compiler: Hardware-level optical simulation for zero-artifact photorealism."""

from __future__ import annotations

from .compiler import OpticalCompiler, compile_ab_harness, compile_scene
from .models import (
    CameraProfile,
    CaptureMode,
    CompiledPayload,
    ContentType,
    LightingEnvironmentSpec,
    LightingPreset,
    LightingSetup,
    MicroPhysics,
    NegativeShield,
    ReferenceImageInput,
    ReferenceMode,
    RendererScorecard,
    SceneInput,
    SensorOptics,
    SeriesCohesionSpec,
    StressProbe,
    TargetEngine,
)
from .pfep import (
    PROMPT_TEMPLATES,
    RUN_LOG_TEMPLATE,
    init_pfep_project,
)
from .profiles import apply_overrides, auto_select_profile, load_profile
from .restoration import (
    EXPORT_PROFILES,
    PrintSpec,
    RestorationConfig,
    RunReport,
    add_micro_noise,
    calculate_exact_ratio_102mp_dimensions,
    export_closed_loop,
    inches_to_pixels,
    restore_and_upscale_102mp,
    scale_multiplier_for_size,
    sha256_file,
    viewing_distance_inches,
)

__version__ = "3.5.0"

__all__ = [
    "OpticalCompiler",
    "compile_scene",
    "compile_ab_harness",
    "SceneInput",
    "CameraProfile",
    "SensorOptics",
    "LightingSetup",
    "MicroPhysics",
    "NegativeShield",
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
    "init_pfep_project",
    "PROMPT_TEMPLATES",
    "RUN_LOG_TEMPLATE",
]

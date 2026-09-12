"""Optical Camera Compiler: Hardware-level optical simulation for zero-artifact photorealism."""

from __future__ import annotations

from .compiler import OpticalCompiler, compile_ab_harness, compile_scene
from .models import (
    CameraProfile,
    CompiledPayload,
    ContentType,
    LightingSetup,
    MicroPhysics,
    NegativeShield,
    ReferenceImageInput,
    ReferenceMode,
    SceneInput,
    SensorOptics,
    TargetEngine,
)
from .profiles import apply_overrides, load_profile
from .restoration import (
    RestorationConfig,
    calculate_exact_ratio_102mp_dimensions,
    restore_and_upscale_102mp,
)

__version__ = "0.1.0"

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
    "load_profile",
    "apply_overrides",
    "restore_and_upscale_102mp",
    "calculate_exact_ratio_102mp_dimensions",
    "RestorationConfig",
]

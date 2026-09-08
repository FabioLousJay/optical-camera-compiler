"""Optical Camera Compiler: Hardware-level optical simulation for zero-artifact photorealism."""

from __future__ import annotations

from .compiler import OpticalCompiler
from .models import (
    CameraProfile,
    CompiledPayload,
    LightingSetup,
    MicroPhysics,
    NegativeShield,
    SceneInput,
    SensorOptics,
    TargetEngine,
)
from .profiles import apply_overrides, load_profile

__version__ = "0.1.0"

__all__ = [
    "OpticalCompiler",
    "SceneInput",
    "CameraProfile",
    "SensorOptics",
    "LightingSetup",
    "MicroPhysics",
    "NegativeShield",
    "CompiledPayload",
    "TargetEngine",
    "load_profile",
    "apply_overrides",
]

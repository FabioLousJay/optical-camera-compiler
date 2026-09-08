"""Base adapter interface for model-specific prompt compilation."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..models import CameraProfile, CompiledPayload, SceneInput, TargetEngine


class BaseAdapter(ABC):
    """Abstract base class for target model prompt adapters."""

    target_engine: TargetEngine

    @abstractmethod
    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        """Compile a scene description and camera profile into a model-specific payload."""
        raise NotImplementedError

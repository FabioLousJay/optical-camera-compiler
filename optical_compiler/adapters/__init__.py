"""Adapter registry and exports."""

from __future__ import annotations

from typing import Type

from ..models import TargetEngine
from .base import BaseAdapter
from .flux import FluxAdapter
from .imagen import ImagenAdapter
from .midjourney import MidjourneyAdapter
from .raw import RawSpecAdapter
from .sdxl import SDXLAdapter

ADAPTER_REGISTRY: dict[TargetEngine, Type[BaseAdapter]] = {
    TargetEngine.IMAGEN: ImagenAdapter,
    TargetEngine.FLUX: FluxAdapter,
    TargetEngine.SDXL: SDXLAdapter,
    TargetEngine.MIDJOURNEY: MidjourneyAdapter,
    TargetEngine.RAW: RawSpecAdapter,
}


def get_adapter(engine: TargetEngine | str) -> BaseAdapter:
    """Instantiate and return the appropriate adapter for a target engine."""
    if isinstance(engine, str):
        engine = TargetEngine.from_str(engine)

    adapter_cls = ADAPTER_REGISTRY.get(engine)
    if not adapter_cls:
        raise ValueError(f"No adapter registered for target engine: {engine}")

    return adapter_cls()


__all__ = [
    "BaseAdapter",
    "ImagenAdapter",
    "FluxAdapter",
    "SDXLAdapter",
    "MidjourneyAdapter",
    "RawSpecAdapter",
    "get_adapter",
    "ADAPTER_REGISTRY",
]

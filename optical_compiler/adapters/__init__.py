"""Adapter registry and exports."""

from __future__ import annotations

from typing import Type

from ..models import TargetEngine
from .base import BaseAdapter
from .firefly import FireflyAdapter
from .flux import FluxAdapter
from .flux_raw import FluxRawAdapter
from .gpt_images import GPTImagesAdapter
from .humain import HumainAdapter
from .imagen import ImagenAdapter
from .json_prompt import JSONAllInOneAdapter
from .midjourney import MidjourneyAdapter
from .raw import RawSpecAdapter
from .runway import RunwayAdapter
from .sdxl import SDXLAdapter

ADAPTER_REGISTRY: dict[TargetEngine, Type[BaseAdapter]] = {
    TargetEngine.GPT_IMAGES: GPTImagesAdapter,
    TargetEngine.IMAGEN: ImagenAdapter,
    TargetEngine.MIDJOURNEY: MidjourneyAdapter,
    TargetEngine.FLUX: FluxAdapter,
    TargetEngine.FLUX_RAW: FluxRawAdapter,
    TargetEngine.FIREFLY: FireflyAdapter,
    TargetEngine.RUNWAY: RunwayAdapter,
    TargetEngine.HUMAIN: HumainAdapter,
    TargetEngine.SDXL: SDXLAdapter,
    TargetEngine.RAW: RawSpecAdapter,
    TargetEngine.JSON_PROMPT: JSONAllInOneAdapter,
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
    "GPTImagesAdapter",
    "ImagenAdapter",
    "FluxAdapter",
    "FluxRawAdapter",
    "FireflyAdapter",
    "RunwayAdapter",
    "HumainAdapter",
    "SDXLAdapter",
    "MidjourneyAdapter",
    "RawSpecAdapter",
    "JSONAllInOneAdapter",
    "get_adapter",
    "ADAPTER_REGISTRY",
]

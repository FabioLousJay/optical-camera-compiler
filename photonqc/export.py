"""Lossless PNG byte-budget search without artificial image modifications."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image

MIB = 1024 * 1024


def save_png_verified(
    image: Image.Image,
    output: Path,
    ppi: int,
    minimum_mib: float = 0.0,
    maximum_mib: float | None = None,
    icc_profile: bytes | None = None,
) -> tuple[int, float]:
    """Search lossless PNG compression levels (6, 1, 0) to satisfy byte-budget constraints.

    Never injects noise, metadata padding, or dimension changes to inflate byte size.
    """
    if image.mode != "RGB":
        raise ValueError("MVP export supports RGB PNG only")
    if minimum_mib < 0 or (maximum_mib is not None and maximum_mib < minimum_mib):
        raise ValueError("Invalid file-size constraints")
    output.parent.mkdir(parents=True, exist_ok=True)
    candidates = []
    with TemporaryDirectory(dir=output.parent) as d:
        for level in (6, 1, 0):
            temp_path = Path(d) / f"candidate_{level}.png"
            kwargs: dict[str, object] = {"format": "PNG", "compress_level": level, "dpi": (ppi, ppi)}
            if icc_profile:
                kwargs["icc_profile"] = icc_profile
            image.save(temp_path, **kwargs)
            size = temp_path.stat().st_size / MIB
            if size >= minimum_mib and (maximum_mib is None or size <= maximum_mib):
                candidates.append((size, level, temp_path))
        if not candidates:
            raise RuntimeError(
                "No lossless PNG encoding meets byte limits at fixed pixels. "
                "Raise resolution or reconsider minimum size; do not add noise/padding."
            )
        size, level, selected = min(candidates, key=lambda item: item[0])
        selected.replace(output)
    return level, size

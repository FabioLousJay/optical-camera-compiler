"""Print geometry, exact pixel sizing, aspect-ratio policy, and input security guards."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from PIL import Image

MAX_INPUT_PIXELS: int = 150_000_000


@dataclass(frozen=True)
class PrintSpec:
    """Physical print dimensions in inches and raster density in pixels per inch (PPI)."""

    width_in: Decimal
    height_in: Decimal
    ppi: int = 300

    def __post_init__(self) -> None:
        if not isinstance(self.width_in, Decimal):
            object.__setattr__(self, "width_in", Decimal(str(self.width_in)))
        if not isinstance(self.height_in, Decimal):
            object.__setattr__(self, "height_in", Decimal(str(self.height_in)))


@dataclass(frozen=True)
class PixelSpec:
    """Explicit target raster pixel dimensions."""

    width_px: int
    height_px: int


def inches_to_pixels(spec: PrintSpec) -> tuple[int, int]:
    """Convert physical print specification (inches × PPI) into exact integer pixel dimensions."""
    if spec.width_in <= 0 or spec.height_in <= 0 or spec.ppi <= 0:
        raise ValueError("Print dimensions and PPI must be positive")
    quantize_int = lambda value: int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    return quantize_int(spec.width_in * spec.ppi), quantize_int(spec.height_in * spec.ppi)


def resolve_target_dimensions(
    width_in: Decimal | None = None,
    height_in: Decimal | None = None,
    ppi: int = 300,
    width_px: int | None = None,
    height_px: int | None = None,
) -> tuple[int, int]:
    """Resolve exact target pixel dimensions with strict mutual exclusion between print and pixel specs."""
    has_print = width_in is not None or height_in is not None
    has_pixels = width_px is not None or height_px is not None

    if has_print and has_pixels:
        raise ValueError(
            "Mutually exclusive sizing options: specify either (--width-in and --height-in) "
            "or (--width-px and --height-px), never both."
        )
    if not has_print and not has_pixels:
        raise ValueError(
            "Missing target dimensions: specify either (--width-in and --height-in) "
            "or (--width-px and --height-px)."
        )
    if has_print:
        if width_in is None or height_in is None:
            raise ValueError("Both --width-in and --height-in are required when specifying print dimensions.")
        return inches_to_pixels(PrintSpec(width_in=Decimal(str(width_in)), height_in=Decimal(str(height_in)), ppi=ppi))

    if width_px is None or height_px is None:
        raise ValueError("Both --width-px and --height-px are required when specifying pixel dimensions.")
    if width_px <= 0 or height_px <= 0 or ppi <= 0:
        raise ValueError("Target pixel dimensions and PPI metadata must be positive integers.")
    return int(width_px), int(height_px)


def check_aspect_ratio(
    source: tuple[int, int],
    target: tuple[int, int],
    tolerance: float = 0.002,
) -> None:
    """Verify source and target dimensions preserve aspect ratio within tolerance."""
    if source[0] <= 0 or source[1] <= 0 or target[0] <= 0 or target[1] <= 0:
        raise ValueError("Dimensions must be positive")
    a = source[0] / source[1]
    b = target[0] / target[1]
    if abs(a / b - 1) > tolerance:
        raise ValueError("Aspect-ratio mismatch. Explicitly crop/pad before export; never stretch silently.")


def apply_crop_or_pad(
    image: Image.Image,
    target: tuple[int, int],
    policy: str = "reject",
    tolerance: float = 0.002,
) -> tuple[Image.Image, str]:
    """Apply explicit aspect-ratio policy ('reject', 'center-crop', or 'pad-black').

    Never stretches an image silently. Returns (prepared_image, transform_record).
    """
    src_w, src_h = image.size
    tgt_w, tgt_h = target
    src_ratio = src_w / src_h
    tgt_ratio = tgt_w / tgt_h

    if abs(src_ratio / tgt_ratio - 1) <= tolerance:
        return image.copy(), "aspect_ratio_matched"

    if policy == "reject":
        check_aspect_ratio(image.size, target, tolerance=tolerance)
        return image.copy(), "aspect_ratio_matched"

    if policy == "center-crop":
        if src_ratio > tgt_ratio:
            new_w = max(1, int(round(src_h * tgt_ratio)))
            left = (src_w - new_w) // 2
            cropped = image.crop((left, 0, left + new_w, src_h))
            return cropped, f"explicit_center_crop_{src_w}x{src_h}_to_{new_w}x{src_h}"
        else:
            new_h = max(1, int(round(src_w / tgt_ratio)))
            top = (src_h - new_h) // 2
            cropped = image.crop((0, top, src_w, top + new_h))
            return cropped, f"explicit_center_crop_{src_w}x{src_h}_to_{src_w}x{new_h}"

    if policy == "pad-black":
        if src_ratio > tgt_ratio:
            new_h = max(src_h, int(round(src_w / tgt_ratio)))
            canvas = Image.new("RGB", (src_w, new_h), (0, 0, 0))
            top = (new_h - src_h) // 2
            canvas.paste(image, (0, top))
            return canvas, f"explicit_pad_black_{src_w}x{src_h}_to_{src_w}x{new_h}"
        else:
            new_w = max(src_w, int(round(src_h * tgt_ratio)))
            canvas = Image.new("RGB", (new_w, src_h), (0, 0, 0))
            left = (new_w - src_w) // 2
            canvas.paste(image, (left, 0))
            return canvas, f"explicit_pad_black_{src_w}x{src_h}_to_{new_w}x{src_h}"

    raise ValueError(f"Unknown crop policy: {policy!r}. Supported: 'reject', 'center-crop', 'pad-black'.")


def validate_input_security(
    input_path: Path,
    max_pixels: int = MAX_INPUT_PIXELS,
) -> dict[str, int | str]:
    """Validate input path existence, file size, and header pixel count against decompression bombs."""
    resolved = input_path.expanduser().resolve()
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError(f"Input image does not exist: {resolved}")
    byte_size = resolved.stat().st_size
    if byte_size <= 0:
        raise ValueError(f"Input file is empty (0 bytes): {resolved}")

    with Image.open(resolved) as im:
        w, h = im.size
        pixels = w * h
        if pixels > max_pixels:
            raise ValueError(
                f"Input image dimensions {w}x{h} ({pixels:,} px) exceed maximum security limit "
                f"of {max_pixels:,} pixels."
            )
        return {
            "path": str(resolved),
            "width": w,
            "height": h,
            "pixels": pixels,
            "mode": im.mode,
            "format": im.format or "UNKNOWN",
            "bytes": byte_size,
        }

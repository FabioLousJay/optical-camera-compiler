"""Data models and schemas for the Optical Camera Compiler."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from enum import Enum
from typing import Any, Optional


class TargetEngine(str, Enum):
    """Supported diffusion and generation model targets."""

    GPT_IMAGES = "gpt_images"
    IMAGEN = "imagen"
    MIDJOURNEY = "midjourney"
    FLUX = "flux"
    SDXL = "sdxl"
    RAW = "raw"
    JSON_PROMPT = "json"
    JSON = "json"

    @classmethod
    def from_str(cls, value: str) -> TargetEngine:
        """Parse engine from string case-insensitively with friendly aliases."""
        normalized = value.strip().lower()
        alias_map = {
            "gpt": cls.GPT_IMAGES,
            "gpt_images": cls.GPT_IMAGES,
            "chatgpt": cls.GPT_IMAGES,
            "dalle": cls.GPT_IMAGES,
            "dalle3": cls.GPT_IMAGES,
            "gpt4o": cls.GPT_IMAGES,
            "gemini": cls.IMAGEN,
            "imagen": cls.IMAGEN,
            "imagen3": cls.IMAGEN,
            "mj": cls.MIDJOURNEY,
            "midjourney": cls.MIDJOURNEY,
            "flux": cls.FLUX,
            "sdxl": cls.SDXL,
            "raw": cls.RAW,
            "json": cls.JSON_PROMPT,
            "json_all": cls.JSON_PROMPT,
            "json_all_in_one": cls.JSON_PROMPT,
            "all_in_one": cls.JSON_PROMPT,
            "all_in_one_json": cls.JSON_PROMPT,
            "json_prompt": cls.JSON_PROMPT,
        }
        if normalized in alias_map:
            return alias_map[normalized]
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(
            f"Unknown target engine: '{value}'. Supported engines: {[e.value for e in cls]}"
        )


@dataclass
class SensorOptics:
    """Hardware sensor, glass, and shutter specifications."""

    camera_system: str
    sensor_type: str = "Back-Side Illuminated (BSI) CMOS Medium Format"
    sensor_dimensions: str = "54x40mm medium-format sensor"
    full_frame_equivalent: str = "~50mm full-frame equivalent normal field of view"
    lens: str = "Schneider Kreuznach 80mm LS f/2.8 Blue Ring"
    aperture_sweet_spot: str = "f/8"
    iso_base: str = "ISO 50 base sensor sensitivity"
    dynamic_range: str = "16-bit raw tonal range with 15 stops of dynamic latitude"
    shutter: str = "Leaf shutter with 1/1600s high-speed flash sync"


@dataclass
class LightingSetup:
    """Lighting geometry, transport, and modifier setup."""

    primary_lighting: str = (
        "Studio strobe, 1/1600s leaf shutter sync, ISO 50 base sensor sensitivity, 16-bit raw tonal range"
    )
    light_transport: str = (
        "Key light with large parabolic modifier, deep shadows carved with black foam-core negative fill, single-axis specular catchlights"
    )


@dataclass
class MicroPhysics:
    """Physically accurate surface micro-relief and optical falloff directives."""

    surface_rendering: list[str] = field(
        default_factory=lambda: [
            "Natural epidermal skin texture with resolved pores, fine vellus hair, and accurate subsurface scattering without artificial blur or waxy specularities",
            "True material micro-relief: fabric weave, micro-abrasions, uncompressed specular highlight falloff",
            "High optical acutance and MTF contrast without digital edge halos or unsharp masking artifacts",
        ]
    )
    depth_and_optics: list[str] = field(
        default_factory=lambda: [
            "Subtle optical falloff characteristic of large-sensor f/8 depth of field",
            "Zero perspective distortion, clean rectilinear projection",
            "Clean edge transitions driven purely by lighting and geometry, not artificial post-process depth slicing",
        ]
    )


class LightingPreset(str, Enum):
    """Photographic lighting recipes from the High-End Pro Master Framework."""

    GOLDEN_HOUR = "golden_hour"
    BLUE_HOUR = "blue_hour"
    STUDIO_SOFT = "studio_soft"
    STUDIO_HARD = "studio_hard"
    FLASH_FREEZE = "flash_freeze"
    OVERCAST = "overcast"
    FLAT_OVERCAST = "flat_overcast"
    DRAMATIC = "dramatic"
    NEON = "neon"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[LightingPreset]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "flat_overcast_daylight": cls.FLAT_OVERCAST,
            "flat_overcast": cls.FLAT_OVERCAST,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None


LIGHTING_PRESET_DESCRIPTIONS: dict[LightingPreset, tuple[str, str]] = {
    LightingPreset.GOLDEN_HOUR: (
        "Low-angle directional golden sunlight (3200K-3800K), warm specular edge wrap, soft atmospheric glow",
        "Key sunlight at 15-degree elevation, deep warm shadows, single-axis specular rim highlights with natural atmospheric scatter",
    ),
    LightingPreset.BLUE_HOUR: (
        "Deep twilight ambient sky illumination (7500K-9000K), cool soft fill, high dynamic range balance against warm practical lights",
        "Omnidirectional soft skylight fill balanced against warm 2700K tungsten practical accents, gradient sky backdrop",
    ),
    LightingPreset.STUDIO_SOFT: (
        "Large parabolic softbox key light, subtle edge negative fill, diffused wrap-around illumination",
        "Key light through large diffusion scrim at 45 degrees, soft fill card opposite, subtle hair rim light, low micro-contrast shadow gradient",
    ),
    LightingPreset.STUDIO_HARD: (
        "Focused direct beauty dish or fresnel key light, crisp shadow boundaries, sculpted micro-contrast",
        "Un-diffused silver reflector key, razor shadow cutoffs, high specular acutance, deep black negative fill",
    ),
    LightingPreset.FLASH_FREEZE: (
        "High-speed optical flash strobe (1/1600s leaf sync), microsecond duration motion freeze, razor-sharp edge definition",
        "Twin high-speed studio strobes, zero ambient spill, tack-sharp specular catchlights, complete motion freeze",
    ),
    LightingPreset.OVERCAST: (
        "Giant natural atmospheric softbox, diffused neutral daylight (5500K-6000K), zero harsh cast shadows",
        "Even hemispherical cloud diffusion, gentle top-down natural light wrap, subtle linear shadow gradient under jaw and chin",
    ),
    LightingPreset.FLAT_OVERCAST: (
        "Flat overcast daylight acting as soft natural diffusion, low contrast, gentle highlight roll-off, zero harsh cast shadows",
        "Even diffuse natural daylight, soft highlight transitions, clean midtones, zero harsh contrast, allowing long motion blur trails without specular blowouts or clipping",
    ),
    LightingPreset.DRAMATIC: (
        "Chiaroscuro high-contrast lighting, single directional key, deep unlit negative space, emotive rim light",
        "Single focused spotlight from steep side angle, 8:1 contrast ratio, deep true black shadows, razor specular cheek highlight",
    ),
    LightingPreset.NEON: (
        "Multi-chromatic saturated ambient rim and key lights, complementary color contrast, high-intensity specular sheen",
        "Dual-tone directional lighting (cyan and magenta/amber), saturated chromatic rim separation, glossy surface reflection bounce",
    ),
}


class CaptureMode(str, Enum):
    """Photographic capture intent modes."""

    STATIC_MAX_DETAIL = "static_max_detail"
    PORTRAIT_MAX_DETAIL = "portrait_max_detail"
    ACTION_MAX_DETAIL = "action_max_detail"
    MACRO_MAX_DETAIL = "macro_max_detail"
    LANDSCAPE_ARCHITECTURE_MAX_DETAIL = "landscape_architecture_max_detail"
    SLOW_SHUTTER_CROWD_MOTION = "slow_shutter_crowd_motion"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[CaptureMode]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "slow_shutter": cls.SLOW_SHUTTER_CROWD_MOTION,
            "slow_shutter_motion": cls.SLOW_SHUTTER_CROWD_MOTION,
            "slow_shutter_crowd_motion": cls.SLOW_SHUTTER_CROWD_MOTION,
            "crowd_motion": cls.SLOW_SHUTTER_CROWD_MOTION,
            "calm_vs_chaos": cls.SLOW_SHUTTER_CROWD_MOTION,
            "motion_blur": cls.SLOW_SHUTTER_CROWD_MOTION,
            "motion_blur_crowd": cls.SLOW_SHUTTER_CROWD_MOTION,
            "motion_blur_photography": cls.SLOW_SHUTTER_CROWD_MOTION,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None


CAPTURE_MODE_DIRECTIVES: dict[CaptureMode, str] = {
    CaptureMode.STATIC_MAX_DETAIL: "Tripod-mounted lock, zero sensor shake, base ISO, maximum MTF optical resolution, ultra-deep tonal gradation",
    CaptureMode.PORTRAIT_MAX_DETAIL: "Focus locked on the near eye, iris and eyelashes tack sharp, resolved epidermal skin pores, natural subcutaneous scatter",
    CaptureMode.ACTION_MAX_DETAIL: "Decisive-moment freeze, high-speed shutter, zero motion smear, dynamic muscle tension, tack-sharp trajectory",
    CaptureMode.MACRO_MAX_DETAIL: "1:1 reproduction ratio, extreme micro-plane depth slicing, razor micro-ridges, diffraction-suppressed optical plane",
    CaptureMode.LANDSCAPE_ARCHITECTURE_MAX_DETAIL: "Rectilinear zero-distortion geometry, infinite optical hyperfocal plane, level horizon, corner-to-corner tack sharpness",
    CaptureMode.SLOW_SHUTTER_CROWD_MOTION: "Slow shutter motion-blur aesthetic (editorial calm vs. chaos): subject stands completely still and centered, locked tack-sharp (near-eye focus, iris and eyelash acutance, visible pores, natural beard texture); surrounding crowd rushes past with smooth multi-directional motion blur trails (left-to-right, right-to-left, toward/away from camera, diagonal crossings); clean streak physics wrapping around subject without anatomical deformation; zero ghost faces, melted bodies, or uniform smear wall",
}


class ContentType(str, Enum):
    """Classification of source imagery for targeted restoration and reproduction logic."""

    PHOTOGRAPH = "photograph"
    PORTRAIT = "portrait"
    PRODUCT_PHOTO = "product_photo"
    DOCUMENT_SCAN = "document_scan"
    POSTER_OR_FLYER = "poster_or_flyer"
    MEME_OR_INFOGRAPHIC = "meme_or_infographic"
    UI_OR_SCREENSHOT = "ui_or_screenshot"
    MIXED_CONTENT = "mixed_content"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[ContentType]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    @property
    def is_flat_reproduction(self) -> bool:
        """Return True if content type requires flat copy-stand reproduction."""
        return self in (
            ContentType.DOCUMENT_SCAN,
            ContentType.POSTER_OR_FLYER,
            ContentType.MEME_OR_INFOGRAPHIC,
            ContentType.UI_OR_SCREENSHOT,
        )


class GripType(str, Enum):
    """Commercial product grip geometry and contact types."""

    PALM_SUPPORT = "palm_support"
    PRECISION_PINCH = "precision_pinch"
    CYLINDRICAL_WRAP = "cylindrical_wrap"
    RELAXED_REST = "relaxed_rest"
    OPEN_PALM = "open_palm"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[GripType]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "pinch": cls.PRECISION_PINCH,
            "pinch_grip": cls.PRECISION_PINCH,
            "fingertip": cls.PRECISION_PINCH,
            "precision": cls.PRECISION_PINCH,
            "precision_pinch": cls.PRECISION_PINCH,
            "wrap": cls.CYLINDRICAL_WRAP,
            "cylindrical": cls.CYLINDRICAL_WRAP,
            "cylindrical_wrap": cls.CYLINDRICAL_WRAP,
            "bottle_wrap": cls.CYLINDRICAL_WRAP,
            "power_grip": cls.CYLINDRICAL_WRAP,
            "support": cls.PALM_SUPPORT,
            "palm": cls.PALM_SUPPORT,
            "palm_support": cls.PALM_SUPPORT,
            "flat_palm": cls.PALM_SUPPORT,
            "rest": cls.RELAXED_REST,
            "relaxed": cls.RELAXED_REST,
            "relaxed_rest": cls.RELAXED_REST,
            "loose": cls.RELAXED_REST,
            "open": cls.OPEN_PALM,
            "open_palm": cls.OPEN_PALM,
            "splay": cls.OPEN_PALM,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class AnamorphicSqueeze(str, Enum):
    """Cinema anamorphic squeeze ratios."""

    SPHERICAL = "1.0x"
    SQUEEZE_1_33X = "1.33x"
    SQUEEZE_1_5X = "1.5x"
    SQUEEZE_1_8X = "1.8x"
    SQUEEZE_2_0X = "2.0x"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[AnamorphicSqueeze]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "spherical": cls.SPHERICAL,
            "1.0": cls.SPHERICAL,
            "1.0x": cls.SPHERICAL,
            "1x": cls.SPHERICAL,
            "1.33": cls.SQUEEZE_1_33X,
            "1.33x": cls.SQUEEZE_1_33X,
            "1.5": cls.SQUEEZE_1_5X,
            "1.5x": cls.SQUEEZE_1_5X,
            "1.8": cls.SQUEEZE_1_8X,
            "1.8x": cls.SQUEEZE_1_8X,
            "2.0": cls.SQUEEZE_2_0X,
            "2.0x": cls.SQUEEZE_2_0X,
            "2x": cls.SQUEEZE_2_0X,
            "anamorphic": cls.SQUEEZE_2_0X,
            "cinema_anamorphic": cls.SQUEEZE_2_0X,
            "2.0x_cinema": cls.SQUEEZE_2_0X,
            "scope": cls.SQUEEZE_2_0X,
            "cinema_scope": cls.SQUEEZE_2_0X,
            "anamorphic_2x": cls.SQUEEZE_2_0X,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class StreakFlare(str, Enum):
    """Anamorphic cylindrical lens flare coatings and chromatic signatures."""

    CYAN_BLUE = "cyan_blue"
    WARM_GOLD = "warm_gold"
    NEUTRAL_SILVER = "neutral_silver"
    VINTAGE_MAGENTA = "vintage_magenta"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[StreakFlare]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "cyan": cls.CYAN_BLUE,
            "blue": cls.CYAN_BLUE,
            "cyan_blue": cls.CYAN_BLUE,
            "sci_fi": cls.CYAN_BLUE,
            "gold": cls.WARM_GOLD,
            "warm_gold": cls.WARM_GOLD,
            "amber": cls.WARM_GOLD,
            "vintage_gold": cls.WARM_GOLD,
            "silver": cls.NEUTRAL_SILVER,
            "neutral": cls.NEUTRAL_SILVER,
            "neutral_silver": cls.NEUTRAL_SILVER,
            "white": cls.NEUTRAL_SILVER,
            "magenta": cls.VINTAGE_MAGENTA,
            "vintage": cls.VINTAGE_MAGENTA,
            "vintage_magenta": cls.VINTAGE_MAGENTA,
            "purple": cls.VINTAGE_MAGENTA,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class IrisBladeCount(str, Enum):
    """Lens iris blade geometry shaping out-of-focus bokeh discs and diffraction spikes."""

    CIRCULAR_14 = "14_blade_circular"
    ROUNDED_9 = "9_blade_rounded"
    OCTAGONAL_8 = "8_blade_octagonal"
    HEXAGONAL_6 = "6_blade_hexagonal"

    BLADES_14_CIRCULAR = "14_blade_circular"
    BLADES_9_ROUNDED = "9_blade_rounded"
    BLADES_8_OCTAGONAL = "8_blade_octagonal"
    BLADES_6_HEXAGONAL = "6_blade_hexagonal"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[IrisBladeCount]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "14": cls.CIRCULAR_14,
            "14_blade": cls.CIRCULAR_14,
            "14_blade_circular": cls.CIRCULAR_14,
            "circular": cls.CIRCULAR_14,
            "9": cls.ROUNDED_9,
            "9_blade": cls.ROUNDED_9,
            "9_blade_rounded": cls.ROUNDED_9,
            "rounded": cls.ROUNDED_9,
            "8": cls.OCTAGONAL_8,
            "8_blade": cls.OCTAGONAL_8,
            "8_blade_octagonal": cls.OCTAGONAL_8,
            "octagonal": cls.OCTAGONAL_8,
            "6": cls.HEXAGONAL_6,
            "6_blade": cls.HEXAGONAL_6,
            "6_blade_hexagonal": cls.HEXAGONAL_6,
            "hexagonal": cls.HEXAGONAL_6,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class GoboPattern(str, Enum):
    """Optical pattern projection cookies / gobos for commercial lighting."""

    VENETIAN_BLINDS = "venetian_blinds"
    DAPPLED_FOLIAGE = "dappled_foliage"
    WINDOW_PANES = "window_panes"
    GEOMETRIC_SLITS = "geometric_slits"
    PRISM_FRACTURE = "prism_fracture"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[GoboPattern]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "blinds": cls.VENETIAN_BLINDS,
            "venetian": cls.VENETIAN_BLINDS,
            "venetian_blinds": cls.VENETIAN_BLINDS,
            "foliage": cls.DAPPLED_FOLIAGE,
            "dappled": cls.DAPPLED_FOLIAGE,
            "dappled_foliage": cls.DAPPLED_FOLIAGE,
            "leaves": cls.DAPPLED_FOLIAGE,
            "window": cls.WINDOW_PANES,
            "windows": cls.WINDOW_PANES,
            "panes": cls.WINDOW_PANES,
            "window_panes": cls.WINDOW_PANES,
            "slits": cls.GEOMETRIC_SLITS,
            "geometric": cls.GEOMETRIC_SLITS,
            "geometric_slits": cls.GEOMETRIC_SLITS,
            "prism": cls.PRISM_FRACTURE,
            "fracture": cls.PRISM_FRACTURE,
            "prism_fracture": cls.PRISM_FRACTURE,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class GripModifier(str, Enum):
    """Professional studio grip modifiers."""

    BEAUTY_DISH_HONEYCOMB = "beauty_dish_honeycomb"
    BUTTERFLY_8X8_SILK = "butterfly_8x8_silk"
    SNOOT_PINPOINT = "snoot_pinpoint"
    SOLID_BLACK_FLOPPY = "solid_black_floppy"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[GripModifier]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "beauty_dish": cls.BEAUTY_DISH_HONEYCOMB,
            "beauty_dish_honeycomb": cls.BEAUTY_DISH_HONEYCOMB,
            "honeycomb": cls.BEAUTY_DISH_HONEYCOMB,
            "grid": cls.BEAUTY_DISH_HONEYCOMB,
            "butterfly": cls.BUTTERFLY_8X8_SILK,
            "butterfly_8x8_silk": cls.BUTTERFLY_8X8_SILK,
            "silk": cls.BUTTERFLY_8X8_SILK,
            "8x8": cls.BUTTERFLY_8X8_SILK,
            "scrim": cls.BUTTERFLY_8X8_SILK,
            "snoot": cls.SNOOT_PINPOINT,
            "snoot_pinpoint": cls.SNOOT_PINPOINT,
            "pinpoint": cls.SNOOT_PINPOINT,
            "floppy": cls.SOLID_BLACK_FLOPPY,
            "solid_black_floppy": cls.SOLID_BLACK_FLOPPY,
            "black_flag": cls.SOLID_BLACK_FLOPPY,
            "negative_fill": cls.SOLID_BLACK_FLOPPY,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class LightingRatio(str, Enum):
    """Key-to-fill contrast ratios for commercial photography."""

    RATIO_1_1 = "1:1"
    RATIO_2_1 = "2:1"
    RATIO_4_1 = "4:1"
    RATIO_8_1 = "8:1"
    RATIO_16_1 = "16:1"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[LightingRatio]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "1:1": cls.RATIO_1_1,
            "flat": cls.RATIO_1_1,
            "2:1": cls.RATIO_2_1,
            "beauty": cls.RATIO_2_1,
            "soft": cls.RATIO_2_1,
            "4:1": cls.RATIO_4_1,
            "commercial": cls.RATIO_4_1,
            "editorial": cls.RATIO_4_1,
            "8:1": cls.RATIO_8_1,
            "dramatic": cls.RATIO_8_1,
            "chiaroscuro": cls.RATIO_8_1,
            "16:1": cls.RATIO_16_1,
            "film_noir": cls.RATIO_16_1,
            "noir": cls.RATIO_16_1,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return None

    from_string = from_str


class CopySpace(str, Enum):
    """Compositional negative space reserved for graphic design and advertising typography."""

    NONE = "none"
    LEFT_THIRD = "left_third"
    RIGHT_THIRD = "right_third"
    TOP_THIRD = "top_third"
    BOTTOM_THIRD = "bottom_third"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[CopySpace]:
        if not value:
            return cls.NONE
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "left": cls.LEFT_THIRD,
            "left_third": cls.LEFT_THIRD,
            "right": cls.RIGHT_THIRD,
            "right_third": cls.RIGHT_THIRD,
            "top": cls.TOP_THIRD,
            "top_third": cls.TOP_THIRD,
            "header": cls.TOP_THIRD,
            "bottom": cls.BOTTOM_THIRD,
            "bottom_third": cls.BOTTOM_THIRD,
            "footer": cls.BOTTOM_THIRD,
            "none": cls.NONE,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return cls.NONE

    from_string = from_str


class AdSafeZone(str, Enum):
    """Social and digital advertising safe-zone guidelines."""

    NONE = "none"
    TIKTOK_REELS_9_16 = "tiktok_reels_9_16"
    INSTAGRAM_FEED_4_5 = "instagram_feed_4_5"
    ECOMMERCE_CATALOG_1_1 = "ecommerce_catalog_1_1"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[AdSafeZone]:
        if not value:
            return cls.NONE
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "tiktok": cls.TIKTOK_REELS_9_16,
            "reels": cls.TIKTOK_REELS_9_16,
            "stories": cls.TIKTOK_REELS_9_16,
            "9:16": cls.TIKTOK_REELS_9_16,
            "vertical": cls.TIKTOK_REELS_9_16,
            "tiktok_reels_9_16": cls.TIKTOK_REELS_9_16,
            "instagram": cls.INSTAGRAM_FEED_4_5,
            "feed": cls.INSTAGRAM_FEED_4_5,
            "4:5": cls.INSTAGRAM_FEED_4_5,
            "instagram_feed_4_5": cls.INSTAGRAM_FEED_4_5,
            "catalog": cls.ECOMMERCE_CATALOG_1_1,
            "ecommerce": cls.ECOMMERCE_CATALOG_1_1,
            "1:1": cls.ECOMMERCE_CATALOG_1_1,
            "ecommerce_catalog_1_1": cls.ECOMMERCE_CATALOG_1_1,
            "none": cls.NONE,
        }
        if norm in aliases:
            return aliases[norm]
        for member in cls:
            if member.value == norm or member.name.lower() == norm:
                return member
        return cls.NONE

    from_string = from_str


class ReferenceMode(str, Enum):
    """Workflow mode when processing a reference image."""

    NONE = "none"
    RESTORE_UPSCALE = "restore_upscale"  # 1:1 Identity restoration and optical remastering
    TRANSFORM_ADAPT = "transform_adapt"  # Aesthetic/scene adaptation with biometric subject lock
    OUTPAINT_FULL_BODY = "outpaint_full_body"  # Outpaint medium shot to full body head-to-toe
    DEPIXELATE_GFX100RF = "depixelate_gfx100rf"  # Universal De-Pixelate + Upscale Restoration (GFX100RF 102MP + Skin Realism Override)
    IDENTITY_LOCK = "identity_lock"  # Strict anatomical and biometric identity lock (zero gender, age, mass, or bone drift)
    PRODUCT_LOCK = "product_lock"  # 100% Commercial SKU lock (cap geometry, label kerning, seams, material finish, SKU color)
    RECONSTRUCTION_LOCK_4X = "reconstruction_lock_4x"  # Professional 4X Reconstruction Lock (source-locked deep SR, anti-hallucination)

    @classmethod
    def from_str(cls, value: Optional[str]) -> ReferenceMode:
        """Parse mode safely with aliases."""
        if not value:
            return cls.NONE
        normalized = value.strip().lower().replace("-", "_").replace(" ", "_")
        alias_map = {
            "depixelate": cls.DEPIXELATE_GFX100RF,
            "depixelate_upscale": cls.DEPIXELATE_GFX100RF,
            "gfx100rf": cls.DEPIXELATE_GFX100RF,
            "gfx100rf_restore": cls.DEPIXELATE_GFX100RF,
            "depixelate_gfx100rf": cls.DEPIXELATE_GFX100RF,
            "restore": cls.RESTORE_UPSCALE,
            "restore_upscale": cls.RESTORE_UPSCALE,
            "transform": cls.TRANSFORM_ADAPT,
            "transform_adapt": cls.TRANSFORM_ADAPT,
            "outpaint": cls.OUTPAINT_FULL_BODY,
            "outpaint_full_body": cls.OUTPAINT_FULL_BODY,
            "identity_lock": cls.IDENTITY_LOCK,
            "identity": cls.IDENTITY_LOCK,
            "id_lock": cls.IDENTITY_LOCK,
            "reference_lock": cls.IDENTITY_LOCK,
            "product_lock": cls.PRODUCT_LOCK,
            "product": cls.PRODUCT_LOCK,
            "product_crop": cls.PRODUCT_LOCK,
            "product_reference": cls.PRODUCT_LOCK,
            "sku_lock": cls.PRODUCT_LOCK,
            "packshot": cls.PRODUCT_LOCK,
            "commercial_lock": cls.PRODUCT_LOCK,
            "reconstruction_lock_4x": cls.RECONSTRUCTION_LOCK_4X,
            "recon_4x": cls.RECONSTRUCTION_LOCK_4X,
            "4x_recon": cls.RECONSTRUCTION_LOCK_4X,
            "4x_reconstruction": cls.RECONSTRUCTION_LOCK_4X,
            "reconstruction_lock": cls.RECONSTRUCTION_LOCK_4X,
            "professional_4x": cls.RECONSTRUCTION_LOCK_4X,
            "p4x_lock": cls.RECONSTRUCTION_LOCK_4X,
        }
        if normalized in alias_map:
            return alias_map[normalized]
        for member in cls:
            if member.value == normalized:
                return member
        return cls.NONE

    from_string = from_str


class SuperResolutionBackend(str, Enum):
    """Deep super-resolution model backends for source-locked 4X reconstruction."""

    REAL_ESRNET_X4PLUS = "realesrnet_x4plus"  # Maximum structural fidelity baseline, minimal hallucination
    SWINIR_M_X4 = "swinir_m_x4"  # Balanced transformer-based restoration
    REAL_ESRGAN_X4V3 = "realesrgan_x4v3"  # Controlled perceptual texture with low denoising strength (-dn 0.15)
    REAL_ESRGAN_X4PLUS = "realesrgan_x4plus"  # Aggressive perceptual sharpness
    HAT_S_X4 = "hat_s_x4"  # Hybrid attention transformer (CPU-manageable HAT-S)
    PIL_CONSERVATIVE = "pil_conservative"  # Zero-dependency local mathematical baseline

    @classmethod
    def from_str(cls, value: Optional[str]) -> SuperResolutionBackend:
        if not value:
            return cls.REAL_ESRNET_X4PLUS
        norm = value.strip().lower().replace("-", "_").replace(" ", "_").replace(".", "_")
        aliases = {
            "realesrnet": cls.REAL_ESRNET_X4PLUS,
            "realesrnet_x4": cls.REAL_ESRNET_X4PLUS,
            "realesrnet_x4plus": cls.REAL_ESRNET_X4PLUS,
            "fidelity": cls.REAL_ESRNET_X4PLUS,
            "swinir": cls.SWINIR_M_X4,
            "swinir_m": cls.SWINIR_M_X4,
            "swinir_m_x4": cls.SWINIR_M_X4,
            "realesrgan_v3": cls.REAL_ESRGAN_X4V3,
            "realesrgan_x4v3": cls.REAL_ESRGAN_X4V3,
            "realesr_general_x4v3": cls.REAL_ESRGAN_X4V3,
            "balanced": cls.REAL_ESRGAN_X4V3,
            "realesrgan": cls.REAL_ESRGAN_X4PLUS,
            "realesrgan_plus": cls.REAL_ESRGAN_X4PLUS,
            "realesrgan_x4plus": cls.REAL_ESRGAN_X4PLUS,
            "perceptual": cls.REAL_ESRGAN_X4PLUS,
            "hat": cls.HAT_S_X4,
            "hat_s": cls.HAT_S_X4,
            "hat_s_x4": cls.HAT_S_X4,
            "pil": cls.PIL_CONSERVATIVE,
            "pil_conservative": cls.PIL_CONSERVATIVE,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.REAL_ESRNET_X4PLUS


@dataclass
class ReconstructionLock4XSpec:
    """Specification for the Professional 4X Reconstruction Lock Protocol."""

    backend: SuperResolutionBackend = SuperResolutionBackend.REAL_ESRNET_X4PLUS
    denoise_strength: float = 0.15  # Recommended range: 0.10 - 0.25 (preserves source texture)
    tile_size: int = 256  # 128 for low-RAM CPU, 256 for balanced
    tile_pad: int = 16
    blend_ratio: float = 0.20  # 15% - 30% blend of sharper detail into fidelity master
    protect_sky_haze: bool = True  # Exclude sky, fog, atmospheric depth from sharpening/noise amplification
    anti_model_stacking: bool = True  # Prohibit serial model stacking that compounds hallucination
    linear_scale: int = 4  # Strictly 4X linear (16X pixel count)

    def to_dict(self) -> dict[str, Any]:
        return {
            "backend": self.backend.value,
            "denoise_strength": self.denoise_strength,
            "tile_size": self.tile_size,
            "tile_pad": self.tile_pad,
            "blend_ratio": self.blend_ratio,
            "protect_sky_haze": self.protect_sky_haze,
            "anti_model_stacking": self.anti_model_stacking,
            "linear_scale": self.linear_scale,
        }


class BodyVolumeRegion(str, Enum):
    """Anatomical regions for reference-guided proportional volume increases."""

    BICEPS = "biceps"
    CHEST = "chest"
    GUT = "gut"
    LEGS = "legs"
    WAIST = "waist"
    FULL_BODY = "full_body"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[BodyVolumeRegion]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "bicep": cls.BICEPS,
            "biceps": cls.BICEPS,
            "arms": cls.BICEPS,
            "upper_arms": cls.BICEPS,
            "chest": cls.CHEST,
            "pecs": cls.CHEST,
            "torso": cls.CHEST,
            "gut": cls.GUT,
            "abdomen": cls.GUT,
            "belly": cls.GUT,
            "stomach": cls.GUT,
            "legs": cls.LEGS,
            "thighs": cls.LEGS,
            "quads": cls.LEGS,
            "waist": cls.WAIST,
            "midsection": cls.WAIST,
            "love_handles": cls.WAIST,
            "hips": cls.WAIST,
            "full_body": cls.FULL_BODY,
            "full": cls.FULL_BODY,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return None

    from_string = from_str


class VolumeDegree(str, Enum):
    """Degree of proportional body volume enlargement."""

    SUBTLE = "subtle"
    NOTICEABLE_RESTRAINED = "noticeable_restrained"
    HEAVY_WEIGHT = "heavy_weight"
    CALIBRATED = "calibrated"

    @classmethod
    def from_str(cls, value: Optional[str]) -> VolumeDegree:
        if not value:
            return cls.NOTICEABLE_RESTRAINED
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "subtle": cls.SUBTLE,
            "slight": cls.SUBTLE,
            "minor": cls.SUBTLE,
            "mild": cls.SUBTLE,
            "light": cls.SUBTLE,
            "noticeable": cls.NOTICEABLE_RESTRAINED,
            "restrained": cls.NOTICEABLE_RESTRAINED,
            "noticeable_restrained": cls.NOTICEABLE_RESTRAINED,
            "moderate": cls.NOTICEABLE_RESTRAINED,
            "medium": cls.NOTICEABLE_RESTRAINED,
            "natural": cls.NOTICEABLE_RESTRAINED,
            "athletic": cls.NOTICEABLE_RESTRAINED,
            "muscular": cls.NOTICEABLE_RESTRAINED,
            "cut": cls.NOTICEABLE_RESTRAINED,
            "significant": cls.HEAVY_WEIGHT,
            "heavy": cls.HEAVY_WEIGHT,
            "heavy_weight": cls.HEAVY_WEIGHT,
            "heavyweight": cls.HEAVY_WEIGHT,
            "large": cls.HEAVY_WEIGHT,
            "bulky": cls.HEAVY_WEIGHT,
            "bodybuilder": cls.HEAVY_WEIGHT,
            "powerlifter": cls.HEAVY_WEIGHT,
            "calibrated": cls.CALIBRATED,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.NOTICEABLE_RESTRAINED

    from_string = from_str


class MaterialStyle(str, Enum):
    """Dimensional 4D and material surface finish styles."""

    NONE = "none"
    LATEX_GLOSS = "latex_gloss"
    LIQUID_GLASS = "liquid_glass"
    DIELECTRIC_ACRYLIC = "dielectric_acrylic"
    MATTE_FINISH = "matte_finish"
    BARYTA_SURFACE = "baryta_surface"
    POLISHED_VINYL = "polished_vinyl"
    ANODIZED_ALUMINUM = "anodized_aluminum"
    VOLUMETRIC_4D = "volumetric_4d"

    @classmethod
    def from_str(cls, value: Optional[str]) -> MaterialStyle:
        if not value:
            return cls.NONE
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "latex": cls.LATEX_GLOSS,
            "latex_gloss": cls.LATEX_GLOSS,
            "shiny_latex": cls.LATEX_GLOSS,
            "glossy_latex": cls.LATEX_GLOSS,
            "black_latex": cls.LATEX_GLOSS,
            "glass": cls.LIQUID_GLASS,
            "liquid_glass": cls.LIQUID_GLASS,
            "glass_cube": cls.LIQUID_GLASS,
            "blown_glass": cls.LIQUID_GLASS,
            "acrylic": cls.DIELECTRIC_ACRYLIC,
            "dielectric_acrylic": cls.DIELECTRIC_ACRYLIC,
            "lucite": cls.DIELECTRIC_ACRYLIC,
            "perspex": cls.DIELECTRIC_ACRYLIC,
            "vinyl": cls.POLISHED_VINYL,
            "pvc": cls.POLISHED_VINYL,
            "polished_vinyl": cls.POLISHED_VINYL,
            "aluminum": cls.ANODIZED_ALUMINUM,
            "metallic": cls.ANODIZED_ALUMINUM,
            "anodized_aluminum": cls.ANODIZED_ALUMINUM,
            "matte": cls.MATTE_FINISH,
            "matte_finish": cls.MATTE_FINISH,
            "baryta": cls.BARYTA_SURFACE,
            "baryta_surface": cls.BARYTA_SURFACE,
            "volumetric_4d": cls.VOLUMETRIC_4D,
            "volumetric": cls.VOLUMETRIC_4D,
            "4d": cls.VOLUMETRIC_4D,
            "none": cls.NONE,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.NONE

    from_string = from_str


class BackgroundStyle(str, Enum):
    """Background treatment and studio isolation styles."""

    DEFAULT = "default"
    OPAQUE_BLACK_BLURRED = "opaque_black_blurred"
    PURE_BLACK_BLUR = "pure_black_blur"
    MINIMALIST_STUDIO_GREY = "minimalist_studio_grey"
    CLEAN_HIGH_KEY_WHITE = "clean_high_key_white"
    STUDIO_SEAMLESS = "studio_seamless"
    OUTDOOR_NATURAL = "outdoor_natural"

    @classmethod
    def from_str(cls, value: Optional[str]) -> BackgroundStyle:
        if not value:
            return cls.DEFAULT
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "pure_black_blur": cls.PURE_BLACK_BLUR,
            "black_blur": cls.PURE_BLACK_BLUR,
            "soft_black": cls.PURE_BLACK_BLUR,
            "black_background": cls.PURE_BLACK_BLUR,
            "minimalist_studio_grey": cls.MINIMALIST_STUDIO_GREY,
            "studio_grey": cls.MINIMALIST_STUDIO_GREY,
            "grey_cyclorama": cls.MINIMALIST_STUDIO_GREY,
            "clean_high_key_white": cls.CLEAN_HIGH_KEY_WHITE,
            "high_key": cls.CLEAN_HIGH_KEY_WHITE,
            "pure_white": cls.CLEAN_HIGH_KEY_WHITE,
            "opaque_black": cls.OPAQUE_BLACK_BLURRED,
            "black_opaque": cls.OPAQUE_BLACK_BLURRED,
            "opaque_black_blurred": cls.OPAQUE_BLACK_BLURRED,
            "blurred_black": cls.OPAQUE_BLACK_BLURRED,
            "black": cls.OPAQUE_BLACK_BLURRED,
            "studio": cls.STUDIO_SEAMLESS,
            "seamless": cls.STUDIO_SEAMLESS,
            "studio_seamless": cls.STUDIO_SEAMLESS,
            "outdoor": cls.OUTDOOR_NATURAL,
            "natural": cls.OUTDOOR_NATURAL,
            "outdoor_natural": cls.OUTDOOR_NATURAL,
            "default": cls.DEFAULT,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.DEFAULT

    from_string = from_str


class PaperProfile(str, Enum):
    """Exhibition and print lab fine-art paper profiles."""

    NONE = "none"
    MATTE_COTTON = "matte_cotton"
    LUSTER = "luster"
    GLOSSY = "glossy"
    BARYTA = "baryta"
    CANVAS = "canvas"

    @classmethod
    def from_str(cls, value: Optional[str]) -> PaperProfile:
        if not value:
            return cls.NONE
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "matte": cls.MATTE_COTTON,
            "cotton": cls.MATTE_COTTON,
            "matte_cotton": cls.MATTE_COTTON,
            "cotton_rag": cls.MATTE_COTTON,
            "rag": cls.MATTE_COTTON,
            "hahnemuhle": cls.MATTE_COTTON,
            "luster": cls.LUSTER,
            "lustre": cls.LUSTER,
            "semi_gloss": cls.LUSTER,
            "satin": cls.LUSTER,
            "glossy": cls.GLOSSY,
            "gloss": cls.GLOSSY,
            "high_gloss": cls.GLOSSY,
            "baryta": cls.BARYTA,
            "baryta_photographique": cls.BARYTA,
            "fiber": cls.BARYTA,
            "exhibition_baryta": cls.BARYTA,
            "canvas": cls.CANVAS,
            "stretched_canvas": cls.CANVAS,
            "none": cls.NONE,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.NONE

    from_string = from_str


class RenderingIntent(str, Enum):
    """ICC color management rendering intent."""

    RELATIVE_COLORIMETRIC = "relative_colorimetric"
    PERCEPTUAL = "perceptual"

    @classmethod
    def from_str(cls, value: Optional[str]) -> RenderingIntent:
        if not value:
            return cls.RELATIVE_COLORIMETRIC
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        aliases = {
            "relative": cls.RELATIVE_COLORIMETRIC,
            "relative_colorimetric": cls.RELATIVE_COLORIMETRIC,
            "colorimetric": cls.RELATIVE_COLORIMETRIC,
            "perceptual": cls.PERCEPTUAL,
            "photographic": cls.PERCEPTUAL,
        }
        if norm in aliases:
            return aliases[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.RELATIVE_COLORIMETRIC

    from_string = from_str


@dataclass
class BodyMorphologyConfig:
    """Anatomical body volume scaling and morphology parameters."""

    weight_lb: Optional[float] = None
    volume_regions: list[str] = field(default_factory=list)
    target_regions: dict[BodyVolumeRegion, VolumeDegree] = field(default_factory=dict)
    degree: VolumeDegree = VolumeDegree.NOTICEABLE_RESTRAINED
    proportionality_lock: bool = True
    natural_asymmetry_lock: bool = True
    gravitational_tissue_behavior: bool = True
    clothing_conformity: bool = True
    anti_exaggeration: bool = True

    @classmethod
    def from_str(cls, text: Optional[str], weight_lb: Optional[float] = None) -> BodyMorphologyConfig:
        cfg = cls(weight_lb=weight_lb)
        if not text:
            return cfg
        parts = [p.strip() for p in text.split(",") if p.strip()]
        for p in parts:
            if ":" in p:
                r_str, d_str = p.split(":", 1)
                reg = BodyVolumeRegion.from_str(r_str)
                deg = VolumeDegree.from_str(d_str)
                if reg:
                    cfg.target_regions[reg] = deg
                    cfg.volume_regions.append(reg.value)
            else:
                reg = BodyVolumeRegion.from_str(p)
                if reg:
                    cfg.target_regions[reg] = cfg.degree
                    cfg.volume_regions.append(reg.value)
                else:
                    cfg.volume_regions.append(p)
        return cfg

    from_string = from_str


@dataclass
class PrintSpec:
    """Print lab calibration specification."""

    width_in: float = 0.0
    height_in: float = 0.0
    ppi: int = 300
    paper: PaperProfile = PaperProfile.NONE
    rendering_intent: RenderingIntent = RenderingIntent.RELATIVE_COLORIMETRIC


class StressProbe(str, Enum):
    """PFEP v1.0 canonical stress diagnostic probes for portrait & render fidelity."""

    NONE = "none"
    MASTER_PORTRAIT_LOCK = "master_portrait_lock"
    OUTPAINT_LENS_HONEST = "outpaint_lens_honest"
    STRESS_HARD_KEY = "stress_hard_key"
    STRESS_CROSS_POLARIZED = "stress_cross_polarized"
    STRESS_GLASSES_REFLECTIONS = "stress_glasses_reflections"
    STRESS_SEATED_COMPRESSION = "stress_seated_compression"
    STRESS_STANDING_COMPRESSION = "stress_standing_compression"
    STRESS_BACKGROUND_SCALE = "stress_background_scale"
    STRESS_HAIR_SPECULAR = "stress_hair_specular"
    STRESS_SHADOW_COLOR = "stress_shadow_color"

    @classmethod
    def from_str(cls, value: Optional[str]) -> StressProbe:
        """Parse probe case-insensitively with friendly aliases."""
        if not value:
            return cls.NONE
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
        alias_map = {
            "none": cls.NONE,
            "master": cls.MASTER_PORTRAIT_LOCK,
            "master_lock": cls.MASTER_PORTRAIT_LOCK,
            "master_portrait_lock": cls.MASTER_PORTRAIT_LOCK,
            "outpaint": cls.OUTPAINT_LENS_HONEST,
            "outpaint_lens": cls.OUTPAINT_LENS_HONEST,
            "outpaint_lens_honest": cls.OUTPAINT_LENS_HONEST,
            "lens_honest": cls.OUTPAINT_LENS_HONEST,
            "hard_key": cls.STRESS_HARD_KEY,
            "stress_hard_key": cls.STRESS_HARD_KEY,
            "cross_polarized": cls.STRESS_CROSS_POLARIZED,
            "cross_polarization": cls.STRESS_CROSS_POLARIZED,
            "stress_cross_polarized": cls.STRESS_CROSS_POLARIZED,
            "glasses": cls.STRESS_GLASSES_REFLECTIONS,
            "glasses_reflections": cls.STRESS_GLASSES_REFLECTIONS,
            "stress_glasses_reflections": cls.STRESS_GLASSES_REFLECTIONS,
            "seated": cls.STRESS_SEATED_COMPRESSION,
            "seated_compression": cls.STRESS_SEATED_COMPRESSION,
            "stress_seated_compression": cls.STRESS_SEATED_COMPRESSION,
            "standing": cls.STRESS_STANDING_COMPRESSION,
            "standing_compression": cls.STRESS_STANDING_COMPRESSION,
            "stress_standing_compression": cls.STRESS_STANDING_COMPRESSION,
            "background_scale": cls.STRESS_BACKGROUND_SCALE,
            "stress_background_scale": cls.STRESS_BACKGROUND_SCALE,
            "hair_specular": cls.STRESS_HAIR_SPECULAR,
            "stress_hair_specular": cls.STRESS_HAIR_SPECULAR,
            "hair": cls.STRESS_HAIR_SPECULAR,
            "shadow_color": cls.STRESS_SHADOW_COLOR,
            "stress_shadow_color": cls.STRESS_SHADOW_COLOR,
            "shadow": cls.STRESS_SHADOW_COLOR,
        }
        if norm in alias_map:
            return alias_map[norm]
        for m in cls:
            if m.value == norm or m.name.lower() == norm:
                return m
        return cls.NONE

    from_string = from_str

    @property
    def directive_text(self) -> str:
        """Photographic directive for the diagnostic probe."""
        directives = {
            self.MASTER_PORTRAIT_LOCK: (
                "PFEP Diagnostic Probe [01: Master Portrait Lock]: Baseline reference anchor. "
                "Lock exact facial geometry, bone structure, ear morphology, natural skin micro-relief, "
                "and directional studio lighting fidelity."
            ),
            self.OUTPAINT_LENS_HONEST: (
                "PFEP Diagnostic Probe [02: Lens-Honest Outpaint]: Lock subject absolute scale, camera distance, "
                "and focal length perspective. Expand frame without wide-angle fish-eye curvature, perspective drift, "
                "or subject biometric morphing."
            ),
            self.STRESS_HARD_KEY: (
                "PFEP Diagnostic Probe [03: Hard Key Stress]: Harsh 50-60° key light, near-zero fill, deep negative fill. "
                "Skin pores, epidermal micro-ridges, and fine vellus texture must remain fully resolved inside deep shadow transitions."
            ),
            self.STRESS_CROSS_POLARIZED: (
                "PFEP Diagnostic Probe [04: Cross-Polarized Surface Stress]: Cross-polarized lighting emulation. "
                "Completely extinguish specular surface glare. Resolve pure subsurface melanin and blood flow micro-chroma without waxy synthetic flattening."
            ),
            self.STRESS_GLASSES_REFLECTIONS: (
                "PFEP Diagnostic Probe [05: Glasses Reflections Stress]: Physically plausible multi-element lens reflections. "
                "Eyes and pupils must remain sharply resolved and visible through spectacles; zero opaque white rectangle artifacts or floating highlights."
            ),
            self.STRESS_SEATED_COMPRESSION: (
                "PFEP Diagnostic Probe [06: Seated Pose Compression]: Subject seated naturally. Lock camera optical height, "
                "distance, and telephoto normal compression identically to standing reference; zero perspective stretching."
            ),
            self.STRESS_STANDING_COMPRESSION: (
                "PFEP Diagnostic Probe [07: Standing Pose Compression]: Subject standing upright. Camera distance, "
                "lens focal compression, and optical perspective locked identically to seated reference."
            ),
            self.STRESS_BACKGROUND_SCALE: (
                "PFEP Diagnostic Probe [08: Background Scale Stress]: Extend environmental framing subtly while locking "
                "subject scale, foreground-to-background spatial compression, and lens field-of-view without focal widening."
            ),
            self.STRESS_HAIR_SPECULAR: (
                "PFEP Diagnostic Probe [09: Hair Specular Dynamics]: 55-65° directional rim/key lighting. "
                "Resolve anisotropic specular response across individual hair fibers and follicles without plastic helmet sheen or solid clump artifacts."
            ),
            self.STRESS_SHADOW_COLOR: (
                "PFEP Diagnostic Probe [10: Shadow Color Integrity]: Strong negative fill on unlit cheek. "
                "Shadow-side skin must retain organic warm undertones, natural melanin, and chromatic integrity without synthetic gray, cyan, or muddy casts."
            ),
        }
        return directives.get(self, "")


@dataclass
class LightingEnvironmentSpec:
    """Gallery exhibition lighting environment and spectral calibration specification."""

    cct_kelvin: int = 5000  # Color temperature in Kelvin (5000K daylight/gallery standard)
    illuminance_lux: int = 500  # Gallery illuminance level (400-500 lux standard)
    spectral_cri: float = 98.0  # TM-30 / CRI spectral fidelity
    wall_surround: str = "Neutral Gray 18%"  # Surround wall reflectance / color


@dataclass
class SeriesCohesionSpec:
    """Exhibition series visual cohesion calibration matrix."""

    anchor_image_id: Optional[str] = None
    gallery_zone: Optional[str] = None
    midtone_density: float = 1.0
    shadow_depth: float = 1.0
    highlight_rolloff: float = 1.0


@dataclass
class RendererScorecard:
    """PFEP v1.0 8-Axis Renderer Diagnostic Scorecard with Identity hard gating.

    8 Canonical Axes (0-2 each, max 16):
      1. identity: 0=drift, 1=minor deviation, 2=locked (HARD GATE: must be 2 to pass)
      2. focus: 0=soft, 1=acceptable, 2=tack sharp
      3. skin_texture: 0=plastic, 1=mixed, 2=natural pores
      4. lighting_honesty: 0=fake, 1=passable, 2=physically coherent
      5. glasses: 0=broken, 1=acceptable, 2=plausible
      6. hair: 0=helmet-like, 1=mixed, 2=strand/specular breakup
      7. geometry: 0=warped, 1=minor errors, 2=correct
      8. background_scale: 0=drifting, 1=minor drift, 2=invariant
    """

    def __init__(
        self,
        identity: int = 0,
        focus: int = 0,
        skin_texture: int = 0,
        lighting_honesty: int = 0,
        glasses: int = 0,
        hair: int = 0,
        geometry: int = 0,
        background_scale: int = 0,
        notes: str = "",
        **kwargs: Any,
    ):
        self.identity = identity
        self.focus = kwargs.get("material_acutance", focus)
        self.skin_texture = kwargs.get("skin_micro_texture", skin_texture)
        self.lighting_honesty = kwargs.get("lighting", lighting_honesty)
        self.glasses = kwargs.get("optical_physics", glasses)
        self.hair = kwargs.get("hair_dynamics", hair)
        self.geometry = geometry
        self.background_scale = kwargs.get("color_fidelity", background_scale)
        self.notes = notes

    # Backward compatibility aliases
    @property
    def skin_micro_texture(self) -> int:
        return self.skin_texture

    @skin_micro_texture.setter
    def skin_micro_texture(self, val: int) -> None:
        self.skin_texture = val

    @property
    def lighting(self) -> int:
        return self.lighting_honesty

    @lighting.setter
    def lighting(self, val: int) -> None:
        self.lighting_honesty = val

    @property
    def optical_physics(self) -> int:
        return self.glasses

    @optical_physics.setter
    def optical_physics(self, val: int) -> None:
        self.glasses = val

    @property
    def hair_dynamics(self) -> int:
        return self.hair

    @hair_dynamics.setter
    def hair_dynamics(self, val: int) -> None:
        self.hair = val

    @property
    def material_acutance(self) -> int:
        return self.focus

    @material_acutance.setter
    def material_acutance(self, val: int) -> None:
        self.focus = val

    @property
    def color_fidelity(self) -> int:
        return self.background_scale

    @color_fidelity.setter
    def color_fidelity(self, val: int) -> None:
        self.background_scale = val

    @property
    def total_score(self) -> int:
        """Sum of all 8 evaluation axes (max 16)."""
        return (
            self.identity
            + self.focus
            + self.skin_texture
            + self.lighting_honesty
            + self.glasses
            + self.hair
            + self.geometry
            + self.background_scale
        )

    @property
    def passed(self) -> bool:
        """PFEP v1.0 Pass Gate: Identity == 2 AND total_score >= 12."""
        return self.identity == 2 and self.total_score >= 12

    def to_dict(self) -> dict[str, Any]:
        """Convert scorecard to dictionary with pass/fail evaluation."""
        return {
            "identity": self.identity,
            "focus": self.focus,
            "skin_texture": self.skin_texture,
            "lighting_honesty": self.lighting_honesty,
            "glasses": self.glasses,
            "hair": self.hair,
            "geometry": self.geometry,
            "background_scale": self.background_scale,
            "total_score": self.total_score,
            "max_score": 16,
            "identity_gate_passed": self.identity == 2,
            "passed": self.passed,
            "notes": self.notes,
        }

    def to_markdown(self) -> str:
        """Render scorecard as Markdown table."""
        status = "**PASSED**" if self.passed else "**FAILED**"
        gate = "PASSED" if self.identity == 2 else "FAILED (Hard Gate Violation: must be 2)"
        id_labels = ["Drift", "Minor Deviation", "Locked (PASS)"]
        focus_labels = ["Soft", "Acceptable", "Tack Sharp"]
        skin_labels = ["Plastic", "Mixed", "Natural Pores"]
        light_labels = ["Fake", "Passable", "Physically Coherent"]
        glasses_labels = ["Broken", "Acceptable", "Plausible"]
        hair_labels = ["Helmet-like", "Mixed", "Strand/Specular Breakup"]
        geo_labels = ["Warped", "Minor Errors", "Correct"]
        bg_labels = ["Drifting", "Minor Drift", "Invariant"]

        return f"""### PFEP v1.0 Renderer Scorecard: {status}
- **Total Score**: {self.total_score} / 16
- **Identity Hard Gate**: {gate}

| Axis | Score | Rating |
| :--- | :--- | :--- |
| Identity | {self.identity}/2 | {id_labels[min(2, max(0, self.identity))]} |
| Focus | {self.focus}/2 | {focus_labels[min(2, max(0, self.focus))]} |
| Skin Texture | {self.skin_texture}/2 | {skin_labels[min(2, max(0, self.skin_texture))]} |
| Lighting Honesty | {self.lighting_honesty}/2 | {light_labels[min(2, max(0, self.lighting_honesty))]} |
| Glasses | {self.glasses}/2 | {glasses_labels[min(2, max(0, self.glasses))]} |
| Hair | {self.hair}/2 | {hair_labels[min(2, max(0, self.hair))]} |
| Geometry | {self.geometry}/2 | {geo_labels[min(2, max(0, self.geometry))]} |
| Background Scale | {self.background_scale}/2 | {bg_labels[min(2, max(0, self.background_scale))]} |

**Notes**: {self.notes or 'None'}
"""



@dataclass
class ReferenceImageInput:
    """Metadata and controls for reference-guided generation and anti-drift locks."""

    filename: Optional[str] = None
    file_path: Optional[str] = None
    data_uri: Optional[str] = None  # Base64 data URI if uploaded via web browser
    mode: ReferenceMode = ReferenceMode.NONE
    denoise_strength: float = 0.35  # 0.30-0.45 for restoration, 0.60-0.75 for transformation
    fidelity_lock: float = 0.95  # 0.0 - 1.0 (extreme anti-drift intensity)
    detected_aspect_ratio: Optional[str] = None
    subject_description: Optional[str] = None
    preserved_elements: list[str] = field(
        default_factory=lambda: [
            "facial geometry",
            "eye structure and gaze",
            "facial bone structure",
            "biometric identity",
            "anatomical proportions",
        ]
    )


@dataclass
class NegativeShield:
    """Categorized anti-artifact and anti-synthetic constraints."""

    render_defects: list[str] = field(
        default_factory=lambda: [
            "CGI",
            "3D render",
            "illustration",
            "digital sharpening halos",
            "chromatic aberration",
            "denoise smearing",
            "compression artifacts",
            "focus miss",
            "double edges",
            "ringing",
            "oversharpening",
            "crunchy HDR",
            "perspective drift",
            "unmotivated bokeh",
            "fake shallow depth of field",
            "tilted horizon",
            "ghost faces in crowd",
            "duplicated people",
            "melted bodies",
            "melted limbs",
            "uniform smear wall",
            "blur deforming subject anatomy",
            "single-direction blur",
            "soft subject face",
            "blurred eyes",
            "smudged features",
            "glow",
            "halation bloom",
        ]
    )
    skin_and_lighting_drift: list[str] = field(
        default_factory=lambda: [
            "airbrushed skin",
            "plastic poreless skin",
            "glamour retouching",
            "computational bokeh",
            "beauty filter glow",
            "blown highlights",
            "crushed shadows",
            "broadcast video sharpness",
            "clipped digital highlights",
            "crushed blacks",
            "oversaturated rec709 tint",
            "artificial pore carving",
            "invented eyelashes",
            "invented fur strands",
            "unmotivated teal-orange grading",
        ]
    )
    anatomical_drift: list[str] = field(
        default_factory=lambda: [
            "mutated hands",
            "extra digits",
            "fused limbs",
            "asymmetrical pupil dilation",
            "deformed facial features",
        ]
    )
    anti_drift_tokens: list[str] = field(
        default_factory=lambda: [
            "facial morphing",
            "feature drift",
            "identity loss",
            "altered facial bone structure",
            "phantom limbs",
            "unnatural eye color shift",
            "warped silhouette",
            "hallucinated background elements",
            "extra fingers",
            "structural divergence",
            "identity drift",
            "facial reconstruction artifacts",
            "gender reinterpretation",
            "age alteration",
            "body type modification",
            "body slimming",
            "body reshaping",
            "facial restructuring",
            "jawline softening",
            "feature feminization or masculinization",
            "weight redistribution",
            "skin smoothing beyond realism",
            "costume styling",
            "flashy accessories",
            "fashion reinterpretation",
            "beard pattern alteration",
        ]
    )

    branding_and_text: list[str] = field(
        default_factory=lambda: [
            "text",
            "watermark",
            "logo",
            "brand name",
            "typography",
            "label",
            "signature",
            "letters",
            "words",
            "trademark",
            "branding",
            "advertisement",
            "graphic design elements",
            "captions",
            "subtitles",
            "barcodes",
            "timestamps",
            "invented text",
            "garbled typography",
            "product-design drift",
            "logo drift",
        ]
    )
    compression_and_quality: list[str] = field(
        default_factory=lambda: [
            "JPEG compression artifacts",
            "low bitrate",
            "banding",
            "chroma subsampling",
            "lossy compression",
            "pixelation",
            "digital noise smearing",
            "posterization",
            "compression banding",
            "chroma subsampling artifacts",
            "video noise clipping",
        ]
    )
    outpaint_drift: list[str] = field(
        default_factory=lambda: [
            "mismatched shoes",
            "inconsistent clothing folds",
            "wrong shadows",
            "twisted legs",
            "floating feet",
            "distorted scale",
            "deformed footwear",
            "mismatched lighting",
        ]
    )
    skin_realism_defects: list[str] = field(
        default_factory=lambda: [
            "plastic skin",
            "wax skin",
            "porcelain skin",
            "airbrushed texture",
            "over-smoothed skin",
            "fake pores",
            "pore stamping",
            "engraved skin",
            "embossed skin",
            "carved skin",
            "swirl texture",
            "repeating micro-patterns",
            "lace-like facial texture",
            "worm-like texture",
            "AI skin grain",
            "painted skin",
            "CGI skin",
            "hyper-sharpened pores",
            "overprocessed HDR skin",
            "synthetic cheek texture",
            "fake forehead texture",
            "fake neck texture",
            "decorative skin detail",
            "Velvia punch",
            "Classic Chrome grading",
            "Acros conversion of color sources",
            "invented fabric patterns",
            "fake shallow depth of field",
            "synthetic bokeh balls",
            "rolling shutter artifacts",
            "smartphone computational look",
        ]
    )
    product_drift: list[str] = field(
        default_factory=lambda: [
            "wrong cap geometry",
            "distorted cap",
            "wrong closure form factor",
            "incorrect label kerning",
            "label typography drift",
            "hallucinated label text",
            "garbled product text",
            "wrong sku color",
            "product color shift",
            "missing mold seams",
            "distorted parting lines",
            "incorrect material finish",
            "plastic bottle instead of glass",
            "warped container silhouette",
            "distorted packaging proportions",
            "misplaced logo",
            "floating label",
            "deformed packaging",
            "asymmetrical bottle shoulders",
            "inaccurate container volume",
            "synthetic label gloss",
            "missing neck threads",
        ]
    )
    hand_drift: list[str] = field(
        default_factory=lambda: [
            "fused digits",
            "clipping fingers",
            "extra phalanges",
            "rubber knuckles",
            "dislocated thumb",
            "webbed fingers",
            "missing joints",
            "deformed fingernails",
            "backwards thumb",
            "six fingers",
            "four fingers",
            "floating fingers",
            "amorphous fingertip pads",
            "plastic hand texture",
            "unconnected thumb base",
            "missing knuckles",
            "finger through solid object",
            "fingers passing through object",
            "deformed thenar eminence",
            "missing lunula",
            "press-on plastic nails",
            "fused finger flesh",
            "noodle fingers",
            "missing fingernails",
            "elongated alien fingers",
            "extra fingers",
            "missing fingers",
            "fused fingers",
            "polydactyly",
            "ectrodactyly",
            "webbed digits",
            "floating knuckles",
        ]
    )
    body_distortion: list[str] = field(
        default_factory=lambda: [
            "extreme bodybuilding",
            "cartoon proportions",
            "balloon muscles",
            "impossible muscle insertions",
            "hyper-inflated limbs",
            "extreme vascularity",
            "unnatural six-pack",
            "deformed limbs",
            "balloon anatomy",
            "plastic toy look",
            "unnatural bilateral symmetry",
            "pinched waist",
            "disconnected thighs",
            "competition bodybuilder",
            "comic-book musculature",
            "mirrored anatomy",
            "spherical muscles",
            "prosthetic abdomen",
            "detached body parts",
            "grotesque exaggeration",
        ]
    )
    reconstruction_drift: list[str] = field(
        default_factory=lambda: [
            "generative hallucination",
            "diffusion drift",
            "invented terrain",
            "altered geology",
            "rock strata distortion",
            "sky grain",
            "sky halos",
            "atmospheric haze noise",
            "sequential upscaling artifacts",
            "over-sharpening halos",
            "tiling boundary seams",
            "model stacking artifacts",
        ]
    )

    def all_tokens(
        self,
        include_anti_drift: bool = False,
        include_branding: bool = True,
        include_compression: bool = True,
        include_outpaint: bool = False,
        include_skin_realism: bool = True,
        include_product_drift: bool = False,
        include_hand_drift: bool = False,
        include_body_distortion: bool = False,
        include_reconstruction_drift: bool = False,
    ) -> list[str]:
        """Return a flat list of all negative tokens across selected categories."""
        tokens = list(self.render_defects + self.skin_and_lighting_drift + self.anatomical_drift)
        seen = set(tokens)

        # Baseline master anti-defect tokens to ensure all profiles get maximum protection
        for t in (
            "focus miss",
            "double edges",
            "ringing",
            "oversharpening",
            "crunchy HDR",
            "perspective drift",
            "unmotivated bokeh",
            "fake shallow depth of field",
            "tilted horizon",
            "artificial pore carving",
            "invented eyelashes",
            "unmotivated teal-orange grading",
        ):
            if t not in seen:
                tokens.append(t)
                seen.add(t)

        if include_skin_realism:
            for t in self.skin_realism_defects:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_branding:
            for t in self.branding_and_text:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_compression:
            for t in self.compression_and_quality:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_anti_drift:
            for t in self.anti_drift_tokens:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_outpaint:
            for t in self.outpaint_drift:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_product_drift:
            for t in self.product_drift:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_hand_drift:
            for t in self.hand_drift:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_body_distortion:
            for t in self.body_distortion:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        if include_reconstruction_drift:
            for t in self.reconstruction_drift:
                if t not in seen:
                    tokens.append(t)
                    seen.add(t)
        return tokens


@dataclass
class CameraProfile:
    """Hardware camera profile encapsulating optical, sensor, and physical constraints."""

    profile_id: str
    title: str
    schema_version: str = "2.0"
    purpose: str = (
        "Hardware-level optical and sensor simulation for zero-artifact photorealism."
    )
    sensor_and_optics: SensorOptics = field(
        default_factory=lambda: SensorOptics(
            camera_system="Phase One XF IQ4 150MP BSI Trichromatic"
        )
    )
    lighting_and_exposure: LightingSetup = field(default_factory=LightingSetup)
    micro_detail_and_physics: MicroPhysics = field(default_factory=MicroPhysics)
    negative_embeddings: NegativeShield = field(default_factory=NegativeShield)
    execution_directive: str = (
        "Enforce true raw-capture fidelity from a 150MP digital back. Eliminate post-processed sharpening looks, synthetic smoothing, and non-physical lighting."
    )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CameraProfile:
        """Hydrate CameraProfile from dictionary representation."""
        def _filter(cls_type: Any, d: dict[str, Any]) -> dict[str, Any]:
            if not isinstance(d, dict):
                return {}
            valid_names = {f.name for f in fields(cls_type)}
            return {k: v for k, v in d.items() if k in valid_names}

        sensor_data = data.get("sensor_and_optics", {})
        lighting_data = data.get("lighting_and_exposure", {})
        micro_data = data.get("micro_detail_and_physics", {})
        neg_data = dict(data.get("negative_embeddings", {}))
        if "content_and_branding_drift" in neg_data and "branding_and_text" not in neg_data:
            neg_data["branding_and_text"] = neg_data.pop("content_and_branding_drift")

        return cls(
            profile_id=data.get("profile_id", "custom"),
            title=data.get("title", "Custom Profile"),
            schema_version=data.get("schema_version", "2.0"),
            purpose=data.get("purpose", ""),
            sensor_and_optics=SensorOptics(**_filter(SensorOptics, sensor_data)),
            lighting_and_exposure=LightingSetup(**_filter(LightingSetup, lighting_data)),
            micro_detail_and_physics=MicroPhysics(**_filter(MicroPhysics, micro_data)),
            negative_embeddings=NegativeShield(**_filter(NegativeShield, neg_data)),
            execution_directive=data.get("execution_directive", ""),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert CameraProfile into dictionary representation."""
        return asdict(self)


@dataclass
class SceneInput:
    """Creative description of the scene and subject with optional optical overrides."""

    subject: str
    framing: Optional[str] = None
    environment: Optional[str] = None
    wardrobe: Optional[str] = None
    mood: Optional[str] = None
    aperture: Optional[str] = None
    lens: Optional[str] = None
    lighting: Optional[str] = None
    aspect_ratio: str = "4:5"
    film_stock: Optional[str] = None
    optical_filter: Optional[str] = None
    shutter_speed: Optional[str] = None
    lighting_modifier: Optional[str] = None
    custom_positives: list[str] = field(default_factory=list)
    custom_negatives: list[str] = field(default_factory=list)
    reference: Optional[ReferenceImageInput] = None
    lighting_preset: Optional[str] = None
    capture_mode: Optional[str] = None
    sharpness_protocol: bool = True
    output_resolution: Optional[str] = None
    suppress_text_branding: bool = True
    human_skin_realism: bool = True
    content_type: Optional[ContentType] = None
    text_preservation: bool = True
    camera_angle: Optional[str] = None
    color_mode: Optional[str] = None
    crowd_action: Optional[str] = None
    product_crop: Optional[str] = None
    sku_color: Optional[str] = None
    cap_geometry: Optional[str] = None
    label_kerning: Optional[str] = None
    material_finish: Optional[str] = None
    seam_geometry: Optional[str] = None
    approval_gate_100pct: bool = True
    hand_lock: bool = False
    grip_type: Optional[GripType] = None
    hand_details: Optional[str] = None
    anamorphic_squeeze: Optional[AnamorphicSqueeze] = None
    streak_flare: Optional[StreakFlare] = None
    iris_blades: Optional[IrisBladeCount] = None
    gobo: Optional[GoboPattern] = None
    grip_modifier: Optional[GripModifier] = None
    lighting_ratio: Optional[LightingRatio] = None
    copy_space: Optional[CopySpace] = None
    ad_safe_zone: Optional[AdSafeZone] = None
    body_volume: Optional[str] = None
    weight_lb: Optional[float] = None
    body_morphology: Optional[BodyMorphologyConfig] = None
    material_style: Optional[MaterialStyle] = None
    background_style: Optional[BackgroundStyle] = None
    is_4d_volumetric: bool = False
    remove_text_when_present: bool = False
    paper_profile: Optional[PaperProfile] = None
    print_spec: Optional[PrintSpec] = None
    policy_safe: bool = False
    stress_probe: Optional[StressProbe] = None
    min_file_mb: Optional[float] = None
    lighting_environment: Optional[LightingEnvironmentSpec] = None
    series_cohesion: Optional[SeriesCohesionSpec] = None
    reconstruction_lock: Optional[ReconstructionLock4XSpec] = None

    @property
    def has_product_lock(self) -> bool:
        """Return True if product reference lock or product fidelity specifications are active."""
        if self.reference and self.reference.mode == ReferenceMode.PRODUCT_LOCK:
            return True
        return bool(
            self.product_crop
            or self.sku_color
            or self.cap_geometry
            or self.label_kerning
            or self.material_finish
            or self.seam_geometry
        )

    @property
    def has_hand_lock(self) -> bool:
        """Return True if hand & finger precision gate is requested or implied by subject action."""
        if self.hand_lock or self.grip_type or self.hand_details:
            return True
        check_text = f"{self.subject} {self.framing or ''}".lower()
        return any(
            k in check_text
            for k in (
                "holding",
                "holds",
                "held",
                "hand",
                "hands",
                "finger",
                "fingers",
                "grip",
                "gripping",
                "clutching",
                "pinching",
                "grasping",
                "fingertips",
            )
        )

    @property
    def is_anamorphic(self) -> bool:
        """Return True if cinema anamorphic optics or streak flares are active."""
        if self.anamorphic_squeeze and self.anamorphic_squeeze != AnamorphicSqueeze.SPHERICAL:
            return True
        if self.streak_flare or self.iris_blades:
            return True
        check_text = f"{self.lens or ''} {self.subject} {self.framing or ''} {self.optical_filter or ''}".lower()
        return any(
            k in check_text
            for k in ("anamorphic", "oval bokeh", "streak flare", "cylindrical flare", "2.0x squeeze")
        )

    @property
    def has_gobo(self) -> bool:
        """Return True if gobo pattern cookies or specialized grip modifiers are active."""
        if self.gobo or self.grip_modifier or self.lighting_ratio:
            return True
        check_text = f"{self.lighting or ''} {self.lighting_modifier or ''}".lower()
        return any(
            k in check_text
            for k in ("gobo", "cookie", "venetian", "foliage", "slits", "honeycomb", "snoot", "floppy")
        )

    @property
    def has_copy_space(self) -> bool:
        """Return True if commercial copy-space or ad safe-zones are specified."""
        return bool(
            (self.copy_space and self.copy_space != CopySpace.NONE)
            or (self.ad_safe_zone and self.ad_safe_zone != AdSafeZone.NONE)
        )

    @property
    def is_monochrome(self) -> bool:
        """Return True if black-and-white or monochrome rendering is requested."""
        if self.color_mode:
            cm = self.color_mode.strip().lower()
            if any(k in cm for k in ("mono", "black_and_white", "b&w", "bw", "grayscale")):
                return True
        check_text = f"{self.subject} {self.mood or ''} {self.film_stock or ''}".lower()
        return any(
            k in check_text
            for k in (
                "black-and-white",
                "black and white",
                "monochrome",
                " b&w ",
                " bw ",
                "indie-cinema monochrome",
                "restrained monochrome",
            )
        )

    @property
    def has_body_morphology(self) -> bool:
        """Return True if body volume scaling or morphology calibration is active."""
        if self.body_volume or self.weight_lb or self.body_morphology:
            return True
        check_text = f"{self.subject} {self.framing or ''}".lower()
        return any(
            k in check_text
            for k in (
                "biceps",
                "chest",
                "gut",
                "waist",
                "thighs",
                "heavier",
                "body mass",
                "lbs",
                "weight",
                "fuller physique",
            )
        )

    @property
    def has_material_style(self) -> bool:
        """Return True if custom material surface or 4D volumetric rendering is active."""
        if self.material_style and self.material_style != MaterialStyle.NONE:
            return True
        if self.is_4d_volumetric:
            return True
        check_text = f"{self.subject} {self.mood or ''}".lower()
        return any(
            k in check_text
            for k in ("latex", "shiny latex", "liquid glass", "acrylic", "4d", "volumetric")
        )

    @property
    def is_print_calibrated(self) -> bool:
        """Return True if exhibition print lab calibration or fine art paper is specified."""
        if self.print_spec:
            return True
        return bool(self.paper_profile and self.paper_profile != PaperProfile.NONE)

    @property
    def is_policy_safe(self) -> bool:
        """Return True if policy-safe compliance recovery layer is active."""
        return self.policy_safe

    @property
    def is_4d(self) -> bool:
        """Return True if 4D volumetric rendering is active."""
        return self.is_4d_volumetric or "4d" in self.subject.lower()

    @property
    def has_stress_probe(self) -> bool:
        """Return True if a PFEP diagnostic stress probe is configured."""
        return bool(self.stress_probe and self.stress_probe != StressProbe.NONE)

    @property
    def has_lighting_environment(self) -> bool:
        """Return True if exhibition lighting environment is configured."""
        return self.lighting_environment is not None

    @property
    def has_series_cohesion(self) -> bool:
        """Return True if series cohesion calibration is configured."""
        return self.series_cohesion is not None

    @property
    def has_closed_loop_constraints(self) -> bool:
        """Return True if closed-loop resolution or file size constraints are specified."""
        return bool(
            self.output_resolution
            or self.min_file_mb
            or (self.print_spec and (self.print_spec.width_in > 0 or self.print_spec.height_in > 0))
        )

    @property
    def has_reconstruction_lock_4x(self) -> bool:
        """Return True if 4X reconstruction lock mode or spec is active."""
        if self.reference and self.reference.mode == ReferenceMode.RECONSTRUCTION_LOCK_4X:
            return True
        return self.reconstruction_lock is not None



@dataclass
class CompiledPayload:
    """Compiled generation payload ready for the target model."""

    target_engine: TargetEngine
    positive_prompt: str
    negative_prompt: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def aspect_ratio(self) -> Optional[str]:
        """Return the target aspect ratio if present in parameters."""
        return self.parameters.get("aspect_ratio")

    @property
    def policy_safe(self) -> bool:
        """Return whether policy safe compliance mode was active."""
        return bool(self.metadata.get("policy_safe", False) or self.parameters.get("policy_safe", False))

    @property
    def unified_prompt(self) -> str:
        """Return the combined prompt payload with the anti-artifact negative shield appended."""
        if self.target_engine in (
            TargetEngine.MIDJOURNEY,
            TargetEngine.GPT_IMAGES,
            TargetEngine.RAW,
            TargetEngine.JSON_PROMPT,
        ):
            return self.positive_prompt
        if self.target_engine == TargetEngine.SDXL:
            return f"{self.positive_prompt}\n\nNegative prompt: {self.negative_prompt}"
        if self.negative_prompt:
            return f"{self.positive_prompt}\n\n[ANTI-ARTIFACT NEGATIVE SHIELD]:\nEliminate {self.negative_prompt}"
        return self.positive_prompt

    def to_dict(self) -> dict[str, Any]:
        """Convert payload to dictionary."""
        return {
            "target_engine": self.target_engine.value,
            "positive_prompt": self.positive_prompt,
            "negative_prompt": self.negative_prompt,
            "unified_prompt": self.unified_prompt,
            "parameters": self.parameters,
            "metadata": self.metadata,
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize payload to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

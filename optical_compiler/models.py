"""Data models and schemas for the Optical Camera Compiler."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
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
    DRAMATIC = "dramatic"
    NEON = "neon"

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[LightingPreset]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
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

    @classmethod
    def from_str(cls, value: Optional[str]) -> Optional[CaptureMode]:
        if not value:
            return None
        norm = value.strip().lower().replace("-", "_").replace(" ", "_")
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
}


class ReferenceMode(str, Enum):
    """Workflow mode when processing a reference image."""

    NONE = "none"
    RESTORE_UPSCALE = "restore_upscale"  # 1:1 Identity restoration and optical remastering
    TRANSFORM_ADAPT = "transform_adapt"  # Aesthetic/scene adaptation with biometric subject lock
    OUTPAINT_FULL_BODY = "outpaint_full_body"  # Outpaint medium shot to full body head-to-toe

    @classmethod
    def from_str(cls, value: Optional[str]) -> ReferenceMode:
        """Parse mode safely."""
        if not value:
            return cls.NONE
        normalized = value.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        return cls.NONE


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

    def all_tokens(
        self,
        include_anti_drift: bool = False,
        include_branding: bool = True,
        include_compression: bool = True,
        include_outpaint: bool = False,
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
        sensor_data = data.get("sensor_and_optics", {})
        lighting_data = data.get("lighting_and_exposure", {})
        micro_data = data.get("micro_detail_and_physics", {})
        neg_data = data.get("negative_embeddings", {})

        return cls(
            profile_id=data.get("profile_id", "custom"),
            title=data.get("title", "Custom Profile"),
            schema_version=data.get("schema_version", "2.0"),
            purpose=data.get("purpose", ""),
            sensor_and_optics=SensorOptics(**sensor_data),
            lighting_and_exposure=LightingSetup(**lighting_data),
            micro_detail_and_physics=MicroPhysics(**micro_data),
            negative_embeddings=NegativeShield(**neg_data),
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


@dataclass
class CompiledPayload:
    """Compiled generation payload ready for the target model."""

    target_engine: TargetEngine
    positive_prompt: str
    negative_prompt: str
    parameters: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

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

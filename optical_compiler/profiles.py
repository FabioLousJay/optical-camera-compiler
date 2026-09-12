"""Profile manager for loading and overriding camera hardware configurations."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
from typing import Optional, Union

from .models import (
    CameraProfile,
    CaptureMode,
    CAPTURE_MODE_DIRECTIVES,
    LightingPreset,
    LIGHTING_PRESET_DESCRIPTIONS,
    LightingSetup,
    MicroPhysics,
    NegativeShield,
    ReferenceMode,
    SceneInput,
    SensorOptics,
)

DEFAULT_PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"
PACKAGE_PROFILES_DIR = Path(__file__).resolve().parent / "profiles_data"

# Master Domain Router Rules: mapping scene genres/keywords to optimized camera systems
CAMERA_ROUTER_RULES: list[tuple[str, list[str]]] = [
    (
        "arri_alexa_35",
        [
            "alexa",
            "arri raw",
            "feature film",
            "hollywood",
            "anamorphic flare",
            "arri signature",
            "cooke look",
        ],
    ),
    (
        "sony_fx_series",
        [
            "cinema",
            "cinematic",
            "movie",
            "film still",
            "video",
            "narrative",
            "venice",
            "s-log",
            "s-log3",
            "180-degree shutter",
            "motion picture",
            "scene still",
            "cinematography",
            "colorist",
        ],
    ),
    (
        "panasonic_lumix_s1rii",
        [
            "macro",
            "scientific",
            "extreme closeup",
            "micro-detail",
            "micro-relief",
            "insect",
            "botanical",
            "specimen",
            "micro texture",
            "texture study",
            "focus stack",
            "close-up detail",
        ],
    ),
    (
        "canon_eos_r1",
        [
            "sports",
            "athlete",
            "athletic",
            "sprint",
            "stadium",
            "decisive moment",
            "fast action",
            "tournament",
            "race",
            "racing",
            "high fps",
            "burst",
            "action capture",
        ],
    ),
    (
        "sony_a1_ii",
        [
            "wildlife",
            "animal",
            "bird",
            "birds",
            "fauna",
            "safari",
            "predator",
            "prey",
            "falcon",
            "eagle",
            "hawk",
            "raptor",
            "telephoto",
            "high-speed tracking",
            "dynamic motion",
            "action wildlife",
            "feather detail",
            "cheetah",
            "lion",
            "tiger",
            "wolf",
        ],
    ),
    (
        "linhof_technika_4x5",
        [
            "architecture",
            "architectural",
            "building",
            "facade",
            "interior design",
            "large format",
            "tilt-shift",
            "perspective control",
            "bellows",
            "rectilinear",
            "monument",
        ],
    ),
    (
        "phase_one_iq4",
        [
            "luxury",
            "fine art",
            "museum",
            "jewelry",
            "timepiece",
            "horology",
            "watchmaker",
            "ultra commercial",
            "campaign",
            "haute couture",
            "still life",
            "gallery",
            "150mp",
            "trichromatic",
            "packshot",
            "commercial packshot",
            "product photography",
            "perfume bottle",
            "cosmetics bottle",
            "commercial product",
        ],
    ),
    (
        "leica_m6_analog",
        [
            "35mm film",
            "vintage film",
            "analog film",
            "kodak tri-x",
            "cinestill",
            "grainy film",
            "silver halide",
            "film grain",
        ],
    ),
    (
        "pentax_67ii",
        [
            "medium format film",
            "120 film",
            "analog portrait",
            "6x7 film",
        ],
    ),
    (
        "leica_sl2",
        [
            "leica sl2",
            "sl2",
            "50mm summilux",
            "summilux-sl",
            "summilux",
            "motion-blur crowd",
            "motion blur",
            "crowd motion",
            "calm vs chaos",
            "slow shutter motion-blur",
            "slow shutter",
            "commuters rushing past",
            "indie-cinema monochrome",
            "chest-level",
        ],
    ),
    (
        "leica_sl3_p",
        [
            "reportage",
            "photojournalism",
            "prestige documentary",
            "editorial assignment",
            "leica optics",
            "war correspondent",
            "investigative",
        ],
    ),
    (
        "fujifilm_gfx100rf",
        [
            "travel",
            "street",
            "documentary",
            "candid",
            "flaneur",
            "urban street",
            "classic chrome",
            "reala ace",
            "rangefinder",
            "city walk",
            "depixelate",
            "upscale",
            "restoration",
            "gfx100rf",
            "skin realism",
        ],
    ),
    (
        "hasselblad_x2d_ii_100c",
        [
            "portrait",
            "beauty",
            "headshot",
            "editorial portrait",
            "face",
            "skin",
            "natural color",
            "fashion model",
            "cosmetics",
            "eyelashes",
            "glamour",
            "model",
        ],
    ),
]


def auto_select_profile(scene: Union[str, SceneInput]) -> str:
    """Intelligently route a scene description or SceneInput to the optimal camera profile."""
    if isinstance(scene, SceneInput):
        if scene.reference and scene.reference.mode == ReferenceMode.DEPIXELATE_GFX100RF:
            return "fujifilm_gfx100rf"
        if scene.reference and scene.reference.mode == ReferenceMode.PRODUCT_LOCK:
            return "phase_one_iq4"
        text = f"{scene.subject} {scene.framing or ''} {scene.environment or ''} {scene.mood or ''} {scene.camera_angle or ''} {scene.crowd_action or ''} {scene.sku_color or ''} {scene.cap_geometry or ''}".lower()
    else:
        text = str(scene).lower()

    best_profile: Optional[str] = None
    longest_match_len = 0

    for profile_id, keywords in CAMERA_ROUTER_RULES:
        for kw in keywords:
            pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
            if re.search(pattern, text):
                if len(kw) > longest_match_len:
                    longest_match_len = len(kw)
                    best_profile = profile_id

    if best_profile:
        return best_profile

    # Default fallback to flagship 150MP Trichromatic medium format reference
    return "phase_one_iq4"


# Built-in Phase One IQ4 profile fallback to ensure zero runtime file lookup issues
PHASE_ONE_IQ4_DEFAULT = CameraProfile(
    profile_id="phase_one_iq4",
    title="Phase One XF IQ4 150MP Trichromatic",
    schema_version="2.0",
    purpose="Hardware-level optical and sensor simulation for zero-artifact photorealism.",
    sensor_and_optics=SensorOptics(
        camera_system="Phase One XF IQ4 150MP BSI Trichromatic",
        sensor_type="Back-Side Illuminated (BSI) CMOS Medium Format",
        sensor_dimensions="54x40mm medium-format sensor",
        full_frame_equivalent="~50mm full-frame equivalent normal field of view",
        lens="Schneider Kreuznach 80mm LS f/2.8 Blue Ring",
        aperture_sweet_spot="f/8",
        iso_base="ISO 50 base sensor sensitivity",
        dynamic_range="16-bit raw tonal range with 15 stops of dynamic latitude",
        shutter="Leaf shutter with 1/1600s high-speed flash sync",
    ),
    lighting_and_exposure=LightingSetup(
        primary_lighting="Studio strobe, 1/1600s leaf shutter sync, ISO 50 base sensor sensitivity, 16-bit raw tonal range",
        light_transport="Key light with large parabolic modifier, deep shadows carved with black foam-core negative fill, single-axis specular catchlights",
    ),
    micro_detail_and_physics=MicroPhysics(
        surface_rendering=[
            "Natural epidermal skin texture with resolved pores, fine vellus hair, and accurate subsurface scattering without artificial blur or waxy specularities",
            "True material micro-relief: fabric weave, micro-abrasions, uncompressed specular highlight falloff",
            "High optical acutance and MTF contrast without digital edge halos or unsharp masking artifacts",
        ],
        depth_and_optics=[
            "Subtle optical falloff characteristic of large-sensor f/8 depth of field",
            "Zero perspective distortion, clean rectilinear projection",
            "Clean edge transitions driven purely by lighting and geometry, not artificial post-process depth slicing",
        ],
    ),
    negative_embeddings=NegativeShield(
        render_defects=[
            "CGI",
            "3D render",
            "illustration",
            "digital sharpening halos",
            "chromatic aberration",
            "denoise smearing",
            "compression artifacts",
        ],
        skin_and_lighting_drift=[
            "airbrushed skin",
            "plastic poreless skin",
            "glamour retouching",
            "computational bokeh",
            "beauty filter glow",
            "blown highlights",
            "crushed shadows",
        ],
        anatomical_drift=[
            "mutated hands",
            "extra digits",
            "fused limbs",
            "asymmetrical pupil dilation",
            "deformed facial features",
        ],
    ),
    execution_directive="Enforce true raw-capture fidelity from a 150MP digital back. Eliminate post-processed sharpening looks, synthetic smoothing, and non-physical lighting.",
)


def load_profile(
    name_or_path: str = "phase_one_iq4",
    scene: Optional[Union[str, SceneInput]] = None,
) -> CameraProfile:
    """Load a CameraProfile from an ID, profile name, direct filepath, or 'auto'.

    Args:
        name_or_path: 'auto', 'phase_one_iq4', path to JSON file, or filename in profiles directory.
        scene: Optional scene context used to intelligently select the camera when name_or_path is 'auto'.

    Returns:
        CameraProfile instance.
    """
    if name_or_path == "auto":
        target_id = auto_select_profile(scene) if scene else "phase_one_iq4"
        return load_profile(target_id)

    # 1. Direct path check
    direct_path = Path(name_or_path)
    if direct_path.is_file():
        with open(direct_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CameraProfile.from_dict(data)

    # 2. Check in standard or package profiles directory
    for pdir in (DEFAULT_PROFILES_DIR, PACKAGE_PROFILES_DIR):
        candidate = pdir / f"{name_or_path}.json"
        if candidate.is_file():
            with open(candidate, "r", encoding="utf-8") as f:
                data = json.load(f)
            return CameraProfile.from_dict(data)

    # 3. Check for home directory CAMERA_PHASE_ONE.json if requested
    home_candidate = Path.home() / "CAMERA_PHASE_ONE.json"
    if (
        name_or_path in ("phase_one_iq4", "phase_one", "default")
        and home_candidate.is_file()
    ):
        with open(home_candidate, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("profile_id", "phase_one_iq4")
        return CameraProfile.from_dict(data)

    # 4. Fallback to bundled constant
    if name_or_path in ("phase_one_iq4", "phase_one", "default"):
        return copy.deepcopy(PHASE_ONE_IQ4_DEFAULT)

    raise FileNotFoundError(
        f"Could not resolve camera profile: '{name_or_path}'. "
        f"Checked direct path '{direct_path}' and profiles dir '{DEFAULT_PROFILES_DIR}'."
    )


def apply_overrides(profile: CameraProfile, scene: SceneInput) -> CameraProfile:
    """Return a new CameraProfile with optical overrides from the SceneInput applied."""
    p = copy.deepcopy(profile)

    # Lighting preset application
    if scene.lighting_preset:
        preset = LightingPreset.from_str(scene.lighting_preset)
        if preset and preset in LIGHTING_PRESET_DESCRIPTIONS:
            primary, transport = LIGHTING_PRESET_DESCRIPTIONS[preset]
            if not scene.lighting:
                p.lighting_and_exposure.primary_lighting = primary
            p.lighting_and_exposure.light_transport = f"{transport}, {p.lighting_and_exposure.light_transport}"

    # Capture mode application
    if scene.capture_mode:
        cm = CaptureMode.from_str(scene.capture_mode)
        if cm and cm in CAPTURE_MODE_DIRECTIVES:
            directive = CAPTURE_MODE_DIRECTIVES[cm]
            p.micro_detail_and_physics.surface_rendering.insert(0, directive)

    if scene.aperture:
        p.sensor_and_optics.aperture_sweet_spot = scene.aperture
    if scene.lens:
        p.sensor_and_optics.lens = scene.lens
    if scene.lighting:
        p.lighting_and_exposure.primary_lighting = scene.lighting
    if scene.shutter_speed:
        p.sensor_and_optics.shutter = scene.shutter_speed
    if scene.film_stock:
        p.sensor_and_optics.iso_base = scene.film_stock
    if scene.lighting_modifier:
        p.lighting_and_exposure.light_transport = f"{scene.lighting_modifier}, {p.lighting_and_exposure.light_transport}"

    if scene.custom_negatives:
        p.negative_embeddings.render_defects.extend(scene.custom_negatives)

    if scene.camera_angle:
        p.micro_detail_and_physics.depth_and_optics.insert(0, f"Camera angle: {scene.camera_angle}")

    if scene.crowd_action:
        p.micro_detail_and_physics.surface_rendering.append(f"Crowd action: {scene.crowd_action}")

    if scene.is_monochrome:
        mono_text = "Restrained black-and-white, indie-cinema monochrome, gentle highlight roll-off, clean midtones, no HDR, fine consistent organic film grain"
        if mono_text not in p.sensor_and_optics.dynamic_range:
            p.sensor_and_optics.dynamic_range = f"{p.sensor_and_optics.dynamic_range}, {mono_text}"

    return p


def list_available_profiles() -> list[dict[str, str]]:
    """Scan and return all available camera profiles."""
    profiles = []
    seen = set()

    # 1. Built-in defaults
    profiles.append({
        "id": PHASE_ONE_IQ4_DEFAULT.profile_id,
        "title": PHASE_ONE_IQ4_DEFAULT.title,
        "purpose": PHASE_ONE_IQ4_DEFAULT.purpose,
        "sensor": PHASE_ONE_IQ4_DEFAULT.sensor_and_optics.camera_system,
        "lens": PHASE_ONE_IQ4_DEFAULT.sensor_and_optics.lens,
        "aperture": PHASE_ONE_IQ4_DEFAULT.sensor_and_optics.aperture_sweet_spot,
    })
    seen.add(PHASE_ONE_IQ4_DEFAULT.profile_id)

    # 2. Check profiles directories
    for pdir in (DEFAULT_PROFILES_DIR, PACKAGE_PROFILES_DIR):
        if pdir.is_dir():
            for json_file in sorted(pdir.glob("*.json")):
                profile_id = json_file.stem
                if profile_id not in seen:
                    try:
                        with open(json_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        profiles.append({
                            "id": data.get("profile_id", profile_id),
                            "title": data.get("title", profile_id.replace("_", " ").title()),
                            "purpose": data.get("purpose", ""),
                            "sensor": data.get("sensor_and_optics", {}).get("camera_system", ""),
                            "lens": data.get("sensor_and_optics", {}).get("lens", ""),
                            "aperture": data.get("sensor_and_optics", {}).get("aperture_sweet_spot", ""),
                        })
                        seen.add(profile_id)
                    except Exception:
                        continue

    return profiles

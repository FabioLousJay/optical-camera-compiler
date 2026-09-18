"""Profile manager for loading and overriding camera hardware configurations."""

from __future__ import annotations

import copy
import json
from pathlib import Path
import re
from typing import Optional, Union

from .models import (
    AdSafeZone,
    AnamorphicSqueeze,
    CameraProfile,
    CaptureMode,
    CAPTURE_MODE_DIRECTIVES,
    CopySpace,
    GoboPattern,
    GripModifier,
    GripType,
    IrisBladeCount,
    LightingPreset,
    LIGHTING_PRESET_DESCRIPTIONS,
    LightingRatio,
    LightingSetup,
    MaterialStyle,
    MicroPhysics,
    NegativeShield,
    PaperProfile,
    ReferenceMode,
    SceneInput,
    SensorOptics,
    SkinLightingModifier,
    SKIN_LIGHTING_DESCRIPTIONS,
    StreakFlare,
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
            "anamorphic",
            "2.0x squeeze",
            "streak flare",
            "oval bokeh",
            "flare engine",
            "anamorphic lens",
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
        "canon_eos_r5_ii",
        [
            "canon eos r5 mark ii",
            "canon eos r5 ii",
            "canon r5 mark ii",
            "canon r5 ii",
            "eos r5 mark ii",
            "eos r5 ii",
            "r5 mark ii",
            "r5 ii",
            "r5ii",
            "r5m2",
            "8k 60p",
            "8k video",
            "canon 45mp",
            "stacked full-frame canon",
            "rf 85mm f1.2",
            "vogue soft",
            "vogue texture",
        ],
    ),
    (
        "canon_eos_r6_iii",
        [
            "canon eos r6 mark iii",
            "canon eos r6 iii",
            "canon r6 mark iii",
            "canon r6 iii",
            "eos r6 mark iii",
            "eos r6 iii",
            "r6 mark iii",
            "r6 iii",
            "r6iii",
            "r6m3",
            "7k 60p",
            "7k video",
            "canon 32.5mp",
            "32.5mp full-frame",
            "canon all-rounder",
            "r6 autofocus",
        ],
    ),
    (
        "nikon_z5_ii",
        [
            "nikon z5 ii",
            "nikon z5 mark ii",
            "nikon z5ii",
            "nikon z 5 ii",
            "z5 ii",
            "z5ii",
            "z5 mark ii",
            "z5m2",
            "nikon z5",
            "z5",
            "4k 60p nikon",
            "nikon 24mp",
            "nikon all-rounder",
            "articulating touchscreen nikon",
        ],
    ),
    (
        "nikon_z9",
        [
            "nikon z 9",
            "nikon z9",
            "z9",
            "nikkor z plena",
            "plena",
            "135mm plena",
            "nikkor z 600mm",
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
            "phase one",
            "phase one xf",
            "iq4",
            "iq4 150mp",
            "150mp",
            "151mp",
            "151 mp",
            "module a",
            "camera module a",
            "resolving authority",
            "schneider 110mm",
            "schneider kreuznach 110mm",
            "110mm ls",
            "opticolor",
            "opticolor+",
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
            "trichromatic",
            "packshot",
            "commercial packshot",
            "product photography",
            "perfume bottle",
            "cosmetics bottle",
            "commercial product",
            "hand lock",
            "grip lock",
            "holding product",
            "precision pinch",
            "palm support",
            "commercial advertising",
            "copy space",
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
            "leica sl3",
            "sl3",
            "leica sl3-p",
            "sl3-p",
            "reportage",
            "photojournalism",
            "prestige documentary",
            "editorial assignment",
            "leica optics",
            "war correspondent",
            "investigative",
            "apo-summicron-sl 90mm",
            "90mm summicron-sl",
        ],
    ),
    (
        "leica_m11",
        [
            "leica m11",
            "m11",
            "m11 rangefinder",
            "noctilux-m 75mm",
            "75mm noctilux",
            "apo-summicron-m 90mm",
            "90mm summicron-m",
            "apo-summicron-m 50mm",
            "50mm summicron apo",
            "summilux-m 35mm",
            "35mm summilux-m",
            "summilux m asph ii",
        ],
    ),
    (
        "leica_q3_monochrom",
        [
            "leica q3 monochrom",
            "q3 monochrom",
            "leica q3",
            "q3m",
            "q3",
            "panchromatic",
            "pure monochrome",
            "monochrom",
            "summilux 28mm",
            "monochrome street",
            "monochrome documentary",
            "silver halide grain",
            "monochrome sensor",
            "black and white street",
            "iso 100-200,000",
            "iso 100-200000",
            "iso 200,000",
            "iso 200000",
            "200,000 iso",
            "200000 iso",
            "60mp monochrome",
            "60mp monochrom",
        ],
    ),
    (
        "sony_a7rv",
        [
            "sony a7r v",
            "sony a7rv",
            "a7rv",
            "a7r5",
            "alpha 7r v",
            "61mp",
            "flat reproduction",
            "copy-stand",
            "infographic reproduction",
            "document reproduction",
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
            "hasselblad x2d",
            "x2d ii",
            "x2d 100c",
            "x2d",
            "module b",
            "camera module b",
            "tonal realism",
            "hncs",
            "hasselblad natural colour",
            "xcd 90v",
            "90v",
            "15.3 stops",
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
    (
        "fujifilm_gfx100ii",
        [
            "gfx 100 ii",
            "gfx100 ii",
            "gfx100ii",
            "gfx 100ii",
            "module c",
            "camera module c",
            "portrait precision",
            "gf 110mm",
            "gf110mm",
            "gf110",
            "fujinon gf 110mm",
            "fujinon gf110mm",
            "87mm equivalent",
            "cmos ii hs",
            "three-quarter body fashion",
        ],
    ),
    (
        "imax_msm_9802",
        [
            "imax",
            "15-perf",
            "65mm film",
            "double-x",
            "70mm film",
            "monumental close-up",
            "imax 65mm",
        ],
    ),
    (
        "arri_alexa_265",
        [
            "alexa 265",
            "arri 265",
            "65mm digital",
            "alexa 65 vista",
            "large-format digital vista",
        ],
    ),
    (
        "nikon_fm2",
        [
            "nikon fm2",
            "fm2",
            "nikkor 105mm",
            "kodachrome",
            "kodachrome 64",
            "slide film portrait",
        ],
    ),
    (
        "contax_645",
        [
            "contax 645",
            "planar 80mm",
            "zeiss 80mm",
            "pro 400h",
            "fuji pro 400h",
            "fine art wedding",
        ],
    ),
    (
        "hasselblad_xpan",
        [
            "hasselblad xpan",
            "xpan",
            "2.7:1",
            "panoramic 35mm",
            "24x65mm",
            "panoramic landscape",
        ],
    ),
    (
        "deardorff_8x10",
        [
            "deardorff",
            "8x10 portrait",
            "deardorff 8x10",
            "360mm symmar",
            "tri-x sheet",
            "white seamless",
        ],
    ),
    (
        "antique_view_8x10",
        [
            "wet-plate",
            "wet plate",
            "collodion",
            "tintype",
            "ambrotype",
            "petzval",
            "brass lens",
            "southern gothic",
        ],
    ),
    (
        "contax_t2",
        [
            "contax t2",
            "t2",
            "sonnar 38mm",
            "direct flash",
            "night candid",
            "snapshot flash",
        ],
    ),
    (
        "ricoh_gr_iv",
        [
            "ricoh gr",
            "gr iv",
            "gr 18.3mm",
            "snap street",
            "pocket camera",
            "zone focus",
            "gr iii",
        ],
    ),
    (
        "dji_mavic_4_pro",
        [
            "mavic 4 pro",
            "dji mavic",
            "nadir",
            "aerial geometry",
            "drone nadir",
            "top-down aerial",
        ],
    ),
    (
        "mamiya_rz67",
        [
            "mamiya rz67",
            "rz67",
            "kino flo",
            "twin kino flo",
            "character portrait",
            "140mm macro",
        ],
    ),
    (
        "polaroid_20x24",
        [
            "polaroid 20x24",
            "20x24",
            "giant instant",
            "polacolor",
            "life-size portrait",
            "contact-scale",
        ],
    ),
]


def auto_select_profile(scene: Union[str, SceneInput]) -> str:
    """Intelligently route a scene description or SceneInput to the optimal camera profile."""
    if isinstance(scene, SceneInput):
        if scene.reference and scene.reference.mode == ReferenceMode.DEPIXELATE_GFX100RF:
            return "fujifilm_gfx100rf"
        if scene.reference and scene.reference.mode == ReferenceMode.DEPIXELATE_V2:
            if scene.is_monochrome:
                return "leica_q3_monochrom"
            if scene.content_type and scene.content_type.is_flat_reproduction:
                return "sony_a7rv"
            return "sony_a7rv"
        if scene.has_depixelate_v2:
            if scene.is_monochrome:
                return "leica_q3_monochrom"
            if scene.content_type and scene.content_type.is_flat_reproduction:
                return "sony_a7rv"
            return "sony_a7rv"
        if scene.reference and scene.reference.mode == ReferenceMode.PRODUCT_LOCK:
            return "phase_one_iq4"
        if scene.is_anamorphic:
            return "arri_alexa_35"
        if scene.has_product_lock:
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
    title="CAMERA MODULE A — Phase One Maximum Resolving Authority",
    schema_version="2.0",
    purpose="Maximum-fidelity full-body and three-quarter portrait rendering emphasizing resolving power, dimensional skin, individual hair definition, textile structure, deep tonal separation, and controlled studio precision.",
    sensor_and_optics=SensorOptics(
        camera_system="Phase One XF IQ4 150MP",
        sensor_type="53.4 x 40.0mm BSI CMOS medium format (151 MP, 14204 x 10652, 3.76 µm pixel pitch)",
        sensor_dimensions="53.4x40.0mm medium-format sensor",
        full_frame_equivalent="~68mm full-frame equivalent normal portrait perspective",
        lens="Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
        aperture_sweet_spot="f/8",
        iso_base="ISO 50 base sensor sensitivity (16-bit Opticolor+)",
        dynamic_range="16-bit Opticolor+ tonal range with 15 f-stops dynamic latitude",
        shutter="Leaf shutter with 1/1600s high-speed flash sync",
    ),
    lighting_and_exposure=LightingSetup(
        primary_lighting="High-quality studio strobe, 1/1600s leaf shutter sync, ISO 50 quality baseline, 16-bit Opticolor+",
        light_transport="Key light 35-45 degrees off camera axis, minimal controlled fill, black foam-core negative fill for dimensional modeling, subtle edge rim separation, defined photographic light preserving smooth highlight transitions on skin",
    ),
    micro_detail_and_physics=MicroPhysics(
        surface_rendering=[
            "Natural epidermal skin texture with resolved pores, fine vellus hair, and accurate subsurface scattering without artificial blur or waxy specularities",
            "Extremely high native-looking information density without digital oversharpening; strong but natural microcontrast emerging from local tonal separation rather than halos",
            "Dimensional rendering with authentic pores, fine facial hair, beard texture, wrinkles, folds, freckles, age spots, and subtle skin variation only where optically plausible",
            "Resolve individual hair strands, overlapping strand groups, roots, flyaways, specular variation, and natural density without wire-like sharpening",
            "Highest local precision at iris, eyelashes, wetline, catchlight boundaries, and natural scleral texture; preserve fabric weave, stitching, seams, fibers, embroidery, leather grain, and metallic reflectance",
        ],
        depth_and_optics=[
            "Natural medium-format perspective generated through realistic camera distance; optically progressive depth transition with zero segmentation-mask blur",
            "Believable optical defocus with continuous transitions and structurally believable highlights; crisp subject edges without cutout halos",
            "Essentially zero chromatic aberration and zero wide-angle body distortion, oversized hands, oversized feet, stretched limbs, or receding head proportions",
        ],
    ),
    negative_embeddings=NegativeShield(
        render_defects=[
            "CGI",
            "3D render",
            "illustration",
            "digital oversharpening",
            "digital sharpening halos",
            "white edge halos",
            "chromatic aberration",
            "denoise smearing",
            "compression artifacts",
            "AI swirls",
            "wire-like hair sharpening",
        ],
        skin_and_lighting_drift=[
            "pore stamping",
            "engraved skin",
            "metallic skin",
            "worm-like microtexture",
            "lace-like skin patterns",
            "synthetic repetitive pores",
            "over-sharpened wrinkles",
            "plastic smoothing",
            "HDR skin",
            "wax skin",
            "hyper-HDR",
            "fake depth blur",
            "invented microdetail",
            "airbrushed skin",
            "computational bokeh",
            "beauty filter glow",
            "blown highlights",
            "crushed shadows",
        ],
        anatomical_drift=[
            "beautification drift",
            "body slimming unless requested",
            "body enlargement unless requested",
            "age reduction",
            "face redesign",
            "AI-perfect symmetry",
            "mutated hands",
            "extra digits",
            "fused limbs",
            "asymmetrical pupil dilation",
            "deformed facial features",
            "wide-angle body distortion",
            "oversized hands",
            "oversized feet",
            "stretched limbs",
        ],
    ),
    execution_directive="Enforce Phase One XF + IQ4 150MP maximum resolving authority with Schneider Kreuznach 110mm LS f/2.8 Blue Ring at f/8, ISO 50. The image should feel as though enormous resolving power existed at capture, not as though a lower-resolution image was sharpened afterward. Human skin realism overrides perceived resolution; skin remains softer than eyelashes, iris, hair strands, and textiles.",
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

    PROFILE_ALIASES = {
        "module_a": "phase_one_iq4",
        "module_b": "hasselblad_x2d_ii_100c",
        "module_c": "fujifilm_gfx100ii",
        "phase_one": "phase_one_iq4",
        "phase_one_iq4": "phase_one_iq4",
        "phase_one_150mp": "phase_one_iq4",
        "iq4": "phase_one_iq4",
        "iq4_150mp": "phase_one_iq4",
        "hasselblad_x2d": "hasselblad_x2d_ii_100c",
        "hasselblad_x2d_100c": "hasselblad_x2d_ii_100c",
        "x2d": "hasselblad_x2d_ii_100c",
        "x2d_ii": "hasselblad_x2d_ii_100c",
        "fujifilm_gfx100ii": "fujifilm_gfx100ii",
        "gfx100ii": "fujifilm_gfx100ii",
        "gfx_100ii": "fujifilm_gfx100ii",
        "gfx100_ii": "fujifilm_gfx100ii",
        "leica_sl3": "leica_sl3_p",
        "sl3": "leica_sl3_p",
        "leica_sl3_p": "leica_sl3_p",
        "leica_m11": "leica_m11",
        "m11": "leica_m11",
        "sony_alpha_7r_v": "sony_a7rv",
        "sony_a7r_v": "sony_a7rv",
        "sony_a7r5": "sony_a7rv",
        "a7rv": "sony_a7rv",
        "a7r5": "sony_a7rv",
        "sony_a7rv": "sony_a7rv",
        "sony_a1": "sony_a1_ii",
        "sony_a1_ii": "sony_a1_ii",
        "a1_ii": "sony_a1_ii",
        "a1m2": "sony_a1_ii",
        "leica_q3_monochrom": "leica_q3_monochrom",
        "leica_q3": "leica_q3_monochrom",
        "q3_monochrom": "leica_q3_monochrom",
        "q3m": "leica_q3_monochrom",
        "q3": "leica_q3_monochrom",
        "imax": "imax_msm_9802",
        "imax_65mm": "imax_msm_9802",
        "imax_9802": "imax_msm_9802",
        "imax_msm": "imax_msm_9802",
        "alexa_265": "arri_alexa_265",
        "arri_265": "arri_alexa_265",
        "alexa265": "arri_alexa_265",
        "fm2": "nikon_fm2",
        "nikon_fm_2": "nikon_fm2",
        "c645": "contax_645",
        "contax645": "contax_645",
        "xpan": "hasselblad_xpan",
        "hasselblad_panoramic": "hasselblad_xpan",
        "deardorff": "deardorff_8x10",
        "deardorff8x10": "deardorff_8x10",
        "wet_plate": "antique_view_8x10",
        "wet_plate_8x10": "antique_view_8x10",
        "antique_view": "antique_view_8x10",
        "antique_view_camera": "antique_view_8x10",
        "t2": "contax_t2",
        "contaxt2": "contax_t2",
        "gr_iv": "ricoh_gr_iv",
        "griv": "ricoh_gr_iv",
        "gr4": "ricoh_gr_iv",
        "ricoh_gr": "ricoh_gr_iv",
        "mavic_4_pro": "dji_mavic_4_pro",
        "dji_mavic": "dji_mavic_4_pro",
        "mavic": "dji_mavic_4_pro",
        "rz67": "mamiya_rz67",
        "mamiya_rz_67": "mamiya_rz67",
        "polaroid_20x24": "polaroid_20x24",
        "polaroid_20_24": "polaroid_20x24",
        "polaroid20x24": "polaroid_20x24",
        "canon_eos_r5_ii": "canon_eos_r5_ii",
        "canon_eos_r5_mark_ii": "canon_eos_r5_ii",
        "canon_r5_ii": "canon_eos_r5_ii",
        "canon_r5_mark_ii": "canon_eos_r5_ii",
        "eos_r5_ii": "canon_eos_r5_ii",
        "eos_r5_mark_ii": "canon_eos_r5_ii",
        "r5_ii": "canon_eos_r5_ii",
        "r5ii": "canon_eos_r5_ii",
        "r5_mark_ii": "canon_eos_r5_ii",
        "canon_eos_r6_iii": "canon_eos_r6_iii",
        "canon_eos_r6_mark_iii": "canon_eos_r6_iii",
        "canon_r6_iii": "canon_eos_r6_iii",
        "canon_r6_mark_iii": "canon_eos_r6_iii",
        "eos_r6_iii": "canon_eos_r6_iii",
        "eos_r6_mark_iii": "canon_eos_r6_iii",
        "r6_iii": "canon_eos_r6_iii",
        "r6iii": "canon_eos_r6_iii",
        "r6_mark_iii": "canon_eos_r6_iii",
        "nikon_z5_ii": "nikon_z5_ii",
        "nikon_z5_mark_ii": "nikon_z5_ii",
        "nikon_z_5_ii": "nikon_z5_ii",
        "nikon_z5ii": "nikon_z5_ii",
        "nikon_z5": "nikon_z5_ii",
        "z5_ii": "nikon_z5_ii",
        "z5ii": "nikon_z5_ii",
        "z5": "nikon_z5_ii",
    }
    normalized_key = name_or_path.strip().lower().replace("-", "_").replace(" ", "_")
    target_name = PROFILE_ALIASES.get(normalized_key, name_or_path)

    # 1. Direct path check
    direct_path = Path(target_name)
    if direct_path.is_file():
        with open(direct_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CameraProfile.from_dict(data)

    # 2. Check in standard or package profiles directory
    for pdir in (DEFAULT_PROFILES_DIR, PACKAGE_PROFILES_DIR):
        candidate = pdir / f"{target_name}.json"
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

    # Anamorphic Cinema Optics & Flare Engine
    if scene.is_anamorphic:
        squeeze_val = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
        flare_val = scene.streak_flare.value.replace("_", " ") if scene.streak_flare else "cyan/blue"
        blades_val = scene.iris_blades.value.replace("_", " ") if scene.iris_blades else "14-blade circular"
        if not scene.lens:
            p.sensor_and_optics.lens = (
                f"Cooke Anamorphic /i Full Frame Plus 2x Squeeze ({squeeze_val} cylindrical front element, "
                f"{flare_val} horizontal streak flare, {blades_val} iris)"
            )
        anamorphic_bokeh_directive = (
            f"Cinema anamorphic optical signature: {squeeze_val} squeeze factor rendering 2:1 vertical elliptical oval bokeh discs, "
            f"horizontal {flare_val} streak flares on bright specular light sources, subtle edge astigmatism, gentle anamorphic barrel curvature"
        )
        p.micro_detail_and_physics.depth_and_optics.insert(0, anamorphic_bokeh_directive)

    # Commercial Advertising Suite: Gobo & Grip Modifiers & Lighting Ratios
    if scene.gobo:
        gobo_desc = scene.gobo.value.replace("_", " ")
        gobo_directive = f"Optical gobo projection cookie: {gobo_desc} casting architectural shadow pattern across subject/background with organic edge diffusion"
        p.lighting_and_exposure.light_transport = f"{gobo_directive}, {p.lighting_and_exposure.light_transport}"

    if scene.grip_modifier:
        grip_desc = scene.grip_modifier.value.replace("_", " ")
        p.lighting_and_exposure.light_transport = f"Studio grip: {grip_desc}, {p.lighting_and_exposure.light_transport}"

    if scene.lighting_ratio:
        ratio_desc = f"{scene.lighting_ratio.value} key-to-fill lighting contrast ratio"
        p.lighting_and_exposure.primary_lighting = f"{p.lighting_and_exposure.primary_lighting} ({ratio_desc})"

    # Commercial Advertising Suite: Copy-Space & Ad Safe-Zones
    if scene.has_copy_space:
        if scene.copy_space and scene.copy_space != CopySpace.NONE:
            cs_desc = scene.copy_space.value.replace("_", " ")
            p.micro_detail_and_physics.depth_and_optics.append(
                f"Commercial advertising framing: Asymmetric negative copy-space strictly reserved in {cs_desc} with calm, uncluttered background for brand headline and typography"
            )
        if scene.ad_safe_zone and scene.ad_safe_zone != AdSafeZone.NONE:
            sz_desc = scene.ad_safe_zone.value.replace("_", " ")
            p.micro_detail_and_physics.depth_and_optics.append(
                f"Social advertising safe-zone: Composition strictly formatted for {sz_desc}, keeping all critical subject matter and focal points safely clear of UI overlay zones"
            )

    # Biomechanical Hand & Finger Precision Gate
    if scene.has_hand_lock:
        grip_desc = scene.grip_type.value.replace("_", " ") if scene.grip_type else "ergonomic contact grip"
        details = f" ({scene.hand_details})" if scene.hand_details else ""
        hand_directive = (
            f"Biomechanical 5-Point Hand Precision Gate ({grip_desc}{details}): "
            "5-ray metacarpal architecture with correct anatomical proportions (2:3:4:3.5:2.5 length ratio), "
            "distinct MCP, PIP, and DIP articulation, authentic palmar and digital flexion creases, "
            "natural contact blanching (micro-capillary blood displacement and tissue compression where skin contacts object), "
            "translucent nail beds with visible lunula crescents, authentic cuticles, and natural skin pores on thenar eminence. "
            "Zero missing knuckles, zero fused digits, zero clipping through objects, zero rubber fingers."
        )
        p.micro_detail_and_physics.surface_rendering.insert(0, hand_directive)

    # Body Morphology & Proportional Volume Calibration
    if scene.has_body_morphology:
        regions = scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else "biceps, chest, gut")
        wt = f" (target body mass: {scene.weight_lb} lbs)" if scene.weight_lb else ""
        morph_directive = (
            f"Body Morphology & Proportional Volume Calibration ({regions}{wt}): "
            "Proportional volume scaling strictly anchored to skeletal frame, limb length, and torso width. "
            "Preserve authentic human bilateral asymmetry without mechanical mirroring or cloned forms. "
            "Realistic soft-tissue gravitational physics, seated tissue compression, and continuous anatomical contours into adjacent musculature. "
            "Clothing must conform and stretch naturally over enlarged forms without altered garment structure or broken patterns. "
            "Strict anti-exaggeration lock: Zero extreme bodybuilding, zero balloon muscles, zero impossible insertions."
        )
        p.micro_detail_and_physics.surface_rendering.insert(0, morph_directive)

    # 4D Volumetric & Premium Material Engine
    if scene.has_material_style:
        mat_name = scene.material_style.value.replace("_", " ") if scene.material_style and scene.material_style != MaterialStyle.NONE else "dimensional volumetric finish"
        mat_directive = (
            f"4D Volumetric & Premium Material Engine ({mat_name}): "
            "High-fidelity dimensional volume with clear foreground-background separation, precise contour rim lighting, "
            "controlled specular highlight curvature, and deep tonal separation. "
            "Material response features realistic surface curvature, high micro-contrast, and clean edge definition without cheap plastic appearance or flat CGI shading."
        )
        p.micro_detail_and_physics.surface_rendering.insert(0, mat_directive)

    # Print-Calibrated Prepress & Exhibition Lab Matrix
    if scene.is_print_calibrated:
        paper_name = scene.paper_profile.value.replace("_", " ") if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value.replace("_", " ") if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else "exhibition fine-art paper")
        prepress_directive = (
            f"Exhibition Prepress Calibration ({paper_name}): "
            "Tonal mapping and contrast curve calibrated for fine-art exhibition print media with authentic paper Dmax response and zero digital banding."
        )
        p.lighting_and_exposure.light_transport = f"{prepress_directive}, {p.lighting_and_exposure.light_transport}"

    # Specialized Skin & Texture Lighting Modifier
    if scene.has_skin_lighting:
        skin_light_directive = SKIN_LIGHTING_DESCRIPTIONS.get(scene.skin_lighting)
        if skin_light_directive:
            p.lighting_and_exposure.primary_lighting = f"{skin_light_directive}, {p.lighting_and_exposure.primary_lighting}"
            p.micro_detail_and_physics.surface_rendering.insert(0, f"Specialized skin lighting: {skin_light_directive}.")

    # Universal Medium Format Portrait Override
    if scene.has_universal_medium_format_override:
        p.execution_directive = (
            f"{p.execution_directive} UNIVERSAL MASTER OVERRIDE ACTIVE: "
            "Photographic realism above synthetic perceived resolution. "
            "Skin realism overrides sharpening (never convert skin into the sharpest texture). "
            "Hair resolves sharper than skin only within focal plane. "
            "HDR means expanded recoverable tonal range, not halos or tone-mapping glow. "
            "Deep blacks must remain dense with subtle near-black texture. "
            "Depth of field behaves optically and progressively without segmentation blur. "
            "Zero anatomical or identity drift."
        )
        p.micro_detail_and_physics.surface_rendering.insert(
            0,
            "Human skin realism overrides sharpening: skin must remain slightly softer than eyelashes, iris detail, individual hair strands, jewelry, fabric edges, and typography."
        )

    # Policy-Safe Compliance Recovery Layer
    if scene.is_policy_safe:
        p.execution_directive = f"Policy-Safe Compliance Layer Active: {p.execution_directive} Modify only minimum required elements to ensure 100% compliance while preserving all camera optics, lighting geometry, and realism."

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

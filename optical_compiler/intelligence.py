"""AI Rig Advisor & Multi-Rig Recommendation Engine with Anti-Drift & Anti-Hallucination Quality Gate.

Provides intelligent scene intent analysis, automated 3-tier camera rig recommendations
(1st Best Primary Optical Master, 2nd Best Distinct Aesthetic, 3rd Best High-Character Rig),
photorealistic prompt enhancement, and strict quality gate certification.
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field
import re
from typing import Any, Optional, Union

from .models import TargetEngine
from .presets import LENS_CATALOG


# ==============================================================================
# 1. DATA MODELS & TELEMETRY
# ==============================================================================

@dataclass
class SceneIntent:
    """Structured semantic intent extracted from a raw scene prompt."""
    raw_prompt: str
    primary_genre: str  # portrait, street, architecture, wildlife, sports_action, macro_detail, cinema, landscape, fashion, documentary, still_life
    subject_entities: list[str] = field(default_factory=list)
    environment_cues: list[str] = field(default_factory=list)
    lighting_cues: list[str] = field(default_factory=list)
    motion_cadence: str = "still"  # still, high_speed, motion_blur, slow_flow
    depth_scale: str = "medium"  # extreme_macro, tight_headshot, medium_three_quarter, full_length, wide_environmental, panoramic, aerial
    mood_tags: list[str] = field(default_factory=list)
    is_monochrome_intent: bool = False
    is_cinematic_intent: bool = False
    is_macro_intent: bool = False
    is_action_intent: bool = False
    is_aerial_intent: bool = False
    is_product_intent: bool = False


@dataclass
class QualityGateResult:
    """Telemetric verification certification for Anti-Drift & Anti-Hallucination."""
    passed: bool = True
    anti_drift_score: float = 100.0  # Percentage of core user entities preserved
    preserved_entities: list[str] = field(default_factory=list)
    missing_entities: list[str] = field(default_factory=list)
    zero_artist_verified: bool = True
    detected_artists: list[str] = field(default_factory=list)
    physical_optics_verified: bool = True
    negative_shield_safe: bool = True
    overall_score: int = 100
    summary: str = "✓ Anti-Drift: 100% Intent Preserved | ✓ Anti-Hallucination: Zero Artists, Valid Physical Optics"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RigRecommendation:
    """A fully calibrated, ranked optical package recommendation."""
    rank: int  # 1, 2, 3
    tier_name: str  # e.g. "1st Best (Primary Optical Master)"
    title: str  # e.g. "Phase One XF IQ4 150MP // Schneider 110mm LS f/2.8"
    camera_name: str
    profile_id: str
    lens: str
    aperture: str
    depth_of_field: str
    lighting: str
    lighting_key: str  # maps to web select: strobe_para, window_daylight, beauty_dish, rembrandt_key, etc.
    aspect_ratio: str  # "4:5", "16:9", "1:1", "2.7:1", "3:2"
    framing: str
    camera_angle: str
    film_stock: str  # "digital_raw", "portra_400", "tri_x_400", etc.
    skin_lighting: Optional[str] = None
    enhanced_scene: str = ""
    rationale: str = ""
    quality_gate: Optional[QualityGateResult] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        if self.quality_gate:
            d["quality_gate"] = self.quality_gate.to_dict()
        return d


# ==============================================================================
# 2. ZERO-ARTIST & PROHIBITED TOKEN CATALOG (ANTI-HALLUCINATION DEFENSE)
# ==============================================================================

# Comprehensive database of famous photographers, painters, digital artists, and directors
# whose inclusion constitutes synthetic artist-name hallucination.
PROHIBITED_ARTIST_NAMES: list[str] = [
    # Famous Photographers
    "ansel adams", "annie leibovitz", "peter lindbergh", "helmut newton", "richard avedon",
    "steve mccurry", "henri cartier-bresson", "cartier-bresson", "robert capa", "dorothea lange",
    "sebastiao salgado", "salgado", "gordon parks", "irving penn", "cindy sherman",
    "diane arbus", "william eggleston", "eggleston", "saul leiter", "nan goldin",
    "martin parr", "daido moriyama", "nobuyoshi araki", "vivian maier", "bruce gilden",
    "mario testino", "david lachapelle", "ellen von unwerth", "steven meisel", "mert and marcus",
    "tim walker", "nick knight", "paolo roversi", "guy bourdin", "walker evans",
    "edward weston", "man ray", "lee miller", "robert frank", "fan ho",
    # Illustrators / Digital Concept Artists
    "artgerm", "greg rutkowski", "alphonse mucha", "mucha", "james jean",
    "wlop", "ross tran", "ilya kuvshinov", "makoto shinkai", "hayao miyazaki",
    "frank frazetta", "boris vallejo", "h.r. giger", "hr giger", "simon stalenhag",
    "craig mullins", "loish", "moebius", "jean giraud", "syd mead",
    # Film Directors (style hijacking)
    "wes anderson", "christopher nolan", "quentin tarantino", "stanley kubrick",
    "david fincher", "denis villeneuve", "ridley scott", "terrence malick",
    "wong kar-wai", "wong kar wai", "guillermo del toro", "tim burton"
]

# Prohibited render defects that should never appear in generated prompts
PROHIBITED_DEFECT_TOKENS: list[str] = [
    "bad face", "ugly face", "deformed face", "disfigured face", "bad eyes",
    "mutated face", "poorly drawn face", "extra limbs", "fused fingers",
    "missing fingers", "mutated hands", "malformed limbs", "ugly", "deformed"
]

# Prohibited negative tokens that must never be injected into negative shields for Midjourney / Firefly
TOXIC_NEGATIVE_SHIELD_TOKENS: list[str] = [
    "forehead", "neck", "cheek", "face", "skin texture", "skin pores", "proportions", "anatomy"
]


# ==============================================================================
# 3. DOMAIN TAXONOMY & HARDWARE MAPPINGS
# ==============================================================================

PROFILE_DISPLAY_NAMES: dict[str, str] = {
    "phase_one_iq4": "Phase One XF IQ4 150MP",
    "hasselblad_x2d_ii_100c": "Hasselblad X2D II 100c",
    "fujifilm_gfx100ii": "Fujifilm GFX 100 II",
    "fujifilm_gfx100rf": "Fujifilm GFX100RF",
    "hasselblad_h6d": "Hasselblad H6D-100c",
    "hasselblad_500cm": "Hasselblad 500C/M",
    "pentax_67ii": "Pentax 67 II",
    "mamiya_rz67": "Mamiya RZ67",
    "contax_645": "Contax 645",
    "hasselblad_xpan": "Hasselblad XPan",
    "deardorff_8x10": "Deardorff 8x10 Large Format",
    "antique_view_8x10": "8x10 Antique View Camera",
    "linhof_technika_4x5": "Linhof Master Technika 4x5",
    "polaroid_20x24": "Polaroid 20x24 Large Format",
    "sony_a1_ii": "Sony a1 II",
    "sony_a7rv": "Sony Alpha 7R V",
    "canon_eos_r1": "Canon EOS R1",
    "canon_eos_r5_ii": "Canon EOS R5 Mark II",
    "canon_eos_r6_iii": "Canon EOS R6 Mark III",
    "nikon_z9": "Nikon Z 9",
    "nikon_z5_ii": "Nikon Z 5 II",
    "leica_m11": "Leica M11 60MP",
    "leica_m6_analog": "Leica M6 Classic 35mm",
    "leica_q3_monochrom": "Leica Q3 Monochrom",
    "leica_sl2": "Leica SL2",
    "leica_sl3_p": "Leica SL3-P 45MP",
    "panasonic_lumix_s1rii": "Panasonic LUMIX S1R II",
    "nikon_fm2": "Nikon FM2",
    "contax_t2": "Contax T2",
    "ricoh_gr_iv": "Ricoh GR IV",
    "dji_mavic_4_pro": "DJI Mavic 4 Pro",
    "arri_alexa_35": "ARRI Alexa 35",
    "arri_alexa_265": "ARRI ALEXA 265",
    "sony_fx_series": "Sony VENICE 2",
    "imax_msm_9802": "IMAX MSM 9802 15-Perf 65mm",
    "canon_powershot_g7x_iii": "Canon PowerShot G7 X Mark III",
    "fujifilm_x_e5": "Fujifilm X-E5 40.2MP",
    "nikon_z50_ii": "Nikon Z50 II 20.9MP",
    "om_system_om5_ii": "OM System OM-5 Mark II",
    "panasonic_lumix_g97": "Panasonic Lumix G97 Hybrid",
    "sony_a7c_ii": "Sony Alpha 7C II 33MP",
}

# Default sweet spots for profiles
DEFAULT_HARDWARE_SPECS: dict[str, dict[str, Any]] = {
    "phase_one_iq4": {
        "lens": "Schneider Kreuznach 110mm LS f/2.8 Blue Ring",
        "aperture": "f/8.0",
        "dof": "Deep focus sweet spot with extraordinary micro-contrast from eyelashes to textiles, crisp edge acuity and zero digital oversharpening",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "strobe_para",
        "lighting": "Studio Strobe: 35-45° Directional Key with Black Foam-Core Negative Fill (1/1600s leaf sync)",
        "framing": "three-quarter editorial body portrait",
        "angle": "eye-level straight-on",
        "medium_type": "medium_format_digital",
    },
    "hasselblad_x2d_ii_100c": {
        "lens": "Hasselblad XCD 90mm f/2.5 V",
        "aperture": "f/4.0",
        "dof": "Medium-format optical separation with HNCS 16-bit color graduation and smooth organic background falloff",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Directional Daylight with Soft Diffusion, Organic Natural Falloff",
        "framing": "medium editorial portrait",
        "angle": "eye-level intimate",
        "medium_type": "medium_format_digital",
    },
    "fujifilm_gfx100ii": {
        "lens": "Fujinon GF 110mm f/2 R LM WR",
        "aperture": "f/2.8",
        "dof": "Shallow depth of field with razor-sharp iris plane and creamy background dissolution",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "strobe_para",
        "lighting": "Studio Strobe: 35-45° Directional Key with Black Flag Negative Fill",
        "framing": "tight head and shoulders portrait",
        "angle": "eye-level direct",
        "medium_type": "medium_format_digital",
    },
    "fujifilm_gfx100rf": {
        "lens": "Fujinon GF 45mm f/2.8 R WR",
        "aperture": "f/5.6",
        "dof": "Deep architectural and street documentary focus with 102MP medium format micro-relief",
        "aspect_ratio": "4:5",
        "film_stock": "classic_chrome",
        "lighting_key": "window_daylight",
        "lighting": "Directional Daylight with Soft Diffusion, Organic Natural Falloff",
        "framing": "medium environmental documentary portrait",
        "angle": "eye-level candid",
        "medium_type": "medium_format_rangefinder",
    },
    "hasselblad_500cm": {
        "lens": "Carl Zeiss Planar T* 80mm f/2.8 CF",
        "aperture": "f/2.8",
        "dof": "Distinct 6x6 medium-format shallow depth of field with legendary Zeiss circular bokeh and soft highlight roll-off",
        "aspect_ratio": "1:1",
        "film_stock": "portra_400",
        "lighting_key": "window_daylight",
        "lighting": "Natural Window Daylight with Soft Muslin Diffusion and Organic Shadow Falloff",
        "framing": "square format medium portrait",
        "angle": "waist-level finder perspective (slightly low angle)",
        "medium_type": "medium_format_analog",
    },
    "pentax_67ii": {
        "lens": "SMC Pentax 67 105mm f/2.4",
        "aperture": "f/2.4",
        "dof": "The Legendary Bokeh King optical signature: paper-thin depth of field with dreamy, painterly three-dimensional background melt",
        "aspect_ratio": "4:5",
        "film_stock": "portra_400",
        "lighting_key": "golden_hour",
        "lighting": "Low-Angle Golden Hour Sunlight with Warm Unbleached Muslin Bounce",
        "framing": "medium environmental portrait",
        "angle": "eye-level gentle",
        "medium_type": "medium_format_analog",
    },
    "mamiya_rz67": {
        "lens": "Mamiya Sekor Z 140mm f/4.5 Macro",
        "aperture": "f/5.6",
        "dof": "Tactile 6x7 character depth with crisp tactile pores and soft studio falloff",
        "aspect_ratio": "4:5",
        "film_stock": "portra_400",
        "lighting_key": "strobe_para",
        "lighting": "Twin Kino Flo Flooded Softbanks with Subtle Negative Fill",
        "framing": "tight character close-up portrait",
        "angle": "eye-level authoritative",
        "medium_type": "medium_format_analog",
    },
    "contax_645": {
        "lens": "Carl Zeiss Planar T* 80mm f/2",
        "aperture": "f/2.0",
        "dof": "Luminous fine-art bridal depth of field, creamy pastel bokeh, and overexposed highlight brilliance",
        "aspect_ratio": "4:5",
        "film_stock": "portra_160",
        "lighting_key": "window_daylight",
        "lighting": "High-Key Soft Window Ambient with Airy Muslin Reflection",
        "framing": "three-quarter editorial portrait",
        "angle": "eye-level elegant",
        "medium_type": "medium_format_analog",
    },
    "hasselblad_xpan": {
        "lens": "Hasselblad 45mm f/4 for XPan",
        "aperture": "f/5.6",
        "dof": "Panoramic 2.7:1 cinematic aspect ratio with expansive peripheral context and uncompressed horizon sharpness",
        "aspect_ratio": "16:9",  # Or mapped to 21:9 / 2.7:1
        "film_stock": "cinestill_800t",
        "lighting_key": "tungsten_candle",
        "lighting": "Atmospheric Night Street Tungsten and Ambient Urban Glow",
        "framing": "panoramic environmental narrative composition",
        "angle": "cinematic eye-level",
        "medium_type": "specialty_panoramic",
    },
    "deardorff_8x10": {
        "lens": "Schneider Kreuznach Symmar-S 360mm f/6.8",
        "aperture": "f/11",
        "dof": "Monumental 8x10 large format bellows depth of field with breathtaking tonal continuity and contact-sheet fidelity",
        "aspect_ratio": "4:5",
        "film_stock": "tri_x_400",
        "lighting_key": "window_daylight",
        "lighting": "North-Facing Studio Skylight with Immense Tonal Gradation",
        "framing": "formal large-format studio portrait",
        "angle": "eye-level stately",
        "medium_type": "large_format_analog",
    },
    "antique_view_8x10": {
        "lens": "Uncoated Brass Petzval Lens ~300mm f/3.8",
        "aperture": "f/4.0",
        "dof": "Swirling Petzval vortex bokeh, heavy vignetting, and authentic wet-plate collodion silver edge aberrations",
        "aspect_ratio": "4:5",
        "film_stock": "tri_x_400",
        "lighting_key": "window_daylight",
        "lighting": "Raking Daylight with Antique Wet-Plate Exposure Physics",
        "framing": "intense period tintype portrait",
        "angle": "eye-level historical",
        "medium_type": "large_format_antique",
    },
    "linhof_technika_4x5": {
        "lens": "Schneider Kreuznach Apo-Symmar 150mm f/5.6 L",
        "aperture": "f/16",
        "dof": "Infinite rectilinear sharpness via front standard rise and tilt; zero keystone converging verticals",
        "aspect_ratio": "4:5",
        "film_stock": "provia_100f",
        "lighting_key": "architectural_skylight",
        "lighting": "Diffused Architectural Clerestory Daylight with Clean Tonal Roll-off",
        "framing": "full-length architectural perspective",
        "angle": "straight-on zero-tilt perspective",
        "medium_type": "large_format_technical",
    },
    "polaroid_20x24": {
        "lens": "Schneider 600mm f/11 for Polaroid 20x24",
        "aperture": "f/11",
        "dof": "Life-size 1:1 contact scale with paper-thin depth at 600mm focal length, monumental presence and dye transfer edges",
        "aspect_ratio": "4:5",
        "film_stock": "portra_400",
        "lighting_key": "strobe_para",
        "lighting": "Massive 20x24 Studio Strobe Bank with Pure Frontal Wrap",
        "framing": "life-size monumental close-up portrait",
        "angle": "eye-level immersive",
        "medium_type": "large_format_instant",
    },
    "sony_a1_ii": {
        "lens": "Sony FE 85mm F1.4 GM II (SEL85F14GM2)",
        "aperture": "f/1.8",
        "dof": "Ultra-sharp focal plane with 1/400s flash sync freezing micro-expressions and velvety circular G-Master bokeh",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "strobe_para",
        "lighting": "1/400s High-Speed Sync Studio Strobe with 20° Honeycomb Grid",
        "framing": "three-quarter dynamic portrait",
        "angle": "eye-level dynamic",
        "medium_type": "35mm_flagship_digital",
    },
    "sony_a7rv": {
        "lens": "Sony FE 90mm f/2.8 Macro G OSS",
        "aperture": "f/8.0",
        "dof": "Microscopic 61MP resolution with 1:1 macro planar sharpness across intricate mechanical or botanical surfaces",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Diffused Precision Macro Workbench Daylight with Fill Bounce",
        "framing": "extreme macro detail",
        "angle": "straight-on perpendicular",
        "medium_type": "35mm_flagship_digital",
    },
    "canon_eos_r1": {
        "lens": "Canon RF 70-200mm F2.8L IS USM Z",
        "aperture": "f/2.8",
        "dof": "Instantaneous cross-type autofocus lock with telephoto subject isolation and frozen athletic motion",
        "aspect_ratio": "16:9",
        "film_stock": "digital_raw",
        "lighting_key": "strobe_para",
        "lighting": "High-Intensity Arena Key Strobe with Razor Edge Rim Separation",
        "framing": "dynamic full-action frame",
        "angle": "low-angle dramatic",
        "medium_type": "35mm_flagship_digital",
    },
    "canon_eos_r5_ii": {
        "lens": "Canon RF 85mm F1.2L USM",
        "aperture": "f/1.4",
        "dof": "Sublime Vogue-grade background melt with tack-sharp focus on near eye iris and micro-dermal texture",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "beauty_dish",
        "lighting": "High-Fashion Beauty Dish with 20° Honeycomb Grid & Diffuser Sock",
        "framing": "tight head and shoulders portrait",
        "angle": "eye-level flattering",
        "medium_type": "35mm_flagship_digital",
    },
    "canon_eos_r6_iii": {
        "lens": "Canon RF 24-70mm F2.8L IS USM",
        "aperture": "f/4.0",
        "dof": "Versatile commercial standard depth with crisp edge-to-edge clarity and natural environment presence",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Natural Directional Window Daylight with Soft Muslin Bounce",
        "framing": "medium environmental editorial portrait",
        "angle": "eye-level natural",
        "medium_type": "35mm_flagship_digital",
    },
    "nikon_z9": {
        "lens": "NIKKOR Z 135mm f/1.8 S Plena",
        "aperture": "f/1.8",
        "dof": "Plena optical signature: absolute zero vignetting, perfectly circular edge-to-edge bokeh discs, and tack-sharp subject acutance",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "beauty_dish",
        "lighting": "Sculptural Key Light with 4:1 Dramatic Contrast Ratio",
        "framing": "tight head and shoulders portrait",
        "angle": "eye-level direct",
        "medium_type": "35mm_flagship_digital",
    },
    "nikon_z5_ii": {
        "lens": "NIKKOR Z 50mm f/1.8 S",
        "aperture": "f/2.8",
        "dof": "True-to-life human eye perspective with benchmark optical acutance and natural dimensional depth",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Available Natural Daylight with Soft Room Diffusion",
        "framing": "medium documentary portrait",
        "angle": "eye-level honest",
        "medium_type": "35mm_flagship_digital",
    },
    "leica_m11": {
        "lens": "Leica APO-Summicron-M 50mm f/2 ASPH",
        "aperture": "f/2.0",
        "dof": "Benchmark Leica micro-contrast ('3D pop') with tack-sharp subject transition and authentic unposed photojournalistic depth",
        "aspect_ratio": "3:2",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Natural Available Ambient Light with Deep Natural Shadow Gradients",
        "framing": "intimate reportage medium portrait",
        "angle": "eye-level photojournalist",
        "medium_type": "35mm_rangefinder_digital",
    },
    "leica_m6_analog": {
        "lens": "Leica Summicron-M 50mm f/2 Dual-Range",
        "aperture": "f/2.0",
        "dof": "Classic 35mm rangefinder depth of field with organic silver grain and gentle highlight halation",
        "aspect_ratio": "3:2",
        "film_stock": "tri_x_400",
        "lighting_key": "window_daylight",
        "lighting": "Available Street Ambient Light with High Contrast Falloff",
        "framing": "candid street documentary frame",
        "angle": "eye-level spontaneous",
        "medium_type": "35mm_rangefinder_analog",
    },
    "leica_q3_monochrom": {
        "lens": "Leica Summilux 28mm f/1.7 ASPH",
        "aperture": "f/2.0",
        "dof": "Pure luminance sensor depth with obsidian blacks, luminous whites, and zero chromatic aberration",
        "aspect_ratio": "3:2",
        "film_stock": "tri_x_400",
        "lighting_key": "rembrandt_key",
        "lighting": "High-Contrast Chiaroscuro Single-Source Key with Deep Shadow Roll-off",
        "framing": "environmental street portrait",
        "angle": "eye-level immersive",
        "medium_type": "35mm_monochrome_compact",
    },
    "leica_sl3_p": {
        "lens": "Leica APO-Summicron-SL 50mm f/2 ASPH",
        "aperture": "f/2.0",
        "dof": "Apochromatic optical perfection with zero color fringing and immaculate skin micro-acutance",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Soft Diffused Daylight with Clean Subsurface Dermal Modeling",
        "framing": "three-quarter editorial portrait",
        "angle": "eye-level refined",
        "medium_type": "35mm_flagship_digital",
    },
    "panasonic_lumix_s1rii": {
        "lens": "Lumix S 100mm f/2.8 Macro",
        "aperture": "f/11",
        "dof": "Microscopic botanical/scientific focus-stacked depth of field with razor sharpness on cellular micro-structures",
        "aspect_ratio": "4:5",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Cross-Polarized Scientific Lighting with Zero Hotspot Glare",
        "framing": "1:1 macro scientific specimen frame",
        "angle": "perpendicular micro-inspection",
        "medium_type": "35mm_macro_scientific",
    },
    "nikon_fm2": {
        "lens": "AI-S Nikkor 105mm f/2.5",
        "aperture": "f/2.5",
        "dof": "Legendary National Geographic portrait depth: creamy background falloff with sharp, expressive eyes and punchy Kodachrome tones",
        "aspect_ratio": "3:2",
        "film_stock": "provia_100f",
        "lighting_key": "window_daylight",
        "lighting": "Available Open-Shade Daylight with Warm Ambient Bounce",
        "framing": "head and shoulders reportage portrait",
        "angle": "eye-level authentic",
        "medium_type": "35mm_slr_analog",
    },
    "contax_t2": {
        "lens": "Carl Zeiss Sonnar T* 38mm f/2.8",
        "aperture": "f/2.8",
        "dof": "Direct on-camera xenon flash with rapid inverse-square falloff, dark backdrop, and 90s celebrity snapshot intimacy",
        "aspect_ratio": "3:2",
        "film_stock": "portra_400",
        "lighting_key": "hard_flash",
        "lighting": "Direct Hard On-Camera Strobe with High-Contrast Falloff (90s Editorial)",
        "framing": "candid snapshot portrait",
        "angle": "eye-level close snapshot",
        "medium_type": "compact_point_and_shoot",
    },
    "ricoh_gr_iv": {
        "lens": "GR Lens 18.3mm f/2.8",
        "aperture": "f/5.6",
        "dof": "Deep snapshot street focus from 1 meter to infinity, rapid snap capture, and gritty urban textures",
        "aspect_ratio": "3:2",
        "film_stock": "classic_chrome",
        "lighting_key": "window_daylight",
        "lighting": "Harsh Midday Urban Sunlight with Crisp Geometric Shadows",
        "framing": "wide dynamic street documentary",
        "angle": "hip-level candid street angle",
        "medium_type": "compact_point_and_shoot",
    },
    "dji_mavic_4_pro": {
        "lens": "Hasselblad 28mm-equivalent f/2.8 Aerial Optics",
        "aperture": "f/5.6",
        "dof": "Infinite aerial depth of field from 400ft altitude with immaculate geometric planar ground resolution",
        "aspect_ratio": "16:9",
        "film_stock": "digital_raw",
        "lighting_key": "golden_hour",
        "lighting": "Low-Angle Sunset Sun Casting Long Raking Shadows Across Landscape",
        "framing": "nadir top-down aerial landscape",
        "angle": "top-down 90-degree nadir",
        "medium_type": "aerial_drone",
    },
    "arri_alexa_35": {
        "lens": "Atlas Orion 65mm T2.0 2x Anamorphic Prime",
        "aperture": "T2.0",
        "dof": "Hollywood feature film 2.0x anamorphic squeeze with horizontal cyan streak flares and tall vertical oval bokeh",
        "aspect_ratio": "16:9",
        "film_stock": "arri_logc4",
        "lighting_key": "tungsten_candle",
        "lighting": "Cinematic Key with Hazy Atmospheric Backlight and Organic Fill",
        "framing": "wide anamorphic cinematic frame",
        "angle": "cinematic shoulder-height",
        "medium_type": "cinema_digital",
    },
    "arri_alexa_265": {
        "lens": "ARRI Rental Prime 65 S 50mm T1.8",
        "aperture": "T2.0",
        "dof": "Monumental 65mm large-format digital cinema vista with majestic falloff and sublime dynamic range",
        "aspect_ratio": "16:9",
        "film_stock": "arri_logc4",
        "lighting_key": "rembrandt_key",
        "lighting": "Directional Soft Cinema Key with Subdued Low-Key Fill",
        "framing": "cinematic medium wide shot",
        "angle": "cinematic eye-level",
        "medium_type": "cinema_digital",
    },
    "sony_fx_series": {
        "lens": "Sony FE 50mm f/1.2 GM",
        "aperture": "f/2.8",
        "dof": "Sony VENICE S-Cinetone aesthetic with soft rolloff, 180-degree motion shutter, and deep shadows",
        "aspect_ratio": "16:9",
        "film_stock": "arri_logc4",
        "lighting_key": "tungsten_candle",
        "lighting": "Practical Neon and Tungsten Night Illumination with S-Cinetone Color Science",
        "framing": "cinematic medium close-up",
        "angle": "cinematic eye-level",
        "medium_type": "cinema_digital",
    },
    "imax_msm_9802": {
        "lens": "IMAX 65mm Large-Format Prime Lens",
        "aperture": "f/4.0",
        "dof": "Monumental 15-perf 65mm motion picture depth, expansive IMAX scale, and fine motion picture silver grain",
        "aspect_ratio": "16:9",
        "film_stock": "tri_x_400",
        "lighting_key": "window_daylight",
        "lighting": "Epic Natural Available Light with Colossal Dynamic Range",
        "framing": "monumental IMAX scale close-up",
        "angle": "eye-level monumental",
        "medium_type": "cinema_large_format",
    },
    "canon_powershot_g7x_iii": {
        "lens": "Integrated 8.8-36.8mm f/1.8-2.8 IS Lens @ 24mm equiv",
        "aperture": "f/4.0",
        "dof": "Deep environmental 1-inch sensor focus with rapid flash falloff, intimate snapshot perspective, and natural background storytelling",
        "aspect_ratio": "3:2",
        "film_stock": "digital_raw",
        "lighting_key": "hard_flash",
        "lighting": "Direct On-Camera Xenon Snapshot Flash with Crisp Inverse-Square Falloff",
        "framing": "spontaneous intimate snapshot medium portrait",
        "angle": "eye-level candid",
        "medium_type": "compact_point_and_shoot",
    },
    "fujifilm_x_e5": {
        "lens": "FUJINON XF 27mm f/2.8 R WR",
        "aperture": "f/5.6",
        "dof": "Tactile 40.2MP APS-C X-Trans micro-acutance without anti-aliasing filter, organic film grain, and balanced zone-focus depth",
        "aspect_ratio": "3:2",
        "film_stock": "classic_chrome",
        "lighting_key": "window_daylight",
        "lighting": "Available Directional Natural Street Light with Organic Shadow Nuances",
        "framing": "medium rangefinder street documentary",
        "angle": "eye-level rangefinder perspective",
        "medium_type": "aps_c_rangefinder",
    },
    "nikon_z50_ii": {
        "lens": "NIKKOR Z DX 24mm f/1.7",
        "aperture": "f/2.8",
        "dof": "Crisp EXPEED 7 optical acutance with smooth subject isolation at f/1.7-f/2.8 and neutral color fidelity",
        "aspect_ratio": "3:2",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Available Workshop Natural Daylight with Soft Room Diffusion",
        "framing": "three-quarter documentary artisan portrait",
        "angle": "eye-level honest documentary",
        "medium_type": "aps_c_mirrorless",
    },
    "om_system_om5_ii": {
        "lens": "M.Zuiko Digital ED 12-40mm f/2.8 PRO II",
        "aperture": "f/4.0",
        "dof": "Deep Micro Four Thirds wilderness depth keeping foreground botanical textures to mountain ridges in sharp focus with 7.5-stop Sync IS",
        "aspect_ratio": "4:3",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Atmospheric Misty Mountain Daylight with Natural Earthy Contrast",
        "framing": "environmental medium wilderness landscape",
        "angle": "eye-level rugged expedition",
        "medium_type": "mft_weatherproof",
    },
    "panasonic_lumix_g97": {
        "lens": "Leica DG Vario-Elmarit 12-60mm f/2.8-4.0 ASPH POWER O.I.S.",
        "aperture": "f/4.0",
        "dof": "Leica DG optical micro-contrast with V-Log L wide tonal latitude and balanced Micro Four Thirds storytelling depth",
        "aspect_ratio": "3:2",
        "film_stock": "digital_raw",
        "lighting_key": "window_daylight",
        "lighting": "Natural Documentary Ambient Daylight with Soft Directional Side-Fill",
        "framing": "three-quarter craft documentary portrait",
        "angle": "chest-level documentary angle",
        "medium_type": "mft_hybrid",
    },
    "sony_a7c_ii": {
        "lens": "Sony FE 40mm F2.5 G (SEL40F25G)",
        "aperture": "f/2.8",
        "dof": "Shallow 33MP full-frame planar subject isolation with cinematic S-Cinetone skin modeling and BIONZ XR AI eye tracking",
        "aspect_ratio": "3:2",
        "film_stock": "digital_raw",
        "lighting_key": "golden_hour",
        "lighting": "Low-Angle Golden Hour Urban Backlight with Subtle Rim Separation",
        "framing": "three-quarter street editorial portrait",
        "angle": "eye-level dynamic street perspective",
        "medium_type": "compact_full_frame",
    },
}


# ==============================================================================
# 4. PROMPT INTELLIGENCE ENGINE
# ==============================================================================

class PromptIntelligenceEngine:
    """Intelligent coordinator for scene intent parsing, camera recommendation, and quality checks."""

    @classmethod
    def extract_intent(cls, prompt: str) -> SceneIntent:
        """Parse natural user prompt into semantic photographic intent."""
        text = prompt.strip().lower()

        # Genre classification
        genre = "portrait"  # default
        if any(w in text for w in ["cinema", "cinematic", "movie", "film still", "anamorphic", "hollywood", "scene still"]):
            genre = "cinema"
        elif any(w in text for w in ["macro", "microscopic", "insect", "specimen", "petal", "dewdrop", "gear teeth", "iris macro", "micro-relief", "extreme closeup", "close-up"]):
            genre = "macro_detail"
        elif any(w in text for w in ["bird", "eagle", "lion", "tiger", "cheetah", "wolf", "wildlife", "animal", "safari", "falcon", "prey"]):
            genre = "wildlife"
        elif any(w in text for w in ["sport", "sports", "athlete", "sprint", "running", "fencing", "ballet", "jump", "dance", "tournament", "race", "match"]):
            genre = "sports_action"
        elif any(w in text for w in ["building", "architecture", "facade", "rotunda", "cathedral", "skyscraper", "concrete", "brutalist"]):
            genre = "architecture"
        elif any(w in text for w in ["street", "alley", "alleyway", "sidewalk", "boulevard", "pedestrian", "candid", "flaneur"]):
            genre = "street"
        elif any(w in text for w in ["landscape", "mountain", "desert", "dune", "ocean", "valley", "horizon", "forest"]):
            genre = "landscape"
        elif any(w in text for w in ["fashion", "haute couture", "vogue", "editorial", "runway", "trench coat", "dress", "model", "silk"]):
            genre = "fashion"
        elif any(w in text for w in ["watchmaker", "tailor", "craftsman", "artisan", "workshop", "sculptor", "blacksmith", "carpenter"]):
            genre = "documentary"
        elif any(w in text for w in ["bottle", "perfume", "cosmetic", "product", "packaging", "glassware", "watch on table"]):
            genre = "still_life"

        # Flags
        is_monochrome = any(w in text for w in ["black and white", "b&w", "monochrome", "monochromatic", "tri-x", "silver halide", "grayscale"])
        is_cinematic = any(w in text for w in ["cinematic", "movie", "film still", "anamorphic", "cinema", "widescreen", "2.39:1"])
        is_macro = genre == "macro_detail" or any(w in text for w in ["macro", "1:1", "close up", "close-up", "extreme detail", "microscopic", "pores", "lashes"])
        is_action = genre == "sports_action" or any(w in text for w in ["running", "sprinting", "jumping", "flying", "leaping", "speed", "fast"])
        is_aerial = any(w in text for w in ["aerial", "drone", "nadir", "top down", "top-down", "bird's eye", "birds eye", "high altitude"])
        is_product = genre == "still_life" or any(w in text for w in ["bottle", "sku", "perfume", "cosmetic", "product shot", "ecommerce"])

        # Extract Subject Entities (nouns and noun phrases)
        subject_entities: list[str] = []
        # Extract meaningful subject keywords from prompt (filtering common stop words)
        stop_words = {
            "a", "an", "the", "in", "on", "at", "with", "and", "or", "of", "to", "for", "by",
            "is", "are", "was", "were", "be", "being", "been", "shot", "photo", "photograph",
            "image", "picture", "camera", "lens", "looking", "standing", "sitting", "there",
            "this", "that", "it", "its", "my", "your", "his", "her", "their", "under", "over"
        }
        words = re.findall(r"[a-zA-Z0-9'-]+", text)
        meaningful_tokens = [w for w in words if w not in stop_words and len(w) > 2]
        subject_entities = meaningful_tokens[:8]

        # Extract Environment cues
        env_cues = []
        env_keywords = ["street", "workshop", "atelier", "studio", "room", "cathedral", "forest", "desert", "beach", "city", "paris", "tokyo", "new york", "london", "rotunda", "library", "mountain", "plains", "savanna", "field", "mews"]
        for ek in env_keywords:
            if ek in text:
                env_cues.append(ek)

        # Extract Lighting cues
        lighting_cues = []
        light_keywords = ["golden hour", "sunset", "dusk", "dawn", "sunlight", "sunbeam", "sun", "afternoon", "window", "strobe", "flash", "neon", "candle", "tungsten", "overcast", "fog", "rain", "dark", "shadow", "chiaroscuro", "high-key", "low-key"]
        for lk in light_keywords:
            if lk in text:
                lighting_cues.append(lk)

        # Depth & Scale preference
        depth_scale = "medium_three_quarter"
        if is_macro:
            depth_scale = "extreme_macro"
        elif is_aerial:
            depth_scale = "aerial"
        elif any(w in text for w in ["panoramic", "panorama", "xpan", "wide horizon"]):
            depth_scale = "panoramic"
        elif any(w in text for w in ["headshot", "close up", "face", "eyes", "lips", "profile"]):
            depth_scale = "tight_headshot"
        elif any(w in text for w in ["full body", "full length", "standing tall", "feet to head", "shoes"]):
            depth_scale = "full_length"
        elif any(w in text for w in ["wide", "environmental", "landscape", "vista", "grand"]):
            depth_scale = "wide_environmental"

        # Motion cadence
        motion_cadence = "still"
        if is_action:
            motion_cadence = "high_speed"
        elif any(w in text for w in ["motion blur", "blur", "trail", "rush", "streaking"]):
            motion_cadence = "motion_blur"

        return SceneIntent(
            raw_prompt=prompt,
            primary_genre=genre,
            subject_entities=subject_entities,
            environment_cues=env_cues,
            lighting_cues=lighting_cues,
            motion_cadence=motion_cadence,
            depth_scale=depth_scale,
            is_monochrome_intent=is_monochrome,
            is_cinematic_intent=is_cinematic,
            is_macro_intent=is_macro,
            is_action_intent=is_action,
            is_aerial_intent=is_aerial,
            is_product_intent=is_product,
        )

    @classmethod
    def score_profile(cls, profile_id: str, intent: SceneIntent) -> float:
        """Score a camera profile's optical fitness for the extracted intent."""
        score = 50.0  # baseline
        spec = DEFAULT_HARDWARE_SPECS.get(profile_id, {})
        medium_type = spec.get("medium_type", "")

        # Genre-specific affinity bonuses
        if intent.primary_genre in ("portrait", "fashion", "documentary"):
            if profile_id in ("phase_one_iq4", "hasselblad_x2d_ii_100c", "fujifilm_gfx100ii"):
                score += 35.0  # Flagship medium format resolves unmatched skin and fabric
            elif profile_id in ("canon_eos_r5_ii", "nikon_z9", "leica_sl3_p", "leica_m11", "sony_a7c_ii"):
                score += 25.0
            elif profile_id in ("pentax_67ii", "contax_645", "hasselblad_500cm", "mamiya_rz67"):
                score += 30.0  # Analog character portraits
            elif profile_id in ("panasonic_lumix_g97", "nikon_z50_ii", "fujifilm_x_e5"):
                score += 25.0  # Tactile artisan/travel documentary

        elif intent.primary_genre == "street":
            if profile_id in ("leica_m11", "leica_m6_analog", "ricoh_gr_iv", "fujifilm_gfx100rf", "fujifilm_x_e5"):
                score += 40.0
            elif profile_id in ("contax_t2", "nikon_fm2", "leica_q3_monochrom", "canon_powershot_g7x_iii", "sony_a7c_ii", "nikon_z50_ii"):
                score += 35.0

        elif intent.primary_genre == "architecture":
            if profile_id in ("linhof_technika_4x5", "fujifilm_gfx100ii", "phase_one_iq4"):
                score += 40.0
            elif profile_id in ("hasselblad_xpan", "sony_a7rv"):
                score += 25.0

        elif intent.primary_genre in ("wildlife", "sports_action"):
            if profile_id in ("sony_a1_ii", "canon_eos_r1", "nikon_z9"):
                score += 45.0
            elif profile_id in ("canon_eos_r5_ii", "canon_eos_r6_iii"):
                score += 30.0

        elif intent.primary_genre == "macro_detail":
            if profile_id in ("panasonic_lumix_s1rii", "sony_a7rv", "phase_one_iq4", "canon_eos_r5_ii"):
                score += 45.0
            elif profile_id in ("mamiya_rz67", "om_system_om5_ii"):
                score += 35.0

        elif intent.primary_genre == "cinema":
            if profile_id in ("arri_alexa_35", "arri_alexa_265", "sony_fx_series", "imax_msm_9802"):
                score += 45.0
            elif profile_id == "hasselblad_xpan":
                score += 30.0

        elif intent.primary_genre == "landscape":
            if profile_id in ("hasselblad_xpan", "deardorff_8x10", "linhof_technika_4x5", "phase_one_iq4"):
                score += 35.0
            elif profile_id in ("fujifilm_gfx100ii", "hasselblad_x2d_ii_100c", "om_system_om5_ii"):
                score += 35.0

        elif intent.primary_genre == "still_life":
            if profile_id in ("phase_one_iq4", "sony_a7rv", "hasselblad_x2d_ii_100c"):
                score += 40.0

        # Special flag and keyword affinities
        prompt_lower = intent.raw_prompt.lower()
        if any(w in prompt_lower for w in ["mist", "rain", "weather", "waterfall", "wilderness", "hike", "hiking", "alpine", "expedition", "outdoor", "moss"]):
            if profile_id == "om_system_om5_ii":
                score += 40.0

        if any(w in prompt_lower for w in ["vlog", "snapshot", "flash", "party", "izakaya", "café", "casual", "friends", "yokocho"]):
            if profile_id == "canon_powershot_g7x_iii":
                score += 40.0

        if any(w in prompt_lower for w in ["craft", "artisan", "workshop", "leather", "pottery", "woodworking", "ceramicist"]):
            if profile_id in ("panasonic_lumix_g97", "nikon_z50_ii"):
                score += 35.0

        if any(w in prompt_lower for w in ["reala", "film simulation", "classic chrome", "fuji", "gion", "kyoto", "machiya"]):
            if profile_id == "fujifilm_x_e5":
                score += 45.0

        if any(w in prompt_lower for w in ["s-cinetone", "compact full frame", "milan", "street style", "street fashion", "fashion stylist"]):
            if profile_id == "sony_a7c_ii":
                score += 40.0

        if intent.is_monochrome_intent:
            if profile_id in ("leica_q3_monochrom", "imax_msm_9802", "deardorff_8x10", "antique_view_8x10", "leica_m6_analog"):
                score += 40.0

        if intent.is_aerial_intent:
            if profile_id == "dji_mavic_4_pro":
                score += 60.0

        if intent.is_cinematic_intent:
            if profile_id in ("arri_alexa_35", "arri_alexa_265", "sony_fx_series", "hasselblad_xpan"):
                score += 35.0

        if intent.is_action_intent:
            if profile_id in ("sony_a1_ii", "canon_eos_r1", "nikon_z9"):
                score += 30.0

        return score

    @classmethod
    def enhance_scene_prompt(cls, raw_prompt: str, intent: SceneIntent, profile_id: str, tier: int) -> str:
        """Transform raw prompt into a rich photographic scene description while preserving 100% of user intent."""
        spec = DEFAULT_HARDWARE_SPECS.get(profile_id, {})
        camera_title = PROFILE_DISPLAY_NAMES.get(profile_id, profile_id)
        lens = spec.get("lens", "Prime Lens")
        dof = spec.get("dof", "authentic depth of field")
        lighting = spec.get("lighting", "natural lighting")
        
        # Clean user prompt without breaking grammar
        clean_user_scene = raw_prompt.strip()
        if clean_user_scene.endswith("."):
            clean_user_scene = clean_user_scene[:-1]

        # Enforce Gaze Anchor for portraits if people are present
        gaze_anchor = ""
        if intent.primary_genre in ("portrait", "fashion", "documentary") and any(w in clean_user_scene.lower() for w in ["man", "woman", "person", "watchmaker", "tailor", "model", "face", "girl", "boy", "artisan", "elderly", "client", "worker"]):
            gaze_anchor = ", facing camera with direct eye contact, natural dignified posture and expression"

        if tier == 1:
            # Primary Optical Master: Maximum micro-relief and resolving authority
            return (
                f"{clean_user_scene}{gaze_anchor}. "
                f"Masterwork photographic capture on {camera_title} with {lens}. "
                f"Tack-sharp focus on primary focal plane with natural micro-contrast and visible epidermal pores and fine textile weave. "
                f"{lighting}. "
                f"{dof}, preserving organic tonal gradation and unretouched authentic physical materiality."
            )
        elif tier == 2:
            # Distinct Aesthetic: Film tone or distinct optical rendering
            medium_desc = "classic analog silver-halide tonal depth" if "analog" in spec.get("medium_type", "") else "distinct high-fidelity optical rendering"
            return (
                f"{clean_user_scene}{gaze_anchor}. "
                f"Photographic study captured on {camera_title} with {lens}. "
                f"Emphasizing {medium_desc}, smooth highlight roll-off, and true-to-life surface textures. "
                f"{lighting}. "
                f"{dof}."
            )
        else:
            # High-Character Rig: Atmospheric, expressive, or monumental presence
            return (
                f"{clean_user_scene}{gaze_anchor}. "
                f"Atmospheric character capture on {camera_title} with {lens}. "
                f"Dramatic photographic presence with authentic dimensional separation, deep shadows, and tactile textural clarity. "
                f"{lighting}. "
                f"{dof}."
            )

    @classmethod
    def verify_quality_gate(
        cls,
        user_prompt: str,
        enhanced_scene: str,
        camera_name: str,
        lens: str,
        aperture: str,
        lighting: str,
        profile_id: str,
    ) -> QualityGateResult:
        """Automated Quality Gate enforcing Anti-Drift and Anti-Hallucination."""
        # 1. Anti-Drift Entity Recall Verification
        # Extract user nouns & key tokens (min length 3, excluding stopwords)
        stop_words = {
            "the", "and", "with", "for", "from", "that", "this", "shot", "photo", "photograph",
            "camera", "lens", "looking", "standing", "under", "over", "into", "onto", "about",
            "your", "his", "her", "their", "best", "some", "like", "very", "just"
        }
        user_tokens = set(re.findall(r"[a-zA-Z0-9]+", user_prompt.lower()))
        filtered_user_tokens = [t for t in user_tokens if t not in stop_words and len(t) > 2]
        
        enhanced_lower = enhanced_scene.lower()
        preserved = []
        missing = []

        for t in filtered_user_tokens:
            if t in enhanced_lower:
                preserved.append(t)
            else:
                missing.append(t)

        drift_score = 100.0 if not filtered_user_tokens else (len(preserved) / len(filtered_user_tokens)) * 100.0

        # 2. Strict Zero-Artist Compliance Scan
        detected_artists = []
        for artist in PROHIBITED_ARTIST_NAMES:
            pattern = r"\b" + re.escape(artist) + r"\b"
            if re.search(pattern, enhanced_lower):
                detected_artists.append(artist)

        zero_artist_verified = (len(detected_artists) == 0)

        # 3. Physical Optics Validation
        # Verify that lens exists in LENS_CATALOG for that profile or is physically realistic
        catalog_lenses = LENS_CATALOG.get(profile_id, [])
        lens_clean = lens.split(" (")[0].strip().lower()
        physical_optics_verified = True
        if catalog_lenses:
            matched_lens = any(lens_clean in cl.lower() for cl in catalog_lenses)
            if not matched_lens:
                # Still check if valid focal length format
                physical_optics_verified = bool(re.search(r"\b\d+mm\b", lens_clean))
        else:
            physical_optics_verified = bool(re.search(r"\b\d+mm\b", lens_clean) or "lens" in lens_clean)

        # 4. Negative Shield Safety and Render Defect Check
        negative_shield_safe = True
        for defect in PROHIBITED_DEFECT_TOKENS:
            if re.search(r"\b" + re.escape(defect) + r"\b", enhanced_lower):
                negative_shield_safe = False
                break

        passed = (drift_score >= 80.0) and zero_artist_verified and physical_optics_verified and negative_shield_safe
        overall = int(round(drift_score * 0.5 + (50.0 if zero_artist_verified else 0.0)))

        summary_parts = []
        if drift_score >= 99.0:
            summary_parts.append("✓ Anti-Drift: 100% Intent Preserved")
        else:
            summary_parts.append(f"✓ Anti-Drift: {drift_score:.1f}% Preserved")

        if zero_artist_verified:
            summary_parts.append("✓ Anti-Hallucination: Zero Artists")
        else:
            summary_parts.append(f"⚠️ Artist Detected: {', '.join(detected_artists)}")

        if physical_optics_verified:
            summary_parts.append("✓ Valid Physical Optics")

        return QualityGateResult(
            passed=passed,
            anti_drift_score=drift_score,
            preserved_entities=preserved,
            missing_entities=missing,
            zero_artist_verified=zero_artist_verified,
            detected_artists=detected_artists,
            physical_optics_verified=physical_optics_verified,
            negative_shield_safe=negative_shield_safe,
            overall_score=overall,
            summary=" | ".join(summary_parts),
        )

    @classmethod
    def recommend_rigs(
        cls,
        prompt: str,
        target: Union[str, TargetEngine] = TargetEngine.FLUX,
        num_recommendations: int = 3,
    ) -> list[RigRecommendation]:
        """Evaluate prompt intent and return top 3 distinct calibrated optical rig recommendations."""
        if not prompt or not prompt.strip():
            prompt = "A high-resolution editorial portrait with natural lighting"

        intent = cls.extract_intent(prompt)

        # Score all profiles
        scored_profiles: list[tuple[str, float]] = []
        for pid in DEFAULT_HARDWARE_SPECS.keys():
            score = cls.score_profile(pid, intent)
            scored_profiles.append((pid, score))

        # Sort descending by score
        scored_profiles.sort(key=lambda x: x[1], reverse=True)

        # Selection of 3 diverse tiers:
        # Tier 1: Highest overall score (Primary Optical Master)
        # Tier 2: Different medium/sensor (e.g. analog film, 35mm rangefinder, or classic medium format)
        # Tier 3: Expressive character rig (e.g. large format, cinematic anamorphic, or high-speed freeze)
        tier1_id = scored_profiles[0][0]
        tier1_spec = DEFAULT_HARDWARE_SPECS[tier1_id]
        tier1_medium = tier1_spec.get("medium_type", "")

        tier2_id = None
        for pid, _ in scored_profiles[1:]:
            p_spec = DEFAULT_HARDWARE_SPECS[pid]
            p_medium = p_spec.get("medium_type", "")
            # Select different medium from Tier 1
            if p_medium != tier1_medium:
                tier2_id = pid
                break
        if not tier2_id:
            tier2_id = scored_profiles[1][0]

        tier3_id = None
        for pid, _ in scored_profiles[2:]:
            if pid not in (tier1_id, tier2_id):
                p_spec = DEFAULT_HARDWARE_SPECS[pid]
                p_medium = p_spec.get("medium_type", "")
                # Prefer large format, cinema, or high-character analog
                if any(k in p_medium for k in ["large_format", "cinema", "panoramic", "compact", "analog"]):
                    tier3_id = pid
                    break
        if not tier3_id:
            tier3_id = scored_profiles[2][0]

        selected_pids = [tier1_id, tier2_id, tier3_id]
        tier_names = [
            "1st Best (Primary Optical Master)",
            "2nd Best (Distinct Aesthetic)",
            "3rd Best (High-Character / Creative Rig)",
        ]

        rationales = [
            f"Ultimate resolving authority for {intent.primary_genre}. Delivers benchmark optical sharpness, natural micro-contrast, and authentic unretouched physical texture.",
            f"Compelling alternative aesthetic. Offers distinct color science, beautiful highlight roll-off, and authentic atmospheric character.",
            f"Specialized creative signature. Provides dramatic depth of field, expressive optics, and unique tactile storytelling presence.",
        ]

        recommendations: list[RigRecommendation] = []

        for rank_idx, (pid, tier_name, base_rationale) in enumerate(zip(selected_pids, tier_names, rationales), start=1):
            spec = DEFAULT_HARDWARE_SPECS[pid]
            camera_name = PROFILE_DISPLAY_NAMES.get(pid, pid)
            lens = spec["lens"]
            aperture = spec["aperture"]
            dof = spec["dof"]
            lighting = spec["lighting"]
            lighting_key = spec["lighting_key"]
            aspect_ratio = spec["aspect_ratio"]
            framing = spec["framing"]
            angle = spec["angle"]
            film_stock = spec["film_stock"]
            skin_lighting = spec.get("skin_lighting")

            # Match aspect ratio to intent if explicitly cinematic or square
            if intent.is_cinematic_intent and aspect_ratio not in ("16:9", "2.7:1"):
                aspect_ratio = "16:9"
            elif intent.is_monochrome_intent and pid == "hasselblad_500cm":
                aspect_ratio = "1:1"

            # Create enhanced prompt
            enhanced = cls.enhance_scene_prompt(prompt, intent, pid, rank_idx)

            # Build detailed rationale
            rationale = (
                f"{base_rationale} "
                f"Paired with {lens} at {aperture} for optimal optical MTF sharpness and {lighting_key.replace('_', ' ')} illumination."
            )

            # Quality gate certification
            qgate = cls.verify_quality_gate(
                user_prompt=prompt,
                enhanced_scene=enhanced,
                camera_name=camera_name,
                lens=lens,
                aperture=aperture,
                lighting=lighting,
                profile_id=pid,
            )

            title = f"{camera_name} // {lens.split(' (')[0]}"

            recommendations.append(
                RigRecommendation(
                    rank=rank_idx,
                    tier_name=tier_name,
                    title=title,
                    camera_name=camera_name,
                    profile_id=pid,
                    lens=lens,
                    aperture=aperture,
                    depth_of_field=dof,
                    lighting=lighting,
                    lighting_key=lighting_key,
                    aspect_ratio=aspect_ratio,
                    framing=framing,
                    camera_angle=angle,
                    film_stock=film_stock,
                    skin_lighting=skin_lighting,
                    enhanced_scene=enhanced,
                    rationale=rationale,
                    quality_gate=qgate,
                )
            )

        return recommendations[:num_recommendations]

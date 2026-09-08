"""Profile manager for loading and overriding camera hardware configurations."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Optional

from .models import (
    CameraProfile,
    LightingSetup,
    MicroPhysics,
    NegativeShield,
    SceneInput,
    SensorOptics,
)

DEFAULT_PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles"

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


def load_profile(name_or_path: str = "phase_one_iq4") -> CameraProfile:
    """Load a CameraProfile from an ID, profile name, or direct filepath.

    Args:
        name_or_path: 'phase_one_iq4', path to JSON file, or filename in profiles directory.

    Returns:
        CameraProfile instance.
    """
    # 1. Direct path check
    direct_path = Path(name_or_path)
    if direct_path.is_file():
        with open(direct_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CameraProfile.from_dict(data)

    # 2. Check in standard profiles directory
    candidate = DEFAULT_PROFILES_DIR / f"{name_or_path}.json"
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

    # 2. Check profiles directory
    if DEFAULT_PROFILES_DIR.is_dir():
        for json_file in sorted(DEFAULT_PROFILES_DIR.glob("*.json")):
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

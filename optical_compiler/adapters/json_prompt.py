"""JSON All-in-One Prompt Adapter.

Compiles a unified, self-contained JSON payload encapsulating scene parameters,
complete hardware camera specs, lighting geometry, micro-physics, negative shields,
and compiled prompts for all supported image generation engines.
"""

from __future__ import annotations

import json
from typing import Any

from ..models import (
    CameraProfile,
    CompiledPayload,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from .base import BaseAdapter
from .flux import FluxAdapter
from .gpt_images import GPTImagesAdapter
from .imagen import ImagenAdapter
from .midjourney import MidjourneyAdapter
from .sdxl import SDXLAdapter


class JSONAllInOneAdapter(BaseAdapter):
    """Compiles prompts into a unified, all-in-one structured JSON specification."""

    target_engine = TargetEngine.JSON_PROMPT

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings

        is_ref = bool(scene.reference and scene.reference.mode != ReferenceMode.NONE)
        ref_mode = scene.reference.mode if (scene.reference and scene.reference.mode) else ReferenceMode.NONE

        # 1. Compile child model prompts
        gpt_payload = GPTImagesAdapter().compile(scene, profile)
        imagen_payload = ImagenAdapter().compile(scene, profile)
        mj_payload = MidjourneyAdapter().compile(scene, profile)
        flux_payload = FluxAdapter().compile(scene, profile)
        sdxl_payload = SDXLAdapter().compile(scene, profile)

        # 2. Extract resolved negative tokens
        # 2. Extract resolved negative tokens
        all_neg_tokens = shield.all_tokens(
            include_anti_drift=is_ref,
            include_branding=scene.suppress_text_branding and not scene.has_product_lock,
            include_compression=True,
            include_outpaint=(ref_mode == ReferenceMode.OUTPAINT_FULL_BODY),
            include_skin_realism=scene.human_skin_realism,
            include_product_drift=scene.has_product_lock,
            include_hand_drift=scene.has_hand_lock,
            include_body_distortion=scene.has_body_morphology,
            include_reconstruction_drift=bool(scene.has_reconstruction_lock_4x or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X),
        )
        if scene.custom_negatives:
            all_neg_tokens.extend(scene.custom_negatives)

        # 3. Resolve resolution
        if ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            resolution_str = scene.output_resolution or "102MP Medium Format (11648 x 8736 native GFX100RF resolution)"
        elif ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X or scene.has_reconstruction_lock_4x:
            resolution_str = scene.output_resolution or "Exact 4X Linear Source-Locked Reconstruction (16X pixel area)"
        else:
            resolution_str = scene.output_resolution or f"12MP PNG, {scene.aspect_ratio}"

        # 4. Build master All-in-One JSON dictionary
        if scene.has_reconstruction_lock_4x or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X:
            protocol_name = "Professional 4X Reconstruction Lock Protocol (Linear Expansion + High-Fidelity Multi-Model Blend)"
        elif scene.has_stress_probe:
            probe_name = scene.stress_probe.name if scene.stress_probe else "NONE"
            protocol_name = f"PFEP v1.0 Diagnostic Stress Probe Protocol [{probe_name}]"
        elif scene.has_lighting_environment or scene.has_series_cohesion:
            protocol_name = "Exhibition Gallery Lighting & Series Cohesion Calibration Matrix"
        elif scene.is_policy_safe:
            protocol_name = "Policy-Safe Compliance Recovery & GenAI Photography Mastery Suite"
        elif scene.has_body_morphology:
            protocol_name = "Body Morphology & Proportional Volume Calibration Protocol"
        elif scene.has_material_style:
            protocol_name = "4D Volumetric & Premium Material Engine Master Specification"
        elif scene.is_print_calibrated:
            protocol_name = "Print-Calibrated Prepress & Exhibition Lab Matrix"
        elif scene.has_hand_lock and scene.has_product_lock:
            protocol_name = "Commercial Product SKU & Biomechanical 5-Point Hand Precision Gate Protocol"
        elif scene.is_anamorphic:
            protocol_name = "Cinema Anamorphic Optics & Flare Engine Master Specification"
        elif ref_mode == ReferenceMode.PRODUCT_LOCK or scene.has_product_lock:
            protocol_name = "Commercial Product SKU Lock & 100% Approval Gate"
        elif scene.has_hand_lock:
            protocol_name = "Biomechanical Hand & Finger Precision Gate Protocol"
        elif ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            protocol_name = "Universal De-Pixelate + Upscale Restoration (GFX100RF 102MP + Skin Realism Override)"
        elif ref_mode == ReferenceMode.IDENTITY_LOCK:
            protocol_name = "Identity-Locked Reference Portrait (Editorial Calm vs Chaos & Slow-Shutter Physics)"
        else:
            protocol_name = "Brutally Sharp Portrait Kit & All-in-One Prompt Engine"

        is_schema_3_6 = bool(
            scene.has_reconstruction_lock_4x
            or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X
        )
        is_schema_3_5 = bool(
            scene.has_stress_probe
            or scene.has_lighting_environment
            or scene.has_series_cohesion
            or scene.min_file_mb
        )
        is_schema_3_4 = bool(
            scene.has_body_morphology
            or scene.has_material_style
            or scene.is_print_calibrated
            or scene.is_policy_safe
            or scene.remove_text_when_present
        )
        is_schema_3_3 = bool(
            scene.has_hand_lock
            or scene.is_anamorphic
            or scene.has_copy_space
            or scene.has_gobo
        )
        schema_ver = "3.6" if is_schema_3_6 else ("3.5" if is_schema_3_5 else ("3.4" if is_schema_3_4 else ("3.3" if is_schema_3_3 else "3.2")))

        all_in_one_data: dict[str, Any] = {
            "$schema": "https://raw.githubusercontent.com/FabioLousJay/optical-camera-compiler/main/schemas/all_in_one_prompt.json",
            "generator": "Optical Camera Compiler",
            "schema_version": schema_ver,
            "protocol": protocol_name,
            "target_engine": "json",
            "scene": {
                "subject": scene.subject,
                "framing": scene.framing or "Not specified",
                "camera_angle": scene.camera_angle or "Not specified",
                "color_mode": "monochrome" if scene.is_monochrome else "color",
                "crowd_action": scene.crowd_action,
                "environment": scene.environment or "Studio / Controlled",
                "wardrobe": scene.wardrobe or "Not specified",
                "mood": scene.mood or "Editorial / Photorealistic",
                "aspect_ratio": scene.aspect_ratio,
                "output_resolution": resolution_str,
                "sharpness_protocol": scene.sharpness_protocol,
                "suppress_text_branding": scene.suppress_text_branding,
                "human_skin_realism": scene.human_skin_realism,
                "content_type": scene.content_type.value if scene.content_type else None,
                "text_preservation": scene.text_preservation,
                "product_crop": scene.product_crop,
                "sku_color": scene.sku_color,
                "cap_geometry": scene.cap_geometry,
                "label_kerning": scene.label_kerning,
                "material_finish": scene.material_finish,
                "seam_geometry": scene.seam_geometry,
                "approval_gate_100pct": scene.approval_gate_100pct,
                "hand_lock": scene.hand_lock,
                "grip_type": scene.grip_type.value if scene.grip_type else None,
                "hand_details": scene.hand_details,
                "anamorphic_squeeze": scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else None,
                "streak_flare": scene.streak_flare.value if scene.streak_flare else None,
                "iris_blades": scene.iris_blades.value if scene.iris_blades else None,
                "gobo": scene.gobo.value if scene.gobo else None,
                "grip_modifier": scene.grip_modifier.value if scene.grip_modifier else None,
                "lighting_ratio": scene.lighting_ratio.value if scene.lighting_ratio else None,
                "copy_space": scene.copy_space.value if scene.copy_space else None,
                "ad_safe_zone": scene.ad_safe_zone.value if scene.ad_safe_zone else None,
                "body_volume": scene.body_volume,
                "weight_lb": scene.weight_lb,
                "material_style": scene.material_style.value if scene.material_style else None,
                "background_style": scene.background_style.value if scene.background_style else None,
                "is_4d_volumetric": scene.is_4d_volumetric,
                "remove_text_when_present": scene.remove_text_when_present,
                "paper_profile": scene.paper_profile.value if scene.paper_profile else None,
                "policy_safe": scene.policy_safe,
                "stress_probe": scene.stress_probe.value if scene.stress_probe else None,
                "min_file_mb": scene.min_file_mb,
            },

            "product_fidelity": {
                "active": scene.has_product_lock,
                "product_crop_reference": scene.product_crop or (scene.reference.filename if scene.reference else None),
                "sku_color": scene.sku_color,
                "cap_geometry": scene.cap_geometry,
                "label_kerning": scene.label_kerning,
                "manufacturing_seams": scene.seam_geometry,
                "material_finish": scene.material_finish,
            },
            "commercial_sku_approval_gate": {
                "active": scene.has_product_lock and scene.approval_gate_100pct,
                "gate_1_cap_geometry": scene.cap_geometry or "Locked to product crop 100%",
                "gate_2_label_kerning": scene.label_kerning or "Locked to product crop 100%",
                "gate_3_parting_seams": scene.seam_geometry or "Locked to manufacturing specs",
                "gate_4_material_finish": scene.material_finish or "Locked to product crop 100%",
                "gate_5_sku_color": scene.sku_color or "Locked to product crop 100%",
                "acceptance_threshold": "100% physical and typographic fidelity required; zero tolerance for drift or hallucination",
            },
            "hand_biomechanics": {
                "active": scene.has_hand_lock,
                "grip_type": scene.grip_type.value if scene.grip_type else "ergonomic_contact_grip",
                "hand_details": scene.hand_details or "Natural 5-finger anatomical articulation",
                "metacarpal_ratio": "2:3:4:3.5:2.5",
                "contact_tissue_blanching": True,
                "gate_h1_metacarpal_architecture": "Thumb, index, middle, ring, pinky with 2:3:4:3.5:2.5 length ratio and distinct MCP, PIP, DIP joints",
                "gate_h2_grip_physics_contact_blanching": "Authentic micro-capillary tissue blanching under pressure, zero solid clipping",
                "gate_h3_flexion_creases_thenar": "Authentic palmar lines, defined thenar and hypothenar eminence musculature, visible wrist tendons",
                "gate_h4_nail_bed_realism": "Translucent nail plates, pink vascular flush, visible lunula crescents, micro-cuticles",
                "gate_h5_zero_mutation_shield": "100% rejection of fused digits, extra phalanges, rubber knuckles, dislocated thumbs",
            },
            "anamorphic_optics": {
                "active": scene.is_anamorphic,
                "squeeze_factor": scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x",
                "streak_flare": scene.streak_flare.value if scene.streak_flare else "cyan_blue",
                "streak_flare_coating": scene.streak_flare.value if scene.streak_flare else "cyan_blue",
                "iris_blade_count": scene.iris_blades.value if scene.iris_blades else "14_blade_circular",
                "bokeh_geometry": "2:1 vertical elliptical oval bokeh discs with cylindrical edge astigmatism",
                "diffraction_signature": "Symmetric starburst diffraction spikes on high-luminance point sources",
            },
            "lighting_grip": {
                "gobo_cookie_pattern": scene.gobo.value if scene.gobo else None,
                "gobo_pattern": scene.gobo.value if scene.gobo else None,
                "grip_modifier": scene.grip_modifier.value if scene.grip_modifier else None,
                "lighting_ratio": scene.lighting_ratio.value if scene.lighting_ratio else None,
            },
            "advertising_framing": {
                "active": scene.has_copy_space,
                "copy_space": scene.copy_space.value if scene.copy_space else "none",
                "ad_safe_zone": scene.ad_safe_zone.value if scene.ad_safe_zone else "none",
            },
            "body_morphology_volume_engine": {
                "active": scene.has_body_morphology,
                "volume_regions": scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else None),
                "target_weight_lb": scene.weight_lb,
                "weight_lb": scene.weight_lb,
                "proportionality_rule": "Strict proportionality to skeletal frame, head size, and total mass",
                "natural_bilateral_asymmetry": True,
                "soft_tissue_gravity_and_compression": True,
                "clothing_conformity": True,
                "anti_exaggeration_lock": True,
            },
            "volumetric_material_engine": {
                "active": scene.has_material_style or scene.is_4d_volumetric,
                "material_style": scene.material_style.value if scene.material_style else None,
                "background_style": scene.background_style.value if scene.background_style else None,
                "contour_rim_lighting": True,
                "specular_micro_physics": True,
                "conditional_text_removal": scene.remove_text_when_present,
            },
            "prepress_matrix": {
                "active": scene.is_print_calibrated,
                "paper_profile": scene.paper_profile.value if scene.paper_profile else (scene.print_spec.paper.value if scene.print_spec else None),
                "width_in": scene.print_spec.width_in if scene.print_spec else None,
                "height_in": scene.print_spec.height_in if scene.print_spec else None,
                "ppi": scene.print_spec.ppi if scene.print_spec else 300,
                "pixel_dimensions": (
                    f"{int(round(scene.print_spec.width_in * scene.print_spec.ppi))} x {int(round(scene.print_spec.height_in * scene.print_spec.ppi))}"
                    if scene.print_spec else None
                ),
                "rendering_intent": scene.print_spec.rendering_intent.value if scene.print_spec else None,
            },
            "policy_compliance_layer": {
                "active": scene.is_policy_safe,
                "compliance_mode": "editorial_dignified_fine_art",
                "fully_clothed": True,
                "physics_preserved": True,
            },
            "pfep_diagnostic_probe": {
                "active": scene.has_stress_probe,
                "probe_id": scene.stress_probe.value if scene.stress_probe else None,
                "probe_name": scene.stress_probe.name if scene.stress_probe else None,
                "directive": scene.stress_probe.directive_text if scene.stress_probe else None,
                "pass_gate_rule": "Identity == 2 AND total_score >= 12 across 8 evaluation axes",
            },
            "closed_loop_constraints": {
                "active": scene.has_closed_loop_constraints,
                "min_file_mb": scene.min_file_mb,
                "output_resolution": resolution_str,
                "physical_print_size": (
                    f"{scene.print_spec.width_in}\" x {scene.print_spec.height_in}\" @ {scene.print_spec.ppi} PPI"
                    if scene.print_spec and (scene.print_spec.width_in > 0 or scene.print_spec.height_in > 0)
                    else None
                ),
                "hash_algorithm": "SHA-256",
            },
            "exhibition_lighting_environment": {
                "active": scene.has_lighting_environment,
                "cct_kelvin": scene.lighting_environment.cct_kelvin if scene.lighting_environment else 5000,
                "illuminance_lux": scene.lighting_environment.illuminance_lux if scene.lighting_environment else 500,
                "spectral_cri": scene.lighting_environment.spectral_cri if scene.lighting_environment else 98.0,
                "wall_surround": scene.lighting_environment.wall_surround if scene.lighting_environment else "Neutral Gray 18%",
            },
            "series_visual_cohesion": {
                "active": scene.has_series_cohesion,
                "anchor_image_id": scene.series_cohesion.anchor_image_id if scene.series_cohesion else None,
                "gallery_zone": scene.series_cohesion.gallery_zone if scene.series_cohesion else None,
                "midtone_density": scene.series_cohesion.midtone_density if scene.series_cohesion else 1.0,
                "shadow_depth": scene.series_cohesion.shadow_depth if scene.series_cohesion else 1.0,
                "highlight_rolloff": scene.series_cohesion.highlight_rolloff if scene.series_cohesion else 1.0,
            },
            "reconstruction_lock_4x": {
                "active": bool(scene.has_reconstruction_lock_4x or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X),
                "linear_scale": 4,
                "area_scale": 16,
                "backend": scene.reconstruction_lock.backend.value if scene.reconstruction_lock else "realesrnet_x4plus",
                "denoise_strength": scene.reconstruction_lock.denoise_strength if scene.reconstruction_lock else 0.15,
                "blend_ratio": scene.reconstruction_lock.blend_ratio if scene.reconstruction_lock else 0.20,
                "protect_sky_haze": scene.reconstruction_lock.protect_sky_haze if scene.reconstruction_lock else True,
                "anti_model_stacking": True,
                "prohibit_diffusion_hallucination": True,
                "target_verification": "shasum -a 256 output_file",
            },
            "content_classification": {
                "type": scene.content_type.value if scene.content_type else "photograph",
                "is_flat_reproduction": bool(scene.content_type and scene.content_type.is_flat_reproduction),
                "reproduction_directive": (
                    "Render as flat reproduction capture. Suppress optical depth-of-field falloff, vignetting, and grain."
                    if (scene.content_type and scene.content_type.is_flat_reproduction)
                    else "Standard three-dimensional optical camera capture."
                ),
            },
            "human_skin_realism_override_protocol": {
                "active": scene.human_skin_realism,
                "enforced": scene.human_skin_realism,
                "priority": "absolute for any visible human skin; outranks all texture reconstruction, micro-detail recovery, and sharpness",
                "core_rule": "Human skin realism is more important than maximum detail. Skin must remain softer than eyes, hair, clothing, jewelry, teeth, text, and hard edges.",
                "rules": [
                    "When realistic skin and maximum sharpness conflict, choose realistic skin.",
                    "Remove AI-generated swirls, decorative micro-patterns, engraved texture, embossed texture, pore stamping, worm-like texture, and lace-like texture.",
                    "Preserve natural uneven skin texture and age-appropriate wrinkles without inventing pores or wrinkles.",
                    "Skin tonal transitions must remain smooth and photographic, never carved, crunchy, metallic, or HDR-like.",
                ],
            },
            "hardware_rendering_target": {
                "camera_system": optics.camera_system,
                "lens": optics.lens,
                "shutter": optics.shutter,
                "sensor_dimensions": optics.sensor_dimensions,
                "color_science": getattr(micro, "color_science", "Accurate 16-bit raw tonal latitude"),
            },
            "camera_hardware": {
                "profile_id": profile.profile_id,
                "title": profile.title,
                "camera_system": optics.camera_system,
                "sensor": {
                    "dimensions": optics.sensor_dimensions,
                    "type": optics.sensor_type,
                    "field_of_view": optics.full_frame_equivalent,
                    "iso_base": optics.iso_base,
                    "dynamic_range": optics.dynamic_range,
                },
                "optics": {
                    "lens": optics.lens,
                    "aperture_sweet_spot": optics.aperture_sweet_spot,
                    "shutter": optics.shutter,
                },
                "lighting_and_geometry": {
                    "primary_lighting": lighting.primary_lighting,
                    "light_transport": lighting.light_transport,
                },
                "micro_physics": {
                    "surface_rendering": micro.surface_rendering,
                    "depth_and_optics": micro.depth_and_optics,
                },
                "execution_directive": profile.execution_directive,
            },
            "reference_image": (
                {
                    "mode": ref_mode.value if hasattr(ref_mode, "value") else str(ref_mode),
                    "fidelity_lock": scene.reference.fidelity_lock,
                    "denoise_strength": scene.reference.denoise_strength,
                    "preserved_elements": scene.reference.preserved_elements,
                    "prohibited_drift": [
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
                    ] if (ref_mode == ReferenceMode.IDENTITY_LOCK or is_ref) else [],
                }
                if is_ref and scene.reference
                else None
            ),
            "negative_shield": {
                "render_defects": shield.render_defects,
                "skin_and_lighting_drift": shield.skin_and_lighting_drift,
                "anatomical_drift": shield.anatomical_drift,
                "branding_and_text": shield.branding_and_text if scene.suppress_text_branding else [],
                "compression_and_quality": shield.compression_and_quality,
                "anti_drift": shield.anti_drift_tokens if is_ref else [],
                "product_drift": shield.product_drift if scene.has_product_lock else [],
                "hand_drift": shield.hand_drift if scene.has_hand_lock else [],
                "body_distortion": shield.body_distortion if scene.has_body_morphology else [],
                "reconstruction_drift": shield.reconstruction_drift if (scene.has_reconstruction_lock_4x or ref_mode == ReferenceMode.RECONSTRUCTION_LOCK_4X) else [],
                "all_negative_tokens": all_neg_tokens,
            },
            "compiled_prompts": {
                "gpt_images": gpt_payload.positive_prompt,
                "gemini_imagen3": imagen_payload.positive_prompt,
                "midjourney_v8_2": mj_payload.positive_prompt,
                "flux": flux_payload.positive_prompt,
                "sdxl": {
                    "positive_prompt": sdxl_payload.positive_prompt,
                    "negative_prompt": sdxl_payload.negative_prompt,
                },
                "unified_master_prompt": flux_payload.unified_prompt,
            },
        }

        json_str = json.dumps(all_in_one_data, indent=2)

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=json_str,
            negative_prompt=", ".join(all_neg_tokens),
            parameters={
                "aspect_ratio": scene.aspect_ratio,
                "output_resolution": resolution_str,
                "format": "json",
            },
            metadata=all_in_one_data,
        )

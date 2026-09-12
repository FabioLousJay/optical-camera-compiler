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
        all_neg_tokens = shield.all_tokens(
            include_anti_drift=is_ref,
            include_branding=scene.suppress_text_branding,
            include_compression=True,
            include_outpaint=(ref_mode == ReferenceMode.OUTPAINT_FULL_BODY),
            include_skin_realism=scene.human_skin_realism,
        )
        if scene.custom_negatives:
            all_neg_tokens.extend(scene.custom_negatives)

        # 3. Resolve resolution
        if ref_mode == ReferenceMode.DEPIXELATE_GFX100RF:
            resolution_str = scene.output_resolution or "102MP Medium Format (11648 x 8736 native GFX100RF resolution)"
        else:
            resolution_str = scene.output_resolution or f"12MP PNG, {scene.aspect_ratio}"

        # 4. Build master All-in-One JSON dictionary
        all_in_one_data: dict[str, Any] = {
            "$schema": "https://raw.githubusercontent.com/FabioLousJay/optical-camera-compiler/main/schemas/all_in_one_prompt.json",
            "generator": "Optical Camera Compiler",
            "schema_version": "3.1",
            "protocol": (
                "Universal De-Pixelate + Upscale Restoration (GFX100RF 102MP + Skin Realism Override)"
                if ref_mode == ReferenceMode.DEPIXELATE_GFX100RF
                else "Brutally Sharp Portrait Kit & All-in-One Prompt Engine"
            ),
            "target_engine": "json",
            "scene": {
                "subject": scene.subject,
                "framing": scene.framing or "Not specified",
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

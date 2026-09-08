from __future__ import annotations

from ..models import CameraProfile, CompiledPayload, ReferenceMode, SceneInput, TargetEngine
from .base import BaseAdapter


class SDXLAdapter(BaseAdapter):
    """Compiles dual-channel positive and negative prompt payloads for SDXL."""

    target_engine = TargetEngine.SDXL

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings
        ref = scene.reference

        is_restore = ref and ref.mode == ReferenceMode.RESTORE_UPSCALE
        is_transform = ref and ref.mode == ReferenceMode.TRANSFORM_ADAPT

        # 1. Positive Prompt (Weighted camera and texture tokens)
        pos_chunks = []

        if is_restore:
            pos_chunks.append(
                "master optical remaster and high-resolution restoration of reference image, "
                "1:1 biometric identity lock, exact facial topology, unaltered bone structure"
            )
        elif is_transform:
            pos_chunks.append(
                "reference-guided photographic adaptation, biometric facial identity lock, "
                "exact facial bone structure and eye gaze anchored to source image"
            )

        # Scene foundation
        scene_str = scene.subject
        if scene.framing:
            scene_str = f"{scene.framing}, {scene_str}"
        if scene.environment:
            scene_str += f", {scene.environment}"
        if scene.wardrobe:
            scene_str += f", wearing {scene.wardrobe}"
        if scene.mood:
            scene_str += f", {scene.mood}"
        pos_chunks.append(scene_str)

        # Hardware & Optics
        hardware_tokens = [
            f"raw photograph captured on {optics.camera_system}",
            f"{optics.lens} at {optics.aperture_sweet_spot}",
            optics.sensor_dimensions,
            optics.shutter,
            optics.iso_base,
            optics.dynamic_range,
        ]
        if scene.optical_filter:
            hardware_tokens.append(scene.optical_filter)
        if scene.film_stock:
            hardware_tokens.append(f"{scene.film_stock} emulsion")
        pos_chunks.extend(hardware_tokens)

        # Lighting setup
        pos_chunks.extend(
            [
                lighting.primary_lighting,
                lighting.light_transport,
            ]
        )

        # Micro-texture & physical optical falloff
        pos_chunks.extend(
            [
                "resolved epidermal skin pores",
                "fine vellus facial hair",
                "subsurface dermal scattering",
                "natural material micro-relief and micro-abrasions",
                "high MTF optical acutance",
                "natural large-sensor f/8 depth of field falloff",
                "rectilinear optical projection",
            ]
        )

        if scene.custom_positives:
            pos_chunks.extend(scene.custom_positives)

        positive_prompt = ", ".join(pos_chunks)

        # 2. Negative Prompt (Comprehensive artifact suppression)
        neg_chunks = []
        neg_chunks.extend(shield.render_defects)
        neg_chunks.extend(shield.skin_and_lighting_drift)
        neg_chunks.extend(shield.anatomical_drift)

        if is_restore or is_transform:
            neg_chunks.extend(shield.anti_drift_tokens)

        # Extra standard SDXL plastic artifact suppressors
        neg_chunks.extend(
            [
                "over-sharpened",
                "unsharp mask halos",
                "doll skin",
                "porcelain skin",
                "airbrushed",
                "filter glow",
                "bad anatomy",
                "watermark",
                "signature",
            ]
        )

        if scene.custom_negatives:
            neg_chunks.extend(scene.custom_negatives)

        # Deduplicate while preserving order
        negative_prompt = ", ".join(dict.fromkeys(neg_chunks))

        # Resolution mapping based on aspect ratio
        ar_to_res = {
            "4:5": (896, 1152),
            "1:1": (1024, 1024),
            "16:9": (1344, 768),
            "9:16": (768, 1344),
            "3:2": (1216, 832),
            "2:3": (832, 1216),
        }
        width, height = ar_to_res.get(scene.aspect_ratio, (896, 1152))

        parameters = {
            "width": width,
            "height": height,
            "cfg_scale": 6.5,
            "steps": 35,
            "sampler": "DPM++ 2M Karras",
        }

        if is_restore and ref:
            parameters.update({
                "reference_mode": "restore_upscale",
                "denoising_strength": ref.denoise_strength,
                "fidelity_lock": f"{int(ref.fidelity_lock * 100)}%",
                "controlnet_tile_weight": 0.85,
                "controlnet_depth_weight": 0.65,
            })
        elif is_transform and ref:
            parameters.update({
                "reference_mode": "transform_adapt",
                "denoising_strength": ref.denoise_strength,
                "fidelity_lock": f"{int(ref.fidelity_lock * 100)}%",
                "ip_adapter_weight": 0.80,
                "controlnet_openpose_weight": 0.75,
            })

        metadata = {
            "camera_system": optics.camera_system,
            "lens": optics.lens,
            "aperture": optics.aperture_sweet_spot,
            "sensor": optics.sensor_dimensions,
        }
        if ref and ref.filename:
            metadata["reference_image"] = ref.filename

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            parameters=parameters,
            metadata=metadata,
        )

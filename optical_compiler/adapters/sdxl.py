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
        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_depixelate = ref and ref.mode == ReferenceMode.DEPIXELATE_GFX100RF

        # 1. Positive Prompt (Weighted camera and texture tokens)
        pos_chunks = []

        if is_outpaint:
            pos_chunks.append(
                "full body downward outpaint extension of reference photo head-to-toe with shoes, "
                "preserving exact facial identity, expression, wardrobe fabric, and wrinkles"
            )
        elif is_depixelate:
            pos_chunks.append(
                "universal de-pixelate and 102MP upscale restoration of reference photo, "
                "fixed Fujifilm GFX100RF 102MP rendering, Fujinon 35mm f/4 leaf shutter, Reala Ace color response, "
                "organic human skin realism overriding artificial clarity, strict text preservation"
            )
        elif is_restore:
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
        texture_tokens = [
            "organic human skin realism overriding perceived sharpness" if is_depixelate else "resolved epidermal skin pores",
            "fine vellus facial hair",
            "subsurface dermal scattering",
            "natural material micro-relief and micro-abrasions",
            "high MTF optical acutance",
            "natural large-sensor f/4 depth of field falloff" if is_depixelate else "natural large-sensor f/8 depth of field falloff",
            "rectilinear optical projection",
        ]
        if scene.sharpness_protocol:
            texture_tokens.extend([
                "focus locked on near eye",
                "iris and eyelashes tack sharp",
                "zero motion blur",
            ])
        if is_depixelate:
            res_tag = scene.output_resolution or "102MP Medium Format (11648 x 8736)"
        else:
            res_tag = scene.output_resolution or f"12MP PNG, vertical {scene.aspect_ratio}"
        texture_tokens.append(f"{res_tag}, uncompressed raw quality")
        pos_chunks.extend(texture_tokens)

        if scene.custom_positives:
            pos_chunks.extend(scene.custom_positives)

        positive_prompt = ", ".join(pos_chunks)

        # 2. Negative Prompt (Comprehensive artifact suppression)
        include_anti_drift = bool(is_restore or is_transform or is_outpaint or is_depixelate)
        all_negatives = shield.all_tokens(
            include_anti_drift=include_anti_drift,
            include_branding=scene.suppress_text_branding,
            include_compression=True,
            include_outpaint=is_outpaint,
            include_skin_realism=scene.human_skin_realism,
        )
        if scene.custom_negatives:
            all_negatives.extend(scene.custom_negatives)

        # Extra standard SDXL plastic artifact suppressors
        all_negatives.extend(
            [
                "over-sharpened",
                "unsharp mask halos",
                "doll skin",
                "porcelain skin",
                "filter glow",
                "bad anatomy",
            ]
        )

        # Deduplicate while preserving order
        negative_prompt = ", ".join(dict.fromkeys(all_negatives))

        # Resolution mapping based on aspect ratio
        ar_to_res = {
            "9:11": (896, 1088),
            "4:5": (896, 1152),
            "1:1": (1024, 1024),
            "16:9": (1344, 768),
            "9:16": (768, 1344),
            "3:2": (1216, 832),
            "2:3": (832, 1216),
            "4:3": (1152, 864),
            "3:4": (864, 1152),
            "5:4": (1152, 928),
        }
        width, height = ar_to_res.get(scene.aspect_ratio, (896, 1152))

        parameters = {
            "width": width,
            "height": height,
            "resolution": res_tag,
            "cfg_scale": 6.5,
            "steps": 35,
            "sampler": "DPM++ 2M Karras",
        }

        if is_outpaint:
            parameters.update({
                "reference_mode": "outpaint_full_body",
                "outpaint_direction": "downward",
                "controlnet_inpaint_weight": 0.90,
            })
        elif is_restore and ref:
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

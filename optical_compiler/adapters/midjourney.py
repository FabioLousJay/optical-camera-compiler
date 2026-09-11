"""Adapter for Midjourney v8.2 and raw parameter flag pipelines."""

from __future__ import annotations

from typing import Any

from ..models import (
    CameraProfile,
    CompiledPayload,
    ReferenceMode,
    SceneInput,
    TargetEngine,
)
from .base import BaseAdapter


class MidjourneyAdapter(BaseAdapter):
    """Compiles prompts with Midjourney v8.2 parameters and --style raw enforcement."""

    target_engine = TargetEngine.MIDJOURNEY

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        shield = profile.negative_embeddings
        ref = scene.reference

        is_restore = ref and ref.mode == ReferenceMode.RESTORE_UPSCALE
        is_transform = ref and ref.mode == ReferenceMode.TRANSFORM_ADAPT
        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY

        # 1. Subject description
        core_elements = []
        if is_outpaint:
            core_elements.append(
                "full body downward outpaint extension of reference photo head-to-toe with shoes, preserving facial identity and clothing"
            )
        elif is_restore:
            core_elements.append("optical remaster and high-resolution restoration of reference image")
        elif is_transform:
            core_elements.append("reference-guided photographic adaptation with biometric character lock")

        if scene.framing:
            core_elements.append(f"{scene.framing} of {scene.subject}")
        else:
            core_elements.append(scene.subject)

        if scene.environment:
            core_elements.append(f"in {scene.environment}")
        if scene.wardrobe:
            core_elements.append(f"wearing {scene.wardrobe}")
        if scene.mood:
            core_elements.append(scene.mood)

        prompt_parts = [", ".join(core_elements)]

        # 2. Camera, glass, and sensor specifications
        camera_tokens = [
            f"shot on {optics.camera_system}",
            f"{optics.lens} at {optics.aperture_sweet_spot}",
            f"{optics.sensor_dimensions}",
            f"{optics.shutter}",
            f"{optics.iso_base}",
        ]
        if scene.optical_filter:
            camera_tokens.append(scene.optical_filter)
        if scene.film_stock:
            camera_tokens.append(f"{scene.film_stock} color profile")
        else:
            camera_tokens.append("16-bit raw capture")
        prompt_parts.extend(camera_tokens)

        # 3. Studio lighting and physical texture
        lighting_tokens = [
            lighting.primary_lighting,
            "negative fill flags",
            "resolved epidermal skin pores",
            "fine vellus hair",
            "subsurface scattering",
            "natural material micro-relief",
        ]
        if scene.sharpness_protocol:
            lighting_tokens.extend([
                "focus locked on near eye",
                "eyelashes tack sharp",
                "iris crisp detail",
                "zero motion blur",
            ])
        prompt_parts.extend(lighting_tokens)

        if scene.custom_positives:
            prompt_parts.extend(scene.custom_positives)

        # 4. Midjourney flags
        flags = [
            f"--ar {scene.aspect_ratio}",
            "--style raw",
            "--v 8.2",
        ]

        if is_restore:
            flags.extend(["--iw 2.0", "--cw 100"])
        elif is_transform:
            flags.extend(["--cref [REFERENCE_IMAGE_URL]", "--cw 80", "--iw 1.5"])
        elif is_outpaint:
            flags.extend(["--cref [REFERENCE_IMAGE_URL]", "--cw 100"])

        # Negative items for --no flag
        banned_mj = [
            "plastic skin",
            "airbrushed",
            "glamour retouch",
            "CGI",
            "3D render",
            "illustration",
            "digital sharpening",
            "computational bokeh",
            "blown highlights",
        ]
        if scene.suppress_text_branding:
            banned_mj.extend([
                "text",
                "watermark",
                "logo",
                "brand name",
                "typography",
                "letters",
                "words",
                "signature",
                "label",
            ])
        if is_restore or is_transform or is_outpaint:
            banned_mj.extend([
                "facial morphing",
                "identity drift",
                "feature distortion",
                "warped face",
                "altered bone structure",
            ])
        if is_outpaint:
            banned_mj.extend([
                "mismatched shoes",
                "twisted legs",
                "floating feet",
                "deformed footwear",
                "wrong shadows",
            ])
        if scene.custom_negatives:
            banned_mj.extend(scene.custom_negatives)

        no_flag = f"--no {', '.join(dict.fromkeys(banned_mj))}"
        flags.append(no_flag)

        prefix = "[REFERENCE_IMAGE_URL] " if (is_restore or is_outpaint) else ""
        positive_base = prefix + ", ".join(prompt_parts)
        full_mj_prompt = f"{positive_base} {' '.join(flags)}"

        # Clean negative prompt representation
        negative_prompt = ", ".join(dict.fromkeys(banned_mj))

        parameters = {
            "aspect_ratio": scene.aspect_ratio,
            "style": "raw",
            "version": "8.2",
            "no": banned_mj,
        }
        if is_restore:
            parameters.update({
                "reference_mode": "restore_upscale",
                "image_weight": 2.0,
                "character_weight": 100,
            })
        elif is_transform:
            parameters.update({
                "reference_mode": "transform_adapt",
                "character_reference": "[REFERENCE_IMAGE_URL]",
                "character_weight": 80,
                "image_weight": 1.5,
            })

        metadata = {
            "camera_system": optics.camera_system,
            "lens": optics.lens,
            "aperture": optics.aperture_sweet_spot,
            "shutter_sync": optics.shutter,
            "sensor": optics.sensor_dimensions,
        }
        if ref and ref.filename:
            metadata["reference_image"] = ref.filename

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=full_mj_prompt,
            negative_prompt=negative_prompt,
            parameters=parameters,
            metadata=metadata,
        )

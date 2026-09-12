"""Adapter for Midjourney v8.2 and raw parameter flag pipelines."""

from __future__ import annotations

from typing import Any

from ..models import (
    AdSafeZone,
    CameraProfile,
    CompiledPayload,
    CopySpace,
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
        is_depixelate = ref and ref.mode == ReferenceMode.DEPIXELATE_GFX100RF
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock

        # 1. Subject description
        core_elements = []
        if is_outpaint:
            core_elements.append(
                "full body downward outpaint extension of reference photo head-to-toe with shoes, preserving facial identity and clothing"
            )
        elif is_product_lock:
            prod_tokens = ["commercial product packshot with 100% SKU lock to reference product crop"]
            if scene.cap_geometry:
                prod_tokens.append(f"exact {scene.cap_geometry}")
            if scene.sku_color:
                prod_tokens.append(f"SKU color {scene.sku_color}")
            if scene.material_finish:
                prod_tokens.append(f"{scene.material_finish}")
            if scene.seam_geometry:
                prod_tokens.append(f"{scene.seam_geometry}")
            if scene.label_kerning:
                prod_tokens.append(f"locked typography {scene.label_kerning}")
            core_elements.append(", ".join(prod_tokens))
        elif is_depixelate:
            core_elements.append(
                "Universal De-Pixelate and 102MP upscale restoration of reference photo, Fujinon 35mm f/4 leaf shutter, Reala Ace color response"
            )
        elif is_identity_lock:
            core_elements.append(
                "reference-locked identity portrait, exact facial structure, bone geometry, body mass, and proportions"
            )
        elif is_restore:
            core_elements.append("optical remaster and high-resolution restoration of reference image")
        elif is_transform:
            core_elements.append("reference-guided photographic adaptation with biometric character lock")

        if scene.camera_angle:
            core_elements.append(scene.camera_angle)
        if scene.crowd_action:
            core_elements.append(scene.crowd_action)
        if scene.is_monochrome:
            core_elements.append("restrained black-and-white indie-cinema monochrome, fine organic film grain")

        if scene.framing:
            core_elements.append(f"{scene.framing} of {scene.subject}")
        else:
            core_elements.append(scene.subject)

        if scene.has_hand_lock:
            grip_desc = scene.grip_type.value.replace("_", " ") if scene.grip_type else "ergonomic grip"
            details = f" {scene.hand_details}" if scene.hand_details else ""
            core_elements.append(
                f"biomechanical 5-point hand precision lock, 5-ray metacarpal architecture, authentic 5-finger anatomy, {grip_desc}{details}, "
                "distinct knuckles and joints, contact tissue blanching, translucent nail beds with lunula"
            )

        if scene.has_copy_space:
            if scene.copy_space and scene.copy_space != CopySpace.NONE:
                core_elements.append(f"commercial negative copy space in {scene.copy_space.value.replace('_', ' ')}")
            if scene.ad_safe_zone and scene.ad_safe_zone != AdSafeZone.NONE:
                core_elements.append(f"{scene.ad_safe_zone.value.replace('_', ' ')} advertising safe zone framing")

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
        if scene.is_anamorphic:
            squeeze = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
            flare = scene.streak_flare.value.replace("_", " ") if scene.streak_flare else "cyan/blue"
            blades = scene.iris_blades.value.replace("_", " ") if scene.iris_blades else "14-blade circular"
            camera_tokens.extend([
                f"cinema anamorphic lens {squeeze} squeeze",
                "vertical elliptical oval bokeh discs",
                f"{flare} horizontal streak flare",
                f"{blades} iris",
            ])
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
            "organic human skin realism overriding artificial clarity",
            "fine vellus hair",
            "subsurface scattering",
            "natural material micro-relief",
        ]
        if scene.lighting_ratio:
            lighting_tokens.append(f"{scene.lighting_ratio.value} lighting contrast ratio")
        if scene.gobo:
            gobo_desc = scene.gobo.value.replace("_", " ")
            lighting_tokens.append(f"optical {gobo_desc} gobo cookie projection shadows")
        if scene.grip_modifier:
            grip_desc = scene.grip_modifier.value.replace("_", " ")
            lighting_tokens.append(f"{grip_desc} studio grip modifier")

        is_slow_shutter = (
            scene.capture_mode == "slow_shutter_crowd_motion"
            or (hasattr(scene.capture_mode, "value") and scene.capture_mode.value == "slow_shutter_crowd_motion")
            or bool(scene.crowd_action)
            or (profile.profile_id == "leica_sl2" and "motion" in scene.subject.lower())
        )
        if is_slow_shutter:
            lighting_tokens.extend([
                "standing completely still subject, tack-sharp eyes, iris crisp detail",
                "surrounded by multi-directional motion blur crowd trails",
                "zero subject motion blur",
            ])
        elif scene.sharpness_protocol:
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
        effective_ar = "2.39:1" if (scene.is_anamorphic and scene.aspect_ratio in ("4:5", "2.39:1")) else scene.aspect_ratio
        flags = [
            f"--ar {effective_ar}",
            "--style raw",
            "--v 8.2",
        ]

        if is_depixelate or is_identity_lock or is_product_lock:
            ref_target = ref.filename if (ref and ref.filename) else (scene.product_crop or "[PRODUCT_CROP_URL]")
            flags.extend([f"--sref {ref_target}", "--iw 2.0", "--cw 100"])
        elif is_restore:
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
        if scene.human_skin_realism or is_depixelate:
            banned_mj.extend([
                "pore stamping",
                "engraved skin",
                "embossed skin",
                "carved skin",
                "swirl texture",
                "repeating micro-patterns",
                "lace-like facial texture",
                "worm-like texture",
                "AI skin grain",
                "hyper-sharpened pores",
                "overprocessed HDR skin",
                "synthetic cheek texture",
                "fake forehead texture",
                "fake neck texture",
                "decorative skin detail",
                "Velvia punch",
                "Classic Chrome grading",
                "Acros conversion",
                "fake shallow depth of field",
                "synthetic bokeh balls",
            ])
        if scene.suppress_text_branding and not is_product_lock:
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
        if is_restore or is_transform or is_outpaint or is_depixelate or is_identity_lock:
            banned_mj.extend([
                "facial morphing",
                "identity drift",
                "feature distortion",
                "warped face",
                "altered bone structure",
                "gender alteration",
                "body slimming",
                "facial reshaping",
            ])
        if is_product_lock:
            banned_mj.extend([
                "wrong cap",
                "distorted label",
                "incorrect kerning",
                "wrong sku color",
                "color drift",
                "missing mold seams",
                "plastic finish",
                "warped bottle",
                "distorted packaging",
            ])
        if scene.has_hand_lock:
            banned_mj.extend([
                "fused digits",
                "clipping fingers",
                "extra phalanges",
                "rubber knuckles",
                "dislocated thumb",
                "six fingers",
                "four fingers",
                "deformed fingernails",
                "webbed fingers",
                "missing knuckles",
                "amorphous fingertip pads",
            ])
        if scene.is_monochrome:
            banned_mj.extend(["color", "sepia", "warm tint"])
        if is_slow_shutter:
            banned_mj.extend(["ghost faces", "melted bodies", "duplicated people", "uniform smear wall", "blur on subject"])
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

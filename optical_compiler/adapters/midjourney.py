"""Adapter for Midjourney v8.2 and raw parameter flag pipelines."""

from __future__ import annotations

from typing import Any

from ..models import (
    AdSafeZone,
    BackgroundStyle,
    CameraProfile,
    CompiledPayload,
    CopySpace,
    MaterialStyle,
    PaperProfile,
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
        is_depixelate_v2 = bool((ref and ref.mode == ReferenceMode.DEPIXELATE_V2) or scene.has_depixelate_v2)
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_recon_4x = bool((ref and ref.mode == ReferenceMode.RECONSTRUCTION_LOCK_4X) or scene.has_reconstruction_lock_4x)
        is_png_lock = bool((ref and ref.mode == ReferenceMode.UNIVERSAL_PNG_LOCK) or scene.has_png_lock)

        # 1. Subject description and mandatory gaze anchor
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
        elif is_depixelate_v2:
            spec = scene.depixelate_v2
            ctype = spec.content_type if spec else "photograph"
            cam_str = (spec.selected_camera if (spec and spec.selected_camera) else optics.camera_system).split("(")[0].strip()
            lens_str = (spec.selected_lens if (spec and spec.selected_lens) else optics.lens).split("(")[0].strip()
            core_elements.append(
                f"Universal De-Pixelate v2.0 restoration, content type {ctype}, single source of truth, "
                f"strict OCR text and geometry lock, evidence-anchored detail reconstruction, shot on {cam_str} {lens_str}"
            )
        elif is_depixelate:
            core_elements.append(
                "Universal De-Pixelate and 102MP upscale restoration of reference photo, Fujinon 35mm f/4 leaf shutter, Reala Ace color response"
            )
        elif is_recon_4x:
            recon = scene.reconstruction_lock
            b_val = recon.backend.value if recon else "realesrnet_x4plus"
            core_elements.append(
                f"Professional 4X Reconstruction Lock, 4X linear expansion 16X area, {b_val} backend, protected sky haze gradients, source-locked geometry, zero hallucination"
            )
        elif is_png_lock:
            png_s = scene.png_lock
            mb_v = png_s.target_min_mb if png_s else 12.0
            core_elements.append(
                f"Universal High-Resolution PNG Output Lock v1.0, true full-color RGB PNG, zero forced palette reduction, "
                f"zero indexed color, high acutance, crisp micro-detail, clear edge separation, ~{mb_v:.0f}MB target, mandatory 4X Lanczos upscale workflow"
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

        # Mandatory Subject Gaze & Orientation Anchor:
        # Prevents subjects from turning their backs or looking away from the camera
        is_portrait = any(k in f"{scene.framing} {scene.subject}".lower() for k in (
            "portrait", "headshot", "close-up", "male", "female", "man", "woman", "person",
            "model", "dancer", "worker", "craftsman", "people", "two", "face", "beauty", "editorial"
        )) and not is_product_lock and not is_recon_4x and not is_depixelate_v2

        has_explicit_rear_angle = any(k in (scene.camera_angle or "").lower() for k in ("behind", "rear", "from back", "back view"))
        if is_portrait and not has_explicit_rear_angle:
            core_elements.append("facing camera, direct eye contact, natural dignified expression and posture")

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

        if scene.is_policy_safe:
            core_elements.append("dignified tasteful portrait, safe ethical fine-art styling")

        if scene.has_body_morphology:
            wt = f" {scene.weight_lb}lbs" if scene.weight_lb else ""
            core_elements.append(
                f"realistic heavyset plus-size body build{wt}, authentic natural weight distribution, natural posture"
            )

        if scene.has_material_style:
            mat_desc = scene.material_style.value.replace("_", " ") if scene.material_style and scene.material_style != MaterialStyle.NONE else "dimensional volumetric finish"
            core_elements.append(f"4D volumetric depth, {mat_desc}, contour rim lighting, controlled specular highlights, deep tonal separation")
            if scene.background_style and scene.background_style != BackgroundStyle.DEFAULT:
                core_elements.append(f"{scene.background_style.value.replace('_', ' ')} background")

        if scene.is_print_calibrated:
            paper_name = scene.paper_profile.value.replace("_", " ") if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value.replace("_", " ") if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else "exhibition fine art paper")
            core_elements.append(f"print-calibrated exhibition prepress {paper_name}")

        if scene.environment:
            core_elements.append(f"in {scene.environment}")
        if scene.wardrobe:
            core_elements.append(f"wearing {scene.wardrobe}")
        if scene.mood:
            core_elements.append(scene.mood)

        prompt_parts = [", ".join(core_elements)]

        # 2. Camera, glass, and optical visual consequences (no catalog serial numbers)
        clean_camera = optics.camera_system.split("(")[0].strip()
        clean_lens = (scene.lens or optics.lens).split("(")[0].strip()
        aperture_val = scene.aperture or optics.aperture_sweet_spot

        camera_tokens = [
            f"shot on {clean_camera}",
            f"{clean_lens} at {aperture_val}",
        ]
        if optics.sensor_dimensions:
            camera_tokens.append(optics.sensor_dimensions)

        # Translate aperture number into concrete optical depth consequence
        f_num = 5.6
        try:
            if "f/" in aperture_val:
                f_num = float(aperture_val.replace("f/", "").split()[0])
            elif "T" in aperture_val:
                f_num = float(aperture_val.replace("T", "").split()[0])
        except Exception:
            f_num = 5.6

        if f_num <= 2.8:
            camera_tokens.append("shallow optical depth of field with creamy background blur")
        else:
            camera_tokens.append("sharp edge-to-edge optical sweet-spot depth of field")

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

        # Concrete film stock and sensor color science visual consequences
        if scene.film_stock:
            camera_tokens.append(f"{scene.film_stock} color profile")
        elif "kodachrome" in optics.camera_system.lower() or "fm2" in optics.camera_system.lower():
            camera_tokens.append("Kodachrome 64 color saturation, rich warm slide film tones")
        elif "fuji pro 400h" in optics.camera_system.lower() or "contax 645" in optics.camera_system.lower():
            camera_tokens.append("Fujifilm Pro 400H luminous pastel skin tones, airy soft highlights")
        elif "portra" in optics.camera_system.lower() or "rz67" in optics.camera_system.lower():
            camera_tokens.append("Kodak Portra 800 warm golden skin tones, fine analog grain")
        elif "monochrom" in optics.camera_system.lower() or "q3" in optics.camera_system.lower() or scene.is_monochrome:
            camera_tokens.append("pure panchromatic black-and-white luminance, deep blacks and luminous midtones")
        elif "imax" in optics.camera_system.lower():
            camera_tokens.append("monumental 65mm motion picture scale, organic film grain, rich silver tonal depth")
        elif "polaroid" in optics.camera_system.lower():
            camera_tokens.append("life-size 1:1 contact portrait scale, rich instant dye transfer tonality")
        elif "contax t2" in optics.camera_system.lower():
            camera_tokens.append("direct on-camera xenon flash with rapid falloff, high-glamour snapshot intimacy")
        elif "phase one" in optics.camera_system.lower() or "hasselblad" in optics.camera_system.lower() or "gfx" in optics.camera_system.lower():
            camera_tokens.append("16-bit medium-format raw dynamic range, smooth highlight roll-off")
        else:
            camera_tokens.append("16-bit raw capture, natural color science")

        prompt_parts.extend(camera_tokens)

        # 3. Studio lighting and physical texture
        lighting_tokens = []
        if "xenon flash" in (lighting.primary_lighting or "").lower() or "t2" in optics.camera_system.lower():
            lighting_tokens.append("harsh direct on-camera flash casting crisp defined shadows")
        elif scene.lighting:
            lighting_tokens.append(scene.lighting)
        else:
            lighting_tokens.append(lighting.primary_lighting)

        lighting_tokens.extend([
            "negative fill flags",
            "natural skin texture with visible micro-pores",
            "subtle subsurface dermal scattering",
            "fine vellus hair",
            "natural material micro-relief",
        ])

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

        if scene.has_stress_probe and scene.stress_probe:
            prompt_parts.append(scene.stress_probe.directive_text)
        if scene.has_lighting_environment and scene.lighting_environment:
            le = scene.lighting_environment
            prompt_parts.append(f"gallery exhibition lighting {le.illuminance_lux} lux {le.cct_kelvin}K CRI {le.spectral_cri}")
        if scene.has_series_cohesion and scene.series_cohesion:
            sc = scene.series_cohesion
            prompt_parts.append(f"series cohesion anchor {sc.anchor_image_id or 'master'} zone {sc.gallery_zone or 'gallery'}")

        # 4. Midjourney flags
        effective_ar = "2.39:1" if (scene.is_anamorphic and scene.aspect_ratio in ("4:5", "2.39:1")) else scene.aspect_ratio
        flags = [
            f"--ar {effective_ar}",
            "--style raw",
            "--v 8.2",
        ]

        if is_recon_4x:
            ref_target = ref.filename if (ref and ref.filename) else "[SOURCE_IMAGE_URL]"
            flags.extend([f"--sref {ref_target}", "--iw 2.0", "--cw 100"])
        elif is_depixelate_v2:
            ref_target = ref.filename if (ref and ref.filename) else "[REFERENCE_IMAGE_URL]"
            flags.extend([f"--sref {ref_target}", "--iw 2.0", "--cw 100"])
        elif is_depixelate or is_identity_lock or is_product_lock:
            ref_target = ref.filename if (ref and ref.filename) else (scene.product_crop or "[PRODUCT_CROP_URL]")
            flags.extend([f"--sref {ref_target}", "--iw 2.0", "--cw 100"])
        elif is_restore:
            flags.extend(["--iw 2.0", "--cw 100"])
        elif is_transform:
            flags.extend(["--cref [REFERENCE_IMAGE_URL]", "--cw 80", "--iw 1.5"])
        elif is_outpaint:
            flags.extend(["--cref [REFERENCE_IMAGE_URL]", "--cw 100"])

        # 5. Non-Toxic Surgical Negative Prompt Defense for Midjourney
        # Strictly universal synthetic render flaws. NEVER include anatomy, face, forehead, neck, or cheek nouns.
        banned_mj = [
            "plastic skin",
            "airbrushed",
            "oversmoothed",
            "CGI",
            "3D render",
            "illustration",
            "cartoon",
            "drawing",
            "painting",
            "anime",
            "blurry",
            "digital sharpening halos",
        ]

        if is_recon_4x:
            banned_mj.extend([
                "generative hallucination",
                "invented geology",
                "altered terrain",
                "rock strata distortion",
                "sky grain",
                "sky halos",
                "stacking artifacts",
            ])

        if scene.human_skin_realism or is_depixelate:
            banned_mj.extend([
                "pore stamping",
                "engraved skin",
                "embossed skin",
                "carved skin",
                "repeating micro-patterns",
                "AI skin grain",
                "hyper-sharpened pores",
                "overprocessed HDR skin",
                "decorative skin detail",
                "Velvia punch",
                "Classic Chrome grading",
                "Acros conversion",
            ])

        if scene.suppress_text_branding and not is_product_lock:
            banned_mj.extend([
                "watermark",
                "logo",
                "brand name",
                "typography",
                "text",
                "signature",
                "label",
            ])

        if is_depixelate_v2:
            banned_mj.extend([
                "restyling",
                "rewriting",
                "hallucination",
                "invented text",
                "invented logos",
                "AI gloss",
                "plastic sheen",
                "over-smoothing",
                "smearing",
                "halos",
                "color shift",
                "composition alteration",
                "decorative filtering",
            ])

        if is_restore or is_transform or is_outpaint or is_depixelate or is_depixelate_v2 or is_identity_lock:
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
                "extra fingers",
                "fused digits",
                "six fingers",
                "four fingers",
                "deformed hands",
            ])

        if scene.is_policy_safe:
            banned_mj.extend(["revealing", "provocative", "inappropriate"])

        if scene.is_monochrome:
            banned_mj.extend(["color", "sepia", "warm tint"])

        if is_slow_shutter:
            banned_mj.extend([
                "ghost faces",
                "melted bodies",
                "duplicated people",
                "uniform smear wall",
                "blur on subject",
            ])

        if is_outpaint:
            banned_mj.extend([
                "mismatched shoes",
                "twisted legs",
                "floating feet",
                "deformed footwear",
                "wrong shadows",
            ])

        if scene.has_body_morphology:
            banned_mj.extend([
                "extreme bodybuilding",
                "comic book muscles",
                "balloon muscles",
                "impossible muscle insertions",
                "hyper-vascularity",
            ])

        if scene.remove_text_when_present:
            banned_mj.extend(["text", "typography", "letters", "writing", "words", "captions"])

        if is_png_lock:
            banned_mj.extend([
                "forced palette reduction",
                "indexed-color PNG",
                "palette quantization",
                "color simplification",
                "mushy surfaces",
                "watercolor-like smearing",
                "fake oversharpening halos",
                "muddy gradients",
                "posterization",
                "lossy PNG compression",
                "flattened textures",
                "compression damage",
            ])

        if scene.custom_negatives:
            banned_mj.extend(scene.custom_negatives)

        no_flag = f"--no {', '.join(dict.fromkeys(banned_mj))}"
        flags.append(no_flag)

        prefix = "[REFERENCE_IMAGE_URL] " if (is_restore or is_outpaint or is_depixelate_v2) else ""
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
        if is_png_lock:
            parameters.update({
                "png_output_lock": True,
                "color_mode": "RGB",
                "compress_level": 0,
                "linear_scale": 4,
            })
        if is_depixelate_v2:
            spec = scene.depixelate_v2
            ref_target = ref.filename if (ref and ref.filename) else "[REFERENCE_IMAGE_URL]"
            parameters.update({
                "reference_mode": "depixelate_v2",
                "sref": ref_target,
                "iw": 2.0,
                "cw": 100,
                "content_type": spec.content_type if spec else "photograph",
            })
        elif is_restore:
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

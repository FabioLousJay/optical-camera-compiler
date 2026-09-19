from __future__ import annotations

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
        is_depixelate_v2 = bool((ref and ref.mode == ReferenceMode.DEPIXELATE_V2) or scene.has_depixelate_v2)
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_recon_4x = bool((ref and ref.mode == ReferenceMode.RECONSTRUCTION_LOCK_4X) or scene.has_reconstruction_lock_4x)
        is_png_lock = bool((ref and ref.mode == ReferenceMode.UNIVERSAL_PNG_LOCK) or scene.has_png_lock)

        # 1. Positive Prompt (Weighted camera and texture tokens)
        pos_chunks = []

        if is_outpaint:
            pos_chunks.append(
                "full body downward outpaint extension of reference photo head-to-toe with shoes, "
                "preserving exact facial identity, expression, wardrobe fabric, and wrinkles"
            )
        elif is_product_lock:
            pos_chunks.append(
                "commercial product packshot, 100% SKU lock to reference product crop, "
                "exact container geometry, locked label typography and kerning, authentic material finish"
            )
            if scene.cap_geometry:
                pos_chunks.append(f"exact cap geometry ({scene.cap_geometry})")
            if scene.sku_color:
                pos_chunks.append(f"exact SKU color ({scene.sku_color})")
            if scene.seam_geometry:
                pos_chunks.append(f"manufacturing seams ({scene.seam_geometry})")
            if scene.material_finish:
                pos_chunks.append(f"material finish ({scene.material_finish})")
            if scene.label_kerning:
                pos_chunks.append(f"label kerning ({scene.label_kerning})")
        elif is_identity_lock:
            pos_chunks.append(
                "strict identity-locked reference portrait, exact anatomical presence, "
                "biometric facial geometry, mass, body proportions, hair, and beard pattern preserved without alteration"
            )
        elif is_depixelate_v2:
            spec = scene.depixelate_v2
            ctype = spec.content_type if spec else "photograph"
            cam_str = spec.selected_camera if (spec and spec.selected_camera) else optics.camera_system
            lens_str = spec.selected_lens if (spec and spec.selected_lens) else optics.lens
            pos_chunks.append(
                f"universal de-pixelate and upscale restoration v2.0 ({ctype}), "
                f"absolute source of truth lock to reference image, shot on {cam_str} with {lens_str}, "
                f"exact text and OCR preservation, evidence-anchored detail reconstruction, zero hallucination"
            )
        elif is_depixelate:
            pos_chunks.append(
                "universal de-pixelate and 102MP upscale restoration of reference photo, "
                "fixed Fujifilm GFX100RF 102MP rendering, Fujinon 35mm f/4 leaf shutter, Reala Ace color response, "
                "organic human skin realism overriding artificial clarity, strict text preservation"
            )
        elif is_recon_4x:
            recon = scene.reconstruction_lock
            b_val = recon.backend.value if recon else "realesrnet_x4plus"
            dn_val = recon.denoise_strength if recon else 0.15
            bl_val = recon.blend_ratio if recon else 0.20
            pos_chunks.append(
                f"Professional 4X Reconstruction Lock, exact 4X linear raster expansion, 16X pixel area, "
                f"{b_val} backend, denoise {dn_val}, selective detail blend {bl_val}, "
                "sky and atmospheric haze gradient protection, zero generative hallucination, unaltered geology"
            )
        elif is_png_lock:
            png_s = scene.png_lock
            mb_v = png_s.target_min_mb if png_s else 12.0
            pos_chunks.append(
                f"Universal High-Resolution PNG Output Lock v1.0, true full-color RGB PNG, zero forced palette reduction, "
                f"zero indexed color, crisp micro-detail, clear edge separation, ~{mb_v:.0f}MB target, mandatory 4X Lanczos pixel upscale workflow"
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
        if scene.camera_angle:
            scene_str += f", {scene.camera_angle}"
        if scene.crowd_action:
            scene_str += f", {scene.crowd_action}"
        if scene.is_monochrome:
            scene_str += ", restrained black-and-white indie-cinema monochrome, fine organic film grain"
        pos_chunks.append(scene_str)

        is_portrait = any(k in f"{scene.framing} {scene.subject}".lower() for k in (
            "portrait", "headshot", "close-up", "male", "female", "man", "woman", "person",
            "model", "dancer", "worker", "craftsman", "people", "two", "face", "beauty", "editorial"
        )) and not is_product_lock and not is_recon_4x and not is_depixelate_v2
        has_explicit_rear = any(k in (scene.camera_angle or "").lower() for k in ("behind", "rear", "from back", "back view"))
        if is_portrait and not has_explicit_rear:
            pos_chunks.append("facing camera, direct eye contact, natural dignified expression and posture")

        if scene.has_copy_space:
            if scene.copy_space and scene.copy_space != CopySpace.NONE:
                pos_chunks.append(f"asymmetric commercial copy space in {scene.copy_space.value.replace('_', ' ')}")
            if scene.ad_safe_zone and scene.ad_safe_zone != AdSafeZone.NONE:
                pos_chunks.append(f"{scene.ad_safe_zone.value.replace('_', ' ')} advertising safe zone framing")

        if scene.has_hand_lock:
            grip_desc = scene.grip_type.value.replace("_", " ") if scene.grip_type else "contact grip"
            details = f" ({scene.hand_details})" if scene.hand_details else ""
            pos_chunks.append(
                f"biomechanical 5-point hand precision lock ({grip_desc}{details}), 5-ray metacarpal architecture, authentic 5-finger anatomy, "
                "distinct knuckles and PIP joints, contact blanching, translucent nail beds, lunula crescents"
            )

        if scene.is_policy_safe:
            pos_chunks.append("dignified tasteful portrait, safe ethical fine-art photography, fully clothed subject")

        if scene.has_body_morphology:
            regions = scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else "biceps, chest, gut")
            wt = f" {scene.weight_lb}lbs" if scene.weight_lb else ""
            pos_chunks.append(
                f"proportional {regions} volume calibration{wt}, natural bilateral asymmetry, realistic soft-tissue gravity and seated compression, authentic weight distribution"
            )

        if scene.has_material_style:
            mat_desc = scene.material_style.value.replace("_", " ") if scene.material_style and scene.material_style != MaterialStyle.NONE else "dimensional volumetric finish"
            pos_chunks.append(f"4D volumetric depth, {mat_desc}, contour rim lighting, controlled specular highlights, deep tonal separation")
            if scene.background_style and scene.background_style != BackgroundStyle.DEFAULT:
                pos_chunks.append(f"{scene.background_style.value.replace('_', ' ')} background")

        if scene.is_print_calibrated:
            paper_name = scene.paper_profile.value.replace("_", " ") if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value.replace("_", " ") if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else "exhibition fine art paper")
            pos_chunks.append(f"print-calibrated exhibition prepress {paper_name}")

        # Hardware & Optics
        clean_camera = optics.camera_system.split("(")[0].strip()
        clean_lens = (scene.lens or optics.lens).split("(")[0].strip()
        aperture_val = scene.aperture or optics.aperture_sweet_spot

        f_num = 5.6
        try:
            if "f/" in aperture_val:
                f_num = float(aperture_val.replace("f/", "").split()[0])
            elif "T" in aperture_val:
                f_num = float(aperture_val.replace("T", "").split()[0])
        except Exception:
            f_num = 5.6

        if f_num <= 2.8:
            dof_token = "shallow optical depth of field with creamy background blur"
        else:
            dof_token = "sharp edge-to-edge optical sweet-spot depth of field"

        hardware_tokens = [
            f"raw photograph captured on {clean_camera}",
            f"{clean_lens} at {aperture_val}",
            dof_token,
            optics.sensor_dimensions,
            optics.shutter,
            optics.iso_base,
            optics.dynamic_range,
        ]
        if scene.is_anamorphic:
            squeeze = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
            flare = scene.streak_flare.value.replace("_", " ") if scene.streak_flare else "cyan/blue"
            blades = scene.iris_blades.value.replace("_", " ") if scene.iris_blades else "14-blade circular"
            hardware_tokens.extend([
                f"cinema anamorphic lens {squeeze} squeeze",
                "vertical 2:1 elliptical oval bokeh discs",
                f"{flare} horizontal streak flare",
                f"{blades} iris",
            ])
        if scene.optical_filter:
            hardware_tokens.append(scene.optical_filter)
        if scene.film_stock:
            hardware_tokens.append(f"{scene.film_stock} emulsion")
        pos_chunks.extend(hardware_tokens)

        # Lighting setup
        lighting_chunks = [
            lighting.primary_lighting,
            lighting.light_transport,
        ]
        if scene.lighting_ratio:
            lighting_chunks.append(f"{scene.lighting_ratio.value} lighting contrast ratio")
        if scene.gobo:
            gobo_desc = scene.gobo.value.replace("_", " ")
            lighting_chunks.append(f"optical {gobo_desc} gobo cookie projection")
        if scene.grip_modifier:
            grip_desc = scene.grip_modifier.value.replace("_", " ")
            lighting_chunks.append(f"{grip_desc} studio grip")
        pos_chunks.extend(lighting_chunks)

        # Micro-texture & physical optical falloff
        if is_product_lock:
            texture_tokens = [
                "critical focus on primary brand label and shoulder seam",
                "authentic product material reflectance",
                "uncompressed specular highlights",
                "high MTF optical acutance",
                "rectilinear optical projection",
            ]
        else:
            texture_tokens = [
                "organic human skin realism overriding perceived sharpness" if is_depixelate else "resolved epidermal skin pores",
                "fine vellus facial hair",
                "subsurface dermal scattering",
                "natural material micro-relief and micro-abrasions",
                "high MTF optical acutance",
                "natural large-sensor f/4 depth of field falloff" if is_depixelate else "natural large-sensor f/8 depth of field falloff",
                "rectilinear optical projection",
            ]
        is_slow_shutter = (
            scene.capture_mode == "slow_shutter_crowd_motion"
            or (hasattr(scene.capture_mode, "value") and scene.capture_mode.value == "slow_shutter_crowd_motion")
            or bool(scene.crowd_action)
            or (profile.profile_id == "leica_sl2" and "motion" in scene.subject.lower())
        )
        if is_slow_shutter:
            texture_tokens.extend([
                "focus locked on near eye",
                "iris and eyelashes tack sharp",
                "subject completely stationary with zero subject motion blur",
                "surrounding crowd motion blur trails",
            ])
        elif scene.sharpness_protocol and not is_product_lock:
            texture_tokens.extend([
                "focus locked on near eye",
                "iris and eyelashes tack sharp",
                "zero motion blur",
            ])
        if is_depixelate_v2:
            spec = scene.depixelate_v2
            res_tag = scene.output_resolution or (spec.target_resolution if spec else "60MP Ultra-High Resolution Capture")
        elif is_depixelate:
            res_tag = scene.output_resolution or "102MP Medium Format (11648 x 8736)"
        elif is_recon_4x:
            res_tag = scene.output_resolution or "Exact 4X Linear Source-Locked Reconstruction (16X pixel area)"
        else:
            res_tag = scene.output_resolution or f"12MP PNG, vertical {scene.aspect_ratio}"
        texture_tokens.append(f"{res_tag}, uncompressed raw quality")
        pos_chunks.extend(texture_tokens)

        if scene.custom_positives:
            pos_chunks.extend(scene.custom_positives)

        if scene.has_stress_probe and scene.stress_probe:
            pos_chunks.append(scene.stress_probe.directive_text)
        if scene.has_lighting_environment and scene.lighting_environment:
            le = scene.lighting_environment
            pos_chunks.append(f"gallery lighting {le.illuminance_lux} lux, {le.cct_kelvin}K CCT, CRI {le.spectral_cri}")
        if scene.has_series_cohesion and scene.series_cohesion:
            sc = scene.series_cohesion
            pos_chunks.append(f"series cohesion anchor {sc.anchor_image_id or 'master'}")

        positive_prompt = ", ".join(pos_chunks)


        # 2. Negative Prompt (Comprehensive artifact suppression)
        include_anti_drift = bool(is_restore or is_transform or is_outpaint or is_depixelate or is_depixelate_v2 or is_identity_lock or is_product_lock or is_recon_4x or is_png_lock)
        all_negatives = shield.all_tokens(
            include_anti_drift=include_anti_drift,
            include_branding=scene.suppress_text_branding and not is_product_lock,
            include_compression=True,
            include_outpaint=is_outpaint,
            include_skin_realism=scene.human_skin_realism,
            include_product_drift=is_product_lock,
            include_hand_drift=scene.has_hand_lock,
            include_body_distortion=scene.has_body_morphology,
            include_reconstruction_drift=is_recon_4x,
            include_png_lock=is_png_lock,
            include_depixelate_v2=is_depixelate_v2,
        )
        if scene.custom_negatives:
            all_negatives.extend(scene.custom_negatives)

        if is_depixelate_v2:
            all_negatives.extend([
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
            ])

        if scene.has_body_morphology:
            all_negatives.extend([
                "extreme bodybuilding", "comic book muscles", "balloon muscles", "impossible muscle insertions",
                "hyper-vascularity", "body distortion", "grotesque proportions",
            ])
        if scene.remove_text_when_present:
            all_negatives.extend(["text", "typography", "letters", "writing", "words", "captions"])
        if scene.is_policy_safe:
            all_negatives.extend(["provocative", "inappropriate", "revealing", "nudity", "nsfw"])

        if is_png_lock:
            all_negatives.extend([
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

        if scene.has_hand_lock:
            all_negatives.extend(
                [
                    "fused fingers",
                    "extra digits",
                    "missing knuckles",
                    "rubber knuckles",
                    "clipping fingers",
                    "deformed nails",
                ]
            )

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
            "5:5": (1024, 1024),
            "9:12": (864, 1152),
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

        if is_png_lock:
            parameters.update({
                "png_output_lock": True,
                "color_mode": "RGB",
                "compress_level": 0,
                "linear_scale": 4,
            })
        if is_depixelate_v2:
            spec = scene.depixelate_v2
            parameters.update({
                "reference_mode": "depixelate_v2",
                "content_type": spec.content_type if spec else "photograph",
                "ocr_safety": spec.ocr_safety_mode if spec else "strict_preserve",
                "confidence_mode": spec.confidence_mode if spec else "evidence_anchored",
                "controlnet_tile_weight": 0.85,
            })
        elif is_outpaint:
            parameters.update({
                "reference_mode": "outpaint_full_body",
                "outpaint_direction": "downward",
                "controlnet_inpaint_weight": 0.90,
            })
        elif is_recon_4x:
            recon = scene.reconstruction_lock
            parameters.update({
                "reference_mode": "reconstruction_lock_4x",
                "linear_scale": 4,
                "backend": recon.backend.value if recon else "realesrnet_x4plus",
                "denoise_strength": recon.denoise_strength if recon else 0.15,
                "blend_ratio": recon.blend_ratio if recon else 0.20,
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

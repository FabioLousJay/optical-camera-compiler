"""Adapter for Google Imagen 3 and Gemini multimodal generation."""

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


class ImagenAdapter(BaseAdapter):
    """Compiles prompts into cohesive photographic prose optimized for Imagen 3."""

    target_engine = TargetEngine.IMAGEN

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
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock
        is_recon_4x = bool((ref and ref.mode == ReferenceMode.RECONSTRUCTION_LOCK_4X) or scene.has_reconstruction_lock_4x)
        is_png_lock = bool((ref and ref.mode == ReferenceMode.UNIVERSAL_PNG_LOCK) or scene.has_png_lock)

        # 1. Subject & Scene foundation
        scene_elements = []
        if scene.is_policy_safe:
            scene_elements.append(
                "Policy-Safe Compliance Directive: Dignified, tasteful editorial photographic execution adhering to platform ethical guidelines with fully clothed subjects and authentic camera physics"
            )
        if is_outpaint:
            scene_elements.append(
                "Using the provided medium-shot photo as the base. Outpaint and extend the frame downward to a full-body portrait. "
                "Preserve the subject's face, identity, expression, hair, and skin texture exactly as in the input image. "
                "Keep the same wardrobe, colors, fabric texture, and wrinkles. Maintain the same camera height and perspective. "
                f"No wide-angle distortion. Full body head-to-toe visible including shoes. Depicting {scene.subject}"
            )
        elif is_product_lock:
            scene_elements.append(
                f"Commercial studio packshot of {scene.subject} with 100% SKU fidelity lock to reference product crop"
            )
            if scene.cap_geometry:
                scene_elements.append(f"featuring exact {scene.cap_geometry}")
            if scene.material_finish:
                scene_elements.append(f"rendered in {scene.material_finish}")
            if scene.sku_color:
                scene_elements.append(f"with exact commercial SKU color {scene.sku_color}")
            if scene.seam_geometry:
                scene_elements.append(f"with {scene.seam_geometry}")
            if scene.label_kerning:
                scene_elements.append(f"label typography and kerning locked to {scene.label_kerning}")
        elif is_identity_lock:
            scene_elements.append(
                "Documentary editorial portrait with strict reference identity lock, preserving exact facial architecture, bone geometry, mass, body proportions, hair, and beard pattern without alteration"
            )
            if scene.camera_angle:
                scene_elements.append(f"captured from a {scene.camera_angle}")
            if scene.framing:
                scene_elements.append(f"in a {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"focusing on {scene.subject}")
        elif is_depixelate:
            scene_elements.append(
                "Universal De-Pixelate and Upscale Restoration of the attached reference image rendered with a fixed Fujifilm GFX100RF 102MP signature. "
                "Eliminating pixelation, blockiness, compression damage, aliasing, mosquito noise, and low-resolution softness "
                "while strictly preserving identity, composition, proportions, materials, lighting logic, and text content"
            )
            if scene.framing:
                scene_elements.append(f"rendered as a {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"focusing faithfully on {scene.subject}")
        elif is_recon_4x:
            recon = scene.reconstruction_lock
            b_val = recon.backend.value if recon else "realesrnet_x4plus"
            dn_val = recon.denoise_strength if recon else 0.15
            bl_val = recon.blend_ratio if recon else 0.20
            scene_elements.append(
                f"Professional 4X Reconstruction Lock of the attached reference image rendered with strict linear raster scaling (4X linear, 16X pixel area). "
                f"Absolute source lock: zero generative hallucination, rock strata distortion, or terrain drift. "
                f"Reconstructed via {b_val} with denoise {dn_val} and selective high-frequency blend {bl_val}, protected smooth sky and haze gradients"
            )
            if scene.framing:
                scene_elements.append(f"rendered as a {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"preserving source framing of {scene.subject}")
        elif is_png_lock:
            png_s = scene.png_lock
            min_mb_v = png_s.target_min_mb if png_s else 12.0
            scene_elements.append(
                "Universal High-Resolution PNG Output Lock v1.0 of the scene rendered at maximum visual fidelity with true full-color RGB output. "
                "Zero forced palette reduction, zero indexed-color quantization, high acutance, crisp micro-detail, and clear edge separation. "
                f"Exported as uncompressed PNG raster (~{min_mb_v:.0f} MB target) via mandatory 4× full-color RGB Lanczos upscale post-process"
            )
            if scene.framing:
                scene_elements.append(f"rendered as a {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"focusing faithfully on {scene.subject}")
        elif is_restore:
            scene_elements.append(f"Master optical remaster and high-resolution restoration of the reference photograph")
            if scene.framing:
                scene_elements.append(f"rendered as a {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"focusing on {scene.subject}")
        elif is_transform:
            scene_elements.append(
                f"Reference-guided photographic transformation preserving the biometric facial identity and proportions of the subject"
            )
            if scene.framing:
                scene_elements.append(f"in a {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"depicting {scene.subject}")
        else:
            if scene.framing:
                scene_elements.append(f"A {scene.framing} of {scene.subject}")
            else:
                scene_elements.append(f"Photograph of {scene.subject}")

        if scene.environment:
            scene_elements.append(f"situated in {scene.environment}")

        if scene.wardrobe:
            scene_elements.append(f"wearing {scene.wardrobe}")

        if scene.mood:
            scene_elements.append(f"evoking {scene.mood}")

        if scene.crowd_action:
            scene_elements.append(f"surrounded by {scene.crowd_action}")

        if scene.is_monochrome:
            scene_elements.append("restrained black-and-white indie-cinema monochrome with gentle highlight roll-off and clean midtones without HDR")

        if scene.has_copy_space:
            if scene.copy_space and scene.copy_space != CopySpace.NONE:
                scene_elements.append(
                    f"commercial advertising composition reserving clean, uncluttered negative copy-space in the {scene.copy_space.value.replace('_', ' ')} for typography"
                )
            if scene.ad_safe_zone and scene.ad_safe_zone != AdSafeZone.NONE:
                scene_elements.append(
                    f"framed strictly within {scene.ad_safe_zone.value.replace('_', ' ')} digital advertising safe-zones to avoid mobile interface occlusion"
                )

        scene_core = ", ".join(scene_elements) + "."

        # Reference-specific anchor instructions
        ref_directives = []
        if scene.has_hand_lock:
            grip_desc = scene.grip_type.value.replace("_", " ") if scene.grip_type else "ergonomic contact grip"
            details = f" ({scene.hand_details})" if scene.hand_details else ""
            ref_directives.append(
                f"Biomechanical 5-Point Hand Precision Gate ({grip_desc}{details}): "
                "Render fully articulated human hands with correct 5-digit metacarpal proportions (2:3:4:3.5:2.5 ratio), "
                "distinct MCP/PIP/DIP joints, palmar flexion creases, authentic tissue blanching under pressure, "
                "translucent nail beds with lunula crescents, natural cuticles, and absolute zero finger mutations."
            )
        if is_depixelate and ref:
            ref_directives.append(
                "Fixed Fujifilm GFX100RF 102MP restoration lock: Use attached image as single source of truth. "
                "Human skin realism strictly overrides sharpness: skin remains naturally soft compared to eyes, hair, teeth, jewelry, and text. "
                "Preserve all visible text exactly without paraphrasing."
            )
            if scene.content_type and scene.content_type.is_flat_reproduction:
                ref_directives.append("Render as flat reproduction capture suppressing optical falloff, vignetting, and grain.")
        elif is_identity_lock and ref:
            ref_directives.append(
                f"Strict anatomical identity lock ({int(ref.fidelity_lock * 100)}% lock): "
                f"Subject must strictly preserve facial geometry, bone structure, body proportions, mass, "
                f"hair, and beard pattern from reference image with zero morphological drift or alteration."
            )
        elif is_restore and ref:
            ref_directives.append(
                f"Strict optical preservation directive ({int(ref.fidelity_lock * 100)}% identity lock): "
                f"Elevate image fidelity to true {optics.camera_system} resolution while maintaining exact "
                f"{', '.join(ref.preserved_elements)} from the reference image with zero morphological change."
            )
        elif is_transform and ref:
            ref_directives.append(
                f"Biometric anchor directive ({int(ref.fidelity_lock * 100)}% lock): "
                f"Strictly preserve {', '.join(ref.preserved_elements)} from reference image, "
                f"preventing facial drift, altered bone structure, or synthetic distortion while adapting context."
            )
        elif is_product_lock:
            ref_directives.append(
                "Commercial SKU 100% Approval Gate: Sellable object must match attached product crop 100%. "
                "Cap geometry, closure threading, label kerning, typographic tracking, mold parting seams, and SKU color are locked. "
                "Reject any distortion, cap substitution, or text hallucination."
            )
        elif is_recon_4x:
            recon = scene.reconstruction_lock
            b_val = recon.backend.value if recon else "realesrnet_x4plus"
            ref_directives.append(
                f"Strict 4X Linear Reconstruction Lock: Absolute photographic geometry lock. "
                f"Output strictly at 4X linear scale (16X pixel area). Backend {b_val}. "
                "Atmospheric and sky gradients protected from noise. Anti-model stacking strictly enforced. "
                "Zero generative hallucination or geological drift."
            )

        if scene.has_body_morphology:
            regions = scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else "biceps, chest, gut")
            wt = f" with calibrated body mass {scene.weight_lb} lbs" if scene.weight_lb else ""
            ref_directives.append(
                f"Proportional Body Volume Calibration ({regions}{wt}): "
                "Enlarged physical regions remain strictly proportional to skeletal frame, head size, and total mass; "
                "preserve authentic bilateral asymmetry, realistic soft-tissue gravity and seated compression, "
                "and natural clothing conformity with zero ballooning or caricature exaggeration."
            )
        if scene.has_material_style:
            mat_desc = scene.material_style.value.replace("_", " ") if scene.material_style and scene.material_style != MaterialStyle.NONE else "dimensional volumetric finish"
            bg_str = f" against {scene.background_style.value.replace('_', ' ')} background" if scene.background_style and scene.background_style != BackgroundStyle.DEFAULT else ""
            ref_directives.append(
                f"4D Volumetric & Premium Material Engine: Rendered with {mat_desc}{bg_str}, "
                "sculpted contour rim lighting, controlled specular highlights, deep tonal separation, "
                "and authentic material micro-physics without synthetic plastic sheen."
            )
        if scene.remove_text_when_present:
            ref_directives.append("Remove visible text and lettering cleanly, filling background contextually.")
        if scene.is_print_calibrated:
            paper_name = scene.paper_profile.value.replace("_", " ") if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value.replace("_", " ") if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else "exhibition fine art paper")
            ref_directives.append(f"Print-calibrated exhibition prepress specification for {paper_name}, preserving tonal gradient depth and Dmax response.")
        ref_prose = (" " + " ".join(ref_directives)) if ref_directives else ""

        # 2. Optical rig description in natural photography prose
        optical_components = [
            f"Captured with a {optics.camera_system} utilizing a {optics.lens} stopped down to its {optics.aperture_sweet_spot} optical sweet spot.",
            f"Framed with a {optics.sensor_dimensions} ({optics.full_frame_equivalent}), utilizing {optics.shutter} and {optics.iso_base}."
        ]
        if scene.is_anamorphic:
            squeeze = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
            flare = scene.streak_flare.value.replace("_", " ") if scene.streak_flare else "cyan/blue"
            blades = scene.iris_blades.value.replace("_", " ") if scene.iris_blades else "14-blade circular"
            optical_components.append(
                f"Cinema anamorphic optics featuring {squeeze} squeeze factor, {flare} horizontal streak flares, and {blades} iris yielding vertical 2:1 elliptical oval bokeh discs."
            )
        if scene.optical_filter:
            optical_components.append(f"Front-mounted optical element: {scene.optical_filter}.")
        if scene.film_stock:
            optical_components.append(f"Color rendition & emulsion profile: {scene.film_stock}.")
        optical_prose = " ".join(optical_components)

        # 3. Lighting & physical transport
        lighting_parts = [f"Lighting: {lighting.primary_lighting}. {lighting.light_transport}."]
        if scene.lighting_ratio:
            lighting_parts.append(f"Key-to-fill contrast balanced at a precise {scene.lighting_ratio.value} lighting ratio.")
        if scene.gobo:
            gobo_desc = scene.gobo.value.replace("_", " ")
            lighting_parts.append(f"Projected through an optical {gobo_desc} gobo cookie producing crisp architectural shadow patterns.")
        if scene.grip_modifier:
            grip_desc = scene.grip_modifier.value.replace("_", " ")
            lighting_parts.append(f"Shaped with professional {grip_desc} studio grip.")
        lighting_prose = " ".join(lighting_parts)

        # 4. Micro-physics & texture enforcement
        micro_parts = [
            f"Detail fidelity: {micro.surface_rendering[0]}.",
            f"{micro.surface_rendering[1]}.",
            f"{micro.depth_and_optics[0]}.",
        ]
        is_slow_shutter = (
            scene.capture_mode == "slow_shutter_crowd_motion"
            or (hasattr(scene.capture_mode, "value") and scene.capture_mode.value == "slow_shutter_crowd_motion")
            or bool(scene.crowd_action)
            or (profile.profile_id == "leica_sl2" and "motion" in scene.subject.lower())
        )
        if is_product_lock:
            micro_parts.append(
                "Focus discipline: critical focal plane locked on primary product branding, typography, and container shoulder seam with edge-to-edge optical acutance."
            )
        elif is_slow_shutter:
            micro_parts.append(
                "Focus discipline: focus locked on near eye with eyelashes and iris tack sharp, subject completely stationary with zero subject motion blur while crowd flows with smooth motion blur trails."
            )
        elif scene.sharpness_protocol:
            micro_parts.append(
                "Focus discipline: focus locked on the near eye with eyelashes and iris tack sharp, zero motion blur."
            )
        micro_prose = " ".join(micro_parts)

        # 5. Aesthetic directive and final output resolution
        if is_depixelate:
            res_text = scene.output_resolution or "102MP Medium Format (11648 x 8736 native GFX100RF resolution)"
        elif is_recon_4x:
            res_text = scene.output_resolution or "Exact 4X Linear Source-Locked Reconstruction (16X pixel area)"
        else:
            res_text = scene.output_resolution or f"12MP PNG, vertical {scene.aspect_ratio}"
        style_prose = (
            f"Aesthetic directive: {profile.execution_directive} "
            f"Output: {res_text}, uncompressed 16-bit raw capture, maximum acutance, zero chroma subsampling. "
            f"Completely avoid {', '.join(shield.skin_and_lighting_drift[:4])}, "
            f"and eliminate {', '.join(shield.render_defects[:4])}."
        )
        if scene.suppress_text_branding and not is_product_lock:
            style_prose += " Strictly eliminate all text, watermarks, logos, brand names, and typography."
        if is_restore or is_transform or is_outpaint or is_depixelate or is_identity_lock:
            style_prose += " Eliminate facial morphing, feature drift, identity loss, and warped geometry."
        if is_recon_4x:
            style_prose += " Eliminate generative hallucination, altered terrain, rock strata distortion, sky grain, and stacking halos."
        if is_product_lock:
            style_prose += " Eliminate wrong cap geometry, incorrect label kerning, sku color drift, missing seams, and packaging distortion."
        if scene.has_hand_lock:
            style_prose += " Eliminate fused fingers, missing knuckles, rubber joints, clipping digits, and hand mutations."
        if scene.has_body_morphology:
            style_prose += " Eliminate balloon muscles, grotesque proportions, comic-book anatomy, and body distortion."

        extra_directives = []
        if scene.has_stress_probe and scene.stress_probe:
            extra_directives.append(scene.stress_probe.directive_text)
        if scene.has_lighting_environment and scene.lighting_environment:
            le = scene.lighting_environment
            extra_directives.append(
                f"Exhibition lighting calibrated for gallery display at {le.illuminance_lux} lux, {le.cct_kelvin}K CCT, CRI {le.spectral_cri} against {le.wall_surround} surround."
            )
        if scene.has_series_cohesion and scene.series_cohesion:
            sc = scene.series_cohesion
            extra_directives.append(
                f"Series visual cohesion anchored to {sc.anchor_image_id or 'master'} in {sc.gallery_zone or 'gallery zone'} with midtone density {sc.midtone_density} and shadow depth {sc.shadow_depth}."
            )
        if scene.min_file_mb:
            extra_directives.append(f"Minimum uncompressed output target: {scene.min_file_mb:.1f} MB.")

        extra_prose = (" " + " ".join(extra_directives)) if extra_directives else ""
        positive_prompt = f"{scene_core}{ref_prose} {optical_prose} {lighting_prose} {micro_prose} {style_prose}{extra_prose}"


        # Negative prompt payload
        include_anti_drift = bool(is_restore or is_transform or is_outpaint or is_depixelate or is_identity_lock or is_product_lock or is_recon_4x or is_png_lock)
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
        )
        if scene.custom_negatives:
            all_negatives.extend(scene.custom_negatives)
        negative_prompt = ", ".join(dict.fromkeys(all_negatives))

        parameters = {
            "aspect_ratio": scene.aspect_ratio,
            "resolution": res_text,
            "safety_filter_level": "block_medium_and_above",
            "person_generation": "allow_adult",
        }
        if is_png_lock:
            parameters.update({
                "png_output_lock": True,
                "color_mode": "RGB",
                "compress_level": 0,
                "linear_scale": 4,
            })
        if is_outpaint:
            parameters.update({
                "reference_mode": "outpaint_full_body",
                "outpaint_direction": "downward",
                "head_to_toe": True,
            })
        elif is_restore and ref:
            parameters.update({
                "reference_mode": "restore_upscale",
                "fidelity_lock": f"{int(ref.fidelity_lock * 100)}%",
                "denoising_strength": ref.denoise_strength,
            })
        elif is_transform and ref:
            parameters.update({
                "reference_mode": "transform_adapt",
                "fidelity_lock": f"{int(ref.fidelity_lock * 100)}%",
                "denoising_strength": ref.denoise_strength,
            })

        metadata = {
            "camera_system": optics.camera_system,
            "lens": optics.lens,
            "aperture": optics.aperture_sweet_spot,
            "sensor": optics.sensor_dimensions,
            "shutter_sync": optics.shutter,
            "dynamic_range": optics.dynamic_range,
        }
        if ref and ref.filename:
            metadata["reference_image"] = ref.filename

        return CompiledPayload(
            target_engine=self.target_engine,
            positive_prompt=positive_prompt.strip(),
            negative_prompt=negative_prompt,
            parameters=parameters,
            metadata=metadata,
        )

"""Adapter for Black Forest Labs Flux.1 (Dev / Schnell)."""

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


class FluxAdapter(BaseAdapter):
    """Compiles prompts into direct, technical physical descriptions optimized for Flux.1."""

    target_engine = TargetEngine.FLUX

    def compile(self, scene: SceneInput, profile: CameraProfile) -> CompiledPayload:
        optics = profile.sensor_and_optics
        lighting = profile.lighting_and_exposure
        micro = profile.micro_detail_and_physics
        shield = profile.negative_embeddings
        ref = scene.reference

        # Flux thrives on clear, factual, declaratively structured sentences
        sections = []

        is_restore = ref and ref.mode == ReferenceMode.RESTORE_UPSCALE
        is_transform = ref and ref.mode == ReferenceMode.TRANSFORM_ADAPT
        is_outpaint = ref and ref.mode == ReferenceMode.OUTPAINT_FULL_BODY
        is_depixelate = ref and ref.mode == ReferenceMode.DEPIXELATE_GFX100RF
        is_identity_lock = ref and ref.mode == ReferenceMode.IDENTITY_LOCK
        is_product_lock = (ref and ref.mode == ReferenceMode.PRODUCT_LOCK) or scene.has_product_lock

        # 1. Subject & Scene
        if scene.is_policy_safe:
            sections.append(
                "Policy-Safe Compliance Directive: Dignified, tasteful editorial photographic execution adhering to platform ethical guidelines with fully clothed subjects and authentic camera physics."
            )
        subject_desc = scene.subject
        if scene.framing:
            subject_desc = f"{scene.framing} of {scene.subject}"
        if scene.environment:
            subject_desc += f", in {scene.environment}"
        if scene.wardrobe:
            subject_desc += f", wearing {scene.wardrobe}"
        if scene.mood:
            subject_desc += f", {scene.mood}"

        if is_outpaint:
            sections.append(
                "Using the provided medium-shot photo as the base. Outpaint and extend the frame downward to a full-body portrait. "
                "Preserve the subject's face, identity, expression, hair, and skin texture exactly as in the input image. "
                "Keep the same wardrobe, colors, fabric texture, and wrinkles. Maintain the same camera height and perspective. "
                f"No wide-angle distortion. Full body head-to-toe visible including shoes. Depicting {subject_desc}."
            )
        elif is_product_lock:
            sections.append(
                f"Commercial studio packshot with 100% SKU lock to reference product crop. "
                f"Photo of {subject_desc}. The sellable commercial object must strictly match the product crop in geometry, "
                f"proportions, closure mechanics, label typography, and color without drift or redesign."
            )
            if scene.cap_geometry:
                sections.append(f"Cap and closure geometry: {scene.cap_geometry}.")
            if scene.label_kerning:
                sections.append(f"Label typography and kerning: {scene.label_kerning}.")
            if scene.seam_geometry:
                sections.append(f"Manufacturing seams: {scene.seam_geometry}.")
            if scene.material_finish:
                sections.append(f"Material finish: {scene.material_finish}.")
            if scene.sku_color:
                sections.append(f"SKU color: {scene.sku_color}.")
            if scene.approval_gate_100pct:
                sections.append(
                    "100% Commercial SKU Approval Gate: Reject any render with incorrect cap geometry, altered label kerning, "
                    "missing mold seams, shifted SKU color, or synthetic material finish."
                )
        elif is_identity_lock:
            sections.append(
                f"Documentary editorial portrait with strict reference identity lock. "
                f"Photo of {subject_desc}. Subject must strictly follow the anatomical structure, facial geometry, "
                f"body proportions, mass, hair, and beard pattern from reference image. "
                f"Prohibit gender reinterpretation, age alteration, body slimming, facial restructuring, and skin smoothing."
            )
        elif is_depixelate:
            sections.append(
                f"Universal De-Pixelate and 102MP Upscale Restoration of source reference image. "
                f"Photo of {subject_desc} rendered with fixed Fujifilm GFX100RF 102MP signature. "
                f"Eliminating pixelation, blockiness, aliasing, and compression artifacts while strictly preserving "
                f"source identity, composition, proportions, colors, and all visible text."
            )
            if scene.human_skin_realism:
                sections.append(
                    "Human skin realism override: Real organic skin softer than eyes, hair, jewelry, and text. "
                    "No pore stamping, no AI swirls, no synthetic skin grain."
                )
            if scene.content_type and scene.content_type.is_flat_reproduction:
                sections.append(
                    "Flat reproduction capture: Suppress optical depth-of-field falloff, vignetting, and grain."
                )
        elif is_restore:
            sections.append(
                f"Master optical remaster and high-resolution restoration of source reference image. "
                f"Photo of {subject_desc} with 1:1 biometric identity lock and physical surface reconstruction."
            )
            if ref and ref.preserved_elements:
                sections.append(f"Strictly preserve from reference image: {', '.join(ref.preserved_elements)}.")
            lock_pct = int(ref.fidelity_lock * 100) if ref else 95
            sections.append(
                f"Extreme anti-drift constraint ({lock_pct}% fidelity lock): Zero facial alteration, "
                f"zero landmark displacement, zero hallucinated background structures."
            )
        elif is_transform:
            sections.append(
                f"Photographic adaptation and contextual transformation of source reference image. "
                f"Preserving the biometric identity, facial bone structure, gaze, and proportions from reference image, "
                f"adapted into: {subject_desc}."
            )
            if ref and ref.preserved_elements:
                sections.append(f"Identity anchor: {', '.join(ref.preserved_elements)} strictly locked to reference.")
            lock_pct = int(ref.fidelity_lock * 100) if ref else 95
            sections.append(
                f"Strict anti-hallucination constraint ({lock_pct}% biometric lock): Prevent facial morphing, "
                f"feature drift, phantom limbs, or identity divergence while rendering new environmental context."
            )
        else:
            sections.append(f"Photo of {subject_desc}.")
        if scene.camera_angle:
            sections.append(f"Angle and perspective: {scene.camera_angle}.")
        if scene.has_copy_space:
            if scene.copy_space and scene.copy_space != CopySpace.NONE:
                sections.append(
                    f"Commercial negative copy-space: Reserved in the {scene.copy_space.value.replace('_', ' ')} of the frame with calm, uncluttered background for brand headline typography."
                )
            if scene.ad_safe_zone and scene.ad_safe_zone != AdSafeZone.NONE:
                sections.append(
                    f"Advertising safe zone: Structured according to {scene.ad_safe_zone.value.replace('_', ' ')} guidelines, keeping subject and hands clear of UI overlays."
                )
        if scene.has_hand_lock:
            grip_desc = scene.grip_type.value.replace("_", " ") if scene.grip_type else "ergonomic contact grip"
            details = f" ({scene.hand_details})" if scene.hand_details else ""
            sections.append(
                f"Biomechanical 5-Point Hand Precision Gate ({grip_desc}{details}): Render five fully articulated human digits with correct metacarpal proportions (2:3:4:3.5:2.5 ratio), distinct knuckles and joints, palmar flexion creases, realistic micro contact blanching where skin presses against objects, translucent nail beds with lunula, and zero finger mutations."
            )
        if scene.crowd_action:
            sections.append(
                f"Crowd dynamics: {scene.crowd_action}. Smooth multi-directional motion blur trails wrapping around still subject without anatomical deformation."
            )
        if scene.is_monochrome:
            sections.append(
                "Tonal response: Restrained black-and-white indie-cinema monochrome, gentle highlight roll-off, clean midtones, no HDR, fine subtle organic film grain."
            )

        if scene.has_body_morphology:
            regions = scene.body_volume or (", ".join(scene.body_morphology.volume_regions) if scene.body_morphology and scene.body_morphology.volume_regions else "biceps, chest, gut")
            wt = f" with calibrated body mass {scene.weight_lb} lbs" if scene.weight_lb else ""
            sections.append(
                f"Proportional Body Volume Calibration ({regions}{wt}): All enlarged regions strictly proportional to skeletal frame and head size; "
                "preserving authentic bilateral asymmetry, realistic soft-tissue gravity and seated compression, and natural clothing conformity without comic-book exaggeration."
            )

        if scene.has_material_style:
            mat_desc = scene.material_style.value.replace("_", " ") if scene.material_style and scene.material_style != MaterialStyle.NONE else "dimensional volumetric finish"
            bg_desc = f" Background: {scene.background_style.value.replace('_', ' ')}." if scene.background_style and scene.background_style != BackgroundStyle.DEFAULT else ""
            sections.append(
                f"4D Volumetric & Premium Material Engine: Rendered with {mat_desc},{bg_desc} sculpted contour rim lighting, controlled specular highlights, deep tonal separation, and physical micro-relief."
            )

        if scene.remove_text_when_present:
            sections.append("Text removal engine: Cleanly remove visible text, typography, and lettering, seamlessly filling background contextually.")

        if scene.is_print_calibrated:
            paper_name = scene.paper_profile.value.replace("_", " ") if scene.paper_profile and scene.paper_profile != PaperProfile.NONE else (scene.print_spec.paper.value.replace("_", " ") if scene.print_spec and scene.print_spec.paper != PaperProfile.NONE else "exhibition fine art paper")
            sections.append(f"Print-calibrated exhibition prepress specification for {paper_name}, preserving tonal gradient depth, Dmax response, and zero digital banding.")

        # 2. Exact physical camera rig
        camera_parts = [
            f"Shot on a {optics.camera_system}, {optics.lens} set to {optics.aperture_sweet_spot},",
            f"{optics.sensor_dimensions} with {optics.full_frame_equivalent}.",
            f"{optics.iso_base}, {optics.shutter}."
        ]
        if scene.is_anamorphic:
            squeeze = scene.anamorphic_squeeze.value if scene.anamorphic_squeeze else "2.0x"
            flare = scene.streak_flare.value.replace("_", " ") if scene.streak_flare else "cyan/blue"
            blades = scene.iris_blades.value.replace("_", " ") if scene.iris_blades else "14-blade circular"
            camera_parts.append(
                f"Cinema anamorphic optics: {squeeze} cylindrical squeeze, {flare} horizontal streak flare, and {blades} iris yielding vertical 2:1 elliptical oval bokeh discs."
            )
        if scene.optical_filter:
            camera_parts.append(f"Front optical element: {scene.optical_filter}.")
        if scene.film_stock:
            camera_parts.append(f"Emulsion / color response: {scene.film_stock}.")
        camera_desc = " ".join(camera_parts)
        sections.append(camera_desc)

        # 3. Studio lighting & light transport
        lighting_parts = [f"Lighting: {lighting.primary_lighting}. {lighting.light_transport}."]
        if scene.lighting_ratio:
            lighting_parts.append(f"Key-to-fill lighting contrast ratio: {scene.lighting_ratio.value}.")
        if scene.gobo:
            gobo_desc = scene.gobo.value.replace("_", " ")
            lighting_parts.append(f"Optical {gobo_desc} gobo cookie projection casting architectural shadow silhouettes.")
        if scene.grip_modifier:
            grip_desc = scene.grip_modifier.value.replace("_", " ")
            lighting_parts.append(f"Studio grip: {grip_desc}.")
        lighting_desc = " ".join(lighting_parts)
        sections.append(lighting_desc)

        # 4. Micro-texture & physical rendering
        micro_parts = [
            f"Sensor detail: {micro.surface_rendering[0]}.",
            f"{micro.surface_rendering[1]}.",
            f"{micro.surface_rendering[2]}.",
            f"{micro.depth_and_optics[0]} and {micro.depth_and_optics[1].lower()}."
        ]
        is_slow_shutter = (
            scene.capture_mode == "slow_shutter_crowd_motion"
            or (hasattr(scene.capture_mode, "value") and scene.capture_mode.value == "slow_shutter_crowd_motion")
            or bool(scene.crowd_action)
            or (profile.profile_id == "leica_sl2" and "motion" in scene.subject.lower())
        )
        if is_product_lock:
            micro_parts.append(
                "Focus discipline: critical focal plane locked on primary product branding label and container shoulder seam with edge-to-edge optical acutance."
            )
        elif is_slow_shutter:
            micro_parts.append(
                "Focus discipline: focus locked on near eye with eyelashes and iris tack sharp, subject completely stationary with zero subject motion blur while crowd flows with smooth motion blur trails."
            )
        elif scene.sharpness_protocol:
            micro_parts.append(
                "Focus discipline: focus locked on near eye with eyelashes and iris tack sharp, zero motion blur."
            )
        micro_desc = " ".join(micro_parts)
        sections.append(micro_desc)

        # 5. Output quality & resolution targets
        if is_depixelate:
            res_text = scene.output_resolution or "102MP Medium Format (11648 x 8736 native GFX100RF resolution)"
        else:
            res_text = scene.output_resolution or f"12MP PNG, vertical {scene.aspect_ratio}"
        output_desc = (
            f"Rendering target: {res_text}, uncompressed 16-bit raw tonal latitude, "
            f"zero lossy compression, native optical MTF acutance without digital edge halos."
        )
        sections.append(output_desc)

        if scene.has_stress_probe and scene.stress_probe:
            sections.append(scene.stress_probe.directive_text)
        if scene.has_lighting_environment and scene.lighting_environment:
            le = scene.lighting_environment
            sections.append(
                f"Exhibition lighting calibrated for gallery display at {le.illuminance_lux} lux, {le.cct_kelvin}K CCT, with TM-30/CRI {le.spectral_cri} spectral fidelity against {le.wall_surround} surround."
            )
        if scene.has_series_cohesion and scene.series_cohesion:
            sc = scene.series_cohesion
            sections.append(
                f"Series visual cohesion anchored to {sc.anchor_image_id or 'master'} in {sc.gallery_zone or 'gallery zone'} with midtone density {sc.midtone_density} and shadow depth {sc.shadow_depth}."
            )
        if scene.min_file_mb:
            sections.append(f"Minimum uncompressed output target: {scene.min_file_mb:.1f} MB.")

        # 6. Natural language negative constraints (Flux thrives on explicit negative assertions in context)

        banned_tropes = (
            f"Output: {res_text}, uncompressed 16-bit raw capture, lossless acutance, zero chroma subsampling. "
            "Eliminate plastic or poreless airbrushed skin, synthetic beauty filters, "
            "fake computational bokeh, digital sharpening halos, chromatic aberration, "
            "and CGI 3D render looks."
        )
        if scene.human_skin_realism or is_depixelate:
            banned_tropes += (
                " Strictly eliminate pore stamping, engraved skin, carved skin, swirl texture, "
                "repeating micro-patterns, lace-like facial texture, worm-like texture, and AI skin grain."
            )
        if scene.suppress_text_branding and not is_product_lock:
            banned_tropes += " Eliminate all text, watermarks, logos, brand names, and typography."
        if is_restore or is_transform or is_outpaint or is_depixelate or is_identity_lock:
            banned_tropes += (
                " Eliminate facial morphing, identity loss, altered bone structure, "
                "warped geometry, and hallucinated anatomical features."
            )
        if is_product_lock:
            banned_tropes += (
                " Eliminate wrong cap geometry, distorted cap, incorrect label kerning, "
                "hallucinated text, wrong sku color, color drift, missing seams, and packaging distortion."
            )
        if is_slow_shutter:
            banned_tropes += " Eliminate ghost faces, melted bodies, duplicated people, uniform smear wall, and blur on the subject."
        if is_outpaint:
            banned_tropes += " Eliminate mismatched shoes, twisted legs, floating feet, and distorted scale."
        if scene.has_hand_lock:
            banned_tropes += " Eliminate fused digits, clipping fingers, extra phalanges, rubber knuckles, dislocated thumbs, missing knuckles, and deformed nails."
        if scene.has_body_morphology:
            banned_tropes += " Eliminate balloon muscles, cartoon proportions, comic-book anatomy, hyper-vascularity, and grotesque body distortion."
        if scene.remove_text_when_present:
            banned_tropes += " Eliminate visible letters, text, typography, and words."
        sections.append(banned_tropes)

        positive_prompt = " ".join(sections)

        # Negative prompt payload
        include_anti_drift = bool(is_restore or is_transform or is_outpaint or is_depixelate or is_identity_lock or is_product_lock)
        all_negatives = shield.all_tokens(
            include_anti_drift=include_anti_drift,
            include_branding=scene.suppress_text_branding and not is_product_lock,
            include_compression=True,
            include_outpaint=is_outpaint,
            include_skin_realism=scene.human_skin_realism,
            include_product_drift=is_product_lock,
            include_hand_drift=scene.has_hand_lock,
            include_body_distortion=scene.has_body_morphology,
        )
        if scene.custom_negatives:
            all_negatives.extend(scene.custom_negatives)
        negative_prompt = ", ".join(dict.fromkeys(all_negatives))

        parameters = {
            "aspect_ratio": scene.aspect_ratio,
            "resolution": res_text,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
        }

        if is_outpaint:
            parameters.update({
                "reference_mode": "outpaint_full_body",
                "outpaint_direction": "downward",
                "head_to_toe": True,
            })
        elif is_restore and ref:
            parameters.update({
                "reference_mode": "restore_upscale",
                "denoising_strength": ref.denoise_strength,
                "fidelity_lock": f"{int(ref.fidelity_lock * 100)}%",
                "controlnet_tile_weight": 0.85,
                "flux_redux_strength": 0.90,
            })
        elif is_transform and ref:
            parameters.update({
                "reference_mode": "transform_adapt",
                "denoising_strength": ref.denoise_strength,
                "fidelity_lock": f"{int(ref.fidelity_lock * 100)}%",
                "flux_redux_strength": 0.80,
                "ip_adapter_weight": 0.85,
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
            positive_prompt=positive_prompt.strip(),
            negative_prompt=negative_prompt,
            parameters=parameters,
            metadata=metadata,
        )

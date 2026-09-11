"""Adapter for Google Imagen 3 and Gemini multimodal generation."""

from __future__ import annotations

from ..models import CameraProfile, CompiledPayload, ReferenceMode, SceneInput, TargetEngine
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

        # 1. Subject & Scene foundation
        scene_elements = []
        if is_outpaint:
            scene_elements.append(
                "Using the provided medium-shot photo as the base. Outpaint and extend the frame downward to a full-body portrait. "
                "Preserve the subject's face, identity, expression, hair, and skin texture exactly as in the input image. "
                "Keep the same wardrobe, colors, fabric texture, and wrinkles. Maintain the same camera height and perspective. "
                f"No wide-angle distortion. Full body head-to-toe visible including shoes. Depicting {scene.subject}"
            )
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

        scene_core = ", ".join(scene_elements) + "."

        # Reference-specific anchor instructions
        ref_directives = []
        if is_restore and ref:
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
        ref_prose = (" " + " ".join(ref_directives)) if ref_directives else ""

        # 2. Optical rig description in natural photography prose
        optical_components = [
            f"Captured with a {optics.camera_system} utilizing a {optics.lens} stopped down to its {optics.aperture_sweet_spot} optical sweet spot.",
            f"Framed with a {optics.sensor_dimensions} ({optics.full_frame_equivalent}), utilizing {optics.shutter} and {optics.iso_base}."
        ]
        if scene.optical_filter:
            optical_components.append(f"Front-mounted optical element: {scene.optical_filter}.")
        if scene.film_stock:
            optical_components.append(f"Color rendition & emulsion profile: {scene.film_stock}.")
        optical_prose = " ".join(optical_components)

        # 3. Lighting & physical transport
        lighting_prose = (
            f"Lighting: {lighting.primary_lighting}. {lighting.light_transport}."
        )

        # 4. Micro-physics & texture enforcement
        micro_parts = [
            f"Detail fidelity: {micro.surface_rendering[0]}.",
            f"{micro.surface_rendering[1]}.",
            f"{micro.depth_and_optics[0]}, with {micro.depth_and_optics[1].lower()}."
        ]
        if scene.sharpness_protocol:
            micro_parts.append(
                "Focus discipline: focus locked on the near eye with eyelashes and iris tack sharp, zero motion blur."
            )
        micro_prose = " ".join(micro_parts)

        # 5. Natural anti-artifact directive & Quality scaling
        res_text = scene.output_resolution or f"12MP PNG, vertical {scene.aspect_ratio}"
        style_prose = (
            f"Aesthetic directive: {profile.execution_directive} "
            f"Output: {res_text}, uncompressed 16-bit raw capture, maximum acutance, zero chroma subsampling. "
            f"Completely avoid {', '.join(shield.skin_and_lighting_drift[:4])}, "
            f"and eliminate {', '.join(shield.render_defects[:4])}."
        )
        if scene.suppress_text_branding:
            style_prose += " Strictly eliminate all text, watermarks, logos, brand names, and typography."
        if is_restore or is_transform or is_outpaint:
            style_prose += " Eliminate facial morphing, feature drift, identity loss, and warped geometry."

        positive_prompt = f"{scene_core}{ref_prose} {optical_prose} {lighting_prose} {micro_prose} {style_prose}"

        # Negative prompt payload
        include_anti_drift = bool(is_restore or is_transform or is_outpaint)
        all_negatives = shield.all_tokens(
            include_anti_drift=include_anti_drift,
            include_branding=scene.suppress_text_branding,
            include_compression=True,
            include_outpaint=is_outpaint,
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

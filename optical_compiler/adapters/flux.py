"""Adapter for Black Forest Labs Flux.1 (Dev / Schnell)."""

from __future__ import annotations

from ..models import CameraProfile, CompiledPayload, ReferenceMode, SceneInput, TargetEngine
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

        # 1. Subject & Scene
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

        # 2. Exact physical camera rig
        camera_parts = [
            f"Shot on a {optics.camera_system}, {optics.lens} set to {optics.aperture_sweet_spot},",
            f"{optics.sensor_dimensions} with {optics.full_frame_equivalent}.",
            f"{optics.iso_base}, {optics.shutter}."
        ]
        if scene.optical_filter:
            camera_parts.append(f"Front optical element: {scene.optical_filter}.")
        if scene.film_stock:
            camera_parts.append(f"Emulsion / color response: {scene.film_stock}.")
        camera_desc = " ".join(camera_parts)
        sections.append(camera_desc)

        # 3. Studio lighting & light transport
        lighting_desc = f"Lighting: {lighting.primary_lighting}. {lighting.light_transport}."
        sections.append(lighting_desc)

        # 4. Micro-texture & physical rendering
        micro_parts = [
            f"Sensor detail: {micro.surface_rendering[0]}.",
            f"{micro.surface_rendering[1]}.",
            f"{micro.surface_rendering[2]}.",
            f"{micro.depth_and_optics[0]} and {micro.depth_and_optics[1].lower()}."
        ]
        if scene.sharpness_protocol:
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
        if scene.suppress_text_branding:
            banned_tropes += " Eliminate all text, watermarks, logos, brand names, and typography."
        if is_restore or is_transform or is_outpaint or is_depixelate:
            banned_tropes += (
                " Eliminate facial morphing, identity loss, altered bone structure, "
                "warped geometry, and hallucinated anatomical features."
            )
        if is_outpaint:
            banned_tropes += " Eliminate mismatched shoes, twisted legs, floating feet, and distorted scale."
        sections.append(banned_tropes)

        positive_prompt = " ".join(sections)

        # Negative prompt payload
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

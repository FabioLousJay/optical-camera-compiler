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

        if is_restore:
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
        micro_desc = (
            f"Sensor detail: {micro.surface_rendering[0]}. "
            f"{micro.surface_rendering[1]}. "
            f"{micro.surface_rendering[2]}. "
            f"{micro.depth_and_optics[0]} and {micro.depth_and_optics[1].lower()}."
        )
        sections.append(micro_desc)

        # 5. Anti-synthetic assertions woven directly into prompt (critical for Flux)
        banned_tropes = (
            "Eliminate plastic or poreless airbrushed skin, synthetic beauty filters, "
            "fake computational bokeh, digital sharpening halos, chromatic aberration, "
            "and CGI 3D render looks."
        )
        if is_restore or is_transform:
            banned_tropes += (
                " Eliminate facial morphing, identity loss, altered bone structure, "
                "warped geometry, and hallucinated anatomical features."
            )
        sections.append(banned_tropes)

        positive_prompt = " ".join(sections)

        # Flux typically runs without CFG-based negative prompts, but we retain it for pipelines that support it
        include_anti_drift = bool(is_restore or is_transform)
        all_negatives = shield.all_tokens(include_anti_drift=include_anti_drift)
        if scene.custom_negatives:
            all_negatives.extend(scene.custom_negatives)
        negative_prompt = ", ".join(dict.fromkeys(all_negatives))

        parameters = {
            "aspect_ratio": scene.aspect_ratio,
            "guidance_scale": 3.5,
            "num_inference_steps": 28,
        }

        if is_restore and ref:
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
